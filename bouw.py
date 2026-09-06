#!/usr/bin/env python3
"""
Bouwt het fotoalbum.

Gebruik:  python3 bouw.py

1. Leest meta.json (opnamedatums) en plekken.txt (welke foto op welke plek)
2. Verkleint de originelen naar twee formaten in fotos/
3. Leest instellingen.txt en schrijft index.html
"""
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageOps

WORTEL = Path(__file__).resolve().parent
ORIGINELEN = WORTEL / "originelen"
UITVOER = WORTEL / "fotos"
META = WORTEL / "meta.json"
PLEKKEN = WORTEL / "plekken.txt"
INSTELLINGEN = WORTEL / "instellingen.txt"
SJABLOON = WORTEL / "sjabloon.html"
DOEL = WORTEL / "index.html"

BREEDTE_GROOT, KWALITEIT_GROOT = 1800, 82
BREEDTE_KLEIN, KWALITEIT_KLEIN = 800, 72


EENHEDEN = ["", "een", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen"]
TIENTALLEN = {2: "twintig", 3: "dertig", 4: "veertig", 5: "vijftig",
              6: "zestig", 7: "zeventig", 8: "tachtig", 9: "negentig"}


def in_woorden(getal):
    """Schrijft een leeftijd van 20 t/m 99 voluit, zoals negenenveertig."""
    tien, een = divmod(getal, 10)
    if tien < 2 or tien > 9:
        return str(getal)
    if een == 0:
        return TIENTALLEN[tien]
    verbinding = "\u00ebn" if EENHEDEN[een][-1] in "e" else "en"
    return EENHEDEN[een] + verbinding + TIENTALLEN[tien]


def leeftijden_per_jaar(geboortedatum, jaren):
    """Hoe oud ze in elk jaar geworden is, als woord. Leeg als er geen datum staat."""
    if not geboortedatum:
        return {}
    try:
        geboren = datetime.strptime(geboortedatum.strip(), "%Y-%m-%d")
    except ValueError:
        return {}
    return {str(j): in_woorden(j - geboren.year) for j in jaren if 0 < j - geboren.year < 100}


def veilige_naam(naam):
    return re.sub(r"[^a-zA-Z0-9]+", "-", naam).strip("-").lower() or "foto"


def verklein(bron, doel, breedte, kwaliteit):
    """Verkleint als het nog niet bestaat. Geeft (breedte, hoogte) terug."""
    if doel.exists() and doel.stat().st_mtime >= bron.stat().st_mtime:
        with Image.open(doel) as im:
            return im.size
    with Image.open(bron) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        if im.width > breedte:
            im = im.resize((breedte, round(im.height * breedte / im.width)), Image.LANCZOS)
        im.save(doel, "JPEG", quality=kwaliteit, optimize=True, progressive=True)
        return im.size


def lees_instellingen():
    waarden = {"titel": "", "namen": "", "ondertitel": "", "tabtitel": "",
               "opening": "", "slot": "", "vraag": "", "sleutel": "",
               "geboortedatum": "", "wegwijzer": "", "omslagfoto": ""}
    laatste = None
    for ruwe in INSTELLINGEN.read_text(encoding="utf-8").splitlines():
        regel = ruwe.strip()
        if not regel or regel.startswith("#"):
            continue
        if "=" in regel and re.match(r"^[a-zA-Z][a-zA-Z ]*=", regel):
            sleutel, _, waarde = regel.partition("=")
            laatste = sleutel.strip().lower()
            waarden[laatste] = waarde.strip()
        elif laatste:
            waarden[laatste] = (waarden[laatste] + "\n" + regel).strip()
    return waarden


def lees_plekken():
    plek_van = {}
    for ruwe in PLEKKEN.read_text(encoding="utf-8").splitlines():
        regel = ruwe.strip()
        if not regel or regel.startswith("#"):
            continue
        bestand, _, plek = regel.partition("|")
        bestand, plek = bestand.strip(), plek.strip()
        if bestand and plek:
            plek_van[bestand] = plek
    return plek_van


def bouw():
    for nodig in (META, PLEKKEN, INSTELLINGEN, SJABLOON):
        if not nodig.exists():
            sys.exit(f"{nodig.name} ontbreekt. Draai eerst voorbereid.py.")

    meta = json.loads(META.read_text(encoding="utf-8"))
    plek_van = lees_plekken()
    instellingen = lees_instellingen()
    UITVOER.mkdir(exist_ok=True)

    fotos, overgeslagen = [], []
    totaal = len(meta)
    for i, gegeven in enumerate(meta, start=1):
        naam = gegeven["bestand"]
        plek = plek_van.get(naam)
        if not plek:
            overgeslagen.append(naam)
            continue
        bron = ORIGINELEN / naam
        if not bron.exists():
            overgeslagen.append(naam)
            continue
        stam = f"{gegeven['nr']:03d}-{veilige_naam(Path(naam).stem)}"
        groot, klein = UITVOER / f"{stam}.jpg", UITVOER / f"{stam}-k.jpg"
        try:
            verklein(bron, groot, BREEDTE_GROOT, KWALITEIT_GROOT)
            b, h = verklein(bron, klein, BREEDTE_KLEIN, KWALITEIT_KLEIN)
        except Exception as fout:
            print(f"  overgeslagen: {naam} ({fout})")
            overgeslagen.append(naam)
            continue
        fotos.append({"groot": f"fotos/{groot.name}", "klein": f"fotos/{klein.name}",
                      "breedte": b, "hoogte": h,
                      "datum": gegeven["datum"], "jaar": gegeven["jaar"], "plek": plek})
        if i % 50 == 0 or i == totaal:
            print(f"  {i}/{totaal} verwerkt")

    if not fotos:
        sys.exit("Geen foto's om te tonen.")

    omslag = ""
    if instellingen["omslagfoto"].strip().isdigit():
        gezocht = int(instellingen["omslagfoto"].strip())
        for gegeven, klaar in zip([m for m in meta if m["bestand"] in plek_van], fotos):
            if gegeven["nr"] == gezocht:
                omslag = klaar["groot"]
                break
        if not omslag:
            print(f"let op: foto {gezocht} niet gevonden, omslag blijft zonder foto")

    jaren_in_album = sorted({f["jaar"] for f in fotos})
    leeftijden = leeftijden_per_jaar(instellingen["geboortedatum"], jaren_in_album)
    sleutels = [s.strip() for s in instellingen["sleutel"].split(",") if s.strip()]
    pagina = SJABLOON.read_text(encoding="utf-8")
    for merk, waarde in (
        ("{{TABTITEL}}",  html.escape(instellingen["tabtitel"] or instellingen["namen"])),
        ("{{NAMEN}}",     html.escape(instellingen["namen"])),
        ("{{ONDERTITEL}}", html.escape(instellingen["ondertitel"])),
        ("{{TITEL}}",     html.escape(instellingen["titel"])),
        ("{{VRAAG}}",     html.escape(instellingen["vraag"])),
        ("{{SLOT}}",      html.escape(instellingen["slot"])),
        ("{{OPENING}}",   json.dumps(instellingen["opening"], ensure_ascii=False)),
        ("{{WEGWIJZER}}", json.dumps(instellingen["wegwijzer"], ensure_ascii=False)),
        ("{{OMSLAGFOTO}}", html.escape(omslag)),
        ("{{SLEUTEL}}",   json.dumps(sleutels, ensure_ascii=False)),
        ("{{LEEFTIJDEN}}", json.dumps(leeftijden, ensure_ascii=False)),
        ("{{FOTOS}}",     json.dumps(fotos, ensure_ascii=False, separators=(",", ":"))),
    ):
        pagina = pagina.replace(merk, waarde)
    DOEL.write_text(pagina, encoding="utf-8")

    jaren = jaren_in_album
    plekken = {}
    for f in fotos:
        plekken[f["plek"]] = plekken.get(f["plek"], 0) + 1
    megabytes = sum(p.stat().st_size for p in UITVOER.glob("*.jpg")) / 1_000_000

    print(f"\nKlaar. {len(fotos)} foto's, {jaren[0]} t/m {jaren[-1]}, {len(plekken)} plekken.")
    print(f"Foto's samen {megabytes:.0f} MB, pagina {DOEL.stat().st_size/1000:.0f} kB.")
    if overgeslagen:
        print(f"{len(overgeslagen)} foto's niet meegenomen (geen plek in plekken.txt).")
    print(f"\nOpen {DOEL} om te kijken.")


if __name__ == "__main__":
    bouw()
