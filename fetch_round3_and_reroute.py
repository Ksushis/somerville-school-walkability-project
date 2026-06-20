"""
Combined script: routes the 15 round-3 corrected points (Harvard St,
Meacham Rd, Evergreen Sq, Chester St, Linden Pl, Harrison Rd, Beacon
Terrace) to their correct school, AND re-routes the 11 points that were
mislabeled West Somerville but are actually Kennedy (Mountain Ave,
Francis St, Ashland St, Hall St, Belmont St, Oak Terrace) to Kennedy.

Run: python3 fetch_round3_and_reroute.py
Outputs: round3_and_reroute_walks.json -- upload to Claude
"""
import urllib.request, json, time, math, csv

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
KENNEDY = [-71.115523, 42.389388]
WEST = [-71.126467, 42.406166]

DEST_BY_SCHOOL = {
    "KENNEDY": KENNEDY,
    "WEST SOMERVILLE": WEST,
}

# Round 3 new geocoded points
round3_samples = []
with open("round3_corrections_clean.csv") as f:
    for row in csv.DictReader(f):
        round3_samples.append({
            "address": row["address"],
            "street":  row["street"],
            "num":     row["num"],
            "school":  row["school"],
            "lat":     float(row["Geocodio Latitude"]),
            "lon":     float(row["Geocodio Longitude"]),
            "source": "round3"
        })

# Points needing re-route from West to Kennedy (coordinates already correct, just wrong destination)
reroute_samples = []
with open("to_reroute_kennedy.json") as f:
    for d in json.load(f):
        reroute_samples.append({
            "address": d.get("address", d["street"] + " " + str(d.get("num",""))),
            "street": d["street"],
            "num": d.get("num", ""),
            "school": "KENNEDY",
            "lat": d["lat"],
            "lon": d["lon"],
            "source": "reroute"
        })

all_samples = round3_samples + reroute_samples

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
total = len(all_samples)
print("Routing " + str(total) + " points...\n")
for i, s in enumerate(all_samples):
    dest = DEST_BY_SCHOOL.get(s["school"].upper())
    try:
        dist, mins = ors_walk(dest, s["lon"], s["lat"])
        adj = math.ceil(mins * 1.13)
        results.append({**s, "walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
        print("[" + str(i+1).rjust(2) + "/" + str(total) + "] (" + s["source"] + ") " + s["street"] + " " + str(s["num"]) + ": " + str(dist) + " mi (" + str(adj) + " min)")
    except Exception as e:
        print("[" + str(i+1).rjust(2) + "/" + str(total) + "] " + s["street"] + " " + str(s["num"]) + ": ERROR " + str(e))
        results.append({**s, "walk_mi": None, "walk_min": None, "walk_min_adj": None})
    time.sleep(2)

with open("round3_and_reroute_walks.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r["walk_mi"] is None]
print("\nDone. Total: " + str(len(results)) + ", Failed: " + str(len(failed)))
print("Upload round3_and_reroute_walks.json to Claude")
