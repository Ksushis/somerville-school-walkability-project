"""
Routes the corrected Revolution Drive 290 coordinate to East Somerville
Community School.

Run: python3 fetch_revolution_drive.py
Outputs: revolution_drive_walks.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
EAST = [-71.084723, 42.389744]

with open("revolution_drive_to_route.json") as f:
    samples = json.load(f)

def ors_walk(lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], EAST], "units": "mi"}).encode()
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

for s in samples:
    dist, mins = ors_walk(s["lon"], s["lat"])
    adj = math.ceil(mins * 1.13)
    s.update({"walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
    print(s["address"] + ": " + str(dist) + " mi (" + str(adj) + " min)")
    time.sleep(2)

with open("revolution_drive_walks.json", "w") as f:
    json.dump(samples, f, indent=2)
print("\nSaved. Upload revolution_drive_walks.json to Claude")
