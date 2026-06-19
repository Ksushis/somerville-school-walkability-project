"""
Walking distances for the 982 high-resolution sample points (West Somerville
and Kennedy zones, ~5 points per street instead of 1) to their assigned
school.

Run: python3 fetch_west_kennedy_resample_walks.py
Outputs: west_kennedy_resample_walks.json -- upload to Claude
"""
import urllib.request, json, time, math, csv

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
KENNEDY = [-71.115523, 42.389388]
WEST = [-71.126467, 42.406166]

DEST_BY_SCHOOL = {
    "KENNEDY": KENNEDY,
    "WEST SOMERVILLE": WEST,
}

samples = []
with open("west_kennedy_resample_clean.csv") as f:
    for row in csv.DictReader(f):
        samples.append({
            "address": row["address"],
            "street":  row["street"],
            "num":     row["num"],
            "school":  row["school"],
            "lat":     float(row["Geocodio Latitude"]),
            "lon":     float(row["Geocodio Longitude"]),
        })

def ors_walk(dest, lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], dest], "units": "mi"}).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers={
                "Authorization": ORS_KEY, "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            feature = data["features"][0]
            return (
                round(feature["properties"]["summary"]["distance"], 2),
                round(feature["properties"]["summary"]["duration"] / 60, 1)
            )
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print("    Rate limited, waiting " + str(wait) + "s...")
                time.sleep(wait)
            else:
                raise

results = []
total = len(samples)
print("Routing " + str(total) + " points...\n")
for i, s in enumerate(samples):
    dest = DEST_BY_SCHOOL.get(s["school"].upper())
    if dest is None:
        print("[" + str(i+1).rjust(4) + "/" + str(total) + "] " + s["street"] + " " + s["num"] + ": SKIPPED (unknown school " + s["school"] + ")")
        continue
    try:
        dist, mins = ors_walk(dest, s["lon"], s["lat"])
        adj = math.ceil(mins * 1.13)
        results.append({**s, "walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
        if (i+1) % 25 == 0 or i == 0:
            print("[" + str(i+1).rjust(4) + "/" + str(total) + "] " + s["street"] + " " + s["num"] + ": " + str(dist) + " mi (" + str(adj) + " min)")
    except Exception as e:
        print("[" + str(i+1).rjust(4) + "/" + str(total) + "] " + s["street"] + " " + s["num"] + ": ERROR " + str(e))
        results.append({**s, "walk_mi": None, "walk_min": None, "walk_min_adj": None})
    time.sleep(2)

with open("west_kennedy_resample_walks.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r["walk_mi"] is None]
print("\nDone. Total: " + str(len(results)) + ", Failed: " + str(len(failed)))
print("Upload west_kennedy_resample_walks.json to Claude")
