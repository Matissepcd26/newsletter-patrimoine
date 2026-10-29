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
DEFAUT = {"style": {"accent": "#111113", "lien": "#9a5b00", "fond": "#f2f2f3", "carte": "#ffffff", "police": "sans", "taille": 16,
                    "largeur": 680, "titres": "numero", "entete": "plein", "arrondis": 12, "densite": "aere", "encadres": True, "marches": "tableau"},
          "contenu": {"format": "condense", "essentiel": True, "bouton": True, "ordre": TITRES[:-1], "masquees": [], "ajouts": [], "suivre": [], "note": "",
                      "jours": list(range(7)), "heure": "09:00", "pause_du": "", "pause_au": "", "question": True}}
QUESTION = "Réponse à la question d'examen"
HEURES = ("08:00", "08:30", "09:00", "09:30")
# Longueurs du cahier des charges (format complet), réduites selon le format choisi, avec un plancher par rubrique.
LONGUEURS = {"L'édito": (250, 300), "Les marchés en un coup d'œil": (250, 300), "Banques centrales et macro": (300, 350),
             "France : épargne, fiscalité, immobilier": (350, 400), "Monde et sujets sensibles": (300, 350), "Focus M2": (500, 600),
             "Le chiffre du jour": (80, 120), "À surveiller aujourd'hui": (120, 150), "L'essentiel": (45, 100), "Réponse à la question d'examen": (50, 130)}
NON_REDUITES = ("L'essentiel", "Réponse à la question d'examen")  # longueur fixe, quel que soit le format
PLANCHERS = {"Les marchés en un coup d'œil": 160, "Le chiffre du jour": 60, "À surveiller aujourd'hui": 70, "L'essentiel": 45}
FORMATS = {"condense": .5, "standard": .75, "complet": 1}
SITE = "https://le-coffre-patrimoine.vercel.app"


def valider(m):
    """Mêmes règles que api/modele.js du dashboard : seules des valeurs connues et bornées passent."""
    s, c, d = m.get("style") or {}, m.get("contenu") or {}, DEFAUT["style"]
    hexa = lambda v, x: v.lower() if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) else x
    borne = lambda v, a, b, x: v if type(v) is int and a <= v <= b else x
    texte = lambda v, n: " ".join(re.sub(r"[<>{}\x00-\x1f]", " ", str(v or "")).split())[:n]
    pris = [x.lower() for x in TITRES]
    ajouts = [{"titre": texte(a.get("titre"), 60), "consigne": texte(a.get("consigne"), 400), "mots": borne(a.get("mots"), 60, 250, 120)}
              for a in (c.get("ajouts") or [])[:2] if isinstance(a, dict)]
    choix = lambda v, permis, x: v if v in permis else x
    oui = lambda v, x: v if isinstance(v, bool) else x
    ordre = c.get("ordre") if isinstance(c.get("ordre"), list) and sorted(c.get("ordre")) == sorted(TITRES[:-1]) else TITRES[:-1]
    return {"style": {k: hexa(s.get(k), d[k]) for k in ("accent", "lien", "fond", "carte")}
            | {"police": s.get("police") if s.get("police") in POLICES else d["police"], "taille": borne(s.get("taille"), 15, 18, d["taille"]),
               "largeur": borne(s.get("largeur"), 560, 720, d["largeur"]),
               "titres": choix(s.get("titres"), ("numero", "filet", "bandeau", "simple"), d["titres"]),
               "entete": choix(s.get("entete"), ("plein", "sobre"), d["entete"]), "arrondis": borne(s.get("arrondis"), 0, 20, d["arrondis"]),
               "densite": choix(s.get("densite"), ("aere", "compact"), d["densite"]), "encadres": oui(s.get("encadres"), d["encadres"]),
               "marches": choix(s.get("marches"), ("tableau", "liste"), d["marches"])},
            "contenu": {"format": choix(c.get("format"), FORMATS, "condense"), "essentiel": oui(c.get("essentiel"), True),
                        "bouton": oui(c.get("bouton"), True), "ordre": list(ordre),
                        "masquees": [x for x in OPTIONNELLES if x in (c.get("masquees") or [])],
                        "ajouts": [a for a in ajouts if a["titre"] and a["consigne"] and not any(a["titre"].lower().startswith(p) for p in pris)],
                        "suivre": list(dict.fromkeys(x for x in (texte(v, 40) for v in (c.get("suivre") or [])) if x))[:8],
                        "note": texte(c.get("note"), 500),
                        "jours": sorted({j for j in (c.get("jours") or []) if type(j) is int and 0 <= j <= 6}) or list(range(7)),
                        "heure": choix(c.get("heure"), HEURES, "09:00"), "question": oui(c.get("question"), True),
                        "pause_du": c.get("pause_du") if isinstance(c.get("pause_du"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", c.get("pause_du")) else "",
                        "pause_au": c.get("pause_au") if isinstance(c.get("pause_au"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", c.get("pause_au")) else ""}}


def charger_modele():
    try:
        return valider(json.load(open("/tmp/modele.json", encoding="utf-8")))
    except Exception:
        return valider({})


def sections(m):
    """Titres attendus, dans l'ordre : rubriques non masquées, rubriques ajoutées, puis Sources."""
    c = m["contenu"]
    corps = [x for x in c["ordre"] if x not in c["masquees"]] + [a["titre"] for a in c["ajouts"]]
    return (["L'essentiel"] if c["essentiel"] else []) + corps + ([QUESTION] if c["question"] else []) + ["Sources"]


def longueurs(m):
    """Fourchette de mots de chaque rubrique écrite, selon le format choisi."""
    f, res = FORMATS[m["contenu"]["format"]], {}
    for nom in sections(m)[:-1]:
        ajout = next((a for a in m["contenu"]["ajouts"] if a["titre"] == nom), None)
        if ajout:
            res[nom] = fourchette(ajout["mots"])
            continue
        bas, haut = LONGUEURS[nom]
        if nom in NON_REDUITES:
            res[nom] = (bas, haut)
            continue
        bas = max(round(bas * f), PLANCHERS.get(nom, 0))
        res[nom] = (bas, max(round(haut * f), bas + 40))
    return res


def fourchette(mots):
    return round(mots * .85), round(mots * 1.15)


def melange(h, t):
    return "#" + "".join(f"{round(int(h[i:i + 2], 16) + (255 - int(h[i:i + 2], 16)) * t):02x}" for i in (1, 3, 5))


def clair(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return .299 * r + .587 * g + .114 * b > 140


def styles(st):
    police, texte = f"font-family:{POLICES[st['police']]};", texte_mail(st)
    titre = {"filet": f"padding-bottom:6px;border-bottom:2px solid {melange(st['accent'], .75)};color:{st['accent']};",
             "bandeau": f"padding:8px 12px;border-radius:4px;background:{st['accent']};color:{st['carte']};",
             "simple": f"color:{st['accent']};", "numero": f"color:{st['accent']};"}[st["titres"]]
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
    with open("/tmp/email.html", "w", encoding="utf-8") as f:  # version envoyée : riche, sans les sources
        f.write(mail(nom, objet, focus, fragment, st, m["contenu"], f"{now:%Y-%m-%d}", f"{JOURS[now.weekday()].capitalize()} {date_fr(now)}"))
    with open("/tmp/complet.html", "w", encoding="utf-8") as f:  # version complète, avec les sources : contrôles et archives
        f.write(f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(objet)}</title></head>
<body style="margin:0;padding:0;background:{st['fond']};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{st['fond']};"><tr><td align="center" style="padding:24px 10px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:{st['largeur']}px;background:{st['carte']};border-radius:8px;">
<tr><td style="padding:28px 24px 4px;font-family:{POLICES[st['police']]};">
<div style="font-size:13px;letter-spacing:1px;text-transform:uppercase;color:{st['accent'] if clair(st['carte']) else '#ececec'};">◆ {html.escape(nom)}</div>
<div style="font-size:14px;color:{'#6b6b6b' if clair(st['carte']) else '#b5b5b5'};margin-top:4px;">{entete}</div></td></tr>
<tr><td style="padding:0 24px 28px;">{style}</td></tr></table></td></tr></table></body></html>""")

    sans_sources = re.split(r"<h2[^>]*>\s*Sources", fragment)[0]
    t = re.sub(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"\2 (\1)", sans_sources, flags=re.S)
    t = re.sub(r"<h2[^>]*>(.*?)</h2>", lambda m: "\n\n" + m.group(1).upper() + "\n\n", t, flags=re.S)
    t = re.sub(r"<li[^>]*>", "\n- ", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"</p>|</ul>", "\n\n", t)))
    with open("/tmp/email.txt", "w", encoding="utf-8") as f:
        f.write(f"Focus M2 du jour : {focus}\n\n" + re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip()
                + f"\n\nÉdition complète et sources : {SITE}/#/n/{now:%Y-%m-%d}\n\n{MENTION}. Elle ne constitue ni un conseil en investissement, ni un conseil fiscal ou juridique personnalisé.\n")


VERT, ROUGE = "#0f7b3e", "#b42318"


def blocs(fragment):
    """(titre, corps) de chaque rubrique du fragment, dans l'ordre."""
    return [(normaliser(re.match(r"<h2[^>]*>(.*?)</h2>", b, re.S).group(1)), re.sub(r"^<h2[^>]*>.*?</h2>", "", b, count=1, flags=re.S).strip())
            for b in re.split(r"(?=<h2)", fragment) if b.startswith("<h2")]


def colorer(s):
    """Variations signées en vert ou en rouge (hausse, baisse)."""
    return re.sub(r"(?<![\w,/])([+−–-]\s?\d[\d \xa0 ]*(?:,\d+)?\s?(?:%|pb|points? de base))",
                  lambda m: f'<b style="color:{VERT if m.group(1)[0] == "+" else ROUGE};white-space:nowrap;">{m.group(1)}</b>', s)


def habiller(s, st):
    for tag, css in styles(st).items():
        s = re.sub(rf"<{tag}(\s[^>]*)?>", lambda m, t=tag, c=css: f'<{t} style="{c}"{m.group(1) or ""}>', s)
    return s


def titre_mail(titre, n, st):
    police, a = f"font-family:{POLICES[st['police']]};", st["accent"] if clair(st["carte"]) else "#f2f2f2"
    if st["titres"] == "numero":
        return (f'<div style="{police}font-size:12px;font-weight:700;letter-spacing:2px;color:{st["lien"]};margin:0 0 4px;">{n:02d}</div>'
                f'<h2 style="{police}margin:0 0 12px;font-size:{st["taille"] + 6}px;line-height:1.25;color:{a};">{titre}</h2>')
    return habiller(f"<h2>{titre}</h2>", st)


def section_mail(titre, corps, n, st):
    texte, r = texte_mail(st), st["arrondis"]
    if titre == "L'essentiel":
        return (f'<div style="background:{melange(st["lien"], .9)};border-left:4px solid {st["lien"]};border-radius:{r}px;padding:16px 18px;">'
                f'<div style="font-family:{POLICES[st["police"]]};font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{st["accent"] if clair(st["carte"]) else texte};margin-bottom:8px;">L\'essentiel</div>'
                f'{habiller(corps, st)}</div>')
    if titre.startswith("Les marchés") and st["marches"] == "tableau" and "<li" in corps:
        lignes = re.findall(r"<li[^>]*>(.*?)</li>", corps, re.S)
        rangs = "".join(f'<tr><td style="padding:9px 10px 9px 0;border-bottom:1px solid {melange(texte, .85) if clair(st["carte"]) else "#333"};font-family:{POLICES[st["police"]]};font-size:{st["taille"] - 1}px;font-weight:700;color:{texte};vertical-align:top;width:32%;">{normaliser(l).split(" : ")[0]}</td>'
                        f'<td style="padding:9px 0;border-bottom:1px solid {melange(texte, .85) if clair(st["carte"]) else "#333"};font-family:{POLICES[st["police"]]};font-size:{st["taille"] - 1}px;line-height:1.5;color:{texte};">{colorer(habiller(" : ".join(l.split(" : ")[1:]) or l, st))}</td></tr>' for l in lignes)
        reste = re.sub(r"<ul[^>]*>.*?</ul>", "", corps, count=1, flags=re.S)
        corps_html = f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 14px;">{rangs}</table>{habiller(reste, st)}'
    else:
        corps_html = habiller(colorer(corps) if titre.startswith("Les marchés") else corps, st)
    bloc = titre_mail(titre, n, st) + corps_html
    if st["encadres"] and titre.startswith("Le chiffre du jour"):
        m = re.search(r"<strong[^>]*>(.*?)</strong>", corps, re.S)
        if m:
            chiffre = f'<div style="font-family:{POLICES[st["police"]]};font-size:40px;font-weight:800;line-height:1.1;color:{st["lien"]};margin:4px 0 10px;">{normaliser(m.group(1))}</div>'
            bloc = titre_mail(titre, n, st) + chiffre + habiller(corps.replace(m.group(0), m.group(1), 1), st)
    if st["encadres"] and (titre.startswith("Focus M2") or titre.startswith("Le chiffre du jour")):
        bloc = f'<div style="border:1px solid {melange(st["accent"], .8) if clair(st["carte"]) else "#3a3a3a"};border-radius:{r}px;padding:18px 18px 4px;">{bloc}</div>'
    return bloc


def texte_mail(st):
    return "#1f1f22" if clair(st["carte"]) else "#ececec"


def mail(nom, objet, focus, fragment, st, contenu, jour_iso, entete_date):
    """Email riche : en-tête, rubriques mises en forme, sans les sources (elles sont sur le Coffre)."""
    police, r, texte = f"font-family:{POLICES[st['police']]};", st["arrondis"], texte_mail(st)
    marge, pad = (34, 28) if st["densite"] == "aere" else (22, 20)
    plein = st["entete"] == "plein"
    fond_tete, texte_tete = (st["accent"], "#ffffff" if not clair(st["accent"]) else "#111113") if plein else (st["carte"], st["accent"] if clair(st["carte"]) else texte)
    rubriques, mention, n = [], "", 0
    for titre, corps in blocs(fragment):
        if titre == QUESTION:
            rubriques.append(f'<tr><td class="int" style="padding:{marge}px {pad}px 0;"><div style="{police}font-size:{st["taille"] - 1}px;line-height:1.5;color:{texte};'
                             f'padding:14px 16px;border:1px dashed {melange(texte, .7) if clair(st["carte"]) else "#444"};border-radius:{r}px;">'
                             f'<b>Question d\'examen :</b> la réponse et le raisonnement sont sur le Coffre. <a href="{SITE}/#/n/{jour_iso}" style="color:{st["lien"]};">Voir la réponse</a></div></td></tr>')
            continue
        if titre.startswith("Sources"):
            mention = " ".join(p for p in re.findall(r"<p[^>]*>.*?</p>", corps, re.S) if MENTION in normaliser(p))
            continue
        n += titre != "L'essentiel"
        rubriques.append(f'<tr><td class="int" style="padding:{marge if rubriques else pad}px {pad}px 0;">{section_mail(titre, corps, n, st)}</td></tr>')
    apercu = normaliser(next((c for t, c in blocs(fragment) if t in ("L'essentiel", "L'édito")), ""))[:140]
    lien = f"{SITE}/#/n/{jour_iso}"
    bouton = (f'<tr><td class="int" style="padding:{marge}px {pad}px 0;" align="center"><a href="{lien}" style="display:inline-block;padding:13px 22px;border-radius:999px;'
              f'background:{st["accent"]};color:{"#ffffff" if not clair(st["accent"]) else "#111113"};{police}font-size:15px;font-weight:700;text-decoration:none;">'
              f'Lire l\'édition complète et ses sources</a></td></tr>') if contenu["bouton"] else ""
    pied_couleur = "#6b6b70" if clair(st["carte"]) else "#a1a1aa"
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light only"><title>{html.escape(objet)}</title>
<style>@media (max-width:640px){{.coque{{padding:0!important}}.carte{{border-radius:0!important}}.int{{padding-left:18px!important;padding-right:18px!important}}}}</style></head>
<body style="margin:0;padding:0;background:{st['fond']};">
<div style="display:none;max-height:0;overflow:hidden;">{html.escape(apercu)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{st['fond']};"><tr><td class="coque" align="center" style="padding:20px 8px;">
<table role="presentation" class="carte" width="100%" cellpadding="0" cellspacing="0" style="max-width:{st['largeur']}px;background:{st['carte']};border-radius:{r}px;overflow:hidden;">
<tr><td class="int" style="padding:{pad + 4}px {pad}px {pad}px;background:{fond_tete};{'' if plein else f'border-bottom:1px solid {melange(texte, .85)};'}{police}">
<div style="font-size:13px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:{texte_tete};"><span style="color:{st['lien'] if not plein else '#ffb547'};">◆</span> {html.escape(nom)}</div>
<div style="font-size:14px;color:{texte_tete};opacity:.75;margin-top:6px;">{entete_date}</div>
<div style="display:inline-block;margin-top:12px;padding:6px 12px;border-radius:999px;background:{'rgba(255,255,255,.12)' if plein and not clair(st['accent']) else melange(st['lien'], .88)};color:{texte_tete};font-size:13px;font-weight:600;">Focus du jour : {html.escape(focus)}</div></td></tr>
{''.join(rubriques)}{bouton}
<tr><td class="int" style="padding:{marge}px {pad}px {pad}px;{police}font-size:12px;line-height:1.6;color:{pied_couleur};">
{re.sub(r'<p[^>]*>', f'<p style="margin:0 0 8px;{police}font-size:12px;line-height:1.6;color:{pied_couleur};">', mention)}
<a href="{SITE}/#/modele" style="color:{pied_couleur};">Modifier le modèle du mail</a> · <a href="{lien}" style="color:{pied_couleur};">Sources et vérifications</a></td></tr>
</table></td></tr></table></body></html>"""


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
    print(f"MODELE={etat}\nFORMAT={c['format']}\nSECTIONS={' | '.join(sections(m))}\nMASQUEES={' | '.join(c['masquees']) or 'aucune'}")
    print("LONGUEURS=" + " | ".join(f"{nom} {bas}-{haut}" for nom, (bas, haut) in longueurs(m).items()))
    if c["essentiel"]:
        print("ESSENTIEL=oui : le fragment commence par <h2>L'essentiel</h2> puis un <ul> de trois puces de 15 à 30 mots, les trois faits à retenir")
    if c["question"]:
        print(f"QUESTION=oui : le Focus M2 se termine par <p><strong>Question d'examen :</strong> …</p>, une question courte de type partiel de M2 sur le mécanisme du jour ; "
              f"la rubrique <h2>{QUESTION}</h2>, juste avant Sources, donne la réponse rédigée et le raisonnement, avec la référence du texte. Elle n'apparaît pas dans le mail, seulement sur le Coffre")
    for a in c["ajouts"]:
        bas, haut = fourchette(a["mots"])
        print(f"AJOUT={a['titre']} ; {bas}-{haut} mots ; {a['consigne']}")
    print(f"SUIVRE={', '.join(c['suivre']) or 'aucun'}\nNOTE={c['note'] or 'aucune'}")
    aujourdhui = datetime.now(ZoneInfo("Europe/Paris"))
    en_pause = c["pause_du"] and c["pause_au"] and c["pause_du"] <= f"{aujourdhui:%Y-%m-%d}" <= c["pause_au"]
    raison = (f"pause du {c['pause_du']} au {c['pause_au']}" if en_pause
              else f"pas d'envoi le {JOURS[aujourdhui.weekday()]}" if aujourdhui.weekday() not in c["jours"] else "")
    print(f"ENVOI={'non (' + raison + ')' if raison else 'oui'}\nHEURE_ENVOI={c['heure']}")


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
        try:
            jour = datetime(int(a), int(mo), int(j)).date()
        except ValueError:  # date à l'américaine (mm/jj/aaaa) ou invalide
            try:
                jour = datetime(int(a), int(j), int(mo)).date()
            except ValueError:
                print(f"DATE_ILLISIBLE={texte_date} … {champs[0][:70]}")
                continue
        if jour < debut and not re.search(r"légifrance|bofip|service-public|yahoo|cnbc|calcul", ligne, re.I):
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
    source = "/tmp/complet.html" if Path("/tmp/complet.html").exists() else "/tmp/email.html"  # version complète, avec les sources
    (dossier / f"{date}.html").write_text(open(source, encoding="utf-8").read(), encoding="utf-8")
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
    commandes = {"variables": variables, "modele": lambda: modele(*sys.argv[2:3]), "gabarit": lambda: gabarit(*sys.argv[2:5]),
                 "chiffres": chiffres, "journal": journal, "fenetre": fenetre_ok, "opinions": opinions, "marches": marches_ok,
                 "archiver": lambda: archiver(*sys.argv[2:5])}
    if len(sys.argv) < 2 or sys.argv[1] not in commandes:
        sys.exit(f"COMMANDE_INCONNUE={' '.join(sys.argv[1:2])} ; commandes : {', '.join(commandes)}")
    commandes[sys.argv[1]]()
