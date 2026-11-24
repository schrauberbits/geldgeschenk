#!/usr/bin/env python3
"""Baut den Geldgeschenk-Kompass: index.html (Rechner), Antwortseiten, Sitemap, robots.txt, IndexNow-Schlüsseldatei.
Alle Zahlen kommen aus daten.json; die Antwortseiten und der Rechner rechnen mit denselben Regeln."""
import json, html, statistics, pathlib, shutil

HIER = pathlib.Path(__file__).parent
ZIEL = HIER.parent / "site"  # Ausgabe; danach den Inhalt von site/ ins Repository-Wurzelverzeichnis kopieren
BASIS = "https://schrauberbits.github.io/geldgeschenk/"
D = json.loads((HIER / "daten.json").read_text(encoding="utf-8"))
KEY = (HIER / "indexnow_key.txt").read_text().strip()
STAND = D["stand"]
GC = '<script data-goatcounter="https://schrauberbits.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'
e = lambda s: html.escape(str(s), quote=True)

PLURAL={"eltern":"Eltern","grosseltern":"Großeltern","pate":"Paten","geschwister":"Geschwister","tante":"Tanten, Onkel und andere Verwandte","trauzeuge":"Trauzeugen","engefreunde":"Enge Freunde","freunde":"Freunde","kollegen":"Kollegen","bekannte":"Bekannte und Nachbarn"}

def r5(x):
    return int(5 * round(x / 5.0))

def auswerten(liste):
    """Kern = Mitte (Median) der geschlossenen Spannen; Spanne = kleinster bis größter genannter Wert."""
    zu = [(lo, hi) for _, lo, hi, _ in liste if lo is not None and hi is not None]
    los = [lo for _, lo, _, _ in liste if lo is not None]
    his = [hi for _, _, hi, _ in liste if hi is not None]
    offen = [lo for _, lo, hi, _ in liste if lo is not None and hi is None]
    k = None
    if zu:
        k = (r5(statistics.median([a for a, _ in zu])), r5(statistics.median([b for _, b in zu])))
    elif offen:
        k = (min(offen), None)
    sp = (min(los) if los else None, max(his) if his else None, max(offen) if offen else None)
    return {"kern": k, "spanne": sp, "n": len(liste)}

def eur(x):
    return f"{x:,}".replace(",", ".") + " €"

def kerntext(k):
    if not k: return "–"
    lo, hi = k
    return f"ab {eur(lo)}" if hi is None else f"{lo}–{eur(hi)}"

def spannetext(sp):
    lo, hi, offen = sp
    teile = []
    if lo is not None and hi is not None: teile.append(f"{lo}–{eur(hi)}")
    elif hi is not None: teile.append(f"bis {eur(hi)}")
    elif lo is not None: teile.append(f"ab {eur(lo)}")
    if offen is not None and (hi is None or offen >= hi): teile.append(f"einzelne Quellen: „{offen} € und mehr“")
    elif offen is not None: teile.append(f"eine Quelle: „ab {offen} €“")
    return "; ".join(teile)

# ---------- Antwortseiten (statisch, ohne JavaScript lesbar) ----------
SEITEN = [
  ("taufe-pate", "taufe", "pate", "Wie viel Geld schenkt man als Pate zur Taufe?", "Pate zur Taufe"),
  ("taufe", "taufe", None, "Wie viel Geld schenkt man zur Taufe?", "Taufe"),
  ("konfirmation-pate", "konfirmation", "pate", "Wie viel Geld schenkt man seinem Patenkind zur Konfirmation?", "Patenkind zur Konfirmation"),
  ("konfirmation", "konfirmation", None, "Wie viel Geld schenkt man zur Konfirmation?", "Konfirmation"),
  ("kommunion", "kommunion", "pate", "Wie viel Geld schenkt man zur Kommunion?", "Kommunion"),
  ("firmung", "firmung", None, "Wie viel Geld schenkt man zur Firmung?", "Firmung"),
  ("jugendweihe", "jugendweihe", None, "Wie viel Geld schenkt man zur Jugendweihe?", "Jugendweihe"),
  ("einschulung", "einschulung", "eltern", "Wie viel Geld zur Einschulung ist angemessen?", "Einschulung"),
  ("abitur", "abitur", None, "Wie viel Geld schenkt man zum Abitur?", "Abitur"),
  ("hochzeit", "hochzeit", "freunde", "Wie viel Geld schenkt man zur Hochzeit?", "Hochzeit"),
  ("hochzeit-kollegen", "hochzeit", "kollegen", "Wie viel Geld schenkt man Kollegen oder dem Chef zur Hochzeit?", "Hochzeit unter Kollegen"),
  ("18-geburtstag", "geburtstag18", "freunde", "Wie viel Geld schenkt man zum 18. Geburtstag?", "18. Geburtstag"),
  ("weihnachten", "weihnachten", None, "Wie viel Geld schenkt man zu Weihnachten?", "Weihnachten"),
  ("gemeinsam-schenken", None, None, "Gemeinsam Geld schenken: Wie viel zahlt jeder?", "Gemeinsam schenken"),
]

CSS = """:root{--bg:#f6f3ee;--card:#fff;--ink:#1d1a16;--muted:#655e55;--line:#e0d9ce;--soft:#efe9df;--accent:#8c2f4b;--accent-ink:#fff;--accent-soft:#f6e3e8;--ok:#2d6e3a;--ok-soft:#e3f0e4;--warn:#8a5a00;--warn-soft:#fbefd9}
@media (prefers-color-scheme:dark){:root{--bg:#15130f;--card:#201d18;--ink:#eee9e1;--muted:#ada59a;--line:#38332c;--soft:#2a2620;--accent:#f0a3b8;--accent-ink:#2b0d16;--accent-soft:#3a1f27;--ok:#86c98f;--ok-soft:#1d321f;--warn:#e8b15d;--warn-soft:#382c17}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:600px;margin:0 auto;padding:18px 16px 60px}
a{color:var(--accent)}
h1{font-size:1.55rem;line-height:1.2;margin:0 0 8px}h2{font-size:1.2rem;margin:26px 0 10px}
.sub{color:var(--muted);margin:0 0 16px}
.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.brand{font-weight:700;text-decoration:none;color:var(--ink)}
.antwort{background:var(--accent-soft);border-radius:16px;padding:16px;margin:12px 0}
.antwort b.gross{display:block;font-size:1.35rem;line-height:1.3;color:var(--accent);margin:2px 0 6px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;font-size:.93rem}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--soft);font-size:.82rem;color:var(--muted)}
td.z{white-space:nowrap;font-weight:700}
.hint{font-size:.86rem;color:var(--muted)}
.btn{display:inline-block;background:var(--accent);color:var(--accent-ink);text-decoration:none;border-radius:12px;padding:12px 16px;font-weight:600;margin:6px 0}
ul.q{padding-left:20px;font-size:.88rem;color:var(--muted)}ul.q li{margin:4px 0}
.links{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}.links a{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:6px 12px;text-decoration:none;font-size:.88rem}
footer{margin-top:30px;font-size:.8rem;color:var(--muted);text-align:center;line-height:1.5}"""

FUSS = f"""<footer>Orientierung, keine Pflicht und keine Finanzberatung. Stand {STAND}; Beträge aus den genannten Ratgebern, ohne Gewähr.<br>Kostenlos, ohne Anmeldung, ohne Werbung – ein Hobbyprojekt, mit KI-Hilfe erstellt. Gezählt wird nur anonym und ohne Cookies (mit GoatCounter): wie oft Seiten aufgerufen und benutzt werden und über welchen Link – ohne persönliche Daten und ohne deine Eingaben.<br>Mehr Helfer: <a href="https://schrauberbits.github.io/festessen-helfer/">Festessen-Helfer</a> · <a href="https://schrauberbits.github.io/paket-helfer/">Paket-Helfer</a> · <a href="https://schrauberbits.github.io/feiertags-helfer/">Feiertags-Helfer</a></footer>"""

def quellenliste(anlass):
    ids = []
    for liste in D["anlaesse"][anlass]["werte"].values():
        for q, *_ in liste:
            if q not in ids: ids.append(q)
    return ids

def tabelle(anlass, hervor=None):
    A = D["anlaesse"][anlass]
    zeilen = []
    for rid, label in D["rollen"].items():
        if rid not in A["werte"]: continue
        a = auswerten(A["werte"][rid])
        st = ' style="background:var(--accent-soft)"' if rid == hervor else ""
        zeilen.append(f'<tr{st}><td>{e(label)}</td><td class="z">{kerntext(a["kern"])}</td><td>{e(spannetext(a["spanne"]))}<br><span class="hint">{a["n"]} {"Quelle" if a["n"]==1 else "Quellen"}</span></td></tr>')
    je = " je Person" if A.get("jePerson") else ""
    return f'<table><thead><tr><th>Wer schenkt?</th><th>Mitte der Quellen{je}</th><th>Spanne laut Ratgebern</th></tr></thead><tbody>{"".join(zeilen)}</tbody></table>'

def quellen_html(ids, extra=()):
    li = []
    for q in list(ids) + list(extra):
        Q = D["quellen"][q]
        li.append(f'<li><a href="{e(Q["url"])}" rel="noopener">{e(Q["name"])}</a> (Stand {e(Q["stand"])})</li>')
    return f'<ul class="q">{"".join(li)}</ul>'

def detail_quellen(anlass, rid):
    li = []
    for q, lo, hi, notiz in D["anlaesse"][anlass]["werte"][rid]:
        Q = D["quellen"][q]
        wert = f"{lo}–{hi} €" if lo is not None and hi is not None else (f"ab {lo} €" if lo is not None else f"bis {hi} €")
        li.append(f'<li><b>{wert}</b> – {e(Q["name"].split(":")[0])}{" (" + e(notiz) + ")" if notiz else ""}, Stand {e(Q["stand"])}</li>')
    return f'<ul class="q">{"".join(li)}</ul>'

def seite(slug, anlass, rid, frage, kurz):
    ref = "as-" + slug
    rechner = f"../?ref={ref}#rechner?anlass={anlass}" + (f"&naehe={rid}" if rid else "") if anlass else f"../?ref={ref}#gemeinsam"
    teile = [f'<p><a class="btn" href="{rechner}">Für deinen Fall rechnen →</a></p>']
    beschr = ""
    if anlass and D["anlaesse"][anlass]["werte"]:
        A = D["anlaesse"][anlass]
        r = rid or next(iter(k for k in ("pate", "eltern", "freunde") if k in A["werte"]))
        a = auswerten(A["werte"][r])
        label = D["rollen"][r]
        je = " je Person" if A.get("jePerson") else ""
        satz = f"{PLURAL[r]} schenken {A['zur']} meist {kerntext(a['kern'])}{je}"
        antwort = f"""<div class="antwort"><span class="hint">Kurz gesagt</span><b class="gross">{e(satz)}.</b>
        Das ist die Mitte aus {a['n']} Ratgebern; insgesamt nennen sie {e(spannetext(a['spanne']))}. Je näher man steht, desto mehr wird üblich gegeben – wer wenig Geld hat, schenkt, was möglich ist.</div>"""
        beschr = f"{satz}{'.'} Übliche Beträge {A['zur']} für Eltern, Großeltern, Paten, Verwandte, Freunde und Bekannte – mit Quellen und Rechner."
        teile.insert(0, antwort)
        teile.append(f"<h2>Übliche Beträge {e(A['zur'])}</h2>" + tabelle(anlass, r))
        if A.get("jePerson"):
            R = D["hochzeitRegel"]
            teile.append(f'<p class="hint">Hochzeit: Die Beträge gelten je Person. Faustregel der Sparkasse: mindestens etwa den Wert des eigenen Essens und der Getränke, meist {R["lo"]}–{R["hi"]} € je Person; Kinder mit vollem Menü etwa die Hälfte. Als Paar also das Doppelte.</p>')
        if A.get("ohneBetrag"): teile.append(f'<p class="hint">{e(A["ohneBetrag"])}</p>')
        teile.append(f"<h2>Was die Ratgeber für „{e(label)}“ nennen</h2>" + detail_quellen(anlass, r))
        teile.append("<h2>Quellen</h2>" + quellen_html(quellenliste(anlass)))
    elif anlass == "weihnachten":
        A = D["anlaesse"]["weihnachten"]; H = D["hde"]
        zeilen = "".join(f'<tr><td>{e(t)}</td><td class="z">{lo}–{hi} € pro {e(per)}</td></tr>' for _, t, lo, hi, per in D["taschengeld"])
        teile.insert(0, f"""<div class="antwort"><span class="hint">Kurz gesagt</span><b class="gross">Für Weihnachten gibt es keinen üblichen Betrag je Verwandtschaft.</b>{e(A['ohneBetrag'])} Für Kinder hilft das empfohlene Taschengeld als Bezugsgröße, für alle Geschenke zusammen der Durchschnitt: {H['budget']} € planen die Befragten {H['jahr']} im Schnitt für Weihnachtsgeschenke ein ({H['unter100']} % weniger als 100 €).</div>""")
        teile.append(f'<h2>Bezugsgröße für Kinder: empfohlenes Taschengeld (DJI)</h2><table><thead><tr><th>Alter</th><th>Taschengeld</th></tr></thead><tbody>{zeilen}</tbody></table><p class="hint">Das ist kein Richtwert für Geschenke, sondern was Kinder laut Deutschem Jugendinstitut regelmäßig von den Eltern bekommen sollten – eine Hilfe, um einen Betrag einzuordnen. Ein Ratgeber der Stuttgarter Zeitung empfiehlt dieselbe Bezugsgröße für Geldgeschenke zu Ostern.</p>')
        teile.append(f'<p><a class="btn" href="../?ref={ref}#budget">Weihnachtsbudget auf alle verteilen →</a></p>')
        teile.append("<h2>Quellen</h2>" + quellen_html(["spk", "dji", "hde", "sz_geburtstag"]))
        beschr = f"Für Weihnachten gibt es keinen üblichen Betrag je Verwandtschaft. Bezugsgröße für Kinder: Taschengeld nach Alter (DJI). Im Schnitt {H['budget']} € für alle Geschenke. Mit Budget-Verteiler."
    else:
        teile.insert(0, """<div class="antwort"><span class="hint">Kurz gesagt</span><b class="gross">Gesamtbetrag durch die Zahl der Schenkenden – auf ganze Euro aufgerundet.</b>Beispiel: 150 € für ein gemeinsames Geschenk zu dritt = 50 € je Person. Wer für die Gruppe sammelt, schickt den Link mit Betrag und Liste an alle.</div>""")
        teile.append('<p class="hint">Gut zu wissen: Bei einer Hochzeit rechnen Ratgeber die Beträge je Person, bei Taufe, Konfirmation und anderen Feiern je Geschenk. Wie viel für das gemeinsame Geschenk üblich ist, zeigt die <a href="../">Übersicht</a>.</p>')
        beschr = "Gemeinsam Geld schenken: Gesamtbetrag aufteilen, Betrag je Person, Link mit Liste an alle, die mitschenken."
    andere = "".join(f'<a href="../{s}/">{e(k)}</a>' for s, _, _, _, k in SEITEN if s != slug)
    return f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(frage)} – Geldgeschenk-Kompass</title>
<meta name="description" content="{e(beschr)}">
<link rel="canonical" href="{BASIS}{slug}/">
<style>{CSS}</style>{GC}</head>
<body><div class="wrap"><div class="top"><a class="brand" href="../">💌 Geldgeschenk-Kompass</a></div>
<h1>{e(frage)}</h1>
{''.join(teile)}
<h2>Weitere Anlässe</h2><div class="links">{andere}</div>
{FUSS}</div></body></html>"""

# ---------- Startseite mit Rechner ----------
def uebersicht():
    zeilen = []
    for aid, A in D["anlaesse"].items():
        if not A["werte"]: continue
        zellen = []
        for rid in ("eltern", "grosseltern", "pate", "freunde", "bekannte"):
            zellen.append(f'<td class="z">{kerntext(auswerten(A["werte"][rid])["kern"]) if rid in A["werte"] else "–"}</td>')
        slug = next((s for s, a, *_ in SEITEN if a == aid), None)
        name = f'<a href="{slug}/">{e(A["name"])}</a>' if slug else e(A["name"])
        je = "<br><span class=\"hint\">je Person</span>" if A.get("jePerson") else ""
        zeilen.append(f"<tr><td>{name}{je}</td>{''.join(zellen)}</tr>")
    return f'<table class="uebersicht"><thead><tr><th>Anlass</th><th>Eltern</th><th>Großeltern</th><th>Pate</th><th>Freunde</th><th>Bekannte</th></tr></thead><tbody>{"".join(zeilen)}</tbody></table><p class="hint">Mitte der genannten Ratgeber, Stand {STAND}. Weihnachten: <a href="weihnachten/">kein üblicher Betrag, aber Bezugsgrößen</a>.</p>'

def schnell():
    t = D["anlaesse"]; out = []
    for aid, rid, txt in (("taufe", "pate", "Pate zur Taufe"), ("konfirmation", "pate", "Pate zur Konfirmation"), ("einschulung", "eltern", "Eltern zur Einschulung"), ("hochzeit", "freunde", "Freunde zur Hochzeit, je Person")):
        out.append(f"<li><b>{kerntext(auswerten(t[aid]['werte'][rid])['kern'])}</b> {e(txt)}</li>")
    return "".join(out)

def daten_js():
    A = {}
    for aid, X in D["anlaesse"].items():
        A[aid] = {"name": X["name"], "zur": X["zur"], "saison": X["saison"], "jePerson": bool(X.get("jePerson")), "ohneBetrag": X.get("ohneBetrag", ""),
                  "werte": {rid: {"a": auswerten(l), "q": l} for rid, l in X["werte"].items()}}
    return json.dumps({"stand": STAND, "rollen": D["rollen"], "quellen": D["quellen"], "anlaesse": A, "taschengeld": D["taschengeld"], "hde": D["hde"], "hochzeitRegel": D["hochzeitRegel"]}, ensure_ascii=False)

def main():
    if ZIEL.exists(): shutil.rmtree(ZIEL)
    ZIEL.mkdir()
    vorlage = (HIER / "index.vorlage.html").read_text(encoding="utf-8")
    idx = (vorlage.replace("{{CSS}}", CSS).replace("{{GC}}", GC).replace("{{FUSS}}", FUSS)
           .replace("{{UEBERSICHT}}", uebersicht()).replace("{{SCHNELL}}", schnell())
           .replace("{{DATEN}}", daten_js()).replace("{{STAND}}", STAND)
           .replace("{{LINKS}}", "".join(f'<a href="{s}/">{e(k)}</a>' for s, _, _, _, k in SEITEN)))
    (ZIEL / "index.html").write_text(idx, encoding="utf-8")
    for s in SEITEN:
        (ZIEL / s[0]).mkdir()
        (ZIEL / s[0] / "index.html").write_text(seite(*s), encoding="utf-8")
    urls = [BASIS] + [f"{BASIS}{s[0]}/" for s in SEITEN]
    (ZIEL / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>2026-11-24</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ZIEL / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASIS}sitemap.xml\n", encoding="utf-8")
    (ZIEL / f"{KEY}.txt").write_text(KEY, encoding="utf-8")
    (ZIEL / "README.md").write_text("# geldgeschenk\nGeldgeschenk-Kompass: Wie viel Geld ist üblich zu Taufe, Kommunion, Konfirmation, Firmung, Jugendweihe, Einschulung, Abitur, Hochzeit, 18. Geburtstag und Weihnachten – nach Nähe und eigener Lage, mit Quellen. Dazu: gemeinsames Geschenk aufteilen und Weihnachtsbudget verteilen. Kostenlos, ohne Anmeldung, ohne Werbung, mit KI-Hilfe erstellt.\n\nDie Datei `" + KEY + ".txt` ist der öffentliche IndexNow-Nachweis für Suchmaschinen, kein Zugangsschlüssel.\n", encoding="utf-8")
    (ZIEL / ".nojekyll").write_text("", encoding="utf-8")
    print("gebaut:", len(SEITEN), "Antwortseiten;", "Schlüsseldatei", KEY)

if __name__ == "__main__":
    main()
