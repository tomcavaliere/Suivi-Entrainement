"""
Parsing de fichiers FIT (Garmin, etc.) — sans I/O Streamlit.
"""

import io

import fitparse

from physiology import _assign_zone

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

            total_size = 0
            ts_off = ts_sz = hr_off = hr_sz = None
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

            # Store ALL definition types (not just record/20) so data messages
            # for session/lap/event/etc. can be skipped rather than breaking.
            local_defs[local_type] = dict(
                size=total_size, le=le,
                ts_off=ts_off, ts_sz=ts_sz,
                hr_off=hr_off, hr_sz=hr_sz,
            )

        # ── Data message ──────────────────────────────────────────────────
        else:
            if local_type not in local_defs:
                # Definition not seen yet — can't determine size, abort.
                # This only happens if the FIT file is malformed (data before def).
                break
            d = local_defs[local_type]
            if pos + d['size'] > len(data):
                break
            rec = data[pos:pos + d['size']]; pos += d['size']

            ts = None
            if d['ts_off'] is not None and d['ts_sz'] == 4:
                fmt32 = '<I' if d['le'] else '>I'
                ts = _s.unpack_from(fmt32, rec, d['ts_off'])[0]
                if ts:
                    last_ts = ts  # update for compressed-timestamp continuity
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
            if dt < 0 or dt > 300:
                continue
            if dt == 0:
                dt = 1  # 1 Hz recording: same timestamp means 1 s elapsed
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
