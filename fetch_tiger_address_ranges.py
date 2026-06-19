"""
Downloads the Census TIGER/Line "Edges" shapefile for Middlesex County, MA,
filters to Somerville street segments, and extracts the address range
(low/high house number, both sides) for every street.

This gives ground-truth address ranges per street segment, instead of
relying on the city street register's "whole street" entries (which often
omit a range) or manual estimates.

Requirements: pip install geopandas pyshp shapely --break-system-packages
  (geopandas pulls in fiona/pyogrio under the hood; if geopandas install is
  painful on your machine, there's a pure-pyshp fallback path noted below.)

Run: python3 fetch_tiger_address_ranges.py
Outputs: somerville_street_ranges.csv — upload to Claude
"""
import urllib.request
import zipfile
import os
import csv

# Middlesex County, MA FIPS = 25017
COUNTY_FIPS = "25017"
YEAR = "2023"  # TIGER/Line vintage; adjust if a newer year is available
EDGES_URL = f"https://www2.census.gov/geo/tiger/TIGER{YEAR}/EDGES/tl_{YEAR}_{COUNTY_FIPS}_edges.zip"

ZIP_PATH = f"tl_{YEAR}_{COUNTY_FIPS}_edges.zip"
EXTRACT_DIR = f"tl_{YEAR}_{COUNTY_FIPS}_edges"
SHP_BASE = f"tl_{YEAR}_{COUNTY_FIPS}_edges"

def download():
    if os.path.exists(ZIP_PATH):
        print(f"{ZIP_PATH} already downloaded, skipping fetch")
        return
    print(f"Downloading {EDGES_URL} ...")
    req = urllib.request.Request(EDGES_URL, headers={"User-Agent": "somerville-street-research/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(ZIP_PATH, "wb") as f:
        f.write(r.read())
    print("Download complete")

def extract():
    if os.path.exists(EXTRACT_DIR):
        print(f"{EXTRACT_DIR} already extracted, skipping")
        return
    print("Extracting zip...")
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(EXTRACT_DIR)
    print("Extraction complete")

def process_with_geopandas():
    import geopandas as gpd

    shp_path = os.path.join(EXTRACT_DIR, f"{SHP_BASE}.shp")
    print(f"Reading {shp_path} ...")
    gdf = gpd.read_file(shp_path)

    print(f"Total edges in Middlesex County: {len(gdf)}")

    # Filter to Somerville: TIGER edges carry left/right place codes
    # (STATEFP/COUNTYFP/COUSUBFP or via TLID join to ADDRFEAT) depending on year.
    # Most reliably, edges include 'FULLNAME' (street name) and address fields
    # LFROMHN, LTOHN, RFROMHN, RTOHN, ZIPL, ZIPR. We filter on Somerville ZIP
    # codes as the most robust available signal in the edges table itself.
    SOMERVILLE_ZIPS = {"02143", "02144", "02145"}

    def has_somerville_zip(row):
        zl = str(row.get("ZIPL", "") or "")
        zr = str(row.get("ZIPR", "") or "")
        return zl in SOMERVILLE_ZIPS or zr in SOMERVILLE_ZIPS

    mask = gdf.apply(has_somerville_zip, axis=1)
    som = gdf[mask].copy()
    print(f"Edges matching Somerville ZIP codes: {len(som)}")

    rows = []
    for _, r in som.iterrows():
        name = r.get("FULLNAME")
        if not name:
            continue
        lfrom, lto = r.get("LFROMHN"), r.get("LTOHN")
        rfrom, rto = r.get("RFROMHN"), r.get("RTOHN")
        rows.append({
            "street": name,
            "left_from": lfrom, "left_to": lto,
            "right_from": rfrom, "right_to": rto,
            "zip_left": r.get("ZIPL"), "zip_right": r.get("ZIPR"),
        })

    out_path = "somerville_street_ranges.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                                 ["street","left_from","left_to","right_from","right_to","zip_left","zip_right"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} street segments to {out_path}")
    print("Upload somerville_street_ranges.csv to Claude")

def process_with_pyshp_fallback():
    """Fallback path if geopandas is hard to install. Pure pyshp + dbf read."""
    import shapefile  # pyshp

    shp_path = os.path.join(EXTRACT_DIR, f"{SHP_BASE}.shp")
    print(f"Reading {shp_path} via pyshp fallback...")
    sf = shapefile.Reader(shp_path)
    fields = [f[0] for f in sf.fields[1:]]  # skip deletion flag
    SOMERVILLE_ZIPS = {"02143", "02144", "02145"}

    rows = []
    for rec in sf.records():
        d = dict(zip(fields, rec))
        zl = str(d.get("ZIPL", "") or "")
        zr = str(d.get("ZIPR", "") or "")
        if zl in SOMERVILLE_ZIPS or zr in SOMERVILLE_ZIPS:
            name = d.get("FULLNAME")
            if not name:
                continue
            rows.append({
                "street": name,
                "left_from": d.get("LFROMHN"), "left_to": d.get("LTOHN"),
                "right_from": d.get("RFROMHN"), "right_to": d.get("RTOHN"),
                "zip_left": zl, "zip_right": zr,
            })

    out_path = "somerville_street_ranges.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["street","left_from","left_to","right_from","right_to","zip_left","zip_right"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} street segments to {out_path}")
    print("Upload somerville_street_ranges.csv to Claude")

if __name__ == "__main__":
    download()
    extract()
    try:
        process_with_geopandas()
    except ImportError:
        print("geopandas not available, falling back to pyshp...")
        print("If pyshp is also missing: pip install pyshp --break-system-packages")
        process_with_pyshp_fallback()
