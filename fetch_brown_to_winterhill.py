"""
Walking distances from all Brown K-5 sample addresses to Winter Hill School.
Run: python3 fetch_brown_to_winterhill.py
Outputs: brown_to_winterhill_walks.json
"""
import urllib.request, json, time, math, csv

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
WINTER_HILL = [-71.098797, 42.391667]  # 115 Sycamore Street

samples = []
with open("brown_samples_geocodio_df74d5fd85cff0842dd85f5c88fd1a8cd3f76725.csv") as f:
    for row in csv.DictReader(f):
        samples.append({
            "address": row["address"],
            "street":  row["street"],
            "num":     row["num"],
            "lat":     float(row["Geocodio Latitude"]),
            "lon":     float(row["Geocodio Longitude"]),
        })

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], WINTER_HILL], "units": "mi"}).encode()
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
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise

results = []
print(f"Routing {len(samples)} addresses to Winter Hill School...\n")
for i, s in enumerate(samples):
    try:
        dist, mins = ors_walk(s["lon"], s["lat"])
        adj_mins = math.ceil(mins * 1.13)
        results.append({**s, "walk_mi": dist, "walk_min": mins, "walk_min_adj": adj_mins})
        print(f"[{i+1:3d}/{len(samples)}] {s['street']} {s['num']}: {dist} mi ({adj_mins} min)")
    except Exception as e:
        print(f"[{i+1:3d}/{len(samples)}] {s['street']} {s['num']}: ERROR {e}")
        results.append({**s, "walk_mi": None, "walk_min": None, "walk_min_adj": None})
    time.sleep(3)

with open("brown_to_winterhill_walks.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r["walk_mi"] is None]
print(f"\nDone. {len(results)} routed, {len(failed)} failed.")
