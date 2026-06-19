"""
Calibration: walking distances from 75 Irving St to two known destinations.
Run: python3 calibrate_walk.py
"""

import urllib.request, json

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="

# Geocodio rooftop coordinates [lon, lat]
IRVING  = [-71.121878, 42.400545]  # 75 Irving St, Somerville
WILLOW  = [-71.114010, 42.397302]  # 201 Willow Ave (Brown School)
POWDER  = [-71.126467, 42.406166]  # 177 Powder House Blvd

routes = [
    ("75 Irving St → 201 Willow Ave (Brown School)", IRVING, WILLOW),
    ("75 Irving St → 177 Powder House Blvd",         IRVING, POWDER),
]

def ors_walk(origin, dest):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [origin, dest], "units": "mi"}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": ORS_KEY,
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    feature = data["features"][0]
    dist = round(feature["properties"]["summary"]["distance"], 2)
    mins = round(feature["properties"]["summary"]["duration"] / 60, 1)
    return dist, mins

for label, origin, dest in routes:
    dist, mins = ors_walk(origin, dest)
    print(f"{label}")
    print(f"  {dist} mi  /  {mins} min walking\n")
