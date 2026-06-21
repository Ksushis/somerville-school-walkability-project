"""
BROWN 6-8 DESTINATION MISMATCH ANALYSIS
=========================================
Attaches each Brown street's known 6-8 destination (from the official
street register) to every Brown address in proximity_analysis.json, then
checks whether that destination is actually the closest of the three
valid 6-8 candidates (Kennedy / West Somerville / Winter Hill) by
straight-line distance.

This does NOT call any API -- pure local math, free to run repeatedly.

USAGE:
  Place this script in the same folder as proximity_analysis.json
  Run: python3 analyze_brown_6_8.py
  Outputs:
    - brown_6_8_analysis.csv
    - brown_6_8_analysis.json
"""
import json
import csv

# Street -> 6-8 destination, from the official Somerville street register
# (Source: Street_Register_2.2.26 -- lines reading "K-5 BROWN / 6-8 X")
STREET_TO_6_8 = {
    "Albion Court": "Winter Hill",
    "Albion Place": "Winter Hill",
    "Albion Street": "Kennedy",       # 94-179 segment
    "Albion Terrace": "Winter Hill",
    "Appleton Street": "West Somerville",
    "Alpine Street": "Kennedy",
    "Bay State Avenue": "West Somerville",
    "Bellevue Terrace": "Winter Hill",
    "Boston Avenue": "West Somerville",   # 1-158 segment
    "Broadway": "West Somerville",        # 585-726 segment
    "Cedar Street": "West Somerville",    # 107-165/154-end segment
    "Clifton Street": "Kennedy",
    "Clyde Street": "Winter Hill",
    "College Avenue": "West Somerville",  # 1-143 segment
    "Ellington Road": "Kennedy",
    "Elm Court": "West Somerville",
    "Foskett Street": "Kennedy",
    "Francesca Avenue": "West Somerville",
    "Grove Street": "West Somerville",
    "Hall Avenue": "West Somerville",
    "Highland Avenue": "Kennedy",         # 219-407 segment
    "Highland Road": "West Somerville",
    "Josephine Avenue": "West Somerville",
    "Kidder Avenue": "West Somerville",
    "Liberty Avenue": "West Somerville",
    "Liberty Road": "West Somerville",
    "Lowden Avenue": "West Somerville",
    "Mallet Street": "West Somerville",
    "Maxwell's Green": "Kennedy",
    "Maxwells Green": "Kennedy",  # apostrophe variant
    "Morrison Avenue": "West Somerville",
    "Morrison Place": "West Somerville",
    "Murdock Street": "Winter Hill",
    "Newman Place": "Winter Hill",
    "Pearson Avenue": "West Somerville",
    "Powder House Terrace": "West Somerville",
    "Prichard Avenue": "West Somerville",
    "Princeton Street": "Kennedy",
    "Rogers Avenue": "West Somerville",
    "Warwick Street": "Winter Hill",
    "Willow Avenue": "West Somerville",   # 130-end segment
    "Wilson Avenue": "West Somerville",
    "Winslow Avenue": "West Somerville",
}

SIX_EIGHT_CANDIDATES = ["Kennedy", "West Somerville", "Winter Hill"]


def main():
    try:
        with open("proximity_analysis.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: proximity_analysis.json not found in this directory.")
        return

    print(f"Loaded {len(data)} total addresses.")

    brown_records = [d for d in data if d.get("zone_k5_assigned") == "Brown"]
    print(f"Brown addresses: {len(brown_records)}")

    unmatched_streets = set()
    mismatch_count = 0
    matched_count = 0

    for d in brown_records:
        street = d.get("street", "")
        dest_6_8 = STREET_TO_6_8.get(street)

        if dest_6_8 is None:
            unmatched_streets.add(street)
            d["dest_6_8_assigned"] = None
            d["dest_6_8_closest_candidate"] = None
            d["dest_6_8_closest_mi"] = None
            d["dest_6_8_margin_mi"] = None
            d["dest_6_8_is_mismatch"] = None
            continue

        matched_count += 1
        d["dest_6_8_assigned"] = dest_6_8

        six_eight_dists = {
            "Kennedy": d.get("dist_to_Kennedy_mi"),
            "West Somerville": d.get("dist_to_WestSomerville_mi"),
            "Winter Hill": d.get("dist_to_WinterHill_mi"),
        }
        sorted_six_eight = sorted(six_eight_dists.items(), key=lambda x: x[1])
        closest_6_8, closest_6_8_dist = sorted_six_eight[0]
        dest_6_8_dist = six_eight_dists.get(dest_6_8)

        margin = round(dest_6_8_dist - closest_6_8_dist, 4) if dest_6_8_dist is not None else None
        is_mismatch = closest_6_8 != dest_6_8
        if is_mismatch:
            mismatch_count += 1

        d["dest_6_8_closest_candidate"] = closest_6_8
        d["dest_6_8_closest_mi"] = closest_6_8_dist
        d["dest_6_8_margin_mi"] = margin
        d["dest_6_8_is_mismatch"] = is_mismatch

    print(f"\nBrown streets matched to a known 6-8 destination: {matched_count}")
    print(f"Brown streets with NO known 6-8 destination (not in register map): {len(unmatched_streets)}")
    if unmatched_streets:
        print("  Unmatched streets:")
        for s in sorted(unmatched_streets):
            print(f"    {s}")

    print(f"\n6-8 destination mismatches (assigned dest is NOT the closest of the 3 candidates): {mismatch_count}")

    # Write outputs -- just the Brown subset, with the new fields
    with open("brown_6_8_analysis.json", "w") as f:
        json.dump(brown_records, f, indent=2)

    fieldnames = list(brown_records[0].keys()) if brown_records else []
    with open("brown_6_8_analysis.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(brown_records)

    print("\nSaved brown_6_8_analysis.csv and brown_6_8_analysis.json")
    print("Upload brown_6_8_analysis.json to Claude if you want it mapped or reviewed further.")


if __name__ == "__main__":
    main()
