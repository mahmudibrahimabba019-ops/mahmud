import os
import shutil
from pathlib import Path

root = Path(r"c:\Users\HP\Desktop\Backup\Desktop\websites\spices-shop")
images_dir = root / "images"
images_dir.mkdir(exist_ok=True)

for item in root.iterdir():
    if not item.is_file():
        continue
    if item.suffix.lower() not in {".jpeg", ".jpg", ".png"}:
        continue
    target = images_dir / item.name
    if target.exists():
        if item.resolve() != target.resolve():
            item.unlink()
    else:
        shutil.move(str(item), str(target))
