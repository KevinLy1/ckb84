# Clavier 75 % sur mesure : boîtier gasket-mount

Boîtier usiné CNC, avec une plaque montée sur joints en Poron et des aimants à la place des vis. Tout est généré à partir du PCB KiCad de `src/02_pcb`, par les scripts build123d de `src/`.

| Caractéristique | Valeur |
|---|---|
| Dimensions | **319,8 × 143,8 mm**, 148 mm de profondeur posé sur le bureau |
| Hauteur (avant / arrière) | **22,1 / 42,1 mm** |
| Angle de frappe | **8°**, donné par le bottom case en coin |
| Masse | top case ≈ 87 g + bottom case ≈ 655 g |
| Montage | 10 pattes de plaque entre des pastilles de Poron |
| Fermeture | 8 paires d'aimants 5 × 2 mm |

## Construction

Depuis `src/03_case`, avec Docker Desktop lancé (environnement figé, build123d 0.13.0) :

```bash
docker compose build
```

```bash
docker compose run --rm cad src/build_all.py
```

```bash
docker compose run --rm cad src/drawings.py
```

```bash
docker compose run --rm cad src/docs_html.py
```

Pour servir le viewer, puis ouvrir `http://localhost:8765/out/viewer.html` :

```bash
docker compose run --rm --service-ports cad -m http.server 8765
```

`build_all.py` vérifie aussi qu'aucune pièce n'en chevauche une autre (tous les résultats doivent valoir `0.0`). Ré-exporter `in/pcb.step` et `in/pcb_full.step` après une modification du PCB demande `kicad-cli` sur la machine.

## Résumé de la conception

Empilement (dessus du PCB = 0, en mm) : PCB −1,51 … 0, plaque 3,5 … 5,0, joints 3,0 (compressés à 2,4), plan de jonction 5,0, dessus 14,0, fond de cavité −6,51.

- **Plaque :** 1,5 mm, découpes de switches 14 × 14 mm, découpes de stabilisateurs Cherry à visser, 10 pattes de joint avec fentes de flexion. Les positions viennent des empreintes KiCad.
- **Top case :** cadre de 9 mm avec un pont de 4,5 mm sur la rangée F.
- **Bottom case :** cavité parallèle à la plaque, rebord de centrage, ouverture USB-C avec une peau de 1 mm pour ne laisser voir que le port, encoche de levage à l'arrière, dessous à 8° avec quatre logements de Ø10,4 pour les patins.
- **Stabilisateurs :** S5 est dans l'orientation Cherry standard, S1–S4 sont tournés de 180° sur le PCB. La plaque suit le PCB, elle s'adapte donc telle quelle.

## Fabrication

- **Top case :** 2 mises en position. **Bottom case :** 3 mises en position (face de jonction, dessous à 8°, ouverture USB-C sur la face arrière).
- **Prototype d'abord :** imprime les STL en 3D pour vérifier l'assemblage avant de payer l'usinage.

## Liste d'achats (amazon.fr)

| # | Article | Qté | Caractéristiques | Recherche sur amazon.fr |
|---|---|---|---|---|
| 1 | Aimants néodyme | 16 (8 paires) + rechange | Disque **5 × 2 mm**, N52 | `aimant néodyme 5x2 mm` (lots de 50) |
| 2 | Mousse pour joints | 20 pastilles | **Poron 3 mm** (ou mousse EPDM 3 mm), adhésive ; à découper en pastilles de 15 × 3 mm | `poron 3mm adhésif` / `joint mousse EPDM adhésif 3 mm` |
| 3 | Patins en caoutchouc | 4 | Patins adhésifs plats **Ø10 × 3 mm** | `patins caoutchouc adhésifs 10 x 3 mm` |
| 4 | Mousse de fond | 1 feuille ≥ 310 × 130 mm | **3 mm**, Poron ou EVA (moins cher) ; découpe selon `case_foam.dxf` | `feuille mousse EVA 3 mm A3` |
| 5 | Mousse PCB/plaque (optionnelle) | 1 feuille | 3–3,5 mm, Poron ou PE, avec les trous des switches | `mousse polyuréthane 3 mm` |
| 6 | Colle | 1 | Cyanoacrylate en **gel** ou époxy bi-composant | `colle cyanoacrylate gel` / `Araldite` |
