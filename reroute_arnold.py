import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
KENNEDY = [-71.115523, 42.389388]

points = [
    {"address": "5 Arnold Avenue, Somerville MA", "street": "Arnold Avenue", "num": "5", "school": "KENNEDY", "lat": 42.386599, "lon": -71.11303},
    {"address": "11 Arnold Avenue, Somerville MA", "street": "Arnold Avenue", "num": "11", "school": "KENNEDY", "lat": 42.386559, "lon": -71.112927},
]

def ors_walk(lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], KENNEDY], "units": "mi"}).encode()
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

with open("arnold_avenue_walks.json", "w") as f:
    json.dump(points, f, indent=2)
print("\nSaved")
