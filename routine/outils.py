"""Calculs exacts de la routine : variables de date (heure de Paris) et mise en forme de l'email.

python3 outils.py variables                      -> DATE, JOUR, FENETRE, HEURE
python3 outils.py gabarit "NOM" "OBJET" "FOCUS"  -> lit /tmp/fragment.html, écrit /tmp/email.html et /tmp/email.txt,
                                                    puis affiche MOTS=… et une ligne MANQUE=… par élément absent
"""
import html
import re
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
POLICE = "font-family:Georgia,'Times New Roman',serif;"
STYLES = {
    "h2": POLICE + "margin:32px 0 12px;padding-bottom:6px;border-bottom:2px solid #e8dcc4;"
                   "font-size:21px;line-height:1.3;color:#1a2b4c;",
    "p": POLICE + "margin:0 0 14px;font-size:16px;line-height:1.65;color:#2b2b2b;",
    "ul": "margin:0 0 16px;padding-left:20px;",
    "li": POLICE + "margin:0 0 8px;font-size:16px;line-height:1.6;color:#2b2b2b;",
    "a": "color:#1a5fb4;text-decoration:underline;",
    "strong": "color:#1a2b4c;",
}


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
    titres = [normaliser(t) for t in re.findall(r"<h2[^>]*>(.*?)</h2>", fragment, re.S)]
    for attendu in TITRES:
        if not any(t.startswith(attendu) for t in titres):
            print(f"MANQUE=section <h2>{attendu}</h2>")
    if MENTION not in normaliser(fragment):
        print("MANQUE=mention finale")
    corps = re.split(r"<h2[^>]*>\s*Sources", fragment)[0]
    print(f"MOTS={len(re.findall(r'\w+(?:[\'’-]\w+)*', normaliser(corps)))}")

    style = fragment
    for tag, css in STYLES.items():
        style = re.sub(rf"<{tag}(\s[^>]*)?>", lambda m, t=tag, c=css: f'<{t} style="{c}"{m.group(1) or ""}>', style)
    now = datetime.now(ZoneInfo("Europe/Paris"))
    entete = f"{JOURS[now.weekday()].capitalize()} {date_fr(now)} · Focus M2 du jour : {html.escape(focus)}"
    with open("/tmp/email.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(objet)}</title></head>
<body style="margin:0;padding:0;background:#f4f1ea;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f1ea;"><tr><td align="center" style="padding:24px 10px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;background:#ffffff;border-radius:8px;">
<tr><td style="padding:28px 24px 4px;{POLICE}">
<div style="font-size:13px;letter-spacing:1px;text-transform:uppercase;color:#8a7350;">☕ {html.escape(nom)}</div>
<div style="font-size:14px;color:#6b6b6b;margin-top:4px;">{entete}</div></td></tr>
<tr><td style="padding:0 24px 28px;">{style}</td></tr></table></td></tr></table></body></html>""")

    t = re.sub(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"\2 (\1)", fragment, flags=re.S)
    t = re.sub(r"<h2[^>]*>(.*?)</h2>", lambda m: "\n\n" + m.group(1).upper() + "\n\n", t, flags=re.S)
    t = re.sub(r"<li[^>]*>", "\n- ", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"</p>|</ul>", "\n\n", t)))
    with open("/tmp/email.txt", "w", encoding="utf-8") as f:
        f.write(f"Focus M2 du jour : {focus}\n\n" + re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip() + "\n")


if __name__ == "__main__":
    variables() if sys.argv[1] == "variables" else gabarit(*sys.argv[2:5])
