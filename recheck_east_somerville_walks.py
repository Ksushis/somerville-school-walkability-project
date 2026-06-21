"""
RECALCULATE EAST SOMERVILLE WALKING DISTANCES (HEALEY BOUNDARY)
====================================================================
Re-routes the 25 addresses in the Healey/East Somerville boundary area
that were previously flagged as "closer to East Somerville" by ORS, but
where real-world checks (Jaques Street, Wheatland Street) showed ORS was
significantly underestimating the East Somerville walk time.

This version also computes the straight-line distance and the
route/straight-line "detour ratio" for each result, so we can flag any
route that still looks suspiciously short (a low ratio close to 1.0 can
indicate ORS is cutting through a barrier -- highway, rail corridor,
river -- that isn't actually walkable).

USAGE:
  Place this script in the same folder as healey_east_recheck.json
  Run: python3 recheck_east_somerville_walks.py
  Outputs: healey_east_recheck_results.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
EAST_SOMERVILLE = [-71.084723, 42.389744]

with open("healey_east_recheck.json") as f:
    samples = json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlambda/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], EAST_SOMERVILLE], "units": "mi"}).encode()
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
total = len(samples)
print("Re-routing " + str(total) + " addresses to East Somerville...\n")
for i, s in enumerate(samples):
    try:
        dist, mins = ors_walk(s["lon"], s["lat"])
        adj = math.ceil(mins * 1.13)
        straight = haversine(s["lat"], s["lon"], 42.389744, -71.084723)
        ratio = round(dist / straight, 2) if straight > 0.01 else None
        flag = ""
        if ratio is not None and ratio < 1.3:
            flag = " <<< SUSPICIOUSLY DIRECT (ratio " + str(ratio) + ", possible barrier cut-through)"
        results.append({**s, "walk_mi_east": dist, "walk_min_east": mins, "walk_min_adj_east": adj,
                         "straight_line_mi": round(straight, 3), "detour_ratio": ratio})
        print("[" + str(i+1).rjust(2) + "/" + str(total) + "] " + s["street"] + " " + str(s.get("num","")) +
              ": " + str(adj) + " min (straight=" + str(round(straight,2)) + "mi, ratio=" + str(ratio) + ")" + flag)
    except Exception as e:
        print("[" + str(i+1).rjust(2) + "/" + str(total) + "] " + s["street"] + ": ERROR " + str(e))
        results.append({**s, "walk_mi_east": None, "walk_min_east": None, "walk_min_adj_east": None})
    time.sleep(2)

with open("healey_east_recheck_results.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r.get("walk_mi_east") is None]
print("\nDone. Total: " + str(len(results)) + ", Failed: " + str(len(failed)))
print("Upload healey_east_recheck_results.json to Claude")
