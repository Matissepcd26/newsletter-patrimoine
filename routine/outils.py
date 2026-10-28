"""Calculs exacts de la routine : variables de date (heure de Paris) et mise en forme de l'email.

python3 outils.py variables                      -> DATE, JOUR, FENETRE, HEURE
python3 outils.py modele                         -> lit le modèle réglé sur le dashboard, écrit /tmp/modele.json
python3 outils.py chiffres                       -> chiffres du fragment absents de /tmp/faits.md
python3 outils.py journal                        -> lignes de /tmp/faits.md dont l'extrait ne contient pas la valeur
python3 outils.py gabarit "NOM" "OBJET" "FOCUS"  -> lit /tmp/fragment.html, écrit /tmp/email.html et /tmp/email.txt,
                                                    puis affiche MOTS=… et une ligne MANQUE=… par élément absent
"""
import html
import json
from pathlib import Path
import re
import subprocess
import urllib.request
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
TITRES = ["L'édito", "Les marchés en un coup d'œil", "Banques centrales et macro",
          "France : épargne, fiscalité, immobilier", "Monde et sujets sensibles", "Focus M2",
          "Le chiffre du jour", "À surveiller aujourd'hui", "Sources"]
MENTION = "Cette newsletter est fournie à titre informatif et pédagogique"
MODELE_URL = "https://le-coffre-patrimoine.vercel.app/api/modele"
OPTIONNELLES = [TITRES[i] for i in (1, 2, 4, 6, 7)]
POLICES = {"serif": "Georgia,'Times New Roman',serif", "sans": "'Helvetica Neue',Helvetica,Arial,sans-serif",
           "systeme": "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif"}
DEFAUT = {"style": {"accent": "#1a2b4c", "lien": "#1a5fb4", "fond": "#f4f1ea", "carte": "#ffffff", "police": "serif",
                    "taille": 16, "largeur": 640, "titres": "filet"}, "contenu": {"masquees": [], "ajouts": [], "suivre": [], "note": ""}}


def valider(m):
    """Mêmes règles que api/modele.js du dashboard : seules des valeurs connues et bornées passent."""
    s, c, d = m.get("style") or {}, m.get("contenu") or {}, DEFAUT["style"]
    hexa = lambda v, x: v.lower() if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) else x
    borne = lambda v, a, b, x: v if type(v) is int and a <= v <= b else x
    texte = lambda v, n: " ".join(re.sub(r"[<>{}\x00-\x1f]", " ", str(v or "")).split())[:n]
    pris = [x.lower() for x in TITRES]
    ajouts = [{"titre": texte(a.get("titre"), 60), "consigne": texte(a.get("consigne"), 400), "mots": borne(a.get("mots"), 60, 250, 120)}
              for a in (c.get("ajouts") or [])[:2] if isinstance(a, dict)]
    return {"style": {k: hexa(s.get(k), d[k]) for k in ("accent", "lien", "fond", "carte")}
            | {"police": s.get("police") if s.get("police") in POLICES else d["police"], "taille": borne(s.get("taille"), 15, 18, d["taille"]),
               "largeur": borne(s.get("largeur"), 560, 720, d["largeur"]),
               "titres": s.get("titres") if s.get("titres") in ("filet", "bandeau", "simple") else d["titres"]},
            "contenu": {"masquees": [x for x in OPTIONNELLES if x in (c.get("masquees") or [])],
                        "ajouts": [a for a in ajouts if a["titre"] and a["consigne"] and not any(a["titre"].lower().startswith(p) for p in pris)],
                        "suivre": list(dict.fromkeys(x for x in (texte(v, 40) for v in (c.get("suivre") or [])) if x))[:8],
                        "note": texte(c.get("note"), 500)}}


def charger_modele():
    try:
        return valider(json.load(open("/tmp/modele.json", encoding="utf-8")))
    except Exception:
        return valider({})


def sections(m):
    """Titres attendus, dans l'ordre : rubriques non masquées, rubriques ajoutées, puis Sources."""
    return [x for x in TITRES[:-1] if x not in m["contenu"]["masquees"]] + [a["titre"] for a in m["contenu"]["ajouts"]] + ["Sources"]


def fourchette(mots):
    return round(mots * .85), round(mots * 1.15)


def melange(h, t):
    return "#" + "".join(f"{round(int(h[i:i + 2], 16) + (255 - int(h[i:i + 2], 16)) * t):02x}" for i in (1, 3, 5))


def clair(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return .299 * r + .587 * g + .114 * b > 140


def styles(st):
    police, texte = f"font-family:{POLICES[st['police']]};", "#2b2b2b" if clair(st["carte"]) else "#ececec"
    titre = {"filet": f"padding-bottom:6px;border-bottom:2px solid {melange(st['accent'], .75)};color:{st['accent']};",
             "bandeau": f"padding:8px 12px;border-radius:4px;background:{st['accent']};color:{st['carte']};",
             "simple": f"color:{st['accent']};"}[st["titres"]]
    t = st["taille"]
    return {"h2": police + f"margin:32px 0 12px;font-size:{t + 5}px;line-height:1.3;" + titre,
            "p": police + f"margin:0 0 14px;font-size:{t}px;line-height:1.65;color:{texte};",
            "ul": "margin:0 0 16px;padding-left:20px;",
            "li": police + f"margin:0 0 8px;font-size:{t}px;line-height:1.6;color:{texte};",
            "a": f"color:{st['lien']};text-decoration:underline;",
            "strong": f"color:{st['accent'] if clair(st['carte']) else texte};"}


def date_fr(d):
    return f"{'1er' if d.day == 1 else d.day} {MOIS[d.month - 1]} {d.year}"


def fenetre(now):
    jour = now.weekday()
    if jour == 0:
        return f"depuis le vendredi {date_fr(now - timedelta(days=3))} au matin, week-end compris"
    if jour == 5:
        return f"la semaine écoulée, depuis le lundi {date_fr(now - timedelta(days=5))}"
    if jour == 6:
        return f"depuis le vendredi {date_fr(now - timedelta(days=2))} au matin, plus l'agenda de la semaine à venir"
    hier = now - timedelta(days=1)
    return f"les dernières 24 heures, depuis le {JOURS[hier.weekday()]} {date_fr(hier)} au matin"


def normaliser(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("’", "'").split())


def variables():
    now = datetime.now(ZoneInfo("Europe/Paris"))
    print(f"DATE={date_fr(now)}\nJOUR={JOURS[now.weekday()]}\nFENETRE={fenetre(now)}\nHEURE={now:%H:%M}")


def gabarit(nom, objet, focus):
    fragment = open("/tmp/fragment.html", encoding="utf-8").read()
    m = charger_modele(); st = m["style"]
    titres = [normaliser(t) for t in re.findall(r"<h2[^>]*>(.*?)</h2>", fragment, re.S)]
    for attendu in sections(m):
        if not any(t.startswith(attendu) for t in titres):
            print(f"MANQUE=section <h2>{attendu}</h2>")
    if MENTION not in normaliser(fragment):
        print("MANQUE=mention finale")
    corps = re.split(r"<h2[^>]*>\s*Sources", fragment)[0]
    mots = len(re.findall(r"\w+(?:['’-]\w+)*", normaliser(corps)))
    print(f"MOTS={mots}")

    style = fragment
    for tag, css in styles(st).items():
        style = re.sub(rf"<{tag}(\s[^>]*)?>", lambda m, t=tag, c=css: f'<{t} style="{c}"{m.group(1) or ""}>', style)
    now = datetime.now(ZoneInfo("Europe/Paris"))
    entete = f"{JOURS[now.weekday()].capitalize()} {date_fr(now)} · Focus M2 du jour : {html.escape(focus)}"
    with open("/tmp/email.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(objet)}</title></head>
<body style="margin:0;padding:0;background:{st['fond']};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{st['fond']};"><tr><td align="center" style="padding:24px 10px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:{st['largeur']}px;background:{st['carte']};border-radius:8px;">
<tr><td style="padding:28px 24px 4px;font-family:{POLICES[st['police']]};">
<div style="font-size:13px;letter-spacing:1px;text-transform:uppercase;color:{st['accent'] if clair(st['carte']) else '#ececec'};">☕ {html.escape(nom)}</div>
<div style="font-size:14px;color:{'#6b6b6b' if clair(st['carte']) else '#b5b5b5'};margin-top:4px;">{entete}</div></td></tr>
<tr><td style="padding:0 24px 28px;">{style}</td></tr></table></td></tr></table></body></html>""")

    t = re.sub(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"\2 (\1)", fragment, flags=re.S)
    t = re.sub(r"<h2[^>]*>(.*?)</h2>", lambda m: "\n\n" + m.group(1).upper() + "\n\n", t, flags=re.S)
    t = re.sub(r"<li[^>]*>", "\n- ", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"</p>|</ul>", "\n\n", t)))
    with open("/tmp/email.txt", "w", encoding="utf-8") as f:
        f.write(f"Focus M2 du jour : {focus}\n\n" + re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip() + "\n")


def modele(url=MODELE_URL):
    copie = Path(__file__).resolve().parent.parent / "config" / "modele.json"  # recopiée chaque heure par .github/workflows/modele.yml
    try:
        brut = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
        m, etat = valider(brut), f"réglé sur le dashboard (modifié le {brut.get('date') or 'jamais'})"
    except Exception as e:
        try:
            brut = json.load(open(copie, encoding="utf-8"))
            m, etat = valider(brut), f"réglé sur le dashboard, copie du dépôt (modifié le {brut.get('date') or 'jamais'})"
        except Exception:
            m, etat = valider({}), f"d'origine (dashboard injoignable : {type(e).__name__}, pas de copie dans le dépôt)"
    json.dump(m, open("/tmp/modele.json", "w", encoding="utf-8"), ensure_ascii=False)
    c = m["contenu"]
    print(f"MODELE={etat}\nSECTIONS={' | '.join(sections(m))}\nMASQUEES={' | '.join(c['masquees']) or 'aucune'}")
    for a in c["ajouts"]:
        bas, haut = fourchette(a["mots"])
        print(f"AJOUT={a['titre']} ; {bas}-{haut} mots ; {a['consigne']}")
    print(f"SUIVRE={', '.join(c['suivre']) or 'aucun'}\nNOTE={c['note'] or 'aucune'}")


def chiffres():
    """Chiffres de la newsletter absents du journal des faits : chacun doit être sourcé, corrigé ou retiré."""
    fragment = open("/tmp/fragment.html", encoding="utf-8").read()
    corps = normaliser(re.split(r"<h2[^>]*>\s*Sources", fragment)[0])
    norm = lambda s: re.sub(r"[\s\u202f\xa0]", "", s).replace(",", ".").strip(".")
    journal = norm(open("/tmp/faits.md", encoding="utf-8").read())
    absents = 0
    for m in re.finditer(r"\d[\d\u202f\xa0 .,]*\d|\d", corps):
        n = norm(m.group())
        if re.fullmatch(r"20\d\d", n) or (re.fullmatch(r"\d{1,2}", n) and int(n) <= 31) or n in journal:
            continue
        absents += 1
        print(f"NON_SOURCÉ={m.group().strip()} … {corps[max(0, m.start() - 50):m.end() + 15]}")
    print(f"NON_SOURCÉS={absents}")


def journal():
    """Lignes du journal dont l'extrait ne contient pas la valeur : le fait n'est pas prouvé par sa source."""
    norm = lambda s: re.sub(r"[\s\u202f\xa0]", "", s).replace(",", ".").replace("’", "'").lower()
    fautes = 0
    for ligne in open("/tmp/faits.md", encoding="utf-8"):
        champs = [c.strip() for c in ligne.split("|")]
        if len(champs) < 3 or not champs[1] or champs[2].lower() in ("calcul", "extrait exact de la source qui contient la valeur"):
            continue
        if norm(champs[1]).strip(".%€$") not in norm(champs[2]):
            fautes += 1
            print(f"EXTRAIT_SANS_VALEUR={champs[1]} … {champs[0][:60]}")
    print(f"EXTRAITS_FAUTIFS={fautes}")
    # Faits publiés avant le début de la fenêtre : à présenter en « pour rappel » ou à retirer.
    now = datetime.now(ZoneInfo("Europe/Paris"))
    debut = (now - timedelta(days={0: 3, 5: 5, 6: 2}.get(now.weekday(), 1))).date()
    for ligne in open("/tmp/faits.md", encoding="utf-8"):
        champs = [c.strip() for c in ligne.split("|")]
        texte_date = champs[-1] if len(champs) >= 7 else ""
        m = (re.search(r"(\d{4})-(\d{2})-(\d{2})", texte_date) or re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", texte_date))
        if not m:
            continue
        a, mo, j = (m.groups() if len(m.group(1)) == 4 else m.groups()[::-1])
        if datetime(int(a), int(mo), int(j)).date() < debut and not re.search(r"légifrance|bofip|service-public|yahoo|cnbc|calcul", ligne, re.I):
            print(f"AVANT_FENETRE={texte_date} … {champs[0][:70]}")


def corps_actualite():
    """Texte des rubriques d'actualité (avant le Focus), où une date ou un jugement doit être justifié."""
    fragment = open("/tmp/fragment.html", encoding="utf-8").read()
    return normaliser(re.split(r"<h2[^>]*>\s*Focus", fragment)[0])


def fenetre_ok():
    """Jours de semaine antérieurs à la fenêtre cités sans « pour rappel » : actualité hors fenêtre probable."""
    now = datetime.now(ZoneInfo("Europe/Paris"))
    recul = {0: 3, 5: 5, 6: 2}.get(now.weekday(), 1)  # jours entre aujourd'hui et le début de la fenêtre
    avant = {JOURS[(now - timedelta(days=d)).weekday()] for d in range(recul + 1, 7)}
    corps, n = corps_actualite(), 0
    for m in re.finditer(r"\b(" + "|".join(avant) + r")\b", corps, re.I):
        contexte = corps[max(0, m.start() - 90):m.end() + 40]
        if not re.search(r"pour rappel|depuis|prochain|à venir|attendu", contexte, re.I):
            n += 1
            print(f"A_VERIFIER_FENETRE={m.group()} … {contexte}")
    print(f"A_VERIFIER_FENETRE_TOTAL={n}")


def opinions():
    """Phrases de jugement sans marqueur d'opinion ni attribution : à baliser ou à reformuler en fait sourcé."""
    jugement = (r"\b(jamais|pire|inquiétant\w*|cruel\w*|paradoxe|spectaculaire|signe que|redout\w+|absurde|"
                r"brutal\w*|dramatique\w*|alarmant\w*|évident\w*|clairement|forcément|décroch\w+|fiasco|"
                r"surréaliste|incroyable\w*|remarquable\w*|scandal\w+|sans doute|probablement|vraisemblablement)\b")
    n = 0
    for phrase in re.split(r"(?<=[.!?])\s+", corps_actualite()):
        if re.search(jugement, phrase, re.I) and not re.search(r"mon avis|à mon sens|selon|d'après|estime|juge", phrase, re.I):
            n += 1
            print(f"A_VERIFIER_OPINION={phrase[:140]}")
    print(f"A_VERIFIER_OPINION_TOTAL={n}")


def marches_ok():
    """Relance routine/marches.py et vérifie que chaque niveau publié figure dans la rubrique marchés."""
    sortie = subprocess.run([sys.executable, str(Path(__file__).with_name("marches.py"))], capture_output=True, text=True).stdout
    blocs = re.split(r"(?=<h2)", open("/tmp/fragment.html", encoding="utf-8").read())
    rubrique = next((normaliser(x) for x in blocs if normaliser(x).startswith("Les marchés")), "")
    ecarts = 0
    for ligne in sortie.splitlines():
        champs = [c.strip() for c in ligne.split(";")]
        m = re.match(r"\d[\d ]*,\d+", champs[1]) if len(champs) >= 4 and not champs[3].startswith("dernier cours") else None
        if not m:
            continue
        niveau = m.group()
        if "%" in champs[1]:  # taux : publié à deux décimales
            niveau = f"{float(niveau.replace(' ', '').replace(',', '.')):.2f}".replace(".", ",")
        if niveau not in rubrique:
            ecarts += 1
            print(f"MARCHE_ECART={champs[0]} : attendu {niveau} ({champs[2]}, {champs[3]})")
    print(f"MARCHE_ECARTS={ecarts}")


THEMES = ["Fiscalité IR", "IS et sociétés", "Immobilier", "Gestion de portefeuille", "Transmission",
          "Cas pratique", "Marchés et macro"]


def archiver(site, objet, focus):
    """Ajoute l'email du jour au site d'archives : page archives/AAAA-MM-JJ.html et entrée dans archives/index.json."""
    now = datetime.now(ZoneInfo("Europe/Paris"))
    date = now.date().isoformat()
    dossier = Path(site) / "archives"
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / f"{date}.html").write_text(open("/tmp/email.html", encoding="utf-8").read(), encoding="utf-8")
    faits = []  # journal des faits : chaque chiffre avec l'extrait de sa source, affiché dans le coffre
    if Path("/tmp/faits.md").exists():
        for ligne in open("/tmp/faits.md", encoding="utf-8"):
            c = [x.strip() for x in ligne.split("|")]
            if len(c) >= 6 and c[0] and c[0] != "affirmation":
                faits.append(dict(zip(["affirmation", "valeur", "extrait", "media", "titre", "url", "date"], c + [""] * 7)))
    (dossier / f"{date}.faits.json").write_text(json.dumps(faits, ensure_ascii=False, indent=1), encoding="utf-8")
    index = dossier / "index.json"
    entrees = [e for e in (json.loads(index.read_text(encoding="utf-8")) if index.exists() else []) if e["date"] != date]
    entrees.append({"date": date, "jour": f"{JOURS[now.weekday()]} {date_fr(now)}", "objet": objet,
                    "focus": focus, "theme": THEMES[now.weekday()]})
    entrees.sort(key=lambda e: e["date"], reverse=True)
    index.write_text(json.dumps(entrees, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ARCHIVE={date}.html ; {len(entrees)} newsletter(s) archivée(s)")


if __name__ == "__main__":
    {"variables": variables, "modele": lambda: modele(*sys.argv[2:3]), "chiffres": chiffres, "journal": journal, "fenetre": fenetre_ok, "opinions": opinions, "marches": marches_ok, "archiver": lambda: archiver(*sys.argv[2:5])}.get(sys.argv[1], lambda: gabarit(*sys.argv[2:5]))()
