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
OUTPUT_KMZ_IMG = os.path.join(INPUT_DIR, "day-1-img.kmz")
OUTPUT_CSV = os.path.join(INPUT_DIR, "data.csv")
REQUIRED_GPS = [
    "GPS GPSLatitude",
    "GPS GPSLatitudeRef",
    "GPS GPSLongitude",
    "GPS GPSLongitudeRef",
    "GPS GPSAltitude",
]
DATA_COLUMNS = [
    "file",
    "EXIF_READ_FAILED",
    "GPS GPSLatitude",
    "GPS GPSLatitudeRef",
    "GPS GPSLongitude",
    "GPS GPSLongitudeRef",
    "GPS GPSAltitude",
    "GPS_PARSE_FAILED",
    "EXIF DateTimeOriginal",
    "Latitude",
    "Longitude",
    "Altitude",
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
def build_kml(placemarks, embed_images=False):
    kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, "Document")
    path_folder = ET.SubElement(doc, "Folder")
    ET.SubElement(path_folder, "name").text = "Path"
    path_pm = ET.SubElement(path_folder, "Placemark")
    ET.SubElement(path_pm, "name").text = "1_to_N_Path"
    line = ET.SubElement(path_pm, "LineString")
    ET.SubElement(line, "tessellate").text = "1"
    coords = [
        f"{pm['lon']:.6f},{pm['lat']:.6f},{pm['alt']:.1f}"
        for pm in placemarks
    ]
    ET.SubElement(line, "coordinates").text = " ".join(coords)
    for pm in placemarks:
        folder = ET.SubElement(doc, "Folder")
        ET.SubElement(folder, "name").text = pm["name"]
        p = ET.SubElement(folder, "Placemark")
        ET.SubElement(p, "name").text = pm["name"]
        if embed_images:
            desc = f"""
<![CDATA[
<b>Point:</b> {pm['name']}<br>
<b>Image Name:</b> {pm['image_name']}<br>
<b>DateTime:</b> {pm['datetime']}<br>
<b>Latitude:</b> {pm['lat']:.6f}<br>
<b>Longitude:</b> {pm['lon']:.6f}<br>
<b>Altitude:</b> {pm['alt']} m<br><br>
<img src="images/{pm['image_name']}" width="800"/>
]]>
"""
        else:
            desc = (
                f"Point: {pm['name']}\n"
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
        if f.lower().endswith((".jpg", ".jpeg"))
    ]
    placemarks_raw = []
    data_rows = []
    for fname in sorted(images):
        row = {
            "file": fname,
            "EXIF_READ_FAILED": "missing",
            "GPS GPSLatitude": "missing",
            "GPS GPSLatitudeRef": "missing",
            "GPS GPSLongitude": "missing",
            "GPS GPSLongitudeRef": "missing",
            "GPS GPSAltitude": "missing",
            "GPS_PARSE_FAILED": "missing",
            "EXIF DateTimeOriginal": "missing",
            "Latitude": "",
            "Longitude": "",
            "Altitude": "",
        }
        fpath = os.path.join(INPUT_DIR, fname)
        try:
            exif = get_exif(fpath)
            row["EXIF_READ_FAILED"] = "present"
        except Exception:
            data_rows.append(row)
            continue
        for field in REQUIRED_GPS:
            if field in exif:
                row[field] = "present"
        dt = exif.get("EXIF DateTimeOriginal", "")
        if dt:
            row["EXIF DateTimeOriginal"] = "present"
        missing_gps = [f for f in REQUIRED_GPS if f not in exif]
        if missing_gps:
            data_rows.append(row)
            continue
        try:
            lat, lon, alt = parse_coords(exif)
            row["GPS_PARSE_FAILED"] = "present"
            row["Latitude"] = lat
            row["Longitude"] = lon
            row["Altitude"] = alt
        except Exception:
            data_rows.append(row)
            continue
        data_rows.append(row)
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
            "name": str(idx),
            "image_name": pm["image_name"],
            "lat": pm["lat"],
            "lon": pm["lon"],
            "alt": pm["alt"],
            "datetime": pm["datetime"],
        })
    # Standard KMZ
    kml_str = build_kml(placemarks, embed_images=False)
    kml_path = OUTPUT_KMZ.replace(".kmz", ".kml")
    with open(kml_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(kml_str)
    with zipfile.ZipFile(OUTPUT_KMZ, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(kml_path, arcname="doc.kml")
    os.remove(kml_path)
    # Image KMZ
    img_kml_str = build_kml(placemarks, embed_images=True)
    img_kml_path = OUTPUT_KMZ_IMG.replace(".kmz", ".kml")
    with open(img_kml_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(img_kml_str)
    with zipfile.ZipFile(OUTPUT_KMZ_IMG, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(img_kml_path, arcname="doc.kml")
        for pm in placemarks:
            src = os.path.join(INPUT_DIR, pm["image_name"])
            if os.path.exists(src):
                zf.write(src, arcname=f"images/{pm['image_name']}")
    os.remove(img_kml_path)
    # Data CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DATA_COLUMNS)
        writer.writeheader()
        writer.writerows(data_rows)
if __name__ == "__main__":
    main()