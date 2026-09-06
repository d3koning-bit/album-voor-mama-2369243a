#!/usr/bin/env python3
"""Zet mijn indeling (op basis van de contactvellen) om in plekken.txt."""
import json
from pathlib import Path

WORTEL = Path(__file__).resolve().parent
fotos = json.loads((WORTEL / "meta.json").read_text(encoding="utf-8"))

# (van, tot, plek) - tot is inclusief. Gebaseerd op wat ik op de contactvellen zag.
INDELING = [
    (1, 2, "Amerika"), (3, 3, "Feesten & mijlpalen"), (4, 4, "Onderweg in Nederland"),
    (5, 9, "Op het water"), (10, 15, "Amerika"), (16, 18, "Feesten & mijlpalen"),
    (19, 21, "Thailand"), (22, 22, "Op het water"), (23, 23, "Feesten & mijlpalen"),
    (24, 25, "Onderweg in Nederland"), (26, 27, "Feesten & mijlpalen"), (28, 28, "Thuis"),
    (29, 29, "Feesten & mijlpalen"), (30, 30, "Onderweg in Nederland"), (31, 48, "Amerika"),
    (49, 49, "Onderweg in Nederland"), (50, 50, "Thuis"), (51, 53, "Onderweg in Nederland"),
    (54, 55, "Feesten & mijlpalen"), (56, 61, "Feesten & mijlpalen"), (62, 62, "Thuis"),
    (63, 64, "Feesten & mijlpalen"), (65, 69, "Onderweg in Nederland"), (70, 94, "Italië"),
    (95, 96, "Thuis"), (97, 107, "Thuis"), (108, 110, "Feesten & mijlpalen"),
    (111, 124, "Amerika"), (125, 129, "Thuis"), (130, 131, "Feesten & mijlpalen"),
    (132, 133, "Onderweg in Nederland"), (134, 161, "Thuis"), (162, 170, "Op het water"),
    (171, 171, "Onderweg in Nederland"), (172, 181, "Feesten & mijlpalen"),
    (182, 186, "Op het water"), (187, 193, "Feesten & mijlpalen"),
    (194, 198, "Onderweg in Nederland"), (199, 199, "Thuis"), (200, 201, "Onderweg in Nederland"),
    (202, 205, "Thuis"), (206, 206, "Onderweg in Nederland"), (207, 209, "Feesten & mijlpalen"),
    (210, 211, "Onderweg in Nederland"), (212, 213, "Op het water"),
    (214, 219, "Onderweg in Nederland"), (220, 221, "Thuis"), (222, 222, "Op het water"),
    (223, 225, "Onderweg in Nederland"), (226, 227, "Thuis"), (228, 234, "België"),
    (235, 238, "Onderweg in Nederland"), (239, 242, "België"),
    (243, 243, "Onderweg in Nederland"), (244, 246, "Feesten & mijlpalen"),
    (247, 248, "Onderweg in Nederland"), (249, 249, "Thuis"), (250, 261, "Onderweg in Nederland"),
    (262, 262, "Thuis"), (263, 266, "Onderweg in Nederland"), (267, 272, "Thuis"),
    (273, 276, "Onderweg in Nederland"), (277, 277, "Spanje"), (278, 280, "Thuis"),
    (281, 282, "België"), (283, 284, "Onderweg in Nederland"), (285, 287, "Thuis"),
    (288, 322, "Thailand"), (323, 331, "Onderweg in Nederland"),
    (332, 333, "Feesten & mijlpalen"), (334, 338, "Onderweg in Nederland"),
    (339, 352, "Spanje"), (353, 355, "Onderweg in Nederland"), (356, 358, "Thuis"),
    (359, 364, "Onderweg in Nederland"), (365, 366, "Thuis"),
    (367, 370, "Feesten & mijlpalen"), (371, 372, "Onderweg in Nederland"), (373, 373, "Thuis"),
    (374, 386, "Feesten & mijlpalen"), (387, 397, "Onderweg in Nederland"),
    (398, 408, "Portugal"), (409, 414, "Onderweg in Nederland"), (415, 417, "Amerika"),
    (418, 418, "Onderweg in Nederland"), (419, 419, "Thuis"),
    # Uit de restbak "Onderweg in Nederland" gelicht, na het bekijken van de foto's.
    (171, 171, "Uit eten"), (194, 198, "Uit eten"), (214, 215, "Uit eten"), (217, 219, "Uit eten"),
    (250, 253, "Uit eten"), (266, 266, "Uit eten"), (336, 338, "Uit eten"), (353, 355, "Uit eten"),
    (363, 364, "Uit eten"), (394, 394, "Uit eten"), (413, 413, "Uit eten"),
    (51, 51, "Wandelen & buiten"), (200, 201, "Wandelen & buiten"), (247, 248, "Wandelen & buiten"), (254, 259, "Wandelen & buiten"),
    (263, 265, "Wandelen & buiten"), (334, 335, "Wandelen & buiten"), (387, 387, "Wandelen & buiten"), (389, 393, "Wandelen & buiten"),
    # Skipper, de kat. Staat na de rest zodat deze de indeling hierboven overschrijft.
    (98, 99, "Skipper"), (101, 107, "Skipper"), (125, 129, "Skipper"), (135, 137, "Skipper"),
    (139, 140, "Skipper"), (144, 149, "Skipper"), (153, 153, "Skipper"), (155, 157, "Skipper"),
    (199, 199, "Skipper"), (202, 202, "Skipper"), (204, 205, "Skipper"), (226, 227, "Skipper"),
    (262, 262, "Skipper"), (267, 269, "Skipper"), (271, 272, "Skipper"), (279, 279, "Skipper"),
    (285, 285, "Skipper"), (287, 287, "Skipper"), (356, 358, "Skipper"), (365, 366, "Skipper"),
    (419, 419, "Skipper"),
]

plek_van = {}
for van, tot, plek in INDELING:
    for n in range(van, tot + 1):
        plek_van[n] = plek

regels = [
    "# Hier staat per foto op welke plek hij hoort. Pas gerust aan.",
    "#   bestandsnaam | plek",
    "# Een regel weghalen of er # voor zetten = foto niet in het album.",
    "# Een plek hernoemen? Vervang de naam, overal waar hij staat.",
    "#",
    "# Plekken die nu gebruikt worden:",
]
gebruikt = sorted(set(plek_van.values()))
regels += [f"#   {p}" for p in gebruikt] + [""]

zonder = 0
for f in fotos:
    plek = plek_van.get(f["nr"])
    if not plek:
        plek, zonder = "Thuis", zonder + 1
    regels.append(f"{f['bestand']} | {plek}")

(WORTEL / "plekken.txt").write_text("\n".join(regels) + "\n", encoding="utf-8")

telling = {}
for f in fotos:
    p = plek_van.get(f["nr"], "Thuis")
    telling[p] = telling.get(p, 0) + 1
print("plekken.txt geschreven.\n")
for p, n in sorted(telling.items(), key=lambda x: -x[1]):
    print(f"  {n:4d}  {p}")
if zonder:
    print(f"\n(let op: {zonder} foto's hadden geen plek en staan nu op Thuis)")
