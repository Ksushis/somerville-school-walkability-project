"""
CITYWIDE K-5 MISMATCH BREAKDOWN BY ZONE
=========================================
Takes the existing proximity_analysis.json (already computed) and breaks
down the K-5 mismatches zone by zone, printing street-level detail so you
can see exactly which streets in each zone are flagged and by how much.

Also computes, for each zone, what fraction of its mismatches are
"clustered" (multiple addresses on the same street, suggesting a real
boundary effect) vs. "isolated" (a single address on its own, which is
more likely to be geocoding noise worth a second look).

This does NOT call any API -- pure local math, free to run repeatedly.

USAGE:
  Place this script in the same folder as proximity_analysis.json
  Run: python3 breakdown_mismatches_by_zone.py
  Outputs:
    - mismatches_by_zone.csv
    - mismatches_by_zone.json
    - prints a summary to the console
"""
import json
import csv
from collections import defaultdict, Counter


def main():
    try:
        with open("proximity_analysis.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: proximity_analysis.json not found in this directory.")
        return

    print(f"Loaded {len(data)} total addresses.\n")

    mismatches = [d for d in data if d.get("is_mismatch")]
    print(f"Total K-5 mismatches: {len(mismatches)}")

    by_zone = defaultdict(list)
    for d in mismatches:
        by_zone[d.get("zone_k5_assigned")].append(d)

    print("\n" + "=" * 70)
    print("BREAKDOWN BY ZONE")
    print("=" * 70)

    zone_summary = []

    for zone in sorted(by_zone.keys(), key=lambda z: -len(by_zone[z])):
        zone_mismatches = by_zone[zone]
        total_in_zone = sum(1 for d in data if d.get("zone_k5_assigned") == zone)

        # Group by street to see clustering
        by_street = defaultdict(list)
        for d in zone_mismatches:
            by_street[d.get("street")].append(d)

        clustered_streets = {s: pts for s, pts in by_street.items() if len(pts) >= 2}
        isolated_streets = {s: pts for s, pts in by_street.items() if len(pts) == 1}

        # What's the most common "closer school" for this zone's mismatches?
        closer_school_counts = Counter(d.get("closest_school_by_straight_line") for d in zone_mismatches)
        top_closer = closer_school_counts.most_common(1)[0] if closer_school_counts else (None, 0)

        avg_margin = sum(abs(d.get("margin_mi", 0) or 0) for d in zone_mismatches) / len(zone_mismatches)
        max_margin = max(abs(d.get("margin_mi", 0) or 0) for d in zone_mismatches)

        print(f"\n--- {zone} ---")
        print(f"  Mismatches: {len(zone_mismatches)} / {total_in_zone} ({len(zone_mismatches)/total_in_zone*100:.1f}%)")
        print(f"  Most common 'actually closer' school: {top_closer[0]} ({top_closer[1]} addresses)")
        print(f"  Average margin: {avg_margin:.3f} mi, Max margin: {max_margin:.3f} mi")
        print(f"  Streets with 2+ mismatched addresses (likely real boundary effect): {len(clustered_streets)}")
        for s, pts in sorted(clustered_streets.items(), key=lambda x: -len(x[1])):
            closer = Counter(p.get("closest_school_by_straight_line") for p in pts).most_common(1)[0][0]
            print(f"    {s}: {len(pts)} addresses, mostly closer to {closer}")
        print(f"  Streets with only 1 mismatched address (check before trusting): {len(isolated_streets)}")
        for s in sorted(isolated_streets.keys()):
            pt = isolated_streets[s][0]
            print(f"    {s} {pt.get('num','')}: closer to {pt.get('closest_school_by_straight_line')} by {abs(pt.get('margin_mi',0)):.3f} mi")

        zone_summary.append({
            "zone": zone,
            "total_in_zone": total_in_zone,
            "mismatch_count": len(zone_mismatches),
            "mismatch_pct": round(len(zone_mismatches) / total_in_zone * 100, 1),
            "most_common_closer_school": top_closer[0],
            "avg_margin_mi": round(avg_margin, 3),
            "max_margin_mi": round(max_margin, 3),
            "clustered_street_count": len(clustered_streets),
            "isolated_street_count": len(isolated_streets),
        })

    # Save outputs
    with open("mismatches_by_zone.json", "w") as f:
        json.dump({"zone_summary": zone_summary, "all_mismatches": mismatches}, f, indent=2)

    with open("mismatches_by_zone.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(zone_summary[0].keys()))
        writer.writeheader()
        writer.writerows(zone_summary)

    print("\n\nSaved mismatches_by_zone.csv (zone-level summary) and mismatches_by_zone.json (full detail)")
    print("Upload mismatches_by_zone.json to Claude if you want any of these mapped.")


if __name__ == "__main__":
    main()
