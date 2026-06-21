"""
STRAIGHT-LINE SCHOOL PROXIMITY ANALYSIS
=========================================
Computes straight-line (haversine) distance from every sampled address to
every Somerville K-5/K-8 school, identifies the currently-assigned school,
and flags addresses where another school is actually closer.

For Brown-zone addresses specifically, also checks the K-5 (Brown) zoning
plus tracks the address's 6-8 destination (Kennedy / West Somerville /
Winter Hill, if known) and flags whether that 6-8 destination is the
closest of the three valid 6-8 candidates.

This script does NOT call any API -- it's pure local math, so it costs
nothing to run and can be run as many times as you like.

USAGE:
  Place this script in the same folder as seven_zone_combined.json
  Run: python3 analyze_proximity.py
  Outputs:
    - proximity_analysis.csv   (open in Excel/Sheets)
    - proximity_analysis.json  (upload back to Claude for mapping)
"""
import json
import math
import csv

# --- School coordinates ---
SCHOOLS = {
    "Brown": (42.397302, -71.114010),
    "Kennedy": (42.389388, -71.115523),
    "West Somerville": (42.406166, -71.126467),
    "Winter Hill": (42.391667, -71.098797),
    "Healey": (42.397530, -71.095360),
    "Argenziano": (42.379030, -71.098674),
    "East Somerville": (42.389744, -71.084723),
}

# Valid 6-8 receiving schools for Brown's K-5 catchment
SIX_EIGHT_CANDIDATES = ["Kennedy", "West Somerville", "Winter Hill"]

# Map the 'zone' field used in seven_zone_combined.json to canonical school names above
ZONE_TO_SCHOOL = {
    "Brown": "Brown",
    "Kennedy": "Kennedy",
    "West": "West Somerville",
    "Winter Hill": "Winter Hill",
    "Healey": "Healey",
    "Argenziano": "Argenziano",
    "East Somerville": "East Somerville",
}

# Flagging thresholds (miles)
ANY_MISMATCH_THRESHOLD = 0.0    # flag if ANY other school is closer at all
HIGH_CONFIDENCE_THRESHOLD = 0.15  # flag as "high confidence" if margin exceeds this


def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def main():
    try:
        with open("seven_zone_combined.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: seven_zone_combined.json not found in this directory.")
        print("Make sure you've exported/copied it here from Claude first.")
        return

    print(f"Loaded {len(data)} addresses.")

    results = []
    mismatch_count = 0
    high_confidence_count = 0
    six_eight_mismatch_count = 0

    for d in data:
        lat, lon = d.get("lat"), d.get("lon")
        if lat is None or lon is None:
            continue

        zone = d.get("zone")
        own_school = ZONE_TO_SCHOOL.get(zone)

        # Distance to every school
        dists = {school: round(haversine(lat, lon, *coord), 4) for school, coord in SCHOOLS.items()}
        sorted_schools = sorted(dists.items(), key=lambda x: x[1])
        closest_school, closest_dist = sorted_schools[0]
        own_dist = dists.get(own_school) if own_school else None

        # Margin: how much closer is the actual nearest school vs the assigned one?
        # Positive margin = assigned school is NOT the closest (a real finding)
        margin = None
        is_mismatch = False
        is_high_confidence = False
        if own_dist is not None:
            margin = round(own_dist - closest_dist, 4)
            is_mismatch = closest_school != own_school
            is_high_confidence = is_mismatch and margin > HIGH_CONFIDENCE_THRESHOLD

        if is_mismatch:
            mismatch_count += 1
        if is_high_confidence:
            high_confidence_count += 1

        record = {
            "address": d.get("address"),
            "street": d.get("street"),
            "num": d.get("num", ""),
            "lat": lat,
            "lon": lon,
            "zone_k5_assigned": zone,
            "school_k5_assigned": own_school,
            "walk_min_to_assigned": d.get("walk_min_adj"),
            "straight_line_to_assigned_mi": own_dist,
            "closest_school_by_straight_line": closest_school,
            "closest_straight_line_mi": closest_dist,
            "margin_mi": margin,  # positive = assigned school is NOT closest
            "is_mismatch": is_mismatch,
            "is_high_confidence_mismatch": is_high_confidence,
            # full distance breakdown for reference / later ORS targeting
            "dist_to_Brown_mi": dists["Brown"],
            "dist_to_Kennedy_mi": dists["Kennedy"],
            "dist_to_WestSomerville_mi": dists["West Somerville"],
            "dist_to_WinterHill_mi": dists["Winter Hill"],
            "dist_to_Healey_mi": dists["Healey"],
            "dist_to_Argenziano_mi": dists["Argenziano"],
            "dist_to_EastSomerville_mi": dists["East Somerville"],
        }

        # --- Brown-specific 6-8 destination tracking ---
        if zone == "Brown":
            dest_6_8 = d.get("dest_6_8") or d.get("six_eight_dest")  # field name may vary
            record["dest_6_8_assigned"] = dest_6_8
            if dest_6_8 in SIX_EIGHT_CANDIDATES:
                six_eight_dists = {s: dists[s] for s in SIX_EIGHT_CANDIDATES}
                sorted_six_eight = sorted(six_eight_dists.items(), key=lambda x: x[1])
                closest_6_8, closest_6_8_dist = sorted_six_eight[0]
                dest_6_8_dist = six_eight_dists.get(dest_6_8)
                six_eight_margin = round(dest_6_8_dist - closest_6_8_dist, 4) if dest_6_8_dist is not None else None
                six_eight_mismatch = closest_6_8 != dest_6_8
                if six_eight_mismatch:
                    six_eight_mismatch_count += 1
                record["dest_6_8_closest_candidate"] = closest_6_8
                record["dest_6_8_closest_mi"] = closest_6_8_dist
                record["dest_6_8_margin_mi"] = six_eight_margin
                record["dest_6_8_is_mismatch"] = six_eight_mismatch
            else:
                record["dest_6_8_closest_candidate"] = None
                record["dest_6_8_closest_mi"] = None
                record["dest_6_8_margin_mi"] = None
                record["dest_6_8_is_mismatch"] = None
        else:
            record["dest_6_8_assigned"] = None
            record["dest_6_8_closest_candidate"] = None
            record["dest_6_8_closest_mi"] = None
            record["dest_6_8_margin_mi"] = None
            record["dest_6_8_is_mismatch"] = None

        results.append(record)

    # --- Write outputs ---
    with open("proximity_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

    fieldnames = list(results[0].keys()) if results else []
    with open("proximity_analysis.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nTotal addresses analyzed: {len(results)}")
    print(f"K-5 mismatches (any other school closer by straight-line): {mismatch_count}")
    print(f"K-5 HIGH-CONFIDENCE mismatches (margin > {HIGH_CONFIDENCE_THRESHOLD} mi): {high_confidence_count}")
    print(f"Brown 6-8 destination mismatches: {six_eight_mismatch_count}")
    print(f"\nSaved proximity_analysis.csv and proximity_analysis.json")
    print("Upload proximity_analysis.json to Claude for mapping.")


if __name__ == "__main__":
    main()
