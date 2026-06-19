import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
WINTERHILL = [-71.098797, 42.391667]

points = [
    {"address": "5 James Street, Somerville MA", "street": "James Street", "num": "5", "school": "WINTER HILL", "lat": 42.387722, "lon": -71.09412},
    {"address": "18 James Street, Somerville MA", "street": "James Street", "num": "18", "school": "WINTER HILL", "lat": 42.388408, "lon": -71.093663},
]

def ors_walk(lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], WINTERHILL], "units": "mi"}).encode()
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

with open("james_street_walks.json", "w") as f:
    json.dump(points, f, indent=2)
print("\nSaved")
