from pathlib import Path
import exifread
image_path = ""
output_md = "image_metadata.md"
exclude_fields = {
    "JPEGThumbnail",
}
with open(image_path, "rb") as f:
    tags = exifread.process_file(f, details=True)
filtered_tags = {
    k: v
    for k, v in tags.items()
    if k not in exclude_fields
}
lines = [
    "# Metadata Report\n",
    f"**File:** `{Path(image_path).name}`\n",
    f"**Total Fields:** {len(filtered_tags)}\n",
    "",
    "| Field | Value |",
    "|-------|-------|",
]
for key in sorted(filtered_tags):
    value = str(filtered_tags[key]).replace("\n", "<br>").replace("|", "\\|")
    lines.append(f"| {key} | {value} |")
Path(output_md).write_text("\n".join(lines), encoding="utf-8")