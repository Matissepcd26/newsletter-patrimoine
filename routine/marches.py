"""Dernières clôtures des 10 actifs de la rubrique marchés, depuis Yahoo Finance (indices, change, matières
premières, Bitcoin) et CNBC (taux à 10 ans). Pour l'or et le Brent, le contrat suivi est celui que cite la presse,
comparé à lui-même. Une séance encore ouverte est ignorée : on garde la dernière close.

python3 routine/marches.py   -> une ligne par actif : actif | clôture | variation | date de clôture | source
"""
import json
import time
import urllib.request
from datetime import datetime, time as heure, timezone
from zoneinfo import ZoneInfo

YAHOO = [("CAC 40", "^FCHI", "pts"), ("S&P 500", "^GSPC", "pts"), ("Nasdaq Composite", "^IXIC", "pts"),
         ("Euro Stoxx 50", "^STOXX50E", "pts"), ("EUR/USD", "EURUSD=X", "")]
# Futures : racine Yahoo, place, mois d'échéance cotés, unité, règle de la presse (or : échéance la plus
# active ; Brent : échéance la plus proche encore cotée).
CONTRATS = [("Or", "GC", "CMX", (2, 4, 6, 8, 10, 12), "$/once", "active"),
            ("Brent", "BZ", "NYM", range(1, 13), "$/baril", "proche")]
CODES = "FGHJKMNQUVXZ"
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
CNBC = [("OAT 10 ans", "FR10Y-FR"), ("Bund 10 ans", "DE10Y-DE")]


def fr(x, decimales=2, signe=False):
    s = f"{x:+,.{decimales}f}" if signe else f"{x:,.{decimales}f}"
    return s.replace(",", " ").replace(".", ",")


def lire(url):
    requete = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(requete, timeout=20))


def graphe(symbole):
    return lire(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbole}?range=15d&interval=1d")["chart"]["result"][0]


def contrat_actif(racine, place, mois_cotes, regle):
    """Échéance suivie par la presse, comparée à elle-même (pas de saut de contrat)."""
    maintenant, candidats = datetime.now(timezone.utc), []
    for i in range(4):
        mois, annee = (maintenant.month - 1 + i) % 12 + 1, maintenant.year + (maintenant.month - 1 + i) // 12
        if mois in mois_cotes:
            symbole = f"{racine}{CODES[mois - 1]}{annee % 100:02d}.{place}"
            try:
                g = graphe(symbole)
                if g["timestamp"][-1] < time.time() - 5 * 86400:
                    continue  # échéance expirée
                volume = max(v or 0 for v in g["indicators"]["quote"][0]["volume"][-3:])
                candidats.append((volume if regle == "active" else -i, symbole, f"{MOIS[mois - 1]} {annee}"))
            except Exception:
                pass
    return max(candidats)[1:]


def seance_close(r, t, reglement_ny):
    """Vrai si la barre datée t est une séance terminée. Futures : terminée dès le règlement (heure de New York)."""
    if reglement_ny is not None:
        ny = ZoneInfo("America/New_York")
        return datetime.now(ny) >= datetime.combine(datetime.fromtimestamp(t, ny).date(), heure(reglement_ny), ny)
    periode = r["meta"]["currentTradingPeriod"]["regular"]
    return not (periode["start"] <= t and time.time() < periode["end"])


def yahoo(nom, symbole, unite, reglement_ny=None):
    r = graphe(symbole)
    barres = [(t, c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c is not None]
    if not seance_close(r, barres[-1][0], reglement_ny):
        barres = barres[:-1]  # séance encore ouverte
    (_, veille), (t, cloture) = barres[-2], barres[-1]
    periode = "la séance"
    if datetime.now(ZoneInfo("Europe/Paris")).weekday() >= 5:  # le week-end : variation sur la semaine
        veille, periode = next(c for tt, c in reversed(barres) if tt <= t - 6.5 * 86400), "la semaine"
    date = datetime.fromtimestamp(t, ZoneInfo("America/New_York") if reglement_ny else timezone.utc).strftime("%d/%m/%Y")
    if symbole == "BTC-USD":
        date += " à 24 h UTC"  # bougie quotidienne close à minuit UTC
    decimales = 4 if symbole == "EURUSD=X" else 2
    return (f"{nom} | {fr(cloture, decimales)} {unite} | {fr(100 * (cloture / veille - 1), 2, True)} % sur {periode} | clôture du {date} | "
            f"https://finance.yahoo.com/quote/{symbole.replace('^', '%5E')}/history")


def cnbc(nom, symbole):
    q = lire("https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols="
             f"{symbole}&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json")
    q = q["FormattedQuoteResult"]["FormattedQuote"][0]
    dernier, veille = float(q["last"].rstrip("%")), float(q["previous_day_closing"].rstrip("%"))
    return (f"{nom} | {fr(dernier, 3)} % | {fr(100 * (dernier - veille), 1, True)} pb | dernier cours {q['last_time'][:16]} | "
            f"https://www.cnbc.com/quotes/{symbole}")


if __name__ == "__main__":
    for args in YAHOO:
        try:
            print(yahoo(*args))
        except Exception as e:
            print(f"{args[0]} | non disponible ({type(e).__name__})")
    for nom, racine, place, mois_cotes, unite, regle in CONTRATS:
        try:
            symbole, echeance = contrat_actif(racine, place, mois_cotes, regle)
            print(yahoo(f"{nom} (contrat {echeance})", symbole, unite, reglement_ny=15))
        except Exception as e:
            print(f"{nom} | non disponible ({type(e).__name__})")
    print(yahoo("Bitcoin", "BTC-USD", "$"))
    for args in CNBC:
        try:
            print(cnbc(*args))
        except Exception as e:
            print(f"{args[0]} | non disponible ({type(e).__name__})")
