"""
Patches McGrath Hwy in argenziano_walk.json.
Place in same directory and run: python3 fetch_argenziano_patch.py
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
DEST = [-71.098674, 42.37903]  # Argenziano School

patches = [
    {"street": "McGrath Hwy 280-430 even", "lat": 42.38038, "lon": -71.09000},
]

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], DEST], "units": "mi"}).encode()
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

existing = json.load(open("argenziano_walk.json"))
lookup = {d["street"]: i for i, d in enumerate(existing)}

for p in patches:
    print(p["street"] + "...")
    try:
        dist, mins = ors_walk(p["lon"], p["lat"])
        adj = math.ceil(mins * 1.13)
        idx = lookup[p["street"]]
        existing[idx]["lat"] = p["lat"]
        existing[idx]["lon"] = p["lon"]
        existing[idx]["walk_mi"] = dist
        existing[idx]["walk_min"] = mins
        existing[idx]["walk_min_adj"] = adj
        print("  " + str(dist) + " mi (" + str(adj) + " min)")
    except Exception as e:
        print("  ERROR: " + str(e))

with open("argenziano_walk.json", "w") as f:
    json.dump(existing, f, indent=2)
print("Done. Upload argenziano_walk.json to Claude")
