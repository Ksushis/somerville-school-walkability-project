"""
Patches bad West Somerville walk distances using corrected coordinates.
Place in same directory as west_walk.json and run:
  python3 fetch_west_patch.py
Outputs: west_walk.json (updated in place)
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
DEST = [-71.126467, 42.406166]  # West Somerville School — geocod.io rooftop

patches = [
    {"street": "Broadway 727-End",       "lat": 42.40212,  "lon": -71.124108},
    {"street": "Harold Road",            "lat": 42.41318,  "lon": -71.1292},
    {"street": "Jerome Street",          "lat": 42.3813,   "lon": -71.1075},
    {"street": "Locke Street",           "lat": 42.39604,  "lon": -71.12277},
    {"street": "Boston Avenue 176-193",  "lat": 42.399404, "lon": -71.11106},
    {"street": "College Avenue 145-245", "lat": 42.403116, "lon": -71.11683},
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

existing = json.load(open("west_walk.json"))
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

with open("west_walk.json", "w") as f:
    json.dump(existing, f, indent=2)

print("\nDone. Upload west_walk.json to Claude")
