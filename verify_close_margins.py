"""
CITYWIDE CLOSE-MARGIN VERIFICATION
=====================================
Routes the 225 addresses flagged as "close call" (straight-line margin
<= 0.15 mi between their assigned school and the next-closest candidate)
to that candidate school, so we can compare REAL walking distance against
the already-known walking distance to their assigned school.

This is the targeted, cost-efficient version of the full citywide
walking-distance check: we already have walk distance to each address's
assigned school, so this script only fetches the ONE missing leg per
address (the walk to the candidate that straight-line distance flagged
as potentially closer).

USAGE:
  Place this script in the same folder as citywide_verify_queue.json
  Run: python3 verify_close_margins.py
  Outputs: citywide_verify_results.json -- upload to Claude
"""
import urllib.request, json, time, math

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="

with open("citywide_verify_queue.json") as f:
    samples = json.load(f)

def ors_walk(dest_lon, dest_lat, lon, lat, retries=3):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], [dest_lon, dest_lat]], "units": "mi"}).encode()
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
print("Routing " + str(total) + " addresses to their candidate closer school...\n")
for i, s in enumerate(samples):
    try:
        dist, mins = ors_walk(s["dest_lon"], s["dest_lat"], s["lon"], s["lat"])
        adj = math.ceil(mins * 1.13)
        results.append({**s, "walk_mi_to_candidate": dist, "walk_min_to_candidate": mins, "walk_min_adj_to_candidate": adj})
        if (i+1) % 25 == 0 or i == 0:
            print("[" + str(i+1).rjust(3) + "/" + str(total) + "] " + s["street"] + " " + str(s.get("num","")) +
                  " -> " + s["destination_school"] + ": " + str(adj) + " min (vs " + str(s.get("existing_walk_to_assigned")) + " min to assigned)")
    except Exception as e:
        print("[" + str(i+1).rjust(3) + "/" + str(total) + "] " + s["street"] + ": ERROR " + str(e))
        results.append({**s, "walk_mi_to_candidate": None, "walk_min_to_candidate": None, "walk_min_adj_to_candidate": None})
    time.sleep(2)

with open("citywide_verify_results.json", "w") as f:
    json.dump(results, f, indent=2)

failed = [r for r in results if r["walk_mi_to_candidate"] is None]
print("\nDone. Total: " + str(len(results)) + ", Failed: " + str(len(failed)))
print("Upload citywide_verify_results.json to Claude")
