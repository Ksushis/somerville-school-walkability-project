"""
Routes the two manually-corrected points: 23 Meacham Road (West Somerville)
and 14 Chester Street (Kennedy).

Run: python3 reroute_meacham_chester.py
Outputs: meacham_chester_walks.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
KENNEDY = [-71.115523, 42.389388]
WEST = [-71.126467, 42.406166]

points = [
    {"address": "23 Meacham Road, Somerville MA", "street": "Meacham Road", "num": "23",
     "school": "WEST SOMERVILLE", "lat": 42.39594556195229, "lon": -71.12638753394944},
    {"address": "14 Chester Street, Somerville MA", "street": "Chester Street", "num": "14",
     "school": "KENNEDY", "lat": 42.39358763729585, "lon": -71.12423030303557},
]

DEST = {"KENNEDY": KENNEDY, "WEST SOMERVILLE": WEST}

def ors_walk(dest, lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], dest], "units": "mi"}).encode()
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

for p in points:
    dest = DEST[p["school"]]
    dist, mins = ors_walk(dest, p["lon"], p["lat"])
    adj = math.ceil(mins * 1.13)
    p.update({"walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
    print(p["address"] + ": " + str(dist) + " mi (" + str(adj) + " min)")
    time.sleep(2)

with open("meacham_chester_walks.json", "w") as f:
    json.dump(points, f, indent=2)
print("\nSaved")
print("Upload meacham_chester_walks.json to Claude")
