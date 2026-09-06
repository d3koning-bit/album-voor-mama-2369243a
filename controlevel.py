#!/usr/bin/env python3
"""Maakt een contactvel van een opgegeven lijst fotonummers, om te controleren."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

WORTEL = Path(__file__).resolve().parent
fotos = {f["nr"]: f for f in json.loads((WORTEL / "meta.json").read_text(encoding="utf-8"))}
KOLOMMEN, CEL, MARGE, BALK = 6, 300, 8, 24

def maak(nummers, naam):
    nummers = [n for n in nummers if n in fotos]
    rijen = (len(nummers) + KOLOMMEN - 1) // KOLOMMEN
    blad = Image.new("RGB", (KOLOMMEN*(CEL+MARGE)+MARGE, rijen*(CEL+MARGE+BALK)+MARGE), (24,24,26))
    tek = ImageDraw.Draw(blad)
    for i, nr in enumerate(nummers):
        x = MARGE + (i % KOLOMMEN)*(CEL+MARGE)
        y = MARGE + (i // KOLOMMEN)*(CEL+MARGE+BALK)
        try:
            with Image.open(WORTEL/"originelen"/fotos[nr]["bestand"]) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((CEL, CEL), Image.LANCZOS)
                blad.paste(im, (x+(CEL-im.width)//2, y+(CEL-im.height)//2))
        except Exception as e:
            tek.text((x+6, y+6), str(e)[:30], fill=(255,90,90))
        tek.text((x+2, y+CEL+5), f"{nr}  {fotos[nr]['datum'][:10]}", fill=(205,205,210))
    blad.save(WORTEL/"contactvellen"/naam, quality=82)
    print(f"{naam}: {len(nummers)} foto's")

if __name__ == "__main__":
    nummers = [int(n) for n in sys.argv[1].split(",")]
    maak(nummers, sys.argv[2])
