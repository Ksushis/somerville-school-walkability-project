"""
Routes Brown's 268 sample addresses to Healey School (the one leg we're
missing for the Brown-catchment 4-school comparison: Winter Hill, Kennedy,
West, Healey).

Run: python3 fetch_brown_to_healey.py
Outputs: brown_to_healey_walks.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
HEALEY = [-71.09536, 42.39753]

with open("brown_addresses_for_healey.json") as f:
    samples = json.load(f)

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], HEALEY], "units": "mi"}).encode()
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
print("Routing " + str(total) + " Brown addresses to Healey...\n")
for i, s in enumerate(samples):
    try:
        dist, mins = ors_walk(s["lon"], s["lat"])
        adj = math.ceil(mins * 1.13)
        results.append({**s, "walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
        if (i+1) % 25 == 0 or i == 0:
            print("[" + str(i+1).rjust(3) + "/" + str(total) + "] " + s["street"] + " " + str(s.get("num","")) + ": " + str(dist) + " mi (" + str(adj) + " min)")
    except Exception as e:
        print("[" + str(i+1).rjust(3) + "/" + str(total) + "] " + s["street"] + ": ERROR " + str(e))
        results.append({**s, "walk_mi": None, "walk_min": None, "walk_min_adj": None})
    time.sleep(2)

with open("brown_to_healey_walks.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r["walk_mi"] is None]
print("\nDone. Total: " + str(len(results)) + ", Failed: " + str(len(failed)))
print("Upload brown_to_healey_walks.json to Claude")
