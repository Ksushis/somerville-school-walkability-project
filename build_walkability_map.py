"""
WALKABILITY VS. REGISTER MAP (LOCAL BUILD)
=============================================
Builds the citywide map showing, for every sampled address: which school
it is registered to, and which school it is actually closest to by real
walking distance (where verified) or straight-line distance (otherwise).

Dots are colored by the actually-closest school. A saturated/dark dot
means the registered school IS the actually-closest school. A pale/light
dot means the address is registered elsewhere, and shows the time gap
in minutes (or, for unverified straight-line cases, the distance gap in
miles) between the registered school and the actually-closer one.

This does NOT call any API and does NOT need Claude -- it's a pure local
HTML-generation script using the data file you already have.

USAGE:
  Place this script in the same folder as seven_zone_with_status.json
  Run: python3 build_walkability_map.py
  Output: walkability_vs_register_map.html -- open directly in a browser
"""
import json

INPUT_FILE = "seven_zone_with_status.json"
OUTPUT_FILE = "walkability_vs_register_map.html"

SCHOOLS = [
    {"name": "Brown School", "grades": "K-5", "lat": 42.397302, "lon": -71.114010,
     "address": "201 Willow Avenue", "key": "Brown"},
    {"name": "Kennedy School", "grades": "K-8", "lat": 42.389388, "lon": -71.115523,
     "address": "5 Cherry Street", "key": "Kennedy"},
    {"name": "West Somerville Neighborhood School", "grades": "PK-8", "lat": 42.406166, "lon": -71.126467,
     "address": "177 Powder House Blvd", "key": "West Somerville"},
    {"name": "Winter Hill Community Innovation School", "grades": "PK-8", "lat": 42.391667, "lon": -71.098797,
     "address": "115 Sycamore Street", "key": "Winter Hill"},
    {"name": "Healey School", "grades": "PK-8", "lat": 42.397530, "lon": -71.095360,
     "address": "5 Meacham Street", "key": "Healey"},
    {"name": "Argenziano School", "grades": "PK-8", "lat": 42.379030, "lon": -71.098674,
     "address": "290 Washington Street", "key": "Argenziano"},
    {"name": "East Somerville Community School", "grades": "K-8", "lat": 42.389744, "lon": -71.084723,
     "address": "50 Cross Street", "key": "East Somerville"},
]

# Other schools shown for context but not part of the K-5/K-8 zoning comparison
OTHER_SCHOOLS = [
    {"name": "Edgerly (Winter Hill Temporary Location)", "grades": "PK-8 (temporary site)",
     "lat": 42.38798214035693, "lon": -71.08728780221357, "address": "33 Cross Street"},
    {"name": "SHS / Next Wave", "grades": "",
     "lat": 42.386971, "lon": -71.096151, "address": "81 Highland Ave / 153 School St"},
         {"name": "Capuano", "grades": "PK-K",
     "lat": 42.383074494377055, "lon":  -71.08728791692477, "address": "150 Glen Street"},
]

COLOR_PAIRS = {
    "Brown":           {"dark": "#6b21a8", "light": "#d8b4fe"},
    "Kennedy":         {"dark": "#92400e", "light": "#fcd34d"},
    "West Somerville": {"dark": "#1e3a8a", "light": "#93c5fd"},
    "Winter Hill":     {"dark": "#065f46", "light": "#6ee7b7"},
    "Healey":          {"dark": "#991b1b", "light": "#fca5a5"},
    "Argenziano":      {"dark": "#155e75", "light": "#67e8f9"},
    "East Somerville": {"dark": "#9d174d", "light": "#f9a8d4"},
}


def main():
    try:
        with open(INPUT_FILE) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {INPUT_FILE} not found in this directory.")
        return

    print(f"Loaded {len(data)} addresses.")
    n_mismatch = sum(1 for d in data if d.get("is_confirmed_mismatch"))
    print(f"Confirmed mismatches: {n_mismatch}")

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Somerville K-5/K-8 -- Walkability vs. Registered Zone</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
* {box-sizing:border-box;margin:0;padding:0;}
body {font-family:system-ui,sans-serif;background:#f5f4f0;display:flex;flex-direction:column;height:100vh;}
#header {padding:12px 18px 8px;background:#fff;border-bottom:1px solid #e0dfd8;flex-shrink:0;}
#header h1 {font-size:15px;font-weight:600;margin-bottom:2px;}
#header p {font-size:12px;color:#666;}
#map {flex:1;}
#legend {display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;padding:8px 18px;background:#fff;border-top:1px solid #e0dfd8;font-size:10px;flex-shrink:0;max-height:90px;overflow-y:auto;}
.leg-group {display:flex;align-items:center;gap:5px;border-right:1px solid #e5e5e5;padding-right:10px;}
.leg-group:last-child {border-right:none;}
.dot {width:10px;height:10px;border-radius:50%;flex-shrink:0;}
</style>
</head>
<body>
<div id="header">
  <h1>Somerville K-5/K-8 -- Walkability vs. Registered Zone</h1>
  <p>""" + str(len(data)) + """ sample addresses &middot; light grey dot = registered school matches the actually-closest school &middot; outlined dot = registered to a different school than the closest one (""" + str(n_mismatch) + """ confirmed), border colored by the closer school</p>
</div>
<div id="map"></div>
<div id="legend">
  <div class="leg-group">
    <div class="dot" style="background:#bfdbfe;border:1px solid #93c5fd"></div><span>Matches registered zone</span>
  </div>
"""
    for s in SCHOOLS:
        pair = COLOR_PAIRS[s["key"]]
        html += f'''  <div class="leg-group">
    <div class="dot" style="background:#e5e7eb;border:2.5px solid {pair["dark"]}"></div><span>Closer to {s["key"]} than registered</span>
  </div>
'''
    html += '''  <div class="leg-group">
    <div class="dot" style="background:#94a3b8"></div><span>Other schools: Edgerly (Winter Hill Temporary Location), SHS/Next Wave</span>
  </div>
'''
    html += """</div>
<script>
const samples = """ + json.dumps(data) + """;
const schools = """ + json.dumps(SCHOOLS) + """;
const colorPairs = """ + json.dumps(COLOR_PAIRS) + """;

function starIcon(fill,stroke,size) {
  const svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="'+fill+'" stroke="'+stroke+'" stroke-width="1.5"/></svg>';
  return L.divIcon({html:svg,className:'',iconAnchor:[size/2,size/2],iconSize:[size,size]});
}

const map = L.map('map').setView([42.392,-71.103],13);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
  attribution:'&copy; OpenStreetMap contributors &copy; CARTO',maxZoom:19
}).addTo(map);

async function addSomervilleBorder() {
  try {
    const url = "https://nominatim.openstreetmap.org/search?q=" + encodeURIComponent("Somerville, Massachusetts, USA") + "&polygon_geojson=1&format=json&limit=1";
    const resp = await fetch(url);
    const data = await resp.json();
    if (data.length && data[0].geojson) {
      L.geoJSON(data[0].geojson, {
        style: { color:"#6366f1", weight:2.5, opacity:0.9, fill:false }
      }).addTo(map);
    }
  } catch(e) { console.warn('Border fetch failed', e); }
}
addSomervilleBorder();

samples.forEach(s => {
  const school = s.actual_closest_school;
  const pair = colorPairs[school];
  if (!pair) return;
  const isMismatch = s.is_confirmed_mismatch;

  let popupExtra = '';
  if (isMismatch) {
    const registeredSchool = s.zone === 'West' ? 'West Somerville' : s.zone;
    const toRegistered = s.walk_min_to_assigned;
    const toCandidate = s.walk_min_to_candidate;
    if (toRegistered !== undefined && toRegistered !== null && toCandidate !== undefined && toCandidate !== null) {
      popupExtra = '<div style="margin-top:4px">' +
        '<div>To ' + registeredSchool + ' (registered): <strong>' + toRegistered + ' min</strong></div>' +
        '<div>To ' + school + ' (closer): <strong>' + toCandidate + ' min</strong></div>' +
        '<div style="color:#b45309;margin-top:2px">' + Math.abs(toRegistered - toCandidate) + ' min faster to ' + school + '</div>' +
        '</div>';
    } else if (s.margin_mi !== undefined && s.margin_mi !== null) {
      popupExtra = '<div style="margin-top:4px;color:#b45309">~' + Math.abs(s.margin_mi).toFixed(2) + ' mi closer to ' + school + ' than to ' + registeredSchool + ' (estimated, not walking-verified)</div>';
    } else {
      popupExtra = '<div style="margin-top:4px;color:#b45309">Closer to ' + school + '</div>';
    }
  } else {
    popupExtra = '<div style="margin-top:4px;color:#666">' + (s.walk_min_adj ? s.walk_min_adj + ' min to ' + school : '') + '</div>';
  }

  if (isMismatch) {
    L.circleMarker([s.lat, s.lon], {
      radius: 5, fillColor: '#ffffff', color: pair.dark, weight: 3, fillOpacity: 1, opacity: 1
    }).addTo(map).bindPopup(
      '<div style="font-weight:600;font-size:14px;margin-bottom:4px">' + s.street + ' ' + (s.num||'') + '</div>' +
      '<div>Registered zone: <strong>' + s.zone + '</strong></div>' +
      popupExtra
    );
  } else {
    L.circleMarker([s.lat, s.lon], {
      radius: 4, fillColor: '#bfdbfe', color: '#93c5fd', weight: 1, fillOpacity: 0.85
    }).addTo(map).bindPopup(
      '<div style="font-weight:600;font-size:14px;margin-bottom:4px">' + s.street + ' ' + (s.num||'') + '</div>' +
      '<div>Registered zone: <strong>' + s.zone + '</strong></div>' +
      popupExtra
    );
  }
});

schools.forEach(s => {
  const pair = colorPairs[s.key];
  L.marker([s.lat,s.lon],{icon:starIcon(pair.dark,'#000',26),zIndexOffset:1000})
    .addTo(map).bindPopup('<strong>' + s.name + '</strong>' + (s.grades?' ('+s.grades+')':'') + '<br>' + s.address);
  const sn = s.name.replace(' Community Innovation School','').replace(' Neighborhood School','').replace(' Community School','');
  L.marker([s.lat,s.lon],{
    icon:L.divIcon({html:'<div style="font-size:11px;font-weight:600;white-space:nowrap;margin-left:15px;margin-top:-6px;color:#1a1a18;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff">' + sn + '</div>',className:'',iconAnchor:[0,6]}),
    zIndexOffset:999, interactive:false
  }).addTo(map);
});

const otherSchools = """ + json.dumps(OTHER_SCHOOLS) + """;
otherSchools.forEach(s => {
  L.marker([s.lat, s.lon],{icon:starIcon('#94a3b8','#475569',20),zIndexOffset:1000})
    .addTo(map).bindPopup('<strong>' + s.name + '</strong>' + (s.grades?' ('+s.grades+')':'') + '<br>' + s.address);
  const sn = s.name.length > 20 ? s.name.split(' (')[0].split(' / ')[0] : s.name;
  L.marker([s.lat, s.lon],{
    icon:L.divIcon({html:'<div style="font-size:10px;font-weight:600;white-space:nowrap;margin-left:13px;margin-top:-5px;color:#374151;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff">' + sn + '</div>',className:'',iconAnchor:[0,6]}),
    zIndexOffset:999, interactive:false
  }).addTo(map);
});
</script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"\nSaved {OUTPUT_FILE} ({len(html):,} bytes)")
    print(f"Open it directly in your browser -- no need to upload anywhere.")


if __name__ == "__main__":
    main()
