# Prompt-et standarde për eksperimentin 2026

Për t'i krahasuar rezultatet me 2023, përdorim **të njëjtin prompt për të gjitha ekzekutimet**.
Prompt-et janë marrë fjalë për fjalë nga logbook-u i pjesëmarrësit 2 (LogBooks.zip,
github.com/atenearesearchgroup/chatgpt-uml), sepse janë më të plotët: i japin emrat e
klasave dhe atributeve, kështu që krahasimi me modelin synim është i drejtë.

Rregullat për çdo ekzekutim:
- bisedë e re (Temporary chat ose memory i çaktivizuar), pa histori;
- prompt-i kopjohet saktësisht si më poshtë, pa ndryshime;
- një prompt i vetëm, pa korrigjime (ndryshe nga autorët), që rezultati të jetë i krahasueshëm;
- ruani kodin PlantUML në outputs/<ushtrimi>_run<k>.puml (k = 1, 2, 3);
- shënoni modelin e ChatGPT-së që shfaqet në ndërfaqe dhe datën/orën.

## 1. Video club (modeli synim: targets/video.puml) – rasti „i suksesshëm” 4/4 te Tab. 2
```
Draw a UML diagram of a Video Store. There are also clients and movies in the system, all of which have a name. Video stores rent out movies, where the same movie can be offered in any video store. Video stores have clients. Please do not add any operation in the UML diagram. Draw the UML diagram in PlantUML.
```

## 2. Airlines (modeli synim: targets/airlines.puml) – teston F13 (association class), 0/4 te Tab. 2
```
Many different airlines can operate in different airports. An airline has a name, and an airport has a code and is in a city. Each airline has associated a cost for operating in a specific airport. Besides, the operation of an airline in a specific airport can be started and stopped at any time, and its operating cost can be updated at any time. Please, draw a UML diagram for this system. Represent the diagram using PlantUML
```

## 3. Amphibious (modeli synim: targets/amphibious.puml) – teston trashëgiminë e shumëfishtë, 4/4 te Tab. 2
```
A Vehicle has a position, a speed and a maximum speed. Besides, it has an environment (with a value among “land”, “water” and “air”). Finally, it can move for a given time. Those are the features of a generic vehicle. Then, we have land vehicles and marine vehicles as specific types of vehicles, where both have all the same features as a vehicle. Finally, an amphibious vehicle can be both a land vehicle and a marine vehicle. Please, draw a UML class diagram with PlantUML notation.
```

Shënim: prompt-et e autorëve ndryshonin nga personi në person (p.sh. për Video club,
pjesëmarrësi 1 shkroi vetëm „I would like to write a plantUML diagram in which a Video Store
has multiple clients and can rent many movies”). Ky është një nga kufizimet që kritikojmë
(sllajdi 9), prandaj këtu prompt-i mbahet i njëjtë.
