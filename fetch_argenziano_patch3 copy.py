"""
Re-patches Highland Avenue with corrected coordinate.
Place in same directory as argenziano_walk.json and run:
  python3 fetch_argenziano_patch3.py
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
DEST = [-71.098674, 42.37903]  # Argenziano School

patches = [
    {"street": "Highland Avenue 6-146", "lat": 42.3846, "lon": -71.09279},
]

def ors_walk(lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], DEST], "units": "mi"}).encode()
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

existing = json.load(open("argenziano_walk.json"))
lookup = {d["street"]: i for i, d in enumerate(existing)}

for p in patches:
    street = p["street"]
    print(street + "...")
    dist, mins = ors_walk(p["lon"], p["lat"])
    adj = math.ceil(mins * 1.13)
    idx = lookup[street]
    existing[idx]["lat"] = p["lat"]
    existing[idx]["lon"] = p["lon"]
    existing[idx]["walk_mi"] = dist
    existing[idx]["walk_min"] = mins
    existing[idx]["walk_min_adj"] = adj
    print("  " + str(dist) + " mi (" + str(adj) + " min)")

with open("argenziano_walk.json", "w") as f:
    json.dump(existing, f, indent=2)
print("\nDone. Upload argenziano_walk.json to Claude")
