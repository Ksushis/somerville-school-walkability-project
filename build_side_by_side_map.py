"""
WALKABILITY COMPARISON, HIGH RESOLUTION (LOCAL BUILD)
=========================================================
Builds the side-by-side comparison map: left pane shows current zoning
(every zone walks to its own school), right pane shows the proposed
redistricting (Brown's K-5 catchment reassigned to Winter Hill). Both
panes share an identical 0-33 minute color scale, pan/zoom in sync, and
include Edgerly (Winter Hill's temporary site) and SHS/Next Wave as
grey "other school" markers.

This does NOT call any API and does NOT need Claude.

USAGE:
  Place this script in the same folder as current_state_export.json
  and proposed_state_export.json
  Run: python3 build_side_by_side_map.py
  Output: walkability_comparison_high_resolution.html
"""
import json

CURRENT_FILE = "current_state_export.json"
PROPOSED_FILE = "proposed_state_export.json"
OUTPUT_FILE = "walkability_comparison_high_resolution.html"

SCHOOLS = [
    {"name": "Brown School", "grades": "K-5", "lat": 42.397302, "lon": -71.114010, "address": "201 Willow Avenue"},
    {"name": "Kennedy School", "grades": "K-8", "lat": 42.389388, "lon": -71.115523, "address": "5 Cherry Street"},
    {"name": "West Somerville Neighborhood School", "grades": "PK-8", "lat": 42.406166, "lon": -71.126467, "address": "177 Powder House Blvd"},
    {"name": "Winter Hill Community Innovation School", "grades": "PK-8", "lat": 42.391667, "lon": -71.098797, "address": "115 Sycamore Street"},
    {"name": "Healey School", "grades": "PK-8", "lat": 42.397530, "lon": -71.095360, "address": "5 Meacham Street"},
    {"name": "Argenziano School", "grades": "PK-8", "lat": 42.379030, "lon": -71.098674, "address": "290 Washington Street"},
    {"name": "East Somerville Community School", "grades": "K-8", "lat": 42.389744, "lon": -71.084723, "address": "50 Cross Street"},
]

OTHER_SCHOOLS = [
    {"name": "Edgerly (Winter Hill Temporary Location)", "grades": "PK-8 (temporary site)",
     "lat": 42.38798214035693, "lon": -71.08728780221357, "address": "33 Cross Street"},
    {"name": "SHS / Next Wave", "grades": "",
     "lat": 42.386971, "lon": -71.096151, "address": "81 Highland Ave / 153 School St"},
         {"name": "Capuano", "grades": "PK-K",
     "lat": 42.383074494377055, "lon":  -71.08728791692477, "address": "150 Glen Street"},
]

SHARED_MAX = 33


def main():
    try:
        with open(CURRENT_FILE) as f:
            current = json.load(f)
        with open(PROPOSED_FILE) as f:
            proposed = json.load(f)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    print(f"Current: {len(current)} points, Proposed: {len(proposed)} points")

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Somerville Schools -- Current vs Proposed Redistricting (Side by Side)</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
* {box-sizing:border-box;margin:0;padding:0;}
body {font-family:system-ui,sans-serif;background:#f5f4f0;display:flex;flex-direction:column;height:100vh;}
#header {padding:10px 18px 6px;background:#fff;border-bottom:1px solid #e0dfd8;flex-shrink:0;}
#header h1 {font-size:15px;font-weight:600;margin-bottom:2px;}
#header p {font-size:12px;color:#666;}
#maps {flex:1;display:flex;}
.map-pane {flex:1;display:flex;flex-direction:column;border-right:1px solid #e0dfd8;}
.map-pane:last-child {border-right:none;}
.pane-title {padding:6px 12px;background:#f8f8f6;font-size:12px;font-weight:600;text-align:center;border-bottom:1px solid #e0dfd8;}
.pane-map {flex:1;}
#legend {display:flex;align-items:center;justify-content:center;gap:18px;flex-wrap:wrap;padding:7px 18px;background:#fff;border-top:1px solid #e0dfd8;font-size:11px;flex-shrink:0;}
.leg {display:flex;align-items:center;gap:5px;}
.grad-bar {width:160px;height:8px;border-radius:4px;background:linear-gradient(to right,#22c55e,#86efac,#fde047,#fb923c,#ef4444);}
</style>
</head>
<body>
<div id="header">
  <h1>Somerville K-5/K-8 Schools -- Current Zoning vs. Proposed Redistricting (Brown to Winter Hill)</h1>
  <p>Same color scale (0-""" + str(SHARED_MAX) + """ min) on both maps for direct comparison</p>
</div>
<div id="maps">
  <div class="map-pane">
    <div class="pane-title">Current -- each zone walks to its own school</div>
    <div id="map-left" class="pane-map"></div>
  </div>
  <div class="map-pane">
    <div class="pane-title">Proposed -- Brown's catchment reassigned to Winter Hill</div>
    <div id="map-right" class="pane-map"></div>
  </div>
</div>
<div id="legend">
  <span style="font-size:11px">0 min</span><div class="grad-bar"></div><span style="font-size:11px">""" + str(SHARED_MAX) + """ min</span>
  <div class="leg" style="margin-left:6px"><svg width="14" height="14" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="#facc15" stroke="#a16207" stroke-width="1.5"/></svg> Destination school</div>
  <div class="leg"><svg width="14" height="14" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="#a855f7" stroke="#7e22ce" stroke-width="1.5"/></svg> Brown School (current site, right map)</div>
  <div class="leg"><svg width="12" height="12" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="#94a3b8" stroke="#475569" stroke-width="1.5"/></svg> Other schools (Edgerly, SHS/Next Wave)</div>
</div>
<script>
const currentSamples = """ + json.dumps(current) + """;
const proposedSamples = """ + json.dumps(proposed) + """;
const schools = """ + json.dumps(SCHOOLS) + """;
const otherSchools = """ + json.dumps(OTHER_SCHOOLS) + """;

const MIN_MIN = 0, MAX_MIN = """ + str(SHARED_MAX) + """;
const STOPS = [[0,[34,197,94]],[0.3,[134,239,172]],[0.55,[253,224,71]],[0.75,[251,146,60]],[1.0,[239,68,68]]];
function lerpColor(t) {
  t = Math.max(0, Math.min(1, t));
  let i = 0;
  while (i < STOPS.length - 2 && t > STOPS[i+1][0]) i++;
  const [t0,c0]=STOPS[i],[t1,c1]=STOPS[i+1],f=(t-t0)/(t1-t0);
  return "rgb("+Math.round(c0[0]+f*(c1[0]-c0[0]))+","+Math.round(c0[1]+f*(c1[1]-c0[1]))+","+Math.round(c0[2]+f*(c1[2]-c0[2]))+")";
}
function walkColor(mins) { return lerpColor((mins-MIN_MIN)/(MAX_MIN-MIN_MIN)); }
function starIcon(fill,stroke,size) {
  const svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 24 24"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="'+fill+'" stroke="'+stroke+'" stroke-width="1.5"/></svg>';
  return L.divIcon({html:svg,className:'',iconAnchor:[size/2,size/2],iconSize:[size,size]});
}

async function addSomervilleBorder(map) {
  try {
    const url = "https://nominatim.openstreetmap.org/search?q=" + encodeURIComponent("Somerville, Massachusetts, USA") + "&polygon_geojson=1&format=json&limit=1";
    const resp = await fetch(url, {headers:{"User-Agent":"somerville-school-map/1.0"}});
    const data = await resp.json();
    if (data.length && data[0].geojson) {
      L.geoJSON(data[0].geojson, { style: { color:"#6366f1", weight:2.5, opacity:0.9, fill:false } }).addTo(map);
    }
  } catch(e) { console.warn('Border fetch failed', e); }
}

function buildMap(elementId, samples, isProposed) {
  const map = L.map(elementId, {zoomControl:true}).setView([42.392,-71.100],13);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; OSM &copy; CARTO', maxZoom:19
  }).addTo(map);

  addSomervilleBorder(map);

  samples.forEach(s => {
    if (!s.walk_min_adj) return;
    L.circleMarker([s.lat,s.lon],{radius:5,fillColor:walkColor(s.walk_min_adj),color:'#fff',weight:1,fillOpacity:0.9})
      .addTo(map).bindPopup(
        '<div style="font-weight:600;font-size:14px;margin-bottom:4px">'+s.street+(s.num?' '+s.num:'')+'</div>'+
        '<div><span style="background:#e2e8f0;padding:1px 6px;border-radius:10px;font-size:11px">'+s.zone+'</span></div>'+
        '<div style="margin-top:4px"><strong>'+s.walk_min_adj+' min</strong> to '+s.dest+'</div>'
      );
  });

  schools.forEach(s => {
    const isBrown = s.name.includes('Brown');
    const fill = (isProposed && isBrown) ? '#a855f7' : '#facc15';
    const stroke = (isProposed && isBrown) ? '#7e22ce' : '#a16207';
    L.marker([s.lat,s.lon],{icon:starIcon(fill,stroke,22),zIndexOffset:1000})
      .addTo(map).bindPopup('<strong>'+s.name+'</strong>'+(s.grades?' ('+s.grades+')':'')+'<br>'+s.address);
    const sn=s.name.replace(' Community Innovation School','').replace(' Neighborhood School','').replace(' Community School','');
    L.marker([s.lat,s.lon],{icon:L.divIcon({html:'<div style="font-size:10px;font-weight:600;white-space:nowrap;margin-left:12px;margin-top:-5px;color:#1a1a18;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff">'+sn+'</div>',className:'',iconAnchor:[0,6]}),zIndexOffset:999,interactive:false}).addTo(map);
  });

  otherSchools.forEach(s => {
    L.marker([s.lat,s.lon],{icon:starIcon('#94a3b8','#475569',18),zIndexOffset:1000})
      .addTo(map).bindPopup('<strong>'+s.name+'</strong>'+(s.grades?' ('+s.grades+')':'')+'<br>'+s.address);
    const sn = s.name.length > 20 ? s.name.split(' (')[0].split(' / ')[0] : s.name;
    L.marker([s.lat,s.lon],{icon:L.divIcon({html:'<div style="font-size:9px;font-weight:600;white-space:nowrap;margin-left:11px;margin-top:-4px;color:#374151;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff">'+sn+'</div>',className:'',iconAnchor:[0,6]}),zIndexOffset:999,interactive:false}).addTo(map);
  });

  return map;
}

const mapLeft = buildMap('map-left', currentSamples, false);
const mapRight = buildMap('map-right', proposedSamples, true);

let syncing = false;
function syncMaps(source, target) {
  source.on('move', function() {
    if (syncing) return;
    syncing = true;
    target.setView(source.getCenter(), source.getZoom(), {animate:false});
    syncing = false;
  });
}
syncMaps(mapLeft, mapRight);
syncMaps(mapRight, mapLeft);
</script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"Saved {OUTPUT_FILE} ({len(html):,} bytes)")
    print("Open it directly in your browser.")


if __name__ == "__main__":
    main()
