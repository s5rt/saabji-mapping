import os
import csv
import zipfile
from fractions import Fraction
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import xml.etree.ElementTree as ET
INPUT_DIR = "images-day-wise/day-1"
OUTPUT_KMZ = os.path.join(INPUT_DIR, "day-1.kmz")
OUTPUT_CSV = os.path.join(INPUT_DIR, "error.csv")
REQUIRED_GPS = [
    "GPS GPSLatitude",
    "GPS GPSLatitudeRef",
    "GPS GPSLongitude",
    "GPS GPSLongitudeRef",
    "GPS GPSAltitude",
]
ERROR_COLUMNS = [
    "EXIF_READ_FAILED",
    "GPS GPSLatitude",
    "GPS GPSLatitudeRef",
    "GPS GPSLongitude",
    "GPS GPSLongitudeRef",
    "GPS GPSAltitude",
    "GPS_PARSE_FAILED",
    "EXIF DateTimeOriginal",
]
def rational_to_float(val):
    if isinstance(val, (list, tuple)):
        return sum(float(Fraction(str(v))) / (60 ** i) for i, v in enumerate(val))
    return float(Fraction(str(val)))
def get_exif(image_path):
    img = Image.open(image_path)
    raw = img._getexif()
    if not raw:
        return {}
    result = {}
    for tag_id, value in raw.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            for gps_id, gps_val in value.items():
                gps_tag = GPSTAGS.get(gps_id, gps_id)
                result[f"GPS {gps_tag}"] = gps_val
        else:
            result[f"EXIF {tag}"] = value
    return result
def parse_coords(exif):
    lat = rational_to_float(exif["GPS GPSLatitude"])
    lon = rational_to_float(exif["GPS GPSLongitude"])
    if exif.get("GPS GPSLatitudeRef", "N") != "N":
        lat = -lat
    if exif.get("GPS GPSLongitudeRef", "E") != "E":
        lon = -lon
    alt = float(Fraction(str(exif.get("GPS GPSAltitude", 0))))
    return lat, lon, alt
def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None
def build_kml(placemarks):
    kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, "Document")
    for pm in placemarks:
        p = ET.SubElement(doc, "Placemark")
        ET.SubElement(p, "name").text = pm["name"]
        desc = (
            f"Image Name: {pm['image_name']}\n"
            f"DateTime: {pm['datetime']}\n"
            f"Lat (DD): {pm['lat']:.6f}\n"
            f"Lon (DD): {pm['lon']:.6f}\n"
            f"Altitude: {pm['alt']} m"
        )
        ET.SubElement(p, "description").text = desc
        pt = ET.SubElement(p, "Point")
        ET.SubElement(pt, "coordinates").text = (
            f"{pm['lon']:.6f},{pm['lat']:.6f},{pm['alt']:.1f}"
        )
    return ET.tostring(kml, encoding="unicode", xml_declaration=False)
def main():
    images = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".jpeg", ".jpg"))
    ]
    placemarks_raw = []
    error_rows = []
    for fname in sorted(images):
        error_record = {"file": fname}
        for col in ERROR_COLUMNS:
            error_record[col] = ""
        fpath = os.path.join(INPUT_DIR, fname)
        try:
            exif = get_exif(fpath)
        except Exception as e:
            error_record["EXIF_READ_FAILED"] = str(e)
            error_rows.append(error_record)
            continue
        missing = [field for field in REQUIRED_GPS if field not in exif]
        for field in missing:
            error_record[field] = "Missing"
        if missing:
            error_rows.append(error_record)
            continue
        try:
            lat, lon, alt = parse_coords(exif)
        except Exception as e:
            error_record["GPS_PARSE_FAILED"] = str(e)
            error_rows.append(error_record)
            continue
        dt = exif.get("EXIF DateTimeOriginal", "")
        if not dt:
            error_record["EXIF DateTimeOriginal"] = "Missing"
        if any(error_record[col] for col in ERROR_COLUMNS):
            error_rows.append(error_record)
        placemarks_raw.append({
            "image_name": fname,
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "datetime": dt,
            "dt_obj": parse_datetime(dt),
        })
    placemarks_raw.sort(
        key=lambda x: (
            x["dt_obj"] is None,
            x["dt_obj"] if x["dt_obj"] else datetime.max,
        )
    )
    placemarks = []
    for idx, pm in enumerate(placemarks_raw, start=1):
        placemarks.append({
            "name": str(idx),  # oldest = 1, newest = n
            "image_name": pm["image_name"],
            "lat": pm["lat"],
            "lon": pm["lon"],
            "alt": pm["alt"],
            "datetime": pm["datetime"],
        })
    kml_str = build_kml(placemarks)
    kml_path = OUTPUT_KMZ.replace(".kmz", ".kml")
    with open(kml_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(kml_str)
    with zipfile.ZipFile(OUTPUT_KMZ, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(kml_path, arcname="doc.kml")
    os.remove(kml_path)
    if error_rows:
        fieldnames = ["file"] + ERROR_COLUMNS
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(error_rows)
if __name__ == "__main__":
    main()