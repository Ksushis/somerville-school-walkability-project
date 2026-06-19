"""
Fetches walking distance + time + route geometry from each Brown K-5 street
endpoint to Winter Hill site (115 Sycamore St).

Run locally: python3 fetch_walk_distances.py
Outputs: walk_distances.json — upload this to Claude
"""

import urllib.request, json, time

ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjJiZjhhNmIxM2NkMDQ4YWFhNDVhYTcwMDkxYjJkOTkwIiwiaCI6Im11cm11cjY0In0="
WH = [-71.0997, 42.3932]  # Winter Hill site [lon, lat]

endpoints = [
  {
    "street": "Albion Court",
    "endpoint": "start",
    "lat": 42.392115,
    "lon": -71.109173,
    "accuracy": "rooftop",
    "address": "128 Albion Court, Somerville MA 02145"
  },
  {
    "street": "Albion Court",
    "endpoint": "end",
    "lat": 42.392195,
    "lon": -71.109307,
    "accuracy": "rooftop",
    "address": "134 Albion Court, Somerville MA 02145"
  },
  {
    "street": "Albion Place",
    "endpoint": "start",
    "lat": 42.392395,
    "lon": -71.108521,
    "accuracy": "rooftop",
    "address": "8 Albion Place, Somerville MA 02145"
  },
  {
    "street": "Albion Place",
    "endpoint": "end",
    "lat": 42.392401,
    "lon": -71.108203,
    "accuracy": "rooftop",
    "address": "17 Albion Place, Somerville MA 02145"
  },
  {
    "street": "Albion Street",
    "endpoint": "start",
    "lat": 42.391315,
    "lon": -71.107361,
    "accuracy": "rooftop",
    "address": "94 Albion Street, Somerville MA 02145"
  },
  {
    "street": "Albion Street",
    "endpoint": "end",
    "lat": 42.393312,
    "lon": -71.111405,
    "accuracy": "rooftop",
    "address": "179 Albion Street, Somerville MA 02145"
  },
  {
    "street": "Albion Terrace",
    "endpoint": "start",
    "lat": 42.391458,
    "lon": -71.1077,
    "accuracy": "rooftop",
    "address": "100 Albion Terrace, Somerville MA 02145"
  },
  {
    "street": "Albion Terrace",
    "endpoint": "end",
    "lat": 42.391543,
    "lon": -71.10789,
    "accuracy": "rooftop",
    "address": "104 Albion Terrace, Somerville MA 02145"
  },
  {
    "street": "Alpine Street",
    "endpoint": "start",
    "lat": 42.393693,
    "lon": -71.110629,
    "accuracy": "rooftop",
    "address": "12 Alpine Street, Somerville MA 02144"
  },
  {
    "street": "Alpine Street",
    "endpoint": "end",
    "lat": 42.392251,
    "lon": -71.106749,
    "accuracy": "rooftop",
    "address": "102 Alpine Street, Somerville MA 02144"
  },
  {
    "street": "Appleton Street",
    "endpoint": "start",
    "lat": 42.396239,
    "lon": -71.115637,
    "accuracy": "rooftop",
    "address": "2 Appleton Street, Somerville MA 02144"
  },
  {
    "street": "Appleton Street",
    "endpoint": "end",
    "lat": 42.397147,
    "lon": -71.11706,
    "accuracy": "range_interpolation",
    "address": "34 Appleton Street, Somerville MA 02144"
  },
  {
    "street": "Bay State Avenue",
    "endpoint": "start",
    "lat": 42.400375,
    "lon": -71.114788,
    "accuracy": "rooftop",
    "address": "7 Bay State Avenue, Somerville MA 02144"
  },
  {
    "street": "Bay State Avenue",
    "endpoint": "end",
    "lat": 42.398516,
    "lon": -71.116152,
    "accuracy": "rooftop",
    "address": "69 Bay State Avenue, Somerville MA 02144"
  },
  {
    "street": "Bellevue Terrace",
    "endpoint": "start",
    "lat": 42.392728,
    "lon": -71.109314,
    "accuracy": "rooftop",
    "address": "7 Bellevue Terrace, Somerville MA 02144"
  },
  {
    "street": "Bellevue Terrace",
    "endpoint": "end",
    "lat": 42.392819,
    "lon": -71.109578,
    "accuracy": "rooftop",
    "address": "10 Bellevue Terrace, Somerville MA 02144"
  },
  {
    "street": "Boston Avenue",
    "endpoint": "start",
    "lat": 42.394851,
    "lon": -71.111016,
    "accuracy": "nearest_rooftop_match",
    "address": "1 Boston Avenue, Somerville MA 02144"
  },
  {
    "street": "Boston Avenue",
    "endpoint": "end",
    "lat": 42.399248,
    "lon": -71.111415,
    "accuracy": "rooftop",
    "address": "158 Boston Avenue, Somerville MA 02144"
  },
  {
    "street": "Bristol Road",
    "endpoint": "start",
    "lat": 42.400742,
    "lon": -71.113458,
    "accuracy": "rooftop",
    "address": "87 Bristol Road, Somerville MA 02145"
  },
  {
    "street": "Bristol Road",
    "endpoint": "end",
    "lat": 42.400239,
    "lon": -71.112549,
    "accuracy": "rooftop",
    "address": "108 Bristol Road, Somerville MA 02145"
  },
  {
    "street": "Broadway",
    "endpoint": "start",
    "lat": 42.398499,
    "lon": -71.108497,
    "accuracy": "range_interpolation",
    "address": "585 Broadway, Somerville MA 02144"
  },
  {
    "street": "Broadway",
    "endpoint": "end",
    "lat": 42.400063,
    "lon": -71.113289,
    "accuracy": "rooftop",
    "address": "726 Broadway, Somerville MA 02144"
  },
  {
    "street": "Cedar Street",
    "endpoint": "start",
    "lat": 42.392443,
    "lon": -71.11204,
    "accuracy": "rooftop",
    "address": "107 Cedar Street, Somerville MA 02144"
  },
  {
    "street": "Cedar Street",
    "endpoint": "end",
    "lat": 42.397096,
    "lon": -71.108745,
    "accuracy": "range_interpolation",
    "address": "298 Cedar Street, Somerville MA 02144"
  },
  {
    "street": "Clifton Street",
    "endpoint": "start",
    "lat": 42.396975,
    "lon": -71.117426,
    "accuracy": "rooftop",
    "address": "1 Clifton Street, Somerville MA 02144"
  },
  {
    "street": "Clifton Street",
    "endpoint": "end",
    "lat": 42.396448,
    "lon": -71.117345,
    "accuracy": "rooftop",
    "address": "14 Clifton Street, Somerville MA 02144"
  },
  {
    "street": "Clyde Street",
    "endpoint": "start",
    "lat": 42.395269,
    "lon": -71.110016,
    "accuracy": "rooftop",
    "address": "2 Clyde Street, Somerville MA 02145"
  },
  {
    "street": "Clyde Street",
    "endpoint": "end",
    "lat": 42.394236,
    "lon": -71.107666,
    "accuracy": "rooftop",
    "address": "56 Clyde Street, Somerville MA 02145"
  },
  {
    "street": "College Avenue",
    "endpoint": "start",
    "lat": 42.396444,
    "lon": -71.121794,
    "accuracy": "rooftop",
    "address": "1 College Avenue, Somerville MA 02144"
  },
  {
    "street": "College Avenue",
    "endpoint": "end",
    "lat": 42.401549,
    "lon": -71.116517,
    "accuracy": "rooftop",
    "address": "143 College Avenue, Somerville MA 02144"
  },
  {
    "street": "Elm Court",
    "endpoint": "start",
    "lat": 42.396831,
    "lon": -71.121122,
    "accuracy": "rooftop",
    "address": "1 Elm Court, Somerville MA 02144"
  },
  {
    "street": "Elm Court",
    "endpoint": "end",
    "lat": 42.396736,
    "lon": -71.121372,
    "accuracy": "rooftop",
    "address": "6 Elm Court, Somerville MA 02144"
  },
  {
    "street": "Ellington Road",
    "endpoint": "start",
    "lat": 42.395451,
    "lon": -71.119509,
    "accuracy": "range_interpolation",
    "address": "16 Ellington Road, Somerville MA 02144"
  },
  {
    "street": "Ellington Road",
    "endpoint": "end",
    "lat": 42.395698,
    "lon": -71.119666,
    "accuracy": "rooftop",
    "address": "32 Ellington Road, Somerville MA 02144"
  },
  {
    "street": "Foskett Street",
    "endpoint": "start",
    "lat": 42.396772,
    "lon": -71.115255,
    "accuracy": "rooftop",
    "address": "4 Foskett Street, Somerville MA 02145"
  },
  {
    "street": "Foskett Street",
    "endpoint": "end",
    "lat": 42.397565,
    "lon": -71.117159,
    "accuracy": "rooftop",
    "address": "52 Foskett Street, Somerville MA 02145"
  },
  {
    "street": "Francesca Avenue",
    "endpoint": "start",
    "lat": 42.398765,
    "lon": -71.119508,
    "accuracy": "rooftop",
    "address": "7 Francesca Avenue, Somerville MA 02144"
  },
  {
    "street": "Francesca Avenue",
    "endpoint": "end",
    "lat": 42.398194,
    "lon": -71.117201,
    "accuracy": "rooftop",
    "address": "58 Francesca Avenue, Somerville MA 02144"
  },
  {
    "street": "Grove Street",
    "endpoint": "start",
    "lat": 42.396341,
    "lon": -71.11992,
    "accuracy": "rooftop",
    "address": "45 Grove Street, Somerville MA 02144"
  },
  {
    "street": "Grove Street",
    "endpoint": "end",
    "lat": 42.396904,
    "lon": -71.119568,
    "accuracy": "rooftop",
    "address": "65 Grove Street, Somerville MA 02144"
  },
  {
    "street": "Hall Avenue",
    "endpoint": "start",
    "lat": 42.398357,
    "lon": -71.12056,
    "accuracy": "rooftop",
    "address": "5 Hall Avenue, Somerville MA 02144"
  },
  {
    "street": "Hall Avenue",
    "endpoint": "end",
    "lat": 42.397366,
    "lon": -71.117755,
    "accuracy": "rooftop",
    "address": "73 Hall Avenue, Somerville MA 02144"
  },
  {
    "street": "Highland Avenue",
    "endpoint": "start",
    "lat": 42.390438,
    "lon": -71.107967,
    "accuracy": "rooftop",
    "address": "219 Highland Avenue, Somerville MA 02144"
  },
  {
    "street": "Highland Avenue",
    "endpoint": "end",
    "lat": 42.396263,
    "lon": -71.121089,
    "accuracy": "rooftop",
    "address": "407 Highland Avenue, Somerville MA 02144"
  },
  {
    "street": "Highland Road",
    "endpoint": "start",
    "lat": 42.394982,
    "lon": -71.113835,
    "accuracy": "rooftop",
    "address": "2 Highland Road, Somerville MA 02144"
  },
  {
    "street": "Highland Road",
    "endpoint": "end",
    "lat": 42.398894,
    "lon": -71.111242,
    "accuracy": "rooftop",
    "address": "140 Highland Road, Somerville MA 02144"
  },
  {
    "street": "Josephine Avenue",
    "endpoint": "start",
    "lat": 42.395747,
    "lon": -71.114571,
    "accuracy": "rooftop",
    "address": "9 Josephine Avenue, Somerville MA 02144"
  },
  {
    "street": "Josephine Avenue",
    "endpoint": "end",
    "lat": 42.399744,
    "lon": -71.112289,
    "accuracy": "rooftop",
    "address": "134 Josephine Avenue, Somerville MA 02144"
  },
  {
    "street": "Kidder Avenue",
    "endpoint": "start",
    "lat": 42.397915,
    "lon": -71.114433,
    "accuracy": "range_interpolation",
    "address": "93 Kidder Avenue, Somerville MA 02144"
  },
  {
    "street": "Kidder Avenue",
    "endpoint": "end",
    "lat": 42.396161,
    "lon": -71.110582,
    "accuracy": "rooftop",
    "address": "157 Kidder Avenue, Somerville MA 02144"
  },
  {
    "street": "Liberty Avenue",
    "endpoint": "start",
    "lat": 42.400597,
    "lon": -71.115056,
    "accuracy": "rooftop",
    "address": "6 Liberty Avenue, Somerville MA 02144"
  },
  {
    "street": "Liberty Avenue",
    "endpoint": "end",
    "lat": 42.397579,
    "lon": -71.117196,
    "accuracy": "range_interpolation",
    "address": "125 Liberty Avenue, Somerville MA 02144"
  },
  {
    "street": "Liberty Road",
    "endpoint": "start",
    "lat": 42.397127,
    "lon": -71.117871,
    "accuracy": "rooftop",
    "address": "121 Liberty Road, Somerville MA 02144"
  },
  {
    "street": "Liberty Road",
    "endpoint": "end",
    "lat": 42.396752,
    "lon": -71.117811,
    "accuracy": "rooftop",
    "address": "130 Liberty Road, Somerville MA 02144"
  },
  {
    "street": "Lowden Avenue",
    "endpoint": "start",
    "lat": 42.400189,
    "lon": -71.11392,
    "accuracy": "rooftop",
    "address": "5 Lowden Avenue, Somerville MA 02144"
  },
  {
    "street": "Lowden Avenue",
    "endpoint": "end",
    "lat": 42.397399,
    "lon": -71.115864,
    "accuracy": "rooftop",
    "address": "93 Lowden Avenue, Somerville MA 02144"
  },
  {
    "street": "Mallet Street",
    "endpoint": "start",
    "lat": 42.399305,
    "lon": -71.113812,
    "accuracy": "rooftop",
    "address": "9 Mallet Street, Somerville MA 02144"
  },
  {
    "street": "Mallet Street",
    "endpoint": "end",
    "lat": 42.399305,
    "lon": -71.113812,
    "accuracy": "rooftop",
    "address": "9 Mallet Street, Somerville MA 02144"
  },
  {
    "street": "Maxwell's Green",
    "endpoint": "start",
    "lat": 42.393231,
    "lon": -71.106296,
    "accuracy": "street_center",
    "address": "Maxwell's Green, Somerville MA 02144"
  },
  {
    "street": "Maxwell's Green",
    "endpoint": "end",
    "lat": 42.393231,
    "lon": -71.106296,
    "accuracy": "street_center",
    "address": "Maxwell's Green, Somerville MA 02144"
  },
  {
    "street": "Morrison Avenue",
    "endpoint": "start",
    "lat": 42.39433,
    "lon": -71.11106,
    "accuracy": "rooftop",
    "address": "2 Morrison Avenue, Somerville MA 02144"
  },
  {
    "street": "Morrison Avenue",
    "endpoint": "end",
    "lat": 42.397579,
    "lon": -71.120096,
    "accuracy": "range_interpolation",
    "address": "232 Morrison Avenue, Somerville MA 02144"
  },
  {
    "street": "Morrison Place",
    "endpoint": "start",
    "lat": 42.397068,
    "lon": -71.118287,
    "accuracy": "rooftop",
    "address": "5 Morrison Place, Somerville MA 02144"
  },
  {
    "street": "Morrison Place",
    "endpoint": "end",
    "lat": 42.397176,
    "lon": -71.118548,
    "accuracy": "rooftop",
    "address": "8 Morrison Place, Somerville MA 02144"
  },
  {
    "street": "Murdock Street",
    "endpoint": "start",
    "lat": 42.396222,
    "lon": -71.109161,
    "accuracy": "rooftop",
    "address": "9 Murdock Street, Somerville MA 02145"
  },
  {
    "street": "Murdock Street",
    "endpoint": "end",
    "lat": 42.394654,
    "lon": -71.108468,
    "accuracy": "rooftop",
    "address": "65 Murdock Street, Somerville MA 02145"
  },
  {
    "street": "Newman Place",
    "endpoint": "start",
    "lat": 42.395787,
    "lon": -71.109663,
    "accuracy": "rooftop",
    "address": "4 Newman Place, Somerville MA 02145"
  },
  {
    "street": "Newman Place",
    "endpoint": "end",
    "lat": 42.395702,
    "lon": -71.109472,
    "accuracy": "rooftop",
    "address": "8 Newman Place, Somerville MA 02145"
  },
  {
    "street": "Pearson Avenue",
    "endpoint": "start",
    "lat": 42.394875,
    "lon": -71.112552,
    "accuracy": "range_interpolation",
    "address": "2 Pearson Avenue, Somerville MA 02144"
  },
  {
    "street": "Pearson Avenue",
    "endpoint": "end",
    "lat": 42.398218,
    "lon": -71.110742,
    "accuracy": "rooftop",
    "address": "116 Pearson Avenue, Somerville MA 02144"
  },
  {
    "street": "Pearson Road",
    "endpoint": "start",
    "lat": 42.400712,
    "lon": -71.113871,
    "accuracy": "rooftop",
    "address": "1 Pearson Road, Somerville MA 02144"
  },
  {
    "street": "Pearson Road",
    "endpoint": "end",
    "lat": 42.401859,
    "lon": -71.114583,
    "accuracy": "rooftop",
    "address": "39 Pearson Road, Somerville MA 02144"
  },
  {
    "street": "Powder House Terrace",
    "endpoint": "start",
    "lat": 42.39898,
    "lon": -71.117338,
    "accuracy": "rooftop",
    "address": "1 Powder House Terrace, Somerville MA 02144"
  },
  {
    "street": "Powder House Terrace",
    "endpoint": "end",
    "lat": 42.399534,
    "lon": -71.116279,
    "accuracy": "rooftop",
    "address": "39 Powder House Terrace, Somerville MA 02144"
  },
  {
    "street": "Prichard Avenue",
    "endpoint": "start",
    "lat": 42.395027,
    "lon": -71.111646,
    "accuracy": "rooftop",
    "address": "5 Prichard Avenue, Somerville MA 02144"
  },
  {
    "street": "Prichard Avenue",
    "endpoint": "end",
    "lat": 42.397651,
    "lon": -71.110294,
    "accuracy": "nearest_rooftop_match",
    "address": "100 Prichard Avenue, Somerville MA 02144"
  },
  {
    "street": "Princeton Street",
    "endpoint": "start",
    "lat": 42.392857,
    "lon": -71.10847,
    "accuracy": "range_interpolation",
    "address": "4 Princeton Street, Somerville MA 02145"
  },
  {
    "street": "Princeton Street",
    "endpoint": "end",
    "lat": 42.392921,
    "lon": -71.107325,
    "accuracy": "range_interpolation",
    "address": "57 Princeton Street, Somerville MA 02145"
  },
  {
    "street": "Rogers Avenue",
    "endpoint": "start",
    "lat": 42.395517,
    "lon": -71.114407,
    "accuracy": "rooftop",
    "address": "2 Rogers Avenue, Somerville MA 02144"
  },
  {
    "street": "Rogers Avenue",
    "endpoint": "end",
    "lat": 42.39935,
    "lon": -71.111782,
    "accuracy": "rooftop",
    "address": "130 Rogers Avenue, Somerville MA 02144"
  },
  {
    "street": "Warwick Street",
    "endpoint": "start",
    "lat": 42.394533,
    "lon": -71.110144,
    "accuracy": "rooftop",
    "address": "10 Warwick Street, Somerville MA 02145"
  },
  {
    "street": "Warwick Street",
    "endpoint": "end",
    "lat": 42.393466,
    "lon": -71.108632,
    "accuracy": "range_interpolation",
    "address": "94 Warwick Street, Somerville MA 02145"
  },
  {
    "street": "Willow Avenue",
    "endpoint": "start",
    "lat": 42.39545,
    "lon": -71.116194,
    "accuracy": "rooftop",
    "address": "130 Willow Avenue, Somerville MA 02144"
  },
  {
    "street": "Willow Avenue",
    "endpoint": "end",
    "lat": 42.399705,
    "lon": -71.112768,
    "accuracy": "rooftop",
    "address": "275 Willow Avenue, Somerville MA 02144"
  },
  {
    "street": "Wilson Avenue",
    "endpoint": "start",
    "lat": 42.398399,
    "lon": -71.108965,
    "accuracy": "rooftop",
    "address": "5 Wilson Avenue, Somerville MA 02144"
  },
  {
    "street": "Wilson Avenue",
    "endpoint": "end",
    "lat": 42.397898,
    "lon": -71.10894,
    "accuracy": "rooftop",
    "address": "20 Wilson Avenue, Somerville MA 02144"
  },
  {
    "street": "Winslow Avenue",
    "endpoint": "start",
    "lat": 42.397053,
    "lon": -71.121142,
    "accuracy": "rooftop",
    "address": "11 Winslow Avenue, Somerville MA 02144"
  },
  {
    "street": "Winslow Avenue",
    "endpoint": "end",
    "lat": 42.395953,
    "lon": -71.118226,
    "accuracy": "nearest_rooftop_match",
    "address": "99 Winslow Avenue, Somerville MA 02144"
  }
]

def ors_walk(lon, lat):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    body = json.dumps({"coordinates": [[lon, lat], WH], "units": "mi"}).encode()
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

results = []
print(f"Routing {len(endpoints)} endpoints to Winter Hill...\n")
for i, ep in enumerate(endpoints):
    try:
        dist, mins, geom = ors_walk(ep["lon"], ep["lat"])
        results.append({**ep, "walk_mi": dist, "walk_min": mins, "route_geometry": geom})
        print(f"[{i+1:2d}/{len(endpoints)}] {ep['street']} ({ep['endpoint']}): {dist} mi ({mins} min)")
    except Exception as e:
        print(f"[{i+1:2d}/{len(endpoints)}] {ep['street']} ({ep['endpoint']}): ERROR {e}")
        results.append({**ep, "walk_mi": None, "walk_min": None, "route_geometry": None})
    time.sleep(0.6)

with open("walk_distances.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nDone — upload walk_distances.json to Claude")
print("\nTop 10 farthest endpoints:")
for r in sorted([x for x in results if x["walk_mi"]], key=lambda x: x["walk_mi"], reverse=True)[:10]:
    print(f"  {r['walk_mi']} mi ({r['walk_min']} min)  {r['street']} ({r['endpoint']})")
