"""
Walking distances from all 108 Kennedy zone sample addresses to Winter Hill site.
Place this in the same directory as kennedy_walk.json and run:
  python3 fetch_kennedy_to_winterhill.py
Outputs: kennedy_walk_to_winterhill.json — upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
WINTERHILL = [-71.098797, 42.391667]  # 115 Sycamore St — geocod.io rooftop

with open("kennedy_walk.json") as f:
    samples = json.load(f)

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], WINTERHILL], "units": "mi"}).encode()
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
print("Routing " + str(len(samples)) + " Kennedy-zone addresses to Winter Hill...\n")
for i, s in enumerate(samples):
    try:
        dist, mins = ors_walk(s["lon"], s["lat"])
        adj_mins = math.ceil(mins * 1.13)
        results.append({**s, "wh_walk_mi": dist, "wh_walk_min": mins, "wh_walk_min_adj": adj_mins})
        print("[" + str(i+1).rjust(3) + "/" + str(len(samples)) + "] " + s["street"] + ": " + str(dist) + " mi (" + str(adj_mins) + " min)")
    except Exception as e:
        print("[" + str(i+1).rjust(3) + "/" + str(len(samples)) + "] " + s["street"] + ": ERROR " + str(e))
        results.append({**s, "wh_walk_mi": None, "wh_walk_min": None, "wh_walk_min_adj": None})
    time.sleep(3)

with open("kennedy_walk_to_winterhill.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r["wh_walk_mi"] is None]
print("\nDone. Failed: " + str(len(failed)))
print("Upload kennedy_walk_to_winterhill.json to Claude")
