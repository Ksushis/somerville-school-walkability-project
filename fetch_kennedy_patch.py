"""
Patches bad/missing Kennedy walk distances using corrected geocod.io coordinates.
Place in same directory as kennedy_walk.json and run:
  python3 fetch_kennedy_patch.py
Outputs: kennedy_walk.json (updated in place)
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
DEST = [-71.115523, 42.389388]  # Kennedy School

patches = [
    {"street": "Summer Street 172-End",    "lat": 42.388578, "lon": -71.111184},
    {"street": "Cedar Street 1-105",       "lat": 42.389967, "lon": -71.113797},
    {"street": "Lowell Street 1-207",      "lat": 42.38834,  "lon": -71.10925},
    {"street": "Willow Avenue 1-111",      "lat": 42.393029, "lon": -71.117347},
    {"street": "Central Street 1-82",      "lat": 42.385914, "lon": -71.105402},
    {"street": "Beacon Street 236-End",    "lat": 42.38422,  "lon": -71.113425},
    {"street": "Hudson Street 93-End",     "lat": 42.392016, "lon": -71.109742},
    {"street": "Somerville Avenue 583-End","lat": 42.384476, "lon": -71.110382},
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

existing = json.load(open("kennedy_walk.json"))
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

with open("kennedy_walk.json", "w") as f:
    json.dump(existing, f, indent=2)

print("\nDone. Upload kennedy_walk.json to Claude")
