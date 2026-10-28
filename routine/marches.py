"""Dernières clôtures des 10 actifs de la rubrique marchés, depuis Yahoo Finance (indices, change, matières
premières, Bitcoin) et CNBC (taux à 10 ans). Une séance encore ouverte est ignorée : on garde la dernière close.

python3 routine/marches.py   -> une ligne par actif : actif | clôture | variation | date de clôture | source
"""
import json
import time
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

YAHOO = [("CAC 40", "^FCHI", "pts"), ("S&P 500", "^GSPC", "pts"), ("Nasdaq Composite", "^IXIC", "pts"),
         ("Euro Stoxx 50", "^STOXX50E", "pts"), ("EUR/USD", "EURUSD=X", ""), ("Or", "GC=F", "$/once"),
         ("Brent", "BZ=F", "$/baril"), ("Bitcoin", "BTC-USD", "$")]
CNBC = [("OAT 10 ans", "FR10Y-FR"), ("Bund 10 ans", "DE10Y-DE")]


def fr(x, decimales=2, signe=False):
    s = f"{x:+,.{decimales}f}" if signe else f"{x:,.{decimales}f}"
    return s.replace(",", " ").replace(".", ",")


def lire(url):
    requete = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(requete, timeout=20))


def yahoo(nom, symbole, unite):
    r = lire(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbole}?range=15d&interval=1d")["chart"]["result"][0]
    barres = [(t, c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c is not None]
    if r["meta"]["currentTradingPeriod"]["regular"]["end"] > time.time():
        barres = barres[:-1]  # séance du jour encore ouverte
    (_, veille), (t, cloture) = barres[-2], barres[-1]
    periode = "la séance"
    if datetime.now(ZoneInfo("Europe/Paris")).weekday() >= 5:  # le week-end : variation sur la semaine
        veille, periode = next(c for tt, c in reversed(barres) if tt <= t - 6.5 * 86400), "la semaine"
    date = datetime.fromtimestamp(t, timezone.utc).strftime("%d/%m/%Y")
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
    for args in CNBC:
        try:
            print(cnbc(*args))
        except Exception as e:
            print(f"{args[0]} | non disponible ({type(e).__name__})")
