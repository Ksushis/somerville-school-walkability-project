"""
Routes the 13 pending manually-corrected points (already geocoded,
just need ORS walking distances).

Run: python3 route_pending_points.py
Outputs: pending_points_walks.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
KENNEDY = [-71.115523, 42.389388]
WEST = [-71.126467, 42.406166]
WINTERHILL = [-71.098797, 42.391667]
HEALEY = [-71.09536, 42.39753]

DEST_BY_SCHOOL = {
    "KENNEDY": KENNEDY,
    "WEST SOMERVILLE": WEST,
    "WINTER HILL": WINTERHILL,
    "HEALEY": HEALEY,
}

points = [
    {"street": "Great River Road", "address": "650 Great River Road, Somerville MA", "school": "HEALEY", "lat": 42.393011197025196, "lon": -71.07770341855196},
    {"street": "Milton Street", "address": "23 Milton Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.39335409502267, "lon": -71.12372668216473},
    {"street": "Bowers Avenue", "address": "7 Bowers Avenue, Somerville MA", "school": "KENNEDY", "lat": 42.394281, "lon": -71.121933},
    {"street": "Herbert Street", "address": "1 Herbert Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.395851, "lon": -71.123199},
    {"street": "Herbert Street", "address": "6 Herbert Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.395056, "lon": -71.122782},
    {"street": "Herbert Street", "address": "16 Herbert Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.395363, "lon": -71.122982},
    {"street": "Day Street", "address": "21 Day Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.394878, "lon": -71.124798},
    {"street": "Day Street", "address": "39 Day Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.395607, "lon": -71.123918},
    {"street": "Dover Street", "address": "55 Dover Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.395684, "lon": -71.125411},
    {"street": "Dover Street", "address": "76 Dover Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.395507, "lon": -71.125093},
    {"street": "Dover Street", "address": "97 Dover Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.396384, "lon": -71.124178},
    {"street": "Kingston Street", "address": "23 Kingston Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.397186, "lon": -71.12612},
    {"street": "Kingston Street", "address": "48 Kingston Street, Somerville MA", "school": "WEST SOMERVILLE", "lat": 42.397029, "lon": -71.12725},
]

def ors_walk(dest, lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], dest], "units": "mi"}).encode()
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

results = []
print("Routing " + str(len(points)) + " points...\n")
for i, p in enumerate(points):
    dest = DEST_BY_SCHOOL[p["school"]]
    try:
        dist, mins = ors_walk(dest, p["lon"], p["lat"])
        adj = math.ceil(mins * 1.13)
        results.append({**p, "walk_mi": dist, "walk_min": mins, "walk_min_adj": adj})
        print("[" + str(i+1).rjust(2) + "/" + str(len(points)) + "] " + p["address"] + ": " + str(dist) + " mi (" + str(adj) + " min)")
    except Exception as e:
        print("[" + str(i+1).rjust(2) + "/" + str(len(points)) + "] " + p["address"] + ": ERROR " + str(e))
        results.append({**p, "walk_mi": None, "walk_min": None, "walk_min_adj": None})
    time.sleep(2)

with open("pending_points_walks.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nDone. Upload pending_points_walks.json to Claude")
