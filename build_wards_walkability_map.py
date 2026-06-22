"""
7-ZONE WALKABILITY MAP WITH WARD BOUNDARIES
=============================================
Walkability dots colored by walk time, ward boundaries + labels on top.
Run: python3 build_wards_walkability_map.py
Output: wards_walkability_map.html
"""
import json, statistics

INPUT_ZONES  = "seven_zone_with_status.json"
INPUT_WARDS  = "wards.geojson"
INPUT_BOUNDS = "boundaries.json"
OUTPUT_FILE  = "wards_walkability_map.html"

SCHOOLS = [
    {"name": "Brown School",                            "grades": "K-5",  "lat": 42.397302, "lon": -71.114010, "address": "201 Willow Avenue"},
    {"name": "Kennedy School",                          "grades": "K-8",  "lat": 42.389388, "lon": -71.115523, "address": "5 Cherry Street"},
    {"name": "West Somerville Neighborhood School",     "grades": "PK-8", "lat": 42.406166, "lon": -71.126467, "address": "177 Powder House Blvd"},
    {"name": "Winter Hill Community Innovation School", "grades": "PK-8", "lat": 42.391667, "lon": -71.098797, "address": "115 Sycamore Street"},
    {"name": "Healey School",                          "grades": "PK-8", "lat": 42.397530, "lon": -71.095360, "address": "5 Meacham Street"},
    {"name": "Argenziano School",                      "grades": "PK-8", "lat": 42.379030, "lon": -71.098674, "address": "290 Washington Street"},
    {"name": "East Somerville Community School",       "grades": "K-8",  "lat": 42.389744, "lon": -71.084723, "address": "50 Cross Street"},
]

OTHER_SCHOOLS = [
    {"name": "Edgerly (Winter Hill Temporary Location)", "grades": "PK-8 (temporary site)",
     "lat": 42.38798214035693, "lon": -71.08728780221357, "address": "33 Cross Street"},
    {"name": "SHS / Next Wave", "grades": "",
     "lat": 42.386971, "lon": -71.096151, "address": "81 Highland Ave / 153 School St"},
    {"name": "Capuano", "grades": "PK-K",
     "lat": 42.383074494377055, "lon": -71.08728791692477, "address": "150 Glen Street"},
]


def polygon_centroid(coords):
    """Simple centroid of outer ring."""
    lats = [c[1] for c in coords[0]]
    lons = [c[0] for c in coords[0]]
    return statistics.mean(lats), statistics.mean(lons)


def main():
    with open(INPUT_ZONES)  as f: zones  = json.load(f)
    with open(INPUT_WARDS)  as f: wards  = json.load(f)
    with open(INPUT_BOUNDS) as f: bounds = json.load(f)

    # compute ward label positions
    ward_labels = []
    for feat in wards["features"]:
        ward_num = feat["properties"]["ward"]
        lat, lon = polygon_centroid(feat["geometry"]["coordinates"])
        ward_labels.append({"ward": ward_num, "lat": lat, "lon": lon})

    somerville_coords = json.dumps(bounds["Somerville"])
    samples = [p for p in zones if p.get("walk_min_adj")]
    print(f"Loaded {len(samples)} samples, {len(wards['features'])} wards")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Somerville K-5/K-8 — Walkability by Ward</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
* {{box-sizing:border-box;margin:0;padding:0;}}
body {{font-family:system-ui,sans-serif;background:#f5f4f0;display:flex;flex-direction:column;height:100vh;}}
#header {{padding:12px 18px 8px;background:#fff;border-bottom:1px solid #e0dfd8;flex-shrink:0;}}
#header h1 {{font-size:15px;font-weight:600;margin-bottom:2px;}}
#header p {{font-size:12px;color:#666;}}
#map {{flex:1;}}
#legend {{display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;
          padding:8px 18px;background:#fff;border-top:1px solid #e0dfd8;font-size:11px;flex-shrink:0;}}
.leg {{display:flex;align-items:center;gap:5px;}}
.grad-bar {{width:160px;height:8px;border-radius:4px;
            background:linear-gradient(to right,#22c55e,#86efac,#fde047,#fb923c,#ef4444);}}
.ward-swatch {{width:28px;height:3px;background:#1e3a8a;border-radius:2px;}}
</style>
</head>
<body>
<div id="header">
  <h1>Somerville K-5/K-8 — Walkability with Ward Boundaries</h1>
  <p>{len(samples)} sample addresses &middot; dot color = walk time to assigned school &middot; ward boundaries overlaid</p>
</div>
<div id="map"></div>
<div id="legend">
  <div class="leg"><span>0 min</span><div class="grad-bar"></div><span>29+ min</span></div>
  <div class="leg">
    <svg width="16" height="16" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="#facc15" stroke="#a16207" stroke-width="1.5"/></svg>
    Destination school
  </div>
  <div class="leg">
    <svg width="16" height="16" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="#94a3b8" stroke="#475569" stroke-width="1.5"/></svg>
    Other schools
  </div>
  <div class="leg"><div class="ward-swatch"></div> Ward boundary</div>
</div>
<script>
const samples = {json.dumps(samples)};
const schools = {json.dumps(SCHOOLS)};
const otherSchools = {json.dumps(OTHER_SCHOOLS)};
const wardsGeoJSON = {json.dumps(wards)};
const wardLabels = {json.dumps(ward_labels)};
const somervilleCoords = {somerville_coords};

const MIN_MIN = 0, MAX_MIN = 29;
const STOPS = [[0,[34,197,94]],[0.3,[134,239,172]],[0.55,[253,224,71]],[0.75,[251,146,60]],[1.0,[239,68,68]]];
function lerpColor(t) {{
  t = Math.max(0, Math.min(1, t));
  let i = 0;
  while (i < STOPS.length - 2 && t > STOPS[i+1][0]) i++;
  const [t0,c0]=STOPS[i],[t1,c1]=STOPS[i+1],f=(t-t0)/(t1-t0);
  return "rgb("+Math.round(c0[0]+f*(c1[0]-c0[0]))+","+Math.round(c0[1]+f*(c1[1]-c0[1]))+","+Math.round(c0[2]+f*(c1[2]-c0[2]))+")";
}}
function walkColor(mins) {{ return lerpColor((mins-MIN_MIN)/(MAX_MIN-MIN_MIN)); }}

function starIcon(fill, stroke, size) {{
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 24 24">' +
    '<polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" ' +
    'fill="'+fill+'" stroke="'+stroke+'" stroke-width="1.5"/></svg>';
  return L.divIcon({{html:svg, className:'', iconAnchor:[size/2,size/2], iconSize:[size,size]}});
}}

const map = L.map('map').setView([42.392, -71.103], 13);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO', maxZoom: 19
}}).addTo(map);

// walkability dots
samples.forEach(s => {{
  if (!s.walk_min_adj) return;
  L.circleMarker([s.lat, s.lon], {{
    radius: 5, fillColor: walkColor(s.walk_min_adj), color: '#fff', weight: 1, fillOpacity: 0.9
  }}).addTo(map).bindPopup(
    '<div style="font-weight:600;font-size:14px;margin-bottom:4px">'+s.street+(s.num?' '+s.num:'')+'</div>' +
    '<div><span style="background:#e2e8f0;padding:1px 6px;border-radius:10px;font-size:11px">'+s.zone+' zone</span></div>' +
    '<div style="margin-top:4px"><strong>'+s.walk_min_adj+' min</strong> to '+s.dest+'</div>'
  );
}});

// school stars
schools.forEach(s => {{
  const isBrown = s.name === 'Brown School';
  const fill = isBrown ? '#7c3aed' : '#facc15';
  const stroke = isBrown ? '#4c1d95' : '#a16207';
  L.marker([s.lat, s.lon], {{icon: starIcon(fill, stroke, 26), zIndexOffset: 1000}})
    .addTo(map).bindPopup('<strong>'+s.name+'</strong>'+(s.grades?' ('+s.grades+')':'')+'<br>'+s.address);
  const sn = s.name.replace(' Community Innovation School','').replace(' Neighborhood School','').replace(' Community School','');
  L.marker([s.lat, s.lon], {{
    icon: L.divIcon({{html:'<div style="font-size:11px;font-weight:600;white-space:nowrap;margin-left:15px;margin-top:-6px;color:#1a1a18;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff">'+sn+'</div>',className:'',iconAnchor:[0,6]}}),
    zIndexOffset: 999, interactive: false
  }}).addTo(map);
}});

otherSchools.forEach(s => {{
  L.marker([s.lat, s.lon], {{icon: starIcon('#94a3b8','#475569',20), zIndexOffset:1000}})
    .addTo(map).bindPopup('<strong>'+s.name+'</strong>'+(s.grades?' ('+s.grades+')':'')+'<br>'+s.address);
}});

// ward boundaries — on top of dots
L.geoJSON(wardsGeoJSON, {{
  style: {{color: '#1e3a8a', weight: 2, opacity: 0.8, fill: false}}
}}).addTo(map);

// ward labels
wardLabels.forEach(w => {{
  L.marker([w.lat, w.lon], {{
    icon: L.divIcon({{
      html: '<div style="font-size:12px;font-weight:700;color:#1e3a8a;text-shadow:0 0 4px #fff,0 0 4px #fff,0 0 4px #fff,0 0 4px #fff;white-space:nowrap">Ward '+w.ward+'</div>',
      className: '', iconAnchor: [24, 8]
    }}),
    zIndexOffset: 2000, interactive: false
  }}).addTo(map);
}});

// Somerville border — last so on top
L.geoJSON({{type:"Feature",geometry:{{type:"MultiLineString",coordinates:somervilleCoords}}}},
  {{style:{{color:"#6366f1",weight:2.5,opacity:0.9,fill:false}}}}).addTo(map);
</script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"Saved {OUTPUT_FILE} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
