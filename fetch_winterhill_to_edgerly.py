"""
ROUTE WINTER HILL CATCHMENT TO EDGERLY (TEMPORARY LOCATION)
================================================================
Routes all 345 Winter Hill zone sample addresses to Edgerly -- the
temporary swing-space location where Winter Hill students currently
attend while their permanent building is unavailable.

This produces the data needed to show what Winter Hill families are
ALREADY experiencing right now (a displaced, longer walk to a temporary
site) as a real-world parallel to what the Brown redistricting proposal
would do PERMANENTLY to Brown families (reassigning them away from their
neighborhood school to Winter Hill's site).

Run: python3 fetch_winterhill_to_edgerly.py
Outputs: winterhill_to_edgerly_walks.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
EDGERLY = [-71.08728780221357, 42.38798214035693]

with open("winterhill_to_edgerly.json") as f:
    samples = json.load(f)

def ors_walk(lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], EDGERLY], "units": "mi"}).encode()
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
print("Routing " + str(total) + " Winter Hill addresses to Edgerly...\n")
for i, s in enumerate(samples):
    try:
        dist, mins = ors_walk(s["lon"], s["lat"])
        adj = math.ceil(mins * 1.13)
        results.append({**s, "walk_mi_edgerly": dist, "walk_min_edgerly": mins, "walk_min_adj_edgerly": adj})
        if (i+1) % 25 == 0 or i == 0:
            print("[" + str(i+1).rjust(3) + "/" + str(total) + "] " + s["street"] + ": " + str(adj) + " min")
    except Exception as e:
        print("[" + str(i+1).rjust(3) + "/" + str(total) + "] " + s["street"] + ": ERROR " + str(e))
        results.append({**s, "walk_mi_edgerly": None, "walk_min_edgerly": None, "walk_min_adj_edgerly": None})
    time.sleep(2)

with open("winterhill_to_edgerly_walks.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r["walk_mi_edgerly"] is None]
print("\nDone. Total: " + str(len(results)) + ", Failed: " + str(len(failed)))
print("Upload winterhill_to_edgerly_walks.json to Claude")
