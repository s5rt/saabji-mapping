from pathlib import Path
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
SOURCE_DIR = Path("unmarked-images")
DEST_ROOT = Path("date-marked")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".webp"}
def get_exif_date(image_path):
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
            if not exif:
                return None
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None
for file in SOURCE_DIR.iterdir():
    if not file.is_file() or file.suffix.lower() not in IMAGE_EXTS:
        continue
    dt = get_exif_date(file)
    if dt is None:
        # fallback to filesystem modified time
        dt = datetime.fromtimestamp(file.stat().st_mtime)
    dest_dir = DEST_ROOT / dt.strftime("%Y-%m-%d")
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(file), str(dest_dir / file.name))
print("Done.")