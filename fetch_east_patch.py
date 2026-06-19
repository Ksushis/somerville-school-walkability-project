"""
Patches 4 bad East Somerville walk distances with corrected coordinates.
Place in same directory as east_walk.json and run:
  python3 fetch_east_patch.py
Outputs: east_walk.json (updated in place)
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
DEST = [-71.084723, 42.389744]  # East Somerville Community School

patches = [
    {"street": "Arlington Street",   "lat": 42.38598, "lon": -71.08214},
    {"street": "Sibley Place",       "lat": 42.38658, "lon": -71.08410},
    {"street": "Sibley Court",       "lat": 42.38640, "lon": -71.08421},
    {"street": "Harold Cohen Drive", "lat": 42.39260, "lon": -71.07920},
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

existing = json.load(open("east_walk.json"))
lookup = {d["street"]: i for i, d in enumerate(existing)}

print("Patching " + str(len(patches)) + " streets...\n")
for p in patches:
    street = p["street"]
    print(street + "...")
    try:
        dist, mins = ors_walk(p["lon"], p["lat"])
        adj = math.ceil(mins * 1.13)
        idx = lookup[street]
        existing[idx]["lat"] = p["lat"]
        existing[idx]["lon"] = p["lon"]
        existing[idx]["walk_mi"] = dist
        existing[idx]["walk_min"] = mins
        existing[idx]["walk_min_adj"] = adj
        print("  " + str(dist) + " mi (" + str(adj) + " min)")
    except Exception as e:
        print("  ERROR: " + str(e))
    time.sleep(3)

with open("east_walk.json", "w") as f:
    json.dump(existing, f, indent=2)

print("\nDone. Upload east_walk.json to Claude")
