#!/usr/bin/env python3
"""Leest de originelen, bepaalt van elke foto de opnamedatum en maakt
contactvellen zodat de plekindeling gemaakt kan worden."""
import json, re, subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

WORTEL = Path(__file__).resolve().parent
ORIGINELEN = WORTEL / "originelen"
VELLEN = WORTEL / "contactvellen"
EXT = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff", ".webp"}

PER_VEL, KOLOMMEN, CEL, MARGE, BALK = 24, 6, 340, 8, 26


def uit_exif(pad):
    try:
        with Image.open(pad) as im:
            ex = im.getexif()
            for tag in (36867, 36868, 306):          # DateTimeOriginal, Digitized, DateTime
                w = ex.get(tag)
                if w:
                    return datetime.strptime(str(w)[:19], "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None


def uit_naam(naam):
    m = re.search(r"(20\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})", naam)
    if m:
        try:
            return datetime(*map(int, m.groups()))
        except ValueError:
            return None
    return None


def uit_spotlight(pad):
    try:
        uit = subprocess.run(["mdls", "-raw", "-name", "kMDItemContentCreationDate", str(pad)],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        if uit and uit != "(null)":
            return datetime.strptime(uit[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    return None


def datum_van(pad):
    for bron, fn in (("exif", uit_exif), ("naam", lambda p: uit_naam(p.name)),
                     ("spotlight", uit_spotlight)):
        d = fn(pad)
        if d and 2000 < d.year < 2027:
            return d, bron
    return datetime.fromtimestamp(pad.stat().st_mtime), "bestand"


bestanden = sorted(p for p in ORIGINELEN.iterdir()
                   if p.is_file() and p.suffix.lower() in EXT and not p.name.startswith("."))
print(f"{len(bestanden)} foto's gevonden, datums uitlezen...")

fotos, bronnen = [], {}
for pad in bestanden:
    d, bron = datum_van(pad)
    bronnen[bron] = bronnen.get(bron, 0) + 1
    fotos.append({"bestand": pad.name, "datum": d.isoformat(), "jaar": d.year})

fotos.sort(key=lambda f: (f["datum"], f["bestand"]))
for i, f in enumerate(fotos):
    f["nr"] = i + 1

(WORTEL / "meta.json").write_text(json.dumps(fotos, ensure_ascii=False, indent=1), encoding="utf-8")
print("datumbronnen:", bronnen)

# ---- contactvellen ----
for oud in VELLEN.glob("*.jpg"):
    oud.unlink()
rijen = (PER_VEL + KOLOMMEN - 1) // KOLOMMEN
vel_b = KOLOMMEN * (CEL + MARGE) + MARGE
vel_h = rijen * (CEL + MARGE + BALK) + MARGE

for start in range(0, len(fotos), PER_VEL):
    groep = fotos[start:start + PER_VEL]
    vel_nr = start // PER_VEL + 1
    blad = Image.new("RGB", (vel_b, vel_h), (24, 24, 26))
    tekenaar = ImageDraw.Draw(blad)
    for i, f in enumerate(groep):
        kx, ky = i % KOLOMMEN, i // KOLOMMEN
        x = MARGE + kx * (CEL + MARGE)
        y = MARGE + ky * (CEL + MARGE + BALK)
        try:
            with Image.open(ORIGINELEN / f["bestand"]) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((CEL, CEL), Image.LANCZOS)
                blad.paste(im, (x + (CEL - im.width) // 2, y + (CEL - im.height) // 2))
        except Exception as e:
            tekenaar.text((x + 6, y + 6), f"fout: {e}", fill=(255, 90, 90))
        tekenaar.text((x + 2, y + CEL + 6),
                      f"{f['nr']}  {f['datum'][:10]}", fill=(200, 200, 205))
    blad.save(VELLEN / f"vel-{vel_nr:02d}.jpg", quality=80)
    print(f"  vel-{vel_nr:02d}.jpg  ({groep[0]['nr']}-{groep[-1]['nr']})")

print(f"\nKlaar. {len(fotos)} foto's, {(len(fotos)+PER_VEL-1)//PER_VEL} contactvellen.")
