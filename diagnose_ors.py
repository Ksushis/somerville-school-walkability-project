"""
DIAGNOSTIC VERSION - routes just the first 3 points and prints the full
error response if anything fails, so we can see exactly what ORS is
complaining about (rate limit vs quota vs key issue vs something else).

Run: python3 diagnose_ors.py
"""
import urllib.request, json, time

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
ARGENZIANO = [-71.098674, 42.37903]

# A few known-good test points
test_points = [
    {"name": "Adrian Street 1", "lat": 42.377331, "lon": -71.09872},
    {"name": "Test point 2", "lat": 42.389388, "lon": -71.115523},
]

def ors_walk_diagnostic(lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], ARGENZIANO], "units": "mi"}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": ORS_KEY, "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            print("SUCCESS")
            return data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        body = e.read().decode()
        print("Full response body:")
        print(body)
        # Try to parse it as JSON for a cleaner look
        try:
            parsed = json.loads(body)
            print("\nParsed error detail:")
            print(json.dumps(parsed, indent=2))
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"Other error: {type(e).__name__}: {e}")
        return None

print("Testing ORS connectivity and error details...\n")
for i, p in enumerate(test_points):
    print(f"--- Test {i+1}: {p['name']} ---")
    ors_walk_diagnostic(p["lon"], p["lat"])
    print()
    time.sleep(5)

print("Done. Share the full output above with Claude.")
