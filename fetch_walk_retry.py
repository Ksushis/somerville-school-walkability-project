"""
Retries the 14 endpoints that hit ORS rate limits in the first run.
Merges results into the original walk_distances.json.

Run locally: python3 fetch_walk_retry.py
Make sure walk_distances.json is in the same directory.
Outputs: walk_distances.json (updated in place)
"""

import urllib.request, json, time

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
WH = [-71.0997, 42.3932]

failed_endpoints = [
  {"street": "Elm Court", "endpoint": "start", "lat": 42.396831, "lon": -71.121122},
  {"street": "Elm Court", "endpoint": "end", "lat": 42.396736, "lon": -71.121372},
  {"street": "Ellington Road", "endpoint": "start", "lat": 42.395451, "lon": -71.119509},
  {"street": "Ellington Road", "endpoint": "end", "lat": 42.395698, "lon": -71.119666},
  {"street": "Foskett Street", "endpoint": "end", "lat": 42.397565, "lon": -71.117159},
  {"street": "Hall Avenue", "endpoint": "start", "lat": 42.398357, "lon": -71.12056},
  {"street": "Hall Avenue", "endpoint": "end", "lat": 42.397366, "lon": -71.117755},
  {"street": "Highland Avenue", "endpoint": "start", "lat": 42.390438, "lon": -71.107967},
  {"street": "Josephine Avenue", "endpoint": "start", "lat": 42.395747, "lon": -71.114571},
  {"street": "Josephine Avenue", "endpoint": "end", "lat": 42.399744, "lon": -71.112289},
  {"street": "Kidder Avenue", "endpoint": "start", "lat": 42.397915, "lon": -71.114433},
  {"street": "Kidder Avenue", "endpoint": "end", "lat": 42.396161, "lon": -71.110582},
  {"street": "Liberty Avenue", "endpoint": "start", "lat": 42.400597, "lon": -71.115056},
  {"street": "Liberty Avenue", "endpoint": "end", "lat": 42.397579, "lon": -71.117196},
]

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], WH], "units": "mi"}).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers={
                "Authorization": ORS_KEY,
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            feature = data["features"][0]
            dist = round(feature["properties"]["summary"]["distance"], 2)
            mins = round(feature["properties"]["summary"]["duration"] / 60, 1)
            route_geom = feature["geometry"]["coordinates"]
            return dist, mins, route_geom
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise

# Load existing results
existing = json.load(open("walk_distances.json"))

# Build lookup by street+endpoint
lookup = {(d["street"], d["endpoint"]): i for i, d in enumerate(existing)}

print(f"Retrying {len(failed_endpoints)} endpoints with 3s delay between calls...\n")
for i, ep in enumerate(failed_endpoints):
    key = (ep["street"], ep["endpoint"])
    print(f"[{i+1:2d}/{len(failed_endpoints)}] {ep['street']} ({ep['endpoint']})...", end=" ", flush=True)
    try:
        dist, mins, geom = ors_walk(ep["lon"], ep["lat"])
        idx = lookup[key]
        existing[idx]["walk_mi"] = dist
        existing[idx]["walk_min"] = mins
        existing[idx]["route_geometry"] = geom
        print(f"{dist} mi ({mins} min)")
    except Exception as e:
        print(f"ERROR {e}")
    time.sleep(3)  # 3s between calls to stay under rate limit

with open("walk_distances.json", "w") as f:
    json.dump(existing, f, indent=2)

still_failed = [d for d in existing if d["walk_mi"] is None]
print(f"\nDone. Still missing: {len(still_failed)}")
if still_failed:
    for d in still_failed:
        print(f"  {d['street']} ({d['endpoint']})")
print("\nUpload updated walk_distances.json to Claude")
