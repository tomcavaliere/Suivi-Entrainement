"""
Dashboard Nutrition & Entraînement — Athlète d'endurance
========================================================
Lancer : streamlit run app.py
"""

import io
import json
import re
import sqlite3
from datetime import date, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from PIL import Image

try:
    import fitparse
    FITPARSE_AVAILABLE = True
except ImportError:
    FITPARSE_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

OCR_AVAILABLE = EASYOCR_AVAILABLE or PYTESSERACT_AVAILABLE

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
DB_PATH = Path(__file__).parent / "sports_nutrition.db"

MEAL_TYPES = [
    "Petit-déjeuner",
    "Collation post-effort",
    "Déjeuner",
    "Goûter",
    "Dîner",
    "Pendant l'effort",
]

MEAL_EMOJI = {
    "Petit-déjeuner":        "🌅",
    "Collation post-effort": "⚡",
    "Déjeuner":              "☀️",
    "Goûter":                "🍎",
    "Dîner":                 "🌙",
    "Repas":                 "🍽️",
    "Pendant l'effort":      "🏃",
}

MEAL_DEFAULT_TIME = {
    "Petit-déjeuner":        time(7, 30),
    "Collation post-effort": time(10, 0),
    "Déjeuner":              time(12, 30),
    "Goûter":                time(16, 0),
    "Dîner":                 time(19, 30),
    "Pendant l'effort":      time(10, 0),
}

_COLORS = {"Glucides": "#2ecc71", "Protéines": "#3498db", "Lipides": "#e67e22"}
_ZONE_COLORS = ["#95a5a6", "#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"]
_ZONE_LABELS = ["Z1 Récup", "Z2 Aérobie", "Z3 Tempo", "Z4 Seuil", "Z5 PMA"]

# ─────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS favorite_foods (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        carbs_per_100 REAL NOT NULL,
        protein_per_100 REAL NOT NULL,
        fat_per_100 REAL NOT NULL,
        kcal_per_100 REAL NOT NULL,
        salt_per_100 REAL NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        meal_type TEXT NOT NULL DEFAULT 'Repas',
        meal_time TEXT NOT NULL DEFAULT '12:00',
        food_name TEXT NOT NULL,
        quantity_g REAL NOT NULL,
        carbs_g REAL NOT NULL,
        protein_g REAL NOT NULL,
        fat_g REAL NOT NULL,
        kcal REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        type TEXT NOT NULL,
        duration_min INTEGER NOT NULL,
        elevation_m INTEGER DEFAULT 0,
        intensity TEXT NOT NULL DEFAULT 'Zone 2',
        kcal_actual REAL,
        avg_hr INTEGER,
        max_hr_session INTEGER,
        hr_z1_min REAL DEFAULT 0,
        hr_z2_min REAL DEFAULT 0,
        hr_z3_min REAL DEFAULT 0,
        hr_z4_min REAL DEFAULT 0,
        hr_z5_min REAL DEFAULT 0,
        source TEXT DEFAULT 'manual'
    );
    CREATE TABLE IF NOT EXISTS weight_log (
        date TEXT PRIMARY KEY,
        weight_kg REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS morning_log (
        date TEXT PRIMARY KEY,
        weight_kg REAL,
        sleep_duration_h REAL,
        sleep_quality INTEGER,
        hrv_readiness REAL,
        hrv_rmssd REAL,
        hrv_pns REAL,
        hrv_sns REAL,
        hrv_mean_hr REAL,
        hrv_time TEXT
    );
    CREATE TABLE IF NOT EXISTS daily_scores (
        date TEXT PRIMARY KEY,
        fatigue INTEGER NOT NULL,
        satiety INTEGER NOT NULL,
        sleep_quality INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY CHECK (id=1),
        weight_kg REAL NOT NULL DEFAULT 72.0,
        height_cm INTEGER NOT NULL DEFAULT 178,
        age INTEGER NOT NULL DEFAULT 33,
        sex TEXT NOT NULL DEFAULT 'Homme',
        base_tdee INTEGER NOT NULL DEFAULT 1800,
        target_carbs INTEGER NOT NULL DEFAULT 350,
        target_protein INTEGER NOT NULL DEFAULT 120,
        target_fat INTEGER NOT NULL DEFAULT 80,
        hr_trail TEXT NOT NULL DEFAULT '[130,148,163,175]',
        hr_velo TEXT NOT NULL DEFAULT '[125,143,157,170]'
    );
    """)

    # Migrate favorite_foods
    existing_ff = {r[1] for r in conn.execute("PRAGMA table_info(favorite_foods)").fetchall()}
    if "salt_per_100" not in existing_ff:
        conn.execute("ALTER TABLE favorite_foods ADD COLUMN salt_per_100 REAL NOT NULL DEFAULT 0")
    if "portion_g" not in existing_ff:
        conn.execute("ALTER TABLE favorite_foods ADD COLUMN portion_g REAL DEFAULT NULL")

    # Migrate workouts
    existing_wk = {r[1] for r in conn.execute("PRAGMA table_info(workouts)").fetchall()}
    for col, defn in [
        ("kcal_actual", "REAL"),
        ("avg_hr", "INTEGER"),
        ("max_hr_session", "INTEGER"),
        ("hr_z1_min", "REAL DEFAULT 0"),
        ("hr_z2_min", "REAL DEFAULT 0"),
        ("hr_z3_min", "REAL DEFAULT 0"),
        ("hr_z4_min", "REAL DEFAULT 0"),
        ("hr_z5_min", "REAL DEFAULT 0"),
        ("source", "TEXT DEFAULT 'manual'"),
    ]:
        if col not in existing_wk:
            conn.execute(f"ALTER TABLE workouts ADD COLUMN {col} {defn}")

    # Migrate meals (add meal_type / meal_time to existing DBs)
    existing_ml = {r[1] for r in conn.execute("PRAGMA table_info(meals)").fetchall()}
    for col, defn in [
        ("meal_type", "TEXT NOT NULL DEFAULT 'Repas'"),
        ("meal_time", "TEXT NOT NULL DEFAULT '12:00'"),
    ]:
        if col not in existing_ml:
            conn.execute(f"ALTER TABLE meals ADD COLUMN {col} {defn}")

    # Migrate profile (add hr_trail / hr_velo to existing DBs)
    existing_pf = {r[1] for r in conn.execute("PRAGMA table_info(profile)").fetchall()}
    for col, defn in [
        ("hr_trail", "TEXT NOT NULL DEFAULT '[130,148,163,175]'"),
        ("hr_velo",  "TEXT NOT NULL DEFAULT '[125,143,157,170]'"),
    ]:
        if col not in existing_pf:
            conn.execute(f"ALTER TABLE profile ADD COLUMN {col} {defn}")

    if conn.execute("SELECT COUNT(*) FROM favorite_foods").fetchone()[0] == 0:
        defaults = [
            ("Flocons d'avoine",    58.7, 13.5,  6.9, 362),
            ("PST (protéines soja)",  3.0, 50.0,  1.0, 280),
            ("Pâtes (cuites)",      25.0,  5.0,  0.9, 131),
            ("Pain de campagne",    49.0,  8.0,  1.5, 250),
            ("Banane",              20.0,  1.1,  0.3,  89),
            ("Œuf entier",           0.7, 13.0, 11.0, 155),
            ("Houmous sans huile",  14.0,  8.0,  6.0, 150),
            ("Beurre de cacahuète", 20.0, 25.0, 50.0, 588),
            ("Riz (cuit)",          28.0,  2.7,  0.3, 130),
            ("Poulet (cuit)",        0.0, 31.0,  3.6, 165),
            ("Lentilles (cuites)",  20.0,  9.0,  0.4, 116),
            ("Fromage blanc 0%",     4.0, 12.0,  0.2,  46),
        ]
        conn.executemany(
            "INSERT INTO favorite_foods "
            "(name,carbs_per_100,protein_per_100,fat_per_100,kcal_per_100) VALUES (?,?,?,?,?)",
            defaults,
        )
    # Migration: add hrv_time column if missing (users with existing DB)
    try:
        conn.execute("ALTER TABLE morning_log ADD COLUMN hrv_time TEXT")
        conn.commit()
    except Exception:
        pass
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# FIT file parsing
# ─────────────────────────────────────────────

SPORT_MAP = {
    "running": "Trail", "trail_running": "Trail",
    "cycling": "Vélo", "swimming": "Natation",
    "walking": "Trail", "generic": "Trail",
}


def _extract_hr_raw(data: bytes) -> list:
    """
    Minimal FIT binary parser: extract (timestamp_sec, heart_rate_bpm) pairs
    from record messages (global_message_num=20, field 253=timestamp, field 3=HR).
    Ignores all other fields and does NOT validate type/size compatibility,
    so malformed fields in the definition don't break extraction.
    Returns list of (int, int) tuples — timestamps are FIT epoch seconds.
    """
    import struct as _s
    if len(data) < 12 or data[8:12] != b'.FIT':
        return []
    header_size = data[0]
    pos = header_size
    end = len(data) - 2  # exclude trailing CRC

    local_defs = {}   # local_type -> dict(size, le, ts_off, ts_sz, hr_off, hr_sz)
    result = []
    last_ts = 0

    while pos < end:
        if pos >= len(data):
            break
        hdr = data[pos]; pos += 1

        # ── Compressed timestamp record ──────────────────────────────────
        if hdr & 0x80:
            local_type = (hdr >> 5) & 0x03
            time_offset = hdr & 0x1F
            if local_type not in local_defs:
                continue
            d = local_defs[local_type]
            ts = (last_ts & 0xFFFFFFE0) | time_offset
            if ts < last_ts:
                ts += 32
            last_ts = ts
            if pos + d['size'] > len(data):
                break
            rec = data[pos:pos + d['size']]; pos += d['size']
            if d['hr_off'] is not None and d['hr_sz'] == 1:
                hr = rec[d['hr_off']]
                if 30 < hr < 220:
                    result.append((ts, hr))
            continue

        is_def  = bool(hdr & 0x40)
        has_dev = bool(hdr & 0x20)
        local_type = hdr & 0x0F

        # ── Definition message ────────────────────────────────────────────
        if is_def:
            if pos + 5 > len(data):
                break
            pos += 1  # reserved
            le = (data[pos] == 0); pos += 1
            fmt16 = '<H' if le else '>H'
            global_num = _s.unpack_from(fmt16, data, pos)[0]; pos += 2
            n_fields = data[pos]; pos += 1
            if pos + n_fields * 3 > len(data):
                break

            total_size = ts_off = ts_sz = hr_off = hr_sz = None
            total_size = 0
            for _ in range(n_fields):
                fnum  = data[pos]; pos += 1
                fsize = data[pos]; pos += 1
                pos += 1  # base_type (ignored — no size validation)
                if global_num == 20:
                    if fnum == 253: ts_off, ts_sz = total_size, fsize
                    elif fnum == 3: hr_off, hr_sz = total_size, fsize
                total_size += fsize

            # Skip developer fields
            if has_dev and pos < len(data):
                n_dev = data[pos]; pos += 1
                pos += n_dev * 3

            if global_num == 20:
                local_defs[local_type] = dict(
                    size=total_size, le=le,
                    ts_off=ts_off, ts_sz=ts_sz,
                    hr_off=hr_off, hr_sz=hr_sz,
                )

        # ── Data message ──────────────────────────────────────────────────
        else:
            if local_type not in local_defs:
                break  # unknown size — can't skip safely
            d = local_defs[local_type]
            if pos + d['size'] > len(data):
                break
            rec = data[pos:pos + d['size']]; pos += d['size']

            ts = None
            if d['ts_off'] is not None and d['ts_sz'] == 4:
                fmt32 = '<I' if d['le'] else '>I'
                ts = _s.unpack_from(fmt32, rec, d['ts_off'])[0]
                last_ts = ts
            if ts and d['hr_off'] is not None and d['hr_sz'] == 1:
                hr = rec[d['hr_off']]
                if 30 < hr < 220:
                    result.append((ts, hr))

    return result


def _iter_fit_messages(fitfile):
    """Iterate FIT messages, skipping malformed ones (e.g. Coros non-standard field sizes)."""
    gen = fitfile.get_messages()
    while True:
        try:
            yield next(gen)
        except StopIteration:
            break
        except Exception:
            continue


def _assign_zone(hr: float, bounds: list) -> int:
    if   hr <= bounds[0]: return 0
    elif hr <= bounds[1]: return 1
    elif hr <= bounds[2]: return 2
    elif hr <= bounds[3]: return 3
    else:                 return 4


def parse_fit(file_bytes: bytes, zone_map: dict) -> dict:
    # ── fitparse for session / lap / sport metadata ───────────────────────
    fitfile = fitparse.FitFile(io.BytesIO(file_bytes), check_crc=False)
    calories = None
    duration_s = None
    elevation_m = 0
    sport = "Trail"
    avg_hr = None
    max_hr_s = None
    lap_data = []   # (elapsed_s, avg_hr) per lap — fallback Tier 2

    for msg in _iter_fit_messages(fitfile):
        fields = {}
        for f in msg:
            try:
                if f.value is not None:
                    fields[f.name] = f.value
            except Exception:
                continue
        name = msg.name
        if name == "session":
            calories    = fields.get("total_calories", calories)
            duration_s  = fields.get("total_elapsed_time", duration_s)
            elevation_m = fields.get("total_ascent", elevation_m) or 0
            raw_sport   = str(fields.get("sport", "")).lower()
            sport       = SPORT_MAP.get(raw_sport, "Trail")
            avg_hr      = fields.get("avg_heart_rate", avg_hr)
            max_hr_s    = fields.get("max_heart_rate", max_hr_s)
        elif name == "lap":
            lap_s  = fields.get("total_elapsed_time") or fields.get("total_timer_time")
            lap_hr = fields.get("avg_heart_rate")
            if lap_s and lap_hr:
                lap_data.append((float(lap_s), float(lap_hr)))

    bounds = zone_map.get(sport, [130, 148, 163, 175])
    z_sec = [0.0] * 5
    expected_s = duration_s or 0

    # Tier 0 — raw binary HR extraction (immune to fitparse field-size errors)
    raw_hr_ts = _extract_hr_raw(file_bytes)
    if raw_hr_ts:
        for i in range(1, len(raw_hr_ts)):
            dt = raw_hr_ts[i][0] - raw_hr_ts[i - 1][0]  # int seconds
            if dt <= 0 or dt > 300:
                continue
            z_sec[_assign_zone(raw_hr_ts[i - 1][1], bounds)] += dt

    # Tier 2 — lap summaries if raw extraction gave < 50 % coverage
    if expected_s > 0 and sum(z_sec) < expected_s * 0.5 and lap_data:
        z_sec = [0.0] * 5
        for lap_s, lap_hr in lap_data:
            z_sec[_assign_zone(lap_hr, bounds)] += lap_s

    # Tier 3 — session avg_hr if still < 50 % coverage
    if expected_s > 0 and sum(z_sec) < expected_s * 0.5 and avg_hr:
        z_sec = [0.0] * 5
        z_sec[_assign_zone(avg_hr, bounds)] = expected_s

    return {
        "sport":           sport,
        "duration_min":    round(duration_s / 60) if duration_s else None,
        "elevation_m":     int(elevation_m),
        "calories":        int(calories) if calories else None,
        "avg_hr":          avg_hr,
        "max_hr_session":  max_hr_s,
        "hr_z1_min": z_sec[0] / 60, "hr_z2_min": z_sec[1] / 60,
        "hr_z3_min": z_sec[2] / 60, "hr_z4_min": z_sec[3] / 60,
        "hr_z5_min": z_sec[4] / 60,
    }


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def bmr_mifflin(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "Homme" else base - 161


MET_TABLE = {
    ("Trail",    "Zone 2"):          8.0,
    ("Trail",    "Fractionné/PMA"): 11.0,
    ("Vélo",     "Zone 2"):          6.5,
    ("Vélo",     "Fractionné/PMA"):  9.5,
    ("Athlé",    "Zone 2"):          7.0,
    ("Athlé",    "Fractionné/PMA"): 10.5,
    ("Natation", "Zone 2"):          6.0,
    ("Natation", "Fractionné/PMA"):  8.5,
}


def training_kcal_estimate(weight_kg, sport, intensity, duration_min, elevation_m):
    met = MET_TABLE.get((sport, intensity), 7.0)
    base = met * weight_kg * (duration_min / 60)
    if elevation_m > 0:
        base += 0.5 * weight_kg * (elevation_m / 100)
    return round(base)


def workout_kcal(row, weight_kg: float) -> float:
    if pd.notna(row.kcal_actual) and row.kcal_actual:
        return float(row.kcal_actual)
    return training_kcal_estimate(weight_kg, row.type, row.intensity,
                                  row.duration_min, row.elevation_m)


@st.cache_resource(show_spinner="Chargement du modèle OCR (première fois uniquement)…")
def _get_easyocr_reader():
    return easyocr.Reader(["fr", "en"], gpu=False)


def ocr_label(image_bytes: bytes) -> str:
    """Run OCR on a label photo and return plain text."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img)
    if EASYOCR_AVAILABLE:
        reader = _get_easyocr_reader()
        results = reader.readtext(arr, detail=1, paragraph=False)
        results.sort(key=lambda r: (r[0][0][1], r[0][0][0]))  # top-to-bottom, left-to-right
        return "\n".join(r[1] for r in results)
    if PYTESSERACT_AVAILABLE:
        return pytesseract.image_to_string(img, lang="fra+eng")
    return ""


def parse_nutrition_text(text: str) -> dict:
    """Extract macro values per 100g from raw OCR text of a nutritional label."""
    result = {
        "name": "", "kcal_per_100": 0.0, "carbs_per_100": 0.0,
        "protein_per_100": 0.0, "fat_per_100": 0.0, "salt_per_100": 0.0,
    }
    t = text.lower()

    def first_num(*patterns: str) -> float:
        for pat in patterns:
            m = re.search(pat, t)
            if m:
                return float(m.group(1).replace(",", "."))
        return 0.0

    result["kcal_per_100"] = first_num(
        r"(\d+(?:[.,]\d+)?)\s*kcal",
        r"kcal[\s:]*(\d+(?:[.,]\d+)?)",
        r"calories?[\s:]*(\d+(?:[.,]\d+)?)",
    )
    result["carbs_per_100"] = first_num(
        r"glucides?[^\d]*?(\d+(?:[.,]\d+)?)\s*g",
        r"carbohydrates?[^\d]*?(\d+(?:[.,]\d+)?)\s*g",
    )
    result["protein_per_100"] = first_num(
        r"prot[eé]ines?[^\d]*?(\d+(?:[.,]\d+)?)\s*g",
        r"proteins?[^\d]*?(\d+(?:[.,]\d+)?)\s*g",
    )
    result["fat_per_100"] = first_num(
        r"mati[eè]res?\s+grasses?[^\d]*?(\d+(?:[.,]\d+)?)\s*g",
        r"graisses?[^\d]*?(\d+(?:[.,]\d+)?)\s*g",
        r"lipides?[^\d]*?(\d+(?:[.,]\d+)?)\s*g",
        r"\bfat\b[^\d]*?(\d+(?:[.,]\d+)?)\s*g",
    )
    m_sel    = re.search(r"\bsel\b[^\d]*?(\d+(?:[.,]\d+)?)", t)
    m_salt   = re.search(r"\bsalt\b[^\d]*?(\d+(?:[.,]\d+)?)", t)
    m_sodium = re.search(r"sodium[^\d]*?(\d+(?:[.,]\d+)?)", t)
    if m_sel:
        result["salt_per_100"] = float(m_sel.group(1).replace(",", "."))
    elif m_salt:
        result["salt_per_100"] = float(m_salt.group(1).replace(",", "."))
    elif m_sodium:
        # Sodium → sel : ×2.5
        result["salt_per_100"] = round(float(m_sodium.group(1).replace(",", ".")) * 2.5, 2)

    return result


_ZONE_CARB_RATE = [0.2, 0.4, 0.65, 0.9, 1.1]  # g glycogen/min burned per zone


def compute_carb_adjustment(wks_df: pd.DataFrame) -> int:
    """Extra carbs (g) to replenish glycogen from today's training zones."""
    if wks_df.empty:
        return 0
    extra = 0.0
    for _, w in wks_df.iterrows():
        for rate, col in zip(_ZONE_CARB_RATE,
                             ["hr_z1_min", "hr_z2_min", "hr_z3_min", "hr_z4_min", "hr_z5_min"]):
            val = getattr(w, col, 0) or 0
            extra += rate * float(val)
    return round(extra)


def load_profile(conn) -> dict:
    row = conn.execute(
        "SELECT weight_kg, height_cm, age, sex, base_tdee, "
        "target_carbs, target_protein, target_fat, hr_trail, hr_velo "
        "FROM profile WHERE id=1"
    ).fetchone()
    if row is None:
        return {
            "weight_kg": 72.0, "height_cm": 178, "age": 33, "sex": "Homme",
            "base_tdee": 1800, "target_carbs": 350, "target_protein": 120, "target_fat": 80,
            "hr_trail": [130, 148, 163, 175],
            "hr_velo":  [125, 143, 157, 170],
        }
    return {
        "weight_kg":      row[0],
        "height_cm":      int(row[1]),
        "age":            int(row[2]),
        "sex":            row[3],
        "base_tdee":      int(row[4]),
        "target_carbs":   int(row[5]),
        "target_protein": int(row[6]),
        "target_fat":     int(row[7]),
        "hr_trail":       json.loads(row[8]) if row[8] else [130, 148, 163, 175],
        "hr_velo":        json.loads(row[9]) if row[9] else [125, 143, 157, 170],
    }


def save_profile(conn, p: dict):
    conn.execute(
        """INSERT OR REPLACE INTO profile
           (id, weight_kg, height_cm, age, sex, base_tdee,
            target_carbs, target_protein, target_fat, hr_trail, hr_velo)
           VALUES (1,?,?,?,?,?,?,?,?,?,?)""",
        (p["weight_kg"], p["height_cm"], p["age"], p["sex"],
         p["base_tdee"], p["target_carbs"], p["target_protein"], p["target_fat"],
         json.dumps(p["hr_trail"]), json.dumps(p["hr_velo"])),
    )
    conn.commit()


def load_meals(conn, d: str) -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT * FROM meals WHERE date=? ORDER BY meal_time, meal_type, id",
        conn, params=(d,),
    )


def load_workouts(conn, d: str) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM workouts WHERE date=?", conn, params=(d,))


# ─────────────────────────────────────────────
# Charts
# ─────────────────────────────────────────────

def macro_donut(carbs_g: float, protein_g: float, fat_g: float,
                height: int = 320, title: str = "") -> go.Figure:
    kcals = [carbs_g * 4, protein_g * 4, fat_g * 9]
    total = sum(kcals)
    fig = go.Figure(go.Pie(
        labels=list(_COLORS.keys()),
        values=kcals,
        hole=0.55,
        marker=dict(colors=list(_COLORS.values())),
        textinfo="label+percent",
        textposition="outside",
        hovertemplate="%{label}: %{value:.0f} kcal (%{percent})<extra></extra>",
        direction="clockwise",
        sort=False,
    ))
    fig.update_layout(
        height=height,
        margin=dict(t=50 if title else 40, b=40, l=10, r=10),
        showlegend=False,
        title=dict(text=title, x=0.5, font=dict(size=14)) if title else None,
        annotations=[dict(
            text=f"<b>{total:.0f}</b><br>kcal",
            x=0.5, y=0.5,
            font=dict(size=16),
            showarrow=False,
        )],
    )
    return fig


def calorie_bar(total_kcal: float, target_kcal: float) -> go.Figure:
    consumed  = min(total_kcal, target_kcal)
    over      = max(total_kcal - target_kcal, 0)
    remaining = max(target_kcal - total_kcal, 0)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=[""], y=[consumed], name="Consommées",
                         marker_color="#2ecc71", text=f"{consumed:.0f}", textposition="inside"))
    if over > 0:
        fig.add_trace(go.Bar(x=[""], y=[over], name="Au-dessus",
                             marker_color="#e74c3c", text=f"+{over:.0f}", textposition="inside"))
    else:
        fig.add_trace(go.Bar(x=[""], y=[remaining], name="Restantes",
                             marker_color="#444", opacity=0.35,
                             text=f"−{remaining:.0f}", textposition="inside"))

    fig.add_hline(y=target_kcal, line_dash="dash", line_color="#f1c40f",
                  annotation_text=f"Cible {target_kcal:.0f}", annotation_position="top right")
    fig.update_layout(
        barmode="stack", height=320,
        margin=dict(t=40, b=40, l=40, r=10),
        yaxis_title="kcal",
        yaxis=dict(range=[0, max(target_kcal * 1.25, total_kcal * 1.1)]),
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, x=0),
        bargap=0.5,
    )
    return fig


def hr_zone_chart(z1, z2, z3, z4, z5, bounds=None) -> go.Figure:
    minutes = [z1, z2, z3, z4, z5]
    if bounds and len(bounds) == 4:
        b = bounds
        ranges = [f"< {b[0]}", f"{b[0]}–{b[1]}", f"{b[1]}–{b[2]}", f"{b[2]}–{b[3]}", f"> {b[3]}"]
    else:
        ranges = [""] * 5
    labels = [f"{lbl}<br><sub>{rng} bpm</sub>" for lbl, rng in zip(_ZONE_LABELS, ranges)]
    fig = go.Figure(go.Bar(
        x=labels, y=minutes,
        marker_color=_ZONE_COLORS,
        text=[f"{m:.0f}'" for m in minutes],
        textposition="outside",
    ))
    fig.update_layout(
        height=260, margin=dict(t=20, b=10, l=30, r=10),
        yaxis_title="minutes", showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Perf Nutrition", page_icon="⚡", layout="wide")
    init_db()

    if "pending_foods" not in st.session_state:
        st.session_state.pending_foods = []
    if "pending_fit_foods" not in st.session_state:
        st.session_state.pending_fit_foods = []

    conn = get_db()
    prof = load_profile(conn)

    # ── Sidebar ──
    st.sidebar.title("⚙️ Profil")
    height_cm = st.sidebar.number_input("Taille (cm)", 140, 210, prof["height_cm"])
    age       = st.sidebar.number_input("Âge", 18, 70, prof["age"])
    sex       = st.sidebar.selectbox(
        "Sexe", ["Homme", "Femme"],
        index=["Homme", "Femme"].index(prof["sex"]),
    )

    last_w = conn.execute(
        "SELECT date, weight_kg FROM weight_log ORDER BY date DESC LIMIT 1"
    ).fetchone()
    weight_current = float(last_w[1]) if last_w else float(prof["weight_kg"])

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Cibles journalières")
    base_tdee = st.sidebar.number_input(
        "TDEE de base (kcal)", 1200, 4000, prof["base_tdee"], 50,
        help="Dépense sans sport. La dépense d'entraînement s'ajoute automatiquement.",
    )
    target_carbs   = st.sidebar.slider("Glucides (g)",  100, 700, prof["target_carbs"])
    target_protein = st.sidebar.slider("Protéines (g)",  60, 250, prof["target_protein"])
    target_fat     = st.sidebar.slider("Lipides (g)",    30, 150, prof["target_fat"])

    st.sidebar.markdown("---")
    st.sidebar.subheader("🫀 Zones FC")
    st.sidebar.caption("Limite supérieure de chaque zone (bpm) — Z5 = tout ce qui dépasse Z4")

    with st.sidebar.expander("🏃 Trail / Cap"):
        tz1 = st.number_input("Z1 Récup     ≤", 80, 220, prof["hr_trail"][0], key="tz1")
        tz2 = st.number_input("Z2 Endurance ≤", 80, 220, prof["hr_trail"][1], key="tz2")
        tz3 = st.number_input("Z3 Tempo     ≤", 80, 220, prof["hr_trail"][2], key="tz3")
        tz4 = st.number_input("Z4 Seuil     ≤", 80, 220, prof["hr_trail"][3], key="tz4")
        st.caption(f"Z1 <{tz1} · Z2 {tz1}–{tz2} · Z3 {tz2}–{tz3} · Z4 {tz3}–{tz4} · Z5 >{tz4}")

    with st.sidebar.expander("🚴 Vélo"):
        vz1 = st.number_input("Z1 Récup     ≤", 80, 220, prof["hr_velo"][0], key="vz1")
        vz2 = st.number_input("Z2 Endurance ≤", 80, 220, prof["hr_velo"][1], key="vz2")
        vz3 = st.number_input("Z3 Tempo     ≤", 80, 220, prof["hr_velo"][2], key="vz3")
        vz4 = st.number_input("Z4 Seuil     ≤", 80, 220, prof["hr_velo"][3], key="vz4")
        st.caption(f"Z1 <{vz1} · Z2 {vz1}–{vz2} · Z3 {vz2}–{vz3} · Z4 {vz3}–{vz4} · Z5 >{vz4}")

    zone_map = {
        "Trail":    [tz1, tz2, tz3, tz4],
        "Vélo":     [vz1, vz2, vz3, vz4],
        "Athlé":    [tz1, tz2, tz3, tz4],
        "Natation": [tz1, tz2, tz3, tz4],
    }

    st.sidebar.markdown("---")
    if st.sidebar.button("💾 Sauvegarder le profil"):
        save_profile(conn, {
            "weight_kg":      weight_current,
            "height_cm":      int(height_cm),
            "age":            int(age),
            "sex":            sex,
            "base_tdee":      int(base_tdee),
            "target_carbs":   int(target_carbs),
            "target_protein": int(target_protein),
            "target_fat":     int(target_fat),
            "hr_trail":       [int(tz1), int(tz2), int(tz3), int(tz4)],
            "hr_velo":        [int(vz1), int(vz2), int(vz3), int(vz4)],
        })
        st.sidebar.success("Profil sauvegardé ✓")

    st.sidebar.markdown("---")

    _, _hcol2 = st.columns([3, 1])
    with _hcol2:
        selected_date = st.date_input("📅 Date", date.today(), label_visibility="collapsed")
    sel_str = selected_date.isoformat()
    tab_nutri, tab_training, tab_forme, tab_perf = st.tabs(
        ["🍽️ Nutrition", "🏃 Entraînement", "🫀 Forme", "📈 Performance"]
    )

    # ═══════════════════ TAB 1 : NUTRITION ═══════════════════
    with tab_nutri:
        favs    = pd.read_sql_query("SELECT * FROM favorite_foods ORDER BY name", conn)
        meals   = load_meals(conn, sel_str)
        wks_day = load_workouts(conn, sel_str)

        # Dynamic calorie target: base + today's training
        training_kcal_today = (
            sum(workout_kcal(w, weight_current) for _, w in wks_day.iterrows())
            if not wks_day.empty else 0.0
        )
        target_kcal     = base_tdee + training_kcal_today
        carb_adjustment = compute_carb_adjustment(wks_day)
        adjusted_carbs  = target_carbs + carb_adjustment

        # ── Header ──
        day_fr = selected_date.strftime("%A %d %B %Y")
        st.markdown(f"## 📅 {day_fr.capitalize()}")
        if training_kcal_today > 0:
            carb_note = (
                f" · 🍞 Glucides : **{adjusted_carbs}g** (+{carb_adjustment}g effort)"
                if carb_adjustment > 0 else ""
            )
            st.caption(
                f"Cible : {base_tdee:.0f} kcal (base) + {training_kcal_today:.0f} kcal (entraînement) "
                f"= **{target_kcal:.0f} kcal**{carb_note}"
            )
        else:
            st.caption(f"Cible : {target_kcal:.0f} kcal — aucune séance enregistrée pour ce jour")

        # ── Daily summary donut ──
        if not meals.empty:
            tot_carbs = meals.carbs_g.sum()
            tot_prot  = meals.protein_g.sum()
            tot_fat   = meals.fat_g.sum()
            tot_kcal  = meals.kcal.sum()

            col_donut, col_bar = st.columns([3, 1])
            with col_donut:
                st.plotly_chart(
                    macro_donut(tot_carbs, tot_prot, tot_fat, title="Journée complète"),
                    use_container_width=True,
                )
            with col_bar:
                st.plotly_chart(calorie_bar(tot_kcal, target_kcal), use_container_width=True)

            m1, m2, m3 = st.columns(3)
            carb_cible_lbl = (f"{adjusted_carbs}g (+{carb_adjustment}g effort)"
                              if carb_adjustment > 0 else f"{target_carbs}g cible")
            m1.metric("Glucides",  f"{tot_carbs:.0f}g",
                      f"{tot_carbs - adjusted_carbs:+.0f}g vs {carb_cible_lbl}", delta_color="off")
            m2.metric("Protéines", f"{tot_prot:.0f}g",
                      f"{tot_prot - target_protein:+.0f}g vs {target_protein}g cible", delta_color="off")
            m3.metric("Lipides",   f"{tot_fat:.0f}g",
                      f"{tot_fat - target_fat:+.0f}g vs {target_fat}g cible", delta_color="off")
        else:
            st.info("Aucun repas enregistré pour cette date.")

        st.markdown("---")

        # ── Per-meal sections ──
        if not meals.empty:
            _meal_order = {t: i for i, t in enumerate(MEAL_TYPES)}
            meal_groups = sorted(
                meals.groupby(["meal_time", "meal_type"], sort=False),
                key=lambda x: (_meal_order.get(x[0][1], 99), x[0][0]),
            )
            for idx, ((m_time, m_type), group) in enumerate(meal_groups):
                emoji  = MEAL_EMOJI.get(m_type, "🍽️")
                g_carbs = group.carbs_g.sum()
                g_prot  = group.protein_g.sum()
                g_fat   = group.fat_g.sum()
                g_kcal  = group.kcal.sum()

                _mhdr, _mdel = st.columns([5, 1])
                _mhdr.markdown(f"### {emoji} {m_type} · {m_time} &nbsp; — &nbsp; {g_kcal:.0f} kcal")
                if _mdel.button("🗑️ Supprimer", key=f"del_meal_{idx}"):
                    conn.execute(
                        "DELETE FROM meals WHERE date=? AND meal_type=? AND meal_time=?",
                        (sel_str, m_type, m_time),
                    )
                    conn.commit()
                    st.rerun()

                mc1, mc2 = st.columns([1, 2])
                with mc1:
                    st.plotly_chart(
                        macro_donut(g_carbs, g_prot, g_fat, height=220),
                        use_container_width=True,
                    )
                with mc2:
                    rm1, rm2, rm3 = st.columns(3)
                    rm1.metric("Glucides",  f"{g_carbs:.0f}g")
                    rm2.metric("Protéines", f"{g_prot:.0f}g")
                    rm3.metric("Lipides",   f"{g_fat:.0f}g")

                    with st.expander("✏️ Modifier ce repas"):
                        disp = group[["food_name", "quantity_g", "carbs_g",
                                      "protein_g", "fat_g", "kcal"]].copy()
                        disp.columns = ["Aliment", "Qté (g)", "Gluc", "Prot", "Lip", "Kcal"]
                        st.dataframe(disp, use_container_width=True, hide_index=True)

                        # ── Supprimer un aliment ──
                        st.markdown("**Supprimer un aliment**")
                        _del_ids = group["id"].tolist()
                        _del_names = {row.id: row.food_name for _, row in group.iterrows()}
                        del_food_id = st.selectbox(
                            "Aliment à supprimer",
                            _del_ids,
                            format_func=lambda x: _del_names.get(x, x),
                            key=f"del_food_{idx}",
                        )
                        if st.button("🗑️ Supprimer cet aliment", key=f"del_btn_{idx}"):
                            conn.execute("DELETE FROM meals WHERE id=?", (int(del_food_id),))
                            conn.commit()
                            st.rerun()

                        st.markdown("---")

                        # ── Ajouter un aliment ──
                        st.markdown("**Ajouter un aliment à ce repas**")
                        _edit_mode = st.radio(
                            "Source",
                            ["Depuis les favoris", "Saisie libre"],
                            horizontal=True,
                            key=f"edit_mode_{idx}",
                        )

                        if _edit_mode == "Depuis les favoris":
                            _ef_choice = st.selectbox(
                                "Aliment", favs["name"].tolist(), key=f"edit_fav_sel_{idx}"
                            )
                            _ef_row = favs[favs["name"] == _ef_choice].iloc[0]
                            _ef_has_portion = (
                                "portion_g" in favs.columns
                                and _ef_row.get("portion_g") is not None
                                and not pd.isna(_ef_row.get("portion_g", float("nan")))
                            )
                            if _ef_has_portion:
                                _ef_pg = float(_ef_row["portion_g"])
                                _ef_unit = st.radio(
                                    "Unité",
                                    ["Grammes", f"Portions ({_ef_pg:.0f} g/portion)"],
                                    horizontal=True,
                                    key=f"edit_fav_unit_{idx}",
                                )
                                if _ef_unit == "Grammes":
                                    _ef_qty = float(st.number_input(
                                        "Quantité (g)", 10, 2000, 100, 10, key=f"edit_fav_qty_{idx}"
                                    ))
                                else:
                                    _ef_nb = st.number_input(
                                        "Nombre de portions", 0.25, 20.0, 1.0, 0.25,
                                        key=f"edit_fav_nb_{idx}",
                                    )
                                    _ef_qty = _ef_nb * _ef_pg
                                    st.caption(f"= {_ef_qty:.0f} g")
                            else:
                                _ef_qty = float(st.number_input(
                                    "Quantité (g)", 10, 2000, 100, 10, key=f"edit_fav_qty_{idx}"
                                ))
                            if st.button("➕ Ajouter", key=f"edit_fav_add_{idx}"):
                                _r = _ef_qty / 100
                                conn.execute(
                                    """INSERT INTO meals
                                       (date, meal_type, meal_time, food_name,
                                        quantity_g, carbs_g, protein_g, fat_g, kcal)
                                       VALUES (?,?,?,?,?,?,?,?,?)""",
                                    (sel_str, m_type, m_time, _ef_choice, _ef_qty,
                                     round(_ef_row.carbs_per_100   * _r, 1),
                                     round(_ef_row.protein_per_100 * _r, 1),
                                     round(_ef_row.fat_per_100     * _r, 1),
                                     round(_ef_row.kcal_per_100    * _r)),
                                )
                                conn.commit()
                                st.rerun()

                        else:  # Saisie libre
                            _em_name = st.text_input("Nom", key=f"edit_m_name_{idx}")
                            _em_qty  = st.number_input(
                                "Quantité (g)", 1, 2000, 100, key=f"edit_m_qty_{idx}"
                            )
                            _ec1, _ec2 = st.columns(2)
                            _em_carbs = _ec1.number_input(
                                "Glucides (g)", 0.0, 500.0, 0.0, 0.5, key=f"edit_m_carbs_{idx}"
                            )
                            _em_prot = _ec2.number_input(
                                "Protéines (g)", 0.0, 500.0, 0.0, 0.5, key=f"edit_m_prot_{idx}"
                            )
                            _em_fat = _ec1.number_input(
                                "Lipides (g)", 0.0, 500.0, 0.0, 0.5, key=f"edit_m_fat_{idx}"
                            )
                            _em_kcal = _ec2.number_input(
                                "Kcal", 0.0, 5000.0, 0.0, 1.0, key=f"edit_m_kcal_{idx}"
                            )
                            if st.button("➕ Ajouter", key=f"edit_m_add_{idx}"):
                                if _em_name:
                                    conn.execute(
                                        """INSERT INTO meals
                                           (date, meal_type, meal_time, food_name,
                                            quantity_g, carbs_g, protein_g, fat_g, kcal)
                                           VALUES (?,?,?,?,?,?,?,?,?)""",
                                        (sel_str, m_type, m_time, _em_name, _em_qty,
                                         _em_carbs, _em_prot, _em_fat, _em_kcal),
                                    )
                                    conn.commit()
                                    st.rerun()

                st.markdown("---")

        # ── Add a meal ──
        st.subheader("➕ Ajouter un repas")

        add_c1, add_c2 = st.columns(2)
        pending_type = add_c1.selectbox("Type de repas", MEAL_TYPES, key="pending_type")
        pending_time = add_c2.time_input(
            "Heure", value=MEAL_DEFAULT_TIME.get(pending_type, time(12, 0)),
            key="pending_time",
        )
        pending_time_str = pending_time.strftime("%H:%M")

        # Pending foods preview
        if st.session_state.pending_foods:
            st.markdown("**Aliments en cours d'ajout :**")
            h1, h2, h3, h4, h5, h6, _ = st.columns([3, 1.2, 1, 1, 1, 1, 0.6])
            for col, label in zip(
                [h1, h2, h3, h4, h5, h6],
                ["Aliment", "Qté (g)", "Gluc", "Prot", "Lip", "Kcal"],
            ):
                col.markdown(f"<small><b>{label}</b></small>", unsafe_allow_html=True)

            to_delete = None
            for i, food in enumerate(st.session_state.pending_foods):
                c1, c2, c3, c4, c5, c6, c7 = st.columns([3, 1.2, 1, 1, 1, 1, 0.6])
                c1.write(food["food_name"])
                c2.write(f"{food['quantity_g']:.0f}g")
                c3.write(f"{food['carbs_g']:.1f}")
                c4.write(f"{food['protein_g']:.1f}")
                c5.write(f"{food['fat_g']:.1f}")
                c6.write(f"{food['kcal']:.0f}")
                if c7.button("❌", key=f"del_pending_{i}"):
                    to_delete = i
            if to_delete is not None:
                st.session_state.pending_foods.pop(to_delete)
                st.rerun()

            pend_df = pd.DataFrame(st.session_state.pending_foods)
            st.markdown(
                f"**Total : {pend_df.kcal.sum():.0f} kcal** — "
                f"G {pend_df.carbs_g.sum():.0f}g · "
                f"P {pend_df.protein_g.sum():.0f}g · "
                f"L {pend_df.fat_g.sum():.0f}g"
            )
            btn_save, btn_clear = st.columns(2)
            if btn_save.button("✅ Enregistrer le repas", type="primary"):
                for food in st.session_state.pending_foods:
                    conn.execute(
                        """INSERT INTO meals
                           (date, meal_type, meal_time, food_name,
                            quantity_g, carbs_g, protein_g, fat_g, kcal)
                           VALUES (?,?,?,?,?,?,?,?,?)""",
                        (sel_str, pending_type, pending_time_str,
                         food["food_name"], food["quantity_g"],
                         food["carbs_g"], food["protein_g"],
                         food["fat_g"], food["kcal"]),
                    )
                conn.commit()
                st.session_state.pending_foods = []
                st.rerun()
            if btn_clear.button("🗑️ Vider la liste"):
                st.session_state.pending_foods = []
                st.rerun()

        # Food selectors
        st.markdown("**Ajouter des aliments :**")
        food_c1, food_c2 = st.columns(2)

        with food_c1:
            st.markdown("**Depuis les favoris**")
            fav_choice = st.selectbox("Aliment", favs["name"].tolist(), key="fav_sel")
            fav_row = favs[favs["name"] == fav_choice].iloc[0]
            _has_portion = (
                "portion_g" in favs.columns
                and fav_row.get("portion_g") is not None
                and not pd.isna(fav_row.get("portion_g", float("nan")))
            )
            if _has_portion:
                _portion_g = float(fav_row["portion_g"])
                _unit = st.radio(
                    "Unité",
                    ["Grammes", f"Portions ({_portion_g:.0f} g/portion)"],
                    horizontal=True,
                    key="fav_unit",
                )
                if _unit == "Grammes":
                    fav_qty_g = float(st.number_input("Quantité (g)", 10, 2000, 100, 10, key="fav_qty"))
                else:
                    _nb = st.number_input("Nombre de portions", 0.25, 20.0, 1.0, 0.25, key="fav_nb")
                    fav_qty_g = _nb * _portion_g
                    st.caption(f"= {fav_qty_g:.0f} g")
            else:
                fav_qty_g = float(st.number_input("Quantité (g)", 10, 2000, 100, 10, key="fav_qty"))
            if st.button("➕ Ajouter au repas", key="fav_add"):
                r = fav_qty_g / 100
                st.session_state.pending_foods.append({
                    "food_name": fav_choice,
                    "quantity_g": fav_qty_g,
                    "carbs_g":   round(fav_row.carbs_per_100   * r, 1),
                    "protein_g": round(fav_row.protein_per_100 * r, 1),
                    "fat_g":     round(fav_row.fat_per_100     * r, 1),
                    "kcal":      round(fav_row.kcal_per_100    * r),
                })
                st.rerun()

        with food_c2:
            st.markdown("**Saisie libre**")
            m_name = st.text_input("Nom", key="m_name")
            m_qty  = st.number_input("Quantité (g)", 1, 2000, 100, key="m_qty")
            mc1, mc2 = st.columns(2)
            m_carbs = mc1.number_input("Glucides (g)", 0.0, 500.0, 0.0, 0.5, key="m_carbs")
            m_prot  = mc2.number_input("Protéines (g)", 0.0, 500.0, 0.0, 0.5, key="m_prot")
            m_fat   = mc1.number_input("Lipides (g)",  0.0, 500.0, 0.0, 0.5, key="m_fat")
            m_kcal  = mc2.number_input("Kcal",         0.0, 5000.0, 0.0, 1.0, key="m_kcal")
            if st.button("➕ Ajouter au repas", key="manual_add"):
                if m_name:
                    st.session_state.pending_foods.append({
                        "food_name": m_name,
                        "quantity_g": m_qty,
                        "carbs_g":   m_carbs,
                        "protein_g": m_prot,
                        "fat_g":     m_fat,
                        "kcal":      m_kcal,
                    })
                    st.rerun()

        # Label scanner
        with st.expander("📷 Scanner une étiquette nutritionnelle"):
            if not OCR_AVAILABLE:
                st.warning(
                    "Aucun moteur OCR disponible. "
                    "Lance `pip install easyocr` (recommandé) ou "
                    "`brew install tesseract && pip install pytesseract pillow`."
                )
            else:
                engine = "EasyOCR" if EASYOCR_AVAILABLE else "Tesseract"
                st.caption(f"Moteur OCR : **{engine}** — local, gratuit, aucune API requise")
                scan_src = st.radio(
                    "Source", ["📷 Caméra", "📁 Fichier image"],
                    horizontal=True, key="scan_src",
                )
                img_data = None
                if scan_src == "📷 Caméra":
                    img_data = st.camera_input("Photo de l'étiquette", key="scan_cam")
                else:
                    img_data = st.file_uploader(
                        "Image", type=["jpg", "jpeg", "png", "webp"], key="scan_upload"
                    )

                if img_data is not None:
                    if st.button("🔍 Extraire les valeurs", key="scan_btn"):
                        with st.spinner("OCR en cours…"):
                            try:
                                raw_text = ocr_label(bytes(img_data.getvalue()))
                                st.session_state.scan_raw_text = raw_text
                                st.session_state.scan_result = parse_nutrition_text(raw_text)
                            except Exception as exc:
                                st.error(f"Erreur OCR : {exc}")
                                st.session_state.scan_result = None

                if st.session_state.get("scan_raw_text"):
                    with st.expander("📄 Texte brut extrait (pour vérification)"):
                        st.text(st.session_state.scan_raw_text)

                if st.session_state.get("scan_result"):
                    r = st.session_state.scan_result
                    st.success("Valeurs extraites ✓ — Corrige si besoin puis sauvegarde")
                    sf1, sf2 = st.columns(2)
                    scan_name = sf1.text_input("Nom du produit", r.get("name", ""), key="scan_name")
                    scan_kcal = sf2.number_input(
                        "Kcal / 100g", 0.0, 900.0, float(r.get("kcal_per_100", 0)), 1.0, key="scan_kcal")
                    sf3, sf4 = st.columns(2)
                    scan_carbs = sf3.number_input(
                        "Glucides / 100g", 0.0, 100.0, float(r.get("carbs_per_100", 0)), 0.1, key="scan_carbs")
                    scan_prot = sf4.number_input(
                        "Protéines / 100g", 0.0, 100.0, float(r.get("protein_per_100", 0)), 0.1, key="scan_prot")
                    sf5, sf6 = st.columns(2)
                    scan_fat = sf5.number_input(
                        "Lipides / 100g", 0.0, 100.0, float(r.get("fat_per_100", 0)), 0.1, key="scan_fat")
                    scan_salt = sf6.number_input(
                        "Sel / 100g", 0.0, 10.0, float(r.get("salt_per_100", 0)), 0.01, key="scan_salt")
                    scan_portion = st.number_input(
                        "Taille d'une portion (g) — optionnel, 0 = pas de portion",
                        0.0, 2000.0, 0.0, 1.0, key="scan_portion",
                    )
                    if st.button("✅ Ajouter aux favoris", type="primary", key="scan_save"):
                        if scan_name:
                            _scan_portion_val = float(scan_portion) if scan_portion > 0 else None
                            conn.execute(
                                "INSERT OR REPLACE INTO favorite_foods "
                                "(name, carbs_per_100, protein_per_100, fat_per_100, "
                                "kcal_per_100, salt_per_100, portion_g) "
                                "VALUES (?,?,?,?,?,?,?)",
                                (scan_name, scan_carbs, scan_prot, scan_fat,
                                 scan_kcal, scan_salt, _scan_portion_val),
                            )
                            conn.commit()
                            st.session_state.scan_result = None
                            st.session_state.scan_raw_text = None
                            st.rerun()

        # Favorites manager
        with st.expander("📋 Gérer les favoris"):
            _favs_disp = favs[["name", "carbs_per_100", "protein_per_100",
                                "fat_per_100", "kcal_per_100"]].copy()
            _favs_disp.columns = ["Aliment", "G/100g", "P/100g", "L/100g", "Kcal/100g"]
            if "portion_g" in favs.columns:
                _favs_disp["Portion (g)"] = favs["portion_g"].apply(
                    lambda x: f"{x:.0f} g" if pd.notna(x) and x is not None else "—"
                )
            st.dataframe(_favs_disp, use_container_width=True, hide_index=True)

            st.markdown("**Ajouter / modifier un favori**")
            fc1, fc2 = st.columns(2)
            fn = fc1.text_input("Nom", key="fn")

            _fav_mode = fc2.radio(
                "Valeurs saisies pour",
                ["100 g", "Une portion"],
                horizontal=True,
                key="fav_input_mode",
            )
            f_portion_g = None
            if _fav_mode == "Une portion":
                f_portion_g = fc2.number_input(
                    "Taille de la portion (g)", 1.0, 2000.0, 100.0, 1.0, key="f_portion_g"
                )

            fi1, fi2 = st.columns(2)
            _unit_lbl = "100g" if _fav_mode == "100 g" else "portion"
            fcarb = fi1.number_input(f"Glucides / {_unit_lbl}",  0.0, 500.0, 0.0, 0.1, key="fcarb")
            fprot = fi2.number_input(f"Protéines / {_unit_lbl}", 0.0, 500.0, 0.0, 0.1, key="fprot")
            ffat  = fi1.number_input(f"Lipides / {_unit_lbl}",   0.0, 500.0, 0.0, 0.1, key="ffat")
            fkcal = fi2.number_input(f"Kcal / {_unit_lbl}",      0.0, 5000.0, 0.0, 1.0, key="fkcal")

            if st.button("Sauver favori"):
                if fn:
                    if _fav_mode == "Une portion" and f_portion_g:
                        _ratio = 100.0 / f_portion_g
                        _carb100  = round(fcarb * _ratio, 2)
                        _prot100  = round(fprot * _ratio, 2)
                        _fat100   = round(ffat  * _ratio, 2)
                        _kcal100  = round(fkcal * _ratio, 2)
                    else:
                        _carb100, _prot100, _fat100, _kcal100 = fcarb, fprot, ffat, fkcal
                        f_portion_g = None
                    conn.execute(
                        "INSERT OR REPLACE INTO favorite_foods "
                        "(name, carbs_per_100, protein_per_100, fat_per_100, kcal_per_100, portion_g) "
                        "VALUES (?,?,?,?,?,?)",
                        (fn, _carb100, _prot100, _fat100, _kcal100, f_portion_g),
                    )
                    conn.commit()
                    st.rerun()

    # ═══════════════════ TAB 2 : ENTRAÎNEMENT ═══════════════════
    with tab_training:
        wks = load_workouts(conn, sel_str)

        st.subheader("Importer une séance (.fit)")
        if not FITPARSE_AVAILABLE:
            st.warning("Module `fitparse` non installé. Lance `pip install fitparse`.")
        else:
            fit_file = st.file_uploader("Glisse ton fichier .fit ici", type=["fit"], key="fit_upload")
            if fit_file is not None:
                # Reset pending foods when a new file is loaded
                if st.session_state.get("_last_fit_name") != fit_file.name:
                    st.session_state._last_fit_name = fit_file.name
                    st.session_state.pending_fit_foods = []
                try:
                    fit_data = parse_fit(bytes(fit_file.getvalue()), zone_map)
                    st.success("Fichier .fit analysé ✓")

                    rc1, rc2, rc3 = st.columns(3)
                    rc1.metric("Durée",    f"{fit_data['duration_min']} min" if fit_data["duration_min"] else "—")
                    rc2.metric("Calories", f"{fit_data['calories']} kcal"    if fit_data["calories"]     else "—")
                    rc3.metric("D+",       f"{fit_data['elevation_m']} m")

                    rh1, rh2, rh3 = st.columns(3)
                    rh1.metric("Sport détecté", fit_data["sport"])
                    rh2.metric("FC moy.", f"{fit_data['avg_hr']} bpm"           if fit_data["avg_hr"]         else "—")
                    rh3.metric("FC max",  f"{fit_data['max_hr_session']} bpm"   if fit_data["max_hr_session"] else "—")

                    z_vals = [fit_data[f"hr_z{i}_min"] for i in range(1, 6)]
                    if sum(z_vals) > 0:
                        st.markdown("**Temps dans les zones FC**")
                        _preview_bounds = zone_map.get(fit_data["sport"], [130, 148, 163, 175])
                        st.plotly_chart(hr_zone_chart(*z_vals, bounds=_preview_bounds),
                                        use_container_width=True, key="zone_chart_preview")
                    elif not fit_data["avg_hr"]:
                        st.caption("Aucune donnée FC dans ce fichier.")

                    sport_opts = ["Trail", "Vélo", "Athlé", "Natation"]
                    default_idx = sport_opts.index(fit_data["sport"]) if fit_data["sport"] in sport_opts else 0
                    fit_sport = st.selectbox("Sport (confirmer)", sport_opts,
                                            index=default_idx, key="fit_sport")

                    # ── Nutrition pendant l'effort ──
                    st.markdown("---")
                    with st.expander("🍌 Nutrition pendant l'effort (optionnel)"):
                        fit_favs = pd.read_sql_query(
                            "SELECT * FROM favorite_foods ORDER BY name", conn)
                        if st.session_state.pending_fit_foods:
                            fh1, fh2, fh3, fh4, fh5, fh6, _ = st.columns([3, 1.2, 1, 1, 1, 1, 0.6])
                            for col, lbl in zip([fh1, fh2, fh3, fh4, fh5, fh6],
                                                ["Aliment", "Qté (g)", "G", "P", "L", "Kcal"]):
                                col.markdown(f"<small><b>{lbl}</b></small>", unsafe_allow_html=True)
                            to_del_fit = None
                            for i, food in enumerate(st.session_state.pending_fit_foods):
                                fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns([3, 1.2, 1, 1, 1, 1, 0.6])
                                fc1.write(food["food_name"])
                                fc2.write(f"{food['quantity_g']:.0f}g")
                                fc3.write(f"{food['carbs_g']:.1f}")
                                fc4.write(f"{food['protein_g']:.1f}")
                                fc5.write(f"{food['fat_g']:.1f}")
                                fc6.write(f"{food['kcal']:.0f}")
                                if fc7.button("❌", key=f"del_fit_{i}"):
                                    to_del_fit = i
                            if to_del_fit is not None:
                                st.session_state.pending_fit_foods.pop(to_del_fit)
                                st.rerun()
                            pf_df = pd.DataFrame(st.session_state.pending_fit_foods)
                            st.caption(
                                f"Total effort : **{pf_df.kcal.sum():.0f} kcal** — "
                                f"G {pf_df.carbs_g.sum():.0f}g · P {pf_df.protein_g.sum():.0f}g · L {pf_df.fat_g.sum():.0f}g"
                            )
                        fit_fa1, fit_fa2 = st.columns(2)
                        with fit_fa1:
                            st.markdown("**Depuis les favoris**")
                            fit_fav_sel = st.selectbox(
                                "Aliment", fit_favs["name"].tolist(), key="fit_fav_sel")
                            fit_fav_qty = st.number_input(
                                "Quantité (g)", 1, 1000, 50, 5, key="fit_fav_qty")
                            if st.button("➕ Ajouter", key="fit_fav_add"):
                                frow = fit_favs[fit_favs["name"] == fit_fav_sel].iloc[0]
                                r = fit_fav_qty / 100
                                st.session_state.pending_fit_foods.append({
                                    "food_name":  fit_fav_sel,
                                    "quantity_g": fit_fav_qty,
                                    "carbs_g":    round(frow.carbs_per_100   * r, 1),
                                    "protein_g":  round(frow.protein_per_100 * r, 1),
                                    "fat_g":      round(frow.fat_per_100     * r, 1),
                                    "kcal":       round(frow.kcal_per_100    * r),
                                })
                                st.rerun()
                        with fit_fa2:
                            st.markdown("**Saisie libre**")
                            fit_mn   = st.text_input("Nom", key="fit_mn")
                            fit_mqty = st.number_input("Qté (g)", 1, 2000, 100, key="fit_mqty")
                            fmc1, fmc2 = st.columns(2)
                            fit_mc = fmc1.number_input("G (g)",  0.0, 500.0, 0.0, 0.5, key="fit_mc")
                            fit_mp = fmc2.number_input("P (g)",  0.0, 500.0, 0.0, 0.5, key="fit_mp")
                            fit_ml = fmc1.number_input("L (g)",  0.0, 500.0, 0.0, 0.5, key="fit_ml")
                            fit_mk = fmc2.number_input("Kcal",   0.0, 2000.0, 0.0, 1.0, key="fit_mk")
                            if st.button("➕ Ajouter", key="fit_manual_add"):
                                if fit_mn:
                                    st.session_state.pending_fit_foods.append({
                                        "food_name":  fit_mn,
                                        "quantity_g": fit_mqty,
                                        "carbs_g":    fit_mc,
                                        "protein_g":  fit_mp,
                                        "fat_g":      fit_ml,
                                        "kcal":       fit_mk,
                                    })
                                    st.rerun()

                    if st.button("💾 Enregistrer la séance FIT"):
                        dur = fit_data["duration_min"] or 60
                        hard_min = z_vals[3] + z_vals[4]
                        intensity = "Fractionné/PMA" if hard_min > dur * 0.2 else "Zone 2"
                        conn.execute(
                            """INSERT INTO workouts
                               (date, type, duration_min, elevation_m, intensity,
                                kcal_actual, avg_hr, max_hr_session,
                                hr_z1_min, hr_z2_min, hr_z3_min, hr_z4_min, hr_z5_min, source)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (sel_str, fit_sport, dur, fit_data["elevation_m"], intensity,
                             fit_data["calories"], fit_data["avg_hr"], fit_data["max_hr_session"],
                             *z_vals, "fit"),
                        )
                        for food in st.session_state.pending_fit_foods:
                            conn.execute(
                                """INSERT INTO meals
                                   (date, meal_type, meal_time, food_name,
                                    quantity_g, carbs_g, protein_g, fat_g, kcal)
                                   VALUES (?,?,?,?,?,?,?,?,?)""",
                                (sel_str, "Pendant l'effort", "12:00",
                                 food["food_name"], food["quantity_g"],
                                 food["carbs_g"], food["protein_g"],
                                 food["fat_g"], food["kcal"]),
                            )
                        conn.commit()
                        st.session_state.pending_fit_foods = []
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur parsing .fit : {e}")

        with st.expander("✏️ Saisie manuelle"):
            tc1, tc2 = st.columns(2)
            w_type      = tc1.selectbox("Type",      ["Trail", "Vélo", "Athlé", "Natation"])
            w_intensity = tc2.selectbox("Intensité", ["Zone 2", "Fractionné/PMA"])
            w_dur  = tc1.number_input("Durée (min)", 10, 600, 60, 5)
            w_elev = tc2.number_input("D+ (m)",       0, 5000,  0, 50)
            if st.button("💾 Enregistrer séance manuelle"):
                conn.execute(
                    "INSERT INTO workouts "
                    "(date,type,duration_min,elevation_m,intensity,source) VALUES (?,?,?,?,?,?)",
                    (sel_str, w_type, w_dur, w_elev, w_intensity, "manual"),
                )
                conn.commit()
                st.rerun()

        if not wks.empty:
            st.markdown(f"**Séances du {sel_str}**")
            for wi, (_, w) in enumerate(wks.iterrows()):
                kcal_w     = workout_kcal(w, weight_current)
                source_tag = "📡 FIT" if w.source == "fit" else "✏️ Manuel"
                wc1, wc2, wc3, wc4 = st.columns(4)
                wc1.markdown(f"**{w.type}** — {source_tag}")
                wc2.metric("Durée", f"{w.duration_min} min")
                wc3.metric("D+",    f"{int(w.elevation_m)} m")
                wc4.metric("Kcal",  f"{kcal_w:.0f}")

                if w.source == "fit":
                    if pd.notna(w.avg_hr) and w.avg_hr:
                        hc1, hc2 = st.columns(2)
                        hc1.metric("FC moy.", f"{int(w.avg_hr)} bpm")
                        if pd.notna(w.max_hr_session) and w.max_hr_session:
                            hc2.metric("FC max", f"{int(w.max_hr_session)} bpm")
                    z_vals = [w.hr_z1_min, w.hr_z2_min, w.hr_z3_min, w.hr_z4_min, w.hr_z5_min]
                    if any(v > 0 for v in z_vals):
                        _wk_bounds = zone_map.get(w.type, [130, 148, 163, 175])
                        st.plotly_chart(hr_zone_chart(*z_vals, bounds=_wk_bounds),
                                        use_container_width=True, key=f"zone_chart_{w.id}_{wi}")

                st.markdown("---")

            total_training_kcal = sum(workout_kcal(w, weight_current) for _, w in wks.iterrows())
            st.info(
                f"⏱️ **Nutrient Timing** — {total_training_kcal:.0f} kcal dépensées. "
                "Prévois 60-80g de glucides dans les 2h avant et 40-60g dans les 30min post-effort."
            )

            del_opts = {int(w.id): f"{w.type} — {w.duration_min}min ({w.source})"
                        for _, w in wks.iterrows()}
            del_id = st.selectbox("Supprimer une séance", list(del_opts.keys()),
                                  format_func=lambda x: del_opts[x])
            if st.button("🗑️ Supprimer séance"):
                conn.execute("DELETE FROM workouts WHERE id=?", (del_id,))
                conn.commit()
                st.rerun()
        else:
            st.info("Aucune séance enregistrée pour cette date.")

    # ═══════════════════ TAB 3 : FORME ═══════════════════
    with tab_forme:
        day_fr_forme = selected_date.strftime("%A %d %B %Y").capitalize()
        st.subheader(f"🌅 Routine du matin — {day_fr_forme}")

        ml_row = conn.execute(
            "SELECT weight_kg, sleep_duration_h, sleep_quality, hrv_readiness, "
            "hrv_rmssd, hrv_pns, hrv_sns, hrv_mean_hr, hrv_time FROM morning_log WHERE date=?",
            (sel_str,),
        ).fetchone()

        with st.form("morning_form"):
            fm_c1, fm_c2 = st.columns(2)

            with fm_c1:
                st.markdown("**⚖️ Corps & Sommeil**")
                fm_weight  = st.number_input(
                    "Poids (kg)", 40.0, 150.0,
                    float(ml_row[0]) if ml_row and ml_row[0] is not None else weight_current,
                    0.1,
                )
                fm_sleep_h = st.number_input(
                    "Durée sommeil (h)", 0.0, 14.0,
                    float(ml_row[1]) if ml_row and ml_row[1] is not None else 7.5,
                    0.25,
                )
                fm_sleep_q = st.slider(
                    "Qualité sommeil (1–5)", 1, 5,
                    int(ml_row[2]) if ml_row and ml_row[2] is not None else 3,
                )

            with fm_c2:
                st.markdown("**🫀 Kubios HRV**")
                _hrv_time_default = (
                    time(int(ml_row[8].split(":")[0]), int(ml_row[8].split(":")[1]))
                    if ml_row and ml_row[8] is not None
                    else time(7, 0)
                )
                fm_hrv_time = st.time_input("Heure de mesure HRV", _hrv_time_default)
                fm_readiness = st.number_input(
                    "Readiness (%)", 0, 100,
                    int(ml_row[3]) if ml_row and ml_row[3] is not None else 70,
                )
                fm_rmssd = st.number_input(
                    "RMSSD (ms)", 0.0, 250.0,
                    float(ml_row[4]) if ml_row and ml_row[4] is not None else 50.0,
                    0.5,
                )
                fm_pns = st.number_input(
                    "PNS index", -5.0, 5.0,
                    float(ml_row[5]) if ml_row and ml_row[5] is not None else 0.0,
                    0.1,
                )
                fm_sns = st.number_input(
                    "SNS index", -5.0, 5.0,
                    float(ml_row[6]) if ml_row and ml_row[6] is not None else 0.0,
                    0.1,
                )
                fm_mean_hr = st.number_input(
                    "FC repos (bpm)", 30, 120,
                    int(ml_row[7]) if ml_row and ml_row[7] is not None else 50,
                )

            if st.form_submit_button("💾 Enregistrer la matinée", type="primary"):
                conn.execute(
                    """INSERT OR REPLACE INTO morning_log
                       (date, weight_kg, sleep_duration_h, sleep_quality,
                        hrv_readiness, hrv_rmssd, hrv_pns, hrv_sns, hrv_mean_hr, hrv_time)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (sel_str, fm_weight, fm_sleep_h, fm_sleep_q,
                     fm_readiness, fm_rmssd, fm_pns, fm_sns, fm_mean_hr,
                     fm_hrv_time.strftime("%H:%M")),
                )
                conn.execute(
                    "INSERT OR REPLACE INTO weight_log (date, weight_kg) VALUES (?,?)",
                    (sel_str, fm_weight),
                )
                conn.commit()
                st.rerun()

        if ml_row:
            if st.button("🗑️ Supprimer cette matinée", key="del_morning"):
                conn.execute("DELETE FROM morning_log WHERE date=?", (sel_str,))
                conn.execute("DELETE FROM weight_log WHERE date=?", (sel_str,))
                conn.commit()
                st.rerun()

        # Reload after possible save
        ml_row = conn.execute(
            "SELECT weight_kg, sleep_duration_h, sleep_quality, hrv_readiness, "
            "hrv_rmssd, hrv_pns, hrv_sns, hrv_mean_hr, hrv_time FROM morning_log WHERE date=?",
            (sel_str,),
        ).fetchone()

        if ml_row and ml_row[3] is not None:
            readiness = float(ml_row[3])
            r_color = "#2ecc71" if readiness >= 70 else "#f1c40f" if readiness >= 50 else "#e74c3c"
            r_label = "Optimal" if readiness >= 70 else "Modéré" if readiness >= 50 else "Faible"
            st.markdown("---")
            st.markdown(
                f"### Forme du jour : "
                f"<span style='color:{r_color}'>{readiness:.0f}% — {r_label}</span>",
                unsafe_allow_html=True,
            )
            sm1, sm2, sm3, sm4, sm5 = st.columns(5)
            sm1.metric(
                "Readiness",
                f"{readiness:.0f}%",
                f"⏱ {ml_row[8]}" if ml_row[8] is not None else "",
            )
            sm2.metric(
                "Sommeil",
                f"{float(ml_row[1]):.1f}h" if ml_row[1] is not None else "—",
                f"Qualité {ml_row[2]}/5" if ml_row[2] is not None else "",
            )
            sm3.metric("RMSSD", f"{float(ml_row[4]):.0f} ms" if ml_row[4] is not None else "—")
            sm4.metric(
                "PNS / SNS",
                f"{float(ml_row[5]):+.1f} / {float(ml_row[6]):+.1f}"
                if ml_row[5] is not None else "—",
            )
            sm5.metric("FC repos", f"{int(ml_row[7])} bpm" if ml_row[7] is not None else "—")

        # Historical trends
        morning_hist = pd.read_sql_query("SELECT * FROM morning_log ORDER BY date", conn)
        if not morning_hist.empty:
            morning_hist["date_dt"] = pd.to_datetime(morning_hist["date"])
            st.markdown("---")
            st.subheader("📈 Tendances")

            # Readiness
            if morning_hist["hrv_readiness"].notna().any():
                fig_r = go.Figure()
                fig_r.add_hrect(y0=70, y1=100, fillcolor="rgba(46,204,113,0.12)",  line_width=0)
                fig_r.add_hrect(y0=50, y1=70,  fillcolor="rgba(241,196,15,0.12)",  line_width=0)
                fig_r.add_hrect(y0=0,  y1=50,  fillcolor="rgba(231,76,60,0.12)",   line_width=0)
                fig_r.add_trace(go.Scatter(
                    x=morning_hist.date_dt, y=morning_hist.hrv_readiness,
                    mode="lines+markers", name="Readiness",
                    line=dict(color="#2ecc71", width=2),
                    fill="tozeroy", fillcolor="rgba(46,204,113,0.08)",
                ))
                fig_r.update_layout(
                    height=220, margin=dict(t=10, b=10),
                    yaxis=dict(title="Readiness (%)", range=[0, 100]),
                )
                st.markdown("**🎯 Readiness**")
                st.plotly_chart(fig_r, use_container_width=True, key="fig_readiness")

            # RMSSD + FC repos
            hv1, hv2 = st.columns(2)
            with hv1:
                if morning_hist["hrv_rmssd"].notna().any():
                    fig_rmssd = go.Figure(go.Scatter(
                        x=morning_hist.date_dt, y=morning_hist.hrv_rmssd,
                        mode="lines+markers", line=dict(color="#3498db", width=2),
                    ))
                    fig_rmssd.update_layout(height=200, margin=dict(t=10, b=10),
                                            yaxis_title="RMSSD (ms)")
                    st.markdown("**RMSSD**")
                    st.plotly_chart(fig_rmssd, use_container_width=True, key="fig_rmssd")
            with hv2:
                if morning_hist["hrv_mean_hr"].notna().any():
                    fig_fcr = go.Figure(go.Scatter(
                        x=morning_hist.date_dt, y=morning_hist.hrv_mean_hr,
                        mode="lines+markers", line=dict(color="#e74c3c", width=2),
                    ))
                    fig_fcr.update_layout(height=200, margin=dict(t=10, b=10),
                                          yaxis_title="FC repos (bpm)")
                    st.markdown("**FC repos**")
                    st.plotly_chart(fig_fcr, use_container_width=True, key="fig_fc_repos")

            # PNS / SNS
            if morning_hist["hrv_pns"].notna().any():
                fig_ans = go.Figure()
                fig_ans.add_trace(go.Bar(
                    x=morning_hist.date_dt, y=morning_hist.hrv_pns,
                    name="PNS (parasympathique)", marker_color="#2ecc71",
                ))
                fig_ans.add_trace(go.Bar(
                    x=morning_hist.date_dt, y=morning_hist.hrv_sns,
                    name="SNS (sympathique)", marker_color="#e74c3c",
                ))
                fig_ans.add_hline(y=0, line_color="#aaaaaa", line_width=1)
                fig_ans.update_layout(
                    height=220, barmode="group",
                    margin=dict(t=10, b=10), yaxis_title="Index",
                    legend=dict(orientation="h", y=-0.3),
                )
                st.markdown("**⚖️ Équilibre SNA — PNS (récup) vs SNS (stress)**")
                st.plotly_chart(fig_ans, use_container_width=True, key="fig_ans")

            # Poids
            wt_hist = morning_hist[morning_hist["weight_kg"].notna()].copy()
            if not wt_hist.empty:
                wt_hist["MA7"] = wt_hist["weight_kg"].rolling(7, min_periods=1).mean()
                fig_w = go.Figure()
                fig_w.add_trace(go.Scatter(
                    x=wt_hist.date_dt, y=wt_hist.weight_kg,
                    mode="markers+lines", name="Poids",
                    line=dict(color="#95a5a6", width=1),
                    marker=dict(size=8, color="#3498db"),
                ))
                if len(wt_hist) >= 2:
                    fig_w.add_trace(go.Scatter(
                        x=wt_hist.date_dt, y=wt_hist.MA7,
                        mode="lines", name="Moy. 7j",
                        line=dict(color="#2980b9", width=3),
                    ))
                fig_w.update_layout(height=220, margin=dict(t=10, b=10), yaxis_title="kg")
                st.markdown("**⚖️ Poids**")
                st.caption("Clique sur un point pour supprimer cette entrée.")
                w_sel_forme = st.plotly_chart(
                    fig_w, use_container_width=True,
                    on_select="rerun", selection_mode="points",
                    key="weight_chart_forme",
                )
                if w_sel_forme and w_sel_forme.selection and w_sel_forme.selection.points:
                    pt = w_sel_forme.selection.points[0]
                    if pt.get("curve_number", 0) == 0:
                        pt_idx    = pt["point_index"]
                        pt_date   = wt_hist.iloc[pt_idx]["date"]
                        pt_weight = wt_hist.iloc[pt_idx]["weight_kg"]
                        st.warning(f"📍 Sélectionné : **{pt_date}** — {pt_weight} kg")
                        if st.button("🗑️ Supprimer cette entrée de poids", type="primary"):
                            conn.execute("DELETE FROM morning_log WHERE date=?", (pt_date,))
                            conn.execute("DELETE FROM weight_log WHERE date=?", (pt_date,))
                            conn.commit()
                            st.rerun()

            # Sommeil
            sl_hist = morning_hist[morning_hist["sleep_duration_h"].notna()].copy()
            if not sl_hist.empty:
                fig_sl = go.Figure()
                fig_sl.add_trace(go.Bar(
                    x=sl_hist.date_dt, y=sl_hist.sleep_duration_h,
                    name="Durée (h)", marker_color="#9b59b6", opacity=0.8,
                ))
                fig_sl.add_hline(y=8, line_dash="dash", line_color="#f1c40f",
                                 annotation_text="8h recommandées")
                if sl_hist["sleep_quality"].notna().any():
                    fig_sl.add_trace(go.Scatter(
                        x=sl_hist.date_dt, y=sl_hist.sleep_quality,
                        mode="lines+markers", name="Qualité (1–5)",
                        yaxis="y2", line=dict(color="#f39c12", width=2),
                        marker=dict(size=8),
                    ))
                    fig_sl.update_layout(yaxis2=dict(
                        title="Qualité (1–5)", overlaying="y", side="right",
                        range=[0, 5], showgrid=False, dtick=1,
                    ))
                fig_sl.update_layout(
                    height=220, margin=dict(t=10, b=10),
                    yaxis=dict(title="Heures", range=[0, 12]),
                    legend=dict(orientation="h", y=-0.3),
                )
                st.markdown("**😴 Sommeil**")
                st.plotly_chart(fig_sl, use_container_width=True, key="fig_sommeil")

    # ═══════════════════ TAB 4 : PERFORMANCE ═══════════════════
    with tab_perf:
        st.subheader("Balance énergétique du jour")
        meals_today  = load_meals(conn, sel_str)
        wks_today_p  = load_workouts(conn, sel_str)
        intake       = float(meals_today.kcal.sum()) if not meals_today.empty else 0.0
        training_exp = (
            sum(workout_kcal(w, weight_current) for _, w in wks_today_p.iterrows())
            if not wks_today_p.empty else 0.0
        )
        total_exp = base_tdee + training_exp

        ec1, ec2, ec3 = st.columns(3)
        ec1.metric("Apport alimentaire",     f"{intake:.0f} kcal")
        ec2.metric("Dépense totale estimée", f"{total_exp:.0f} kcal",
                   help=f"Base TDEE {base_tdee:.0f} kcal + entraînement {training_exp:.0f} kcal")
        ec3.metric("Balance",                f"{intake - total_exp:+.0f} kcal", delta_color="off")

        st.subheader("Ressenti du soir")
        sc1, sc2 = st.columns(2)
        s_fatigue = sc1.slider("Fatigue (1=frais → 5=épuisé)",  1, 5, 2, key="s_fat")
        s_satiety = sc2.slider("Satiété (1=faim → 5=rassasié)", 1, 5, 3, key="s_sat")
        st.caption("Le sommeil est saisi dans l'onglet 🫀 Forme.")
        if st.button("💾 Enregistrer ressenti"):
            ml_sq = conn.execute(
                "SELECT sleep_quality FROM morning_log WHERE date=?", (sel_str,)
            ).fetchone()
            s_sleep = int(ml_sq[0]) if ml_sq and ml_sq[0] is not None else 3
            conn.execute(
                "INSERT OR REPLACE INTO daily_scores "
                "(date,fatigue,satiety,sleep_quality) VALUES (?,?,?,?)",
                (sel_str, s_fatigue, s_satiety, s_sleep),
            )
            conn.commit()
            st.success("Ressenti enregistré.")

        st.subheader("Charge hebdo (7 derniers jours)")
        week_start = (date.today() - timedelta(days=6)).isoformat()
        week_wks   = pd.read_sql_query(
            "SELECT * FROM workouts WHERE date >= ? ORDER BY date",
            conn, params=(week_start,),
        )
        if not week_wks.empty:
            week_wks["kcal_disp"] = week_wks.apply(
                lambda r: workout_kcal(r, weight_current), axis=1)
            fig_week = px.bar(
                week_wks, x="date", y="duration_min", color="type",
                labels={"duration_min": "Durée (min)", "date": "", "type": "Sport"},
                title="Volume hebdomadaire",
            )
            fig_week.update_layout(height=280)
            st.plotly_chart(fig_week, use_container_width=True)

            wk1, wk2, wk3 = st.columns(3)
            wk1.metric("Volume total",      f"{week_wks.duration_min.sum() / 60:.1f}h")
            wk2.metric("D+ cumulé",         f"{week_wks.elevation_m.sum():.0f}m")
            wk3.metric("Kcal entraînement", f"{week_wks.kcal_disp.sum():.0f}")

            _zone_cols_week = ["hr_z1_min", "hr_z2_min", "hr_z3_min", "hr_z4_min", "hr_z5_min"]
            fit_wks_week = week_wks[week_wks[_zone_cols_week].fillna(0).sum(axis=1) > 0].copy()
            if not fit_wks_week.empty:
                zone_col_map = {f"hr_z{i}_min": _ZONE_LABELS[i - 1] for i in range(1, 6)}
                melted_zones = fit_wks_week.melt(
                    id_vars=["type"],
                    value_vars=_zone_cols_week,
                    var_name="zone",
                    value_name="minutes",
                )
                melted_zones["zone"] = melted_zones["zone"].map(zone_col_map)
                melted_zones["zone"] = pd.Categorical(
                    melted_zones["zone"], categories=_ZONE_LABELS, ordered=True)
                zone_agg = (
                    melted_zones.groupby(["zone", "type"], observed=True)["minutes"]
                    .sum()
                    .reset_index()
                    .sort_values("zone")
                )
                fig_zones = px.bar(
                    zone_agg, x="zone", y="minutes", color="type",
                    barmode="stack",
                    labels={"minutes": "Durée (min)", "zone": "Zone FC", "type": "Sport"},
                    title="Temps dans les zones FC (7 jours)",
                )
                fig_zones.update_layout(height=280, margin=dict(t=40, b=20, l=30, r=10))
                st.plotly_chart(fig_zones, use_container_width=True)
        else:
            st.caption("Aucune séance cette semaine.")

        st.subheader("Corrélation charge ↔ ressenti")
        scores_df = pd.read_sql_query("SELECT * FROM daily_scores ORDER BY date", conn)
        if len(scores_df) >= 5:
            history = []
            for _, row in scores_df.iterrows():
                d       = row["date"]
                day_wks = pd.read_sql_query(
                    "SELECT * FROM workouts WHERE date=?", conn, params=(d,))
                day_load = (
                    sum(workout_kcal(w, weight_current) for _, w in day_wks.iterrows())
                    if not day_wks.empty else 0
                )
                history.append({
                    "date": d, "charge_kcal": day_load,
                    "fatigue": row.fatigue, "satiety": row.satiety,
                    "sleep": row.sleep_quality,
                })
            hist_df  = pd.DataFrame(history)
            fig_corr = px.scatter(
                hist_df, x="charge_kcal", y="fatigue", color="sleep",
                labels={"charge_kcal": "Charge (kcal)", "fatigue": "Fatigue (1-5)",
                        "sleep": "Sommeil"},
                color_continuous_scale="RdYlGn_r",
                title="Fatigue vs Charge entraînement (couleur = sommeil)",
            )
            fig_corr.update_layout(height=320)
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.caption("5 jours de données minimum pour afficher les corrélations.")

    conn.close()


if __name__ == "__main__":
    main()
