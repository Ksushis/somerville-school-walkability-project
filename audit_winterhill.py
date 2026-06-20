"""
WINTER HILL ZONE — COMPREHENSIVE AUDIT SCRIPT
================================================
This script does three things in sequence:

1. Loads the current Winter Hill zone dataset (winterhill_final.json, which
   you should have saved from earlier in this conversation -- if you don't
   have it, ask Claude to regenerate it first).

2. Computes straight-line (haversine) distance from every sample point to
   the Winter Hill school, and flags any point where the routed walk
   distance is drastically larger than the straight-line distance (ratio
   > 2.5x) OR where straight-line distance itself exceeds 1.5 miles --
   these are the signatures we've repeatedly found indicate a bad geocode
   (usually an address number that doesn't really exist on that street,
   causing geocod.io to fall back to a same-named street elsewhere).

3. Prints a clean report of flagged streets/addresses for manual review,
   sorted by how suspicious they are.

This does NOT automatically delete anything -- it just flags candidates,
the same way we've been doing it together. Bring the printed report back
and we'll go through it street-by-street like before.

USAGE:
  Place this in the same folder as winterhill_final.json
  Run: python3 audit_winterhill.py
  Review the printed report (also saved to winterhill_audit_report.txt)
"""
import json
import math

WINTERHILL = (42.391667, -71.098797)

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def main():
    try:
        with open("winterhill_final.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: winterhill_final.json not found in this directory.")
        print("Ask Claude to regenerate/export this file before running this script.")
        return

    print(f"Loaded {len(data)} Winter Hill zone sample points.\n")

    flagged = []
    clean = []

    for d in data:
        lat, lon = d.get("lat"), d.get("lon")
        walk_mi = d.get("walk_mi")
        if lat is None or lon is None or walk_mi is None:
            continue

        straight = haversine(lat, lon, *WINTERHILL)
        ratio = walk_mi / straight if straight > 0.01 else 1.0

        is_suspicious = (straight > 1.5) or (ratio > 2.5 and straight > 0.3)

        record = {
            "street": d.get("street", "?"),
            "address": d.get("address", "?"),
            "walk_min_adj": d.get("walk_min_adj"),
            "walk_mi": walk_mi,
            "straight_mi": round(straight, 2),
            "ratio": round(ratio, 2),
            "lat": lat,
            "lon": lon,
        }

        if is_suspicious:
            flagged.append(record)
        else:
            clean.append(record)

    flagged.sort(key=lambda r: -r["straight_mi"])

    lines = []
    lines.append("=" * 70)
    lines.append("WINTER HILL ZONE AUDIT REPORT")
    lines.append("=" * 70)
    lines.append(f"Total points checked: {len(data)}")
    lines.append(f"Clean (plausible): {len(clean)}")
    lines.append(f"Flagged (likely bad geocode, needs manual review): {len(flagged)}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("FLAGGED POINTS (sorted by straight-line distance, worst first):")
    lines.append("-" * 70)
    for r in flagged:
        lines.append(
            f"  {r['street']:30s} addr_num={r['address'].split(',')[0].split()[0] if r['address'] != '?' else '?':>6s} "
            f"walk={r['walk_min_adj']}min ({r['walk_mi']}mi)  straight={r['straight_mi']}mi  ratio={r['ratio']}x"
        )

    lines.append("")
    lines.append("-" * 70)
    lines.append("Next steps:")
    lines.append("-" * 70)
    lines.append("1. For each flagged street above, look up the REAL address range")
    lines.append("   (low and high house numbers that actually exist on that street).")
    lines.append("2. Send those ranges back to Claude.")
    lines.append("3. Claude will regenerate correct sample points, you geocode them")
    lines.append("   via geocod.io, then run the routing script Claude provides.")
    lines.append("")
    lines.append("If a flagged street already has OTHER clean points on the same")
    lines.append("street (check the clean list / map), you likely only need to drop")
    lines.append("the one bad point rather than re-doing the whole street.")

    report = "\n".join(lines)
    print(report)

    with open("winterhill_audit_report.txt", "w") as f:
        f.write(report)
    print("\n\nReport saved to winterhill_audit_report.txt")
    print("Upload winterhill_audit_report.txt (or paste the flagged section) to Claude.")

if __name__ == "__main__":
    main()
