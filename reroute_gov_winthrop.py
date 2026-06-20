"""
Routes the three manually-corrected Gov. Winthrop Road points.
Run: python3 reroute_gov_winthrop.py
Outputs: gov_winthrop_walks.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
HEALEY = [-71.09536, 42.39753]

points = [
    {"address": "1 Gov. Winthrop Road, Somerville MA", "street": "Gov. Winthrop Road", "num": "1", "school": "HEALEY", "lat": 42.39519197577029, "lon": -71.08563404481608},
    {"address": "102 Gov. Winthrop Road, Somerville MA", "street": "Gov. Winthrop Road", "num": "102", "school": "HEALEY", "lat": 42.397399983395815, "lon": -71.0891601871881},
    {"address": "128 Gov. Winthrop Road, Somerville MA", "street": "Gov. Winthrop Road", "num": "128", "school": "HEALEY", "lat": 42.397994212663654, "lon": -71.08990358294065},
]

def ors_walk(lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], HEALEY], "units": "mi"}).encode()
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
    dist, mins = ors_walk(p["lon"], p["lat"])
    adj = math.ceil(mins * 1.13)
    p.update({"walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
    print(p["address"] + ": " + str(dist) + " mi (" + str(adj) + " min)")
    time.sleep(2)

with open("gov_winthrop_walks.json", "w") as f:
    json.dump(points, f, indent=2)
print("\nSaved")
print("Upload gov_winthrop_walks.json to Claude")
