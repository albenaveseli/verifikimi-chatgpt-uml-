# Verifikimi praktik i Cámara et al. (2023): ChatGPT dhe modelimi UML

Rast studimor për lëndën **Dizajni dhe analiza e softuerit**, Master, FIEK – Universiteti i Prishtinës.
Autoret: **Agnesa Rama, Albena Veseli**, 2026.

Punimi i verifikuar: J. Cámara, J. Troya, L. Burgueño, A. Vallecillo (2023). *On the assessment of
generative AI in modeling tasks: an experience report with ChatGPT and UML.* Software and Systems
Modeling 22(3), 781–793. https://doi.org/10.1007/s10270-023-01105-5

Artefaktet e autorëve: https://github.com/atenearesearchgroup/chatgpt-uml (GPL-3.0)

## Çfarë verifikojmë

| Niveli | Çfarë bëjmë | Çfarë teston |
|---|---|---|
| A | Numërojmë sesionet në 4 logbook-ët publikë dhe i krahasojmë me Tab. 2 | Riprodhueshmërinë e Tab. 2 (f. 787) |
| B | Vlerësojmë me precision/recall/F1 output-et e ChatGPT nga logbook-ët e 2023 | Kriterin binar „sukses/dështim”, F13, F15 |
| C | Përsërisim 3 ushtrime me ChatGPT-në e 2026 (3 biseda të reja secili, prompt i njëjtë) | F10, F13, F15 sot |

## Rezultatet

**A – Tab. 2:** mesatarja e sesioneve përputhet vetëm për 2 nga 8 ushtrime (Students, Video club).
Logbook-ët e pjesëmarrësve 2 dhe 3 janë identikë (99,95%).

**B dhe C – F1 kundrejt modelit synim:**

| Ushtrimi | Tab. 2 (2023) | 2023: output-e | 2023: F1 mes. | 2023: përputhje e plotë | 2026: F1 mes. | 2026: përputhje e plotë | Pikë kyçe |
|---|---|---|---|---|---|---|---|
| Video club | 4/4 | 5 | 0,70 | 0/5 | 0,98 | 0/3 | shumëfishësia VideoStore–Client gabim në 3/3 |
| Airlines | 0/4 | 13 | 0,48 | 0/13 | 0,38 | 0/3 | association class: 0/13 (2023), 0/3 (2026) |
| Amphibious | 4/4 | 8 | 0,71 | 0/8 | 0,94 | 1/3 | 4 trashëgimi të sakta: 2/8 (2023), 3/3 (2026) |

Vërejtje për 2026:
- **Airlines:** në të 3 bisedat ChatGPT krijon klasë të ndërmjetme (`AirlineOperation` / `Operation`)
  me dy asociacione 1–0..*, në vend të association class. E kupton që kostoja i përket çiftit
  linjë ajrore–aeroport, por nuk përdor konstruktin UML të duhur: F13 qëndron edhe në 2026.
- **Amphibious:** run2 përputhet plotësisht. Gabimet e tjera: `Vehicle` jo abstract (run1, run3),
  `environment : String` pa enum (run3).
- **Video club:** run2 shton klasën `Rental` pa asnjë lidhje.
- Me të njëjtin prompt, 3 bisedat dhanë diagrame të ndryshme në çdo ushtrim (F10).

Detajet janë te `results/` (një rresht për çdo output, F1 për çdo kategori).

## Si ta riprodhoni

```
pip install pypdf
git clone https://github.com/atenearesearchgroup/chatgpt-uml
# çziponi chatgpt-uml/LogBooks.zip në chatgpt-uml/LogBooks/
```

**A – sesionet dhe nxjerrja e diagrameve 2023** (krijon dosjen `logbook_2023/`):
```
python extract_logbooks.py chatgpt-uml/LogBooks
```

**B – vlerësimi i output-eve 2023** (P3 përjashtohet, sepse është kopje e P2):
```
python score_uml.py targets/video.puml      logbook_2023/P[124]_video_*.puml      --csv results/retro_2023_video.csv
python score_uml.py targets/airlines.puml   logbook_2023/P[124]_airlines_*.puml   --csv results/retro_2023_airlines.csv
python score_uml.py targets/amphibious.puml logbook_2023/P[124]_amphibious_*.puml --csv results/retro_2023_amphibious.csv
```

**C – vlerësimi i output-eve 2026** (output-et tona janë te `outputs/`):
```
python score_uml.py targets/video.puml      outputs/video_run1.puml outputs/video_run2.puml outputs/video_run3.puml --csv results/2026_video.csv
python score_uml.py targets/airlines.puml   outputs/airlines_run1.puml outputs/airlines_run2.puml outputs/airlines_run3.puml --csv results/2026_airlines.csv
python score_uml.py targets/amphibious.puml outputs/amphibious_run1.puml outputs/amphibious_run2.puml outputs/amphibious_run3.puml --alias maximumSpeed=maxSpeed --csv results/2026_amphibious.csv
```

Për ta përsëritur eksperimentin 2026 vetë: hapni një Temporary Chat në ChatGPT, ngjitni prompt-in
nga `prompts.md` pa ndryshime, ruani kodin PlantUML në `outputs/<ushtrimi>_run<k>.puml` dhe
ekzekutoni komandat e nivelit C.

## Protokolli i eksperimentit 2026
- Data: 21.11.2026; ChatGPT, Temporary Chat (pa memorie dhe pa histori).
- Modeli: _[shkruani emrin që shfaqej në ChatGPT]_
- 3 ushtrime × 3 biseda të reja; një prompt i vetëm, pa korrigjime.
- Prompt-et janë marrë fjalë për fjalë nga logbook-u i pjesëmarrësit 2 (shih `prompts.md`).
- Sinonim i trajtuar me `--alias`: `maximumSpeed` = `maxSpeed` (Amphibious, run1).

## Përmbajtja
| Skedari | Përshkrimi |
|---|---|
| `extract_logbooks.py` | Numëron sesionet në logbook-ët PDF dhe nxjerr diagramet PlantUML të 2023 |
| `score_uml.py` | Krahason një diagram PlantUML me modelin synim: TP/FP/FN, precision, recall dhe F1 për klasa, atribute, operacione, asociacione, trashëgimi, association class; kontrollon shumëfishësitë |
| `targets/` | 3 modelet synim në PlantUML, të transkriptuara nga figurat e repozitorit të autorëve |
| `prompts.md` | Prompt-et standarde |
| `outputs/` | 9 output-et e ChatGPT 2026 |
| `results/` | Rezultatet në CSV (2023 dhe 2026) |
| `screenshots/` | Bisedat, diagramet e renderuara dhe dalja e skripteve |

## Kufizimet
- Modelet synim janë transkriptuar nga figurat e autorëve; kufizimet OCL të Amphibious nuk vlerësohen.
- Krahasimi bëhet sipas emrave (pa dallim shkronjash të mëdha/vogla, njëjës/shumës); sinonimet trajtohen me `--alias`.
- 3 ekzekutime për ushtrim janë kampion i vogël; versioni i ChatGPT 2026 nuk është ai i 2023.
- Ne përdorim një prompt të vetëm pa korrigjime, ndërsa autorët përdorën biseda me disa prompt-e.
  Krahasimi tregon ndryshimin e ChatGPT-së në kohë, jo gabim të autorëve.

## Deklarimi i AI
Skriptet `extract_logbooks.py` dhe `score_uml.py` janë shkruar me ndihmën e AI (Claude, Anthropic)
dhe janë kontrolluar nga ne. Eksperimenti me ChatGPT, output-et dhe interpretimi janë tonat.

## Licenca
GPL-3.0, si repozitori i autorëve nga i cili janë marrë prompt-et dhe modelet synim.
