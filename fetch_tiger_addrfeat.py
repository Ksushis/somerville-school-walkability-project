"""
Downloads the Census TIGER/Line "ADDRFEAT" (Address Range Feature) shapefile
for Middlesex County, MA, filters to Somerville street segments, and extracts
the address range (low/high house number, both sides) for every street.

NOTE: the "Edges" layer (tl_YYYY_FIPS_edges) usually has empty LFROMHN/LTOHN/
RFROMHN/RTOHN fields for most segments. ADDRFEAT is the TIGER product that
actually carries populated address ranges -- use this instead.

Run: python3 fetch_tiger_addrfeat.py
Outputs: somerville_street_ranges.csv -- upload to Claude
"""
import urllib.request
import zipfile
import os
import csv

COUNTY_FIPS = "25017"  # Middlesex County, MA
YEAR = "2023"
ADDRFEAT_URL = f"https://www2.census.gov/geo/tiger/TIGER{YEAR}/ADDRFEAT/tl_{YEAR}_{COUNTY_FIPS}_addrfeat.zip"

ZIP_PATH = f"tl_{YEAR}_{COUNTY_FIPS}_addrfeat.zip"
EXTRACT_DIR = f"tl_{YEAR}_{COUNTY_FIPS}_addrfeat"
SHP_BASE = f"tl_{YEAR}_{COUNTY_FIPS}_addrfeat"

SOMERVILLE_ZIPS = {"02143", "02144", "02145"}

def download():
    if os.path.exists(ZIP_PATH):
        print(f"{ZIP_PATH} already downloaded, skipping fetch")
        return
    print(f"Downloading {ADDRFEAT_URL} ...")
    req = urllib.request.Request(ADDRFEAT_URL, headers={"User-Agent": "somerville-street-research/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(ZIP_PATH, "wb") as f:
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
    print(f"Total address-range features in Middlesex County: {len(gdf)}")
    print(f"Columns available: {list(gdf.columns)}")

    def has_somerville_zip(row):
        zl = str(row.get("ZIPL", "") or "")
        zr = str(row.get("ZIPR", "") or "")
        return zl in SOMERVILLE_ZIPS or zr in SOMERVILLE_ZIPS

    mask = gdf.apply(has_somerville_zip, axis=1)
    som = gdf[mask].copy()
    print(f"Segments matching Somerville ZIP codes: {len(som)}")

    rows = []
    for _, r in som.iterrows():
        name = r.get("FULLNAME")
        if not name:
            continue
        rows.append({
            "street": name,
            "left_from": r.get("LFROMHN"), "left_to": r.get("LTOHN"),
            "right_from": r.get("RFROMHN"), "right_to": r.get("RTOHN"),
            "zip_left": r.get("ZIPL"), "zip_right": r.get("ZIPR"),
        })

    write_csv(rows)

def process_with_pyshp_fallback():
    import shapefile  # pyshp

    shp_path = os.path.join(EXTRACT_DIR, f"{SHP_BASE}.shp")
    print(f"Reading {shp_path} via pyshp fallback...")
    sf = shapefile.Reader(shp_path)
    fields = [f[0] for f in sf.fields[1:]]
    print(f"Fields available: {fields}")

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

    write_csv(rows)

def write_csv(rows):
    out_path = "somerville_street_ranges.csv"
    fieldnames = ["street","left_from","left_to","right_from","right_to","zip_left","zip_right"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} street segments to {out_path}")

    non_empty = [r for r in rows if r["left_from"] or r["right_from"]]
    print(f"Of which {len(non_empty)} have at least one populated address-range field")
    print("Upload somerville_street_ranges.csv to Claude")

if __name__ == "__main__":
    download()
    extract()
    try:
        process_with_geopandas()
    except ImportError:
        print("geopandas not available, falling back to pyshp...")
        process_with_pyshp_fallback()
