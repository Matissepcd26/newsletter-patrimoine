"""Note automatique du cahier des charges (critères C1 à C5 et C7 de eval/grille.md, 23 points).

python3 eval/evaluer.py email.html "OBJET DU MAIL"   -> JSON des points et des écarts relevés
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "routine"))
from outils import charger_modele, longueurs  # noqa: E402

FOURCHETTES = [("L'édito", 250, 300), ("Les marchés en un coup d'œil", 250, 300),
               ("Banques centrales et macro", 300, 350), ("France : épargne, fiscalité, immobilier", 350, 400),
               ("Monde et sujets sensibles", 300, 350), ("Focus M2", 500, 600),
               ("Le chiffre du jour", 80, 120), ("À surveiller aujourd'hui", 120, 150), ("Sources", 0, 10**6)]
MENTION = ("Cette newsletter est fournie à titre informatif et pédagogique. Elle ne constitue ni un conseil en "
           "investissement, ni un conseil fiscal ou juridique personnalisé. Les performances passées ne préjugent "
           "pas des performances futures.")
JOURS = "lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche"


def texte(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("’", "'").split())


def mots(s):
    return len(re.findall(r"\w+(?:['-]\w+)*", texte(s)))


def evaluer(page, objet):
    debut = page.find("<h2")
    contenu = page[debut:page.rfind("</p>") + 4]
    blocs = re.split(r"(?=<h2)", contenu)[1:]
    titres = [texte(re.match(r"<h2[^>]*>(.*?)</h2>", b, re.S).group(1)) for b in blocs]
    notes, ecarts = {}, []
    m = charger_modele()  # modèle réglé par Mathéo (/tmp/modele.json), sinon celui d'origine
    fourchettes = [(nom, bas, haut) for nom, (bas, haut) in longueurs(m).items()] + [FOURCHETTES[-1]]
    avec_marches = "Les marchés en un coup d'œil" not in m["contenu"]["masquees"]

    attendus = [f[0] for f in fourchettes]
    ok = len(titres) == len(attendus) and all(t.startswith(a) for t, a in zip(titres, attendus))
    notes["C1"] = 5 if ok else 0
    if not ok:
        ecarts.append(f"titres trouvés : {titres}")

    total = sum(mots(b) for b in blocs[:-1])
    bas_t, haut_t = sum(f[1] for f in fourchettes[:-1]), sum(f[2] for f in fourchettes[:-1])
    notes["C2"] = 4 if bas_t <= total <= haut_t else 2 if bas_t - 100 <= total <= haut_t + 200 else 0
    dans = 0
    for (nom, bas, haut), bloc in zip(fourchettes[:-1], blocs[:-1]):
        n = mots(bloc)
        dans += bas <= n <= haut
        if not bas <= n <= haut:
            ecarts.append(f"{nom} : {n} mots (attendu {bas}-{haut})")
    notes["C2"] += round(4 * dans / (len(fourchettes) - 1), 2)
    ecarts.append(f"total : {total} mots hors Sources")

    c3 = 0 if "<table" in contenu else 1
    listes_hors = [t for t, b in zip(titres, blocs) if "<ul" in b and not t.startswith(("Les marchés", "Sources", "L'essentiel", "Réponse à la question"))]
    c3 += 0 if listes_hors else 1
    marches = next((b for t, b in zip(titres, blocs) if t.startswith("Les marchés")), "")
    lignes = len(re.findall(r"<li", marches))
    c3 += 2 if lignes == 10 or not avec_marches else 0
    notes["C3"] = c3
    if listes_hors or (avec_marches and lignes != 10) or "<table" in contenu:
        ecarts.append(f"format : listes hors marchés/sources {listes_hors}, {lignes} lignes de marché")

    notes["C4"] = 2 if MENTION in texte(contenu) else 0
    m = re.match(rf"(?:☕|◆) .+ — ({JOURS}) (?:1er|\d{{1,2}}) \w+ \d{{4}} : (.+)$", objet.strip())
    notes["C5"] = 2 if m and len(m.group(2).split()) < 8 else 0
    if not notes["C5"]:
        ecarts.append(f"objet non conforme : {objet}")

    lignes_m = [texte(li) for li in re.findall(r"<li[^>]*>(.*?)</li>", marches, re.S)]
    trouve = lambda cle: next((l for l in lignes_m if l.lower().startswith(cle.lower())), "")
    pb = lambda l: "%" in l and ("pb" in l or "point" in l)
    formats = [re.search(r"\d,\d{4}", trouve("EUR/USD")), pb(trouve("OAT")), pb(trouve("Bund")), "$" in trouve("Or") and "once" in trouve("Or"),
               "$" in trouve("Brent") and "baril" in trouve("Brent"), "$" in trouve("Bitcoin")]
    notes["C7"] = round(2 * sum(bool(f) for f in formats) / 6, 2) if avec_marches else 2
    if notes["C7"] < 2:
        ecarts.append(f"formats marchés respectés : {sum(bool(f) for f in formats)}/6")

    notes["total_auto"] = round(sum(notes.values()), 2)
    notes["sur"] = 23
    notes["ecarts"] = ecarts
    return notes


if __name__ == "__main__":
    print(json.dumps(evaluer(open(sys.argv[1], encoding="utf-8").read(), sys.argv[2]), ensure_ascii=False, indent=1))
