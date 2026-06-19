"""
Re-routes 1 Cedar Street and 53 Cedar Street using their corrected coordinates.
Run: python3 reroute_cedar.py
Outputs: cedar_corrected_walks.json — upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
KENNEDY = [-71.115523, 42.389388]
WINTERHILL = [-71.098797, 42.391667]

points = [
    {"address": "1 Cedar Street, Somerville MA", "lat": 42.38804809357665, "lon": -71.115190019966},
    {"address": "53 Cedar Street, Somerville MA", "lat": 42.39019937548418, "lon": -71.11367253187214},
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

for p in points:
    print(p["address"] + "...")
    k_dist, k_mins = ors_walk(KENNEDY, p["lon"], p["lat"])
    time.sleep(2)
    wh_dist, wh_mins = ors_walk(WINTERHILL, p["lon"], p["lat"])
    k_adj = math.ceil(k_mins * 1.13)
    wh_adj = math.ceil(wh_mins * 1.13)
    print("  Kennedy: " + str(k_dist) + " mi (" + str(k_adj) + " min)")
    print("  Winter Hill: " + str(wh_dist) + " mi (" + str(wh_adj) + " min)")
    p.update({
        "kennedy_walk_mi": k_dist, "kennedy_walk_min": k_mins, "kennedy_walk_min_adj": k_adj,
        "wh_walk_mi": wh_dist, "wh_walk_min": wh_mins, "wh_walk_min_adj": wh_adj
    })
    time.sleep(2)

with open("cedar_corrected_walks.json", "w") as f:
    json.dump(points, f, indent=2)
print("\nSaved cedar_corrected_walks.json")
print("Upload to Claude")
