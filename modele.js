// Le Coffre : réglage du modèle du mail. L'aperçu reprend routine/outils.py (styles, mail) : garder les deux alignés.
const API_MODELE = "api/modele", SITE = "https://le-coffre-patrimoine.vercel.app";
const OPTIONNELLES = ["Les marchés en un coup d'œil", "Banques centrales et macro", "Monde et sujets sensibles", "Le chiffre du jour", "À surveiller aujourd'hui"];
const RUBRIQUES = ["L'édito", OPTIONNELLES[0], OPTIONNELLES[1], "France : épargne, fiscalité, immobilier", OPTIONNELLES[2], "Focus M2", OPTIONNELLES[3], OPTIONNELLES[4]];
const POLICES_MAIL = {serif: "Georgia,'Times New Roman',serif", sans: "'Helvetica Neue',Helvetica,Arial,sans-serif",
  systeme: "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif"};
const PALETTES = {Coffre: ["#111113", "#9a5b00", "#f2f2f3", "#ffffff"], Marine: ["#14213d", "#1a5fb4", "#eef1f6", "#ffffff"],
  Forêt: ["#1f4d3a", "#1f6f8b", "#eef2ec", "#ffffff"], Bordeaux: ["#6b1d2a", "#8a2a3a", "#f6f0ee", "#ffffff"], Nuit: ["#ffb547", "#7cb4ff", "#0b0b0d", "#16161a"]};
const ORIGINE = {style: {accent: "#111113", lien: "#9a5b00", fond: "#f2f2f3", carte: "#ffffff", police: "sans", taille: 16, largeur: 680, titres: "numero",
    entete: "plein", arrondis: 12, densite: "aere", encadres: true, marches: "tableau"},
  contenu: {format: "condense", essentiel: true, bouton: true, ordre: RUBRIQUES, masquees: [], ajouts: [], suivre: [], note: "",
    jours: [0, 1, 2, 3, 4, 5, 6], heure: "09:00", pause_du: "", pause_au: "", question: true}};
const EXEMPLES = {
  "L'essentiel": "<ul><li>La Fed garde ses taux, mais deux membres voulaient déjà les relever.</li><li>À Paris, le CAC 40 finit stable avant la BCE.</li><li>Focus : la duration, ou pourquoi une obligation perd quand les taux montent.</li></ul>",
  "L'édito": "<p><strong>Texte d'exemple.</strong> L'édito dit en quelques lignes ce qui compte ce matin pour l'épargne, les marchés et les révisions.</p>",
  "Les marchés en un coup d'œil": "<ul><li>CAC 40 : 7 886,96 pts ; 0,00 % ; stable avant la Fed</li><li>S&amp;P 500 : 7 743,98 pts ; +0,28 %</li><li>OAT 10 ans : 4,93 % ; +1,0 pb</li><li>Brent : 114,19 $/baril ; -0,52 %</li></ul><p>Chaque mouvement est expliqué et daté.</p>",
  "Banques centrales et macro": "<p>Décisions de la BCE et de la Fed, inflation, emploi : les chiffres viennent des sites des institutions.</p>",
  "France : épargne, fiscalité, immobilier": "<p>Livret A, PER, assurance vie, crédit immobilier, budget : chaque mesure indique son stade.</p>",
  "Monde et sujets sensibles": "<p>Les sujets disputés sont présentés avec chaque lecture et son auteur.</p>",
  "Focus M2": "<p><strong>Principe, texte de référence, exemple chiffré et piège d'examen</strong>, avec les liens Légifrance et BOFiP.</p>",
  "Le chiffre du jour": "<p><strong>3,8 %</strong> : l'inflation de la zone euro en septembre, son plus haut depuis deux ans.</p>",
  "À surveiller aujourd'hui": "<ul><li>14 h 15 : décision de la BCE, conférence de presse à 14 h 45</li></ul>",
};
let modele = null, modeleDate = null, cleSession = "";

const melange = (h, t) => "#" + [1, 3, 5].map(i => { const v = parseInt(h.slice(i, i + 2), 16); return Math.round(v + (255 - v) * t).toString(16).padStart(2, "0"); }).join("");
const luminance = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255).map(v => v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
  .reduce((s, v, i) => s + v * [.2126, .7152, .0722][i], 0);
const contraste = (a, b) => { const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p); return (x + .05) / (y + .05); };
const clair = h => { const [r, g, b] = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)); return .299 * r + .587 * g + .114 * b > 140; };
const texteMail = st => clair(st.carte) ? "#1f1f22" : "#ececec";
const sansBalises = s => s.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();

function stylesMail(st) {
  const police = `font-family:${POLICES_MAIL[st.police]};`, t = st.taille, texte = texteMail(st);
  const titre = {filet: `padding-bottom:6px;border-bottom:2px solid ${melange(st.accent, .75)};color:${st.accent};`,
    bandeau: `padding:8px 12px;border-radius:4px;background:${st.accent};color:${st.carte};`, simple: `color:${st.accent};`, numero: `color:${st.accent};`}[st.titres];
  return {h2: police + `margin:32px 0 12px;font-size:${t + 5}px;line-height:1.3;` + titre,
    p: police + `margin:0 0 14px;font-size:${t}px;line-height:1.65;color:${texte};`, ul: "margin:0 0 16px;padding-left:20px;",
    li: police + `margin:0 0 8px;font-size:${t}px;line-height:1.6;color:${texte};`, a: `color:${st.lien};text-decoration:underline;`,
    strong: `color:${clair(st.carte) ? st.accent : texte};`};
}
const habiller = (s, st) => Object.entries(stylesMail(st)).reduce((h, [tag, css]) => h.replace(new RegExp(`<${tag}(\\s[^>]*)?>`, "g"), (_, at) => `<${tag} style="${css}"${at || ""}>`), s);
const colorer = s => s.replace(/(^|[^\w,/])([+−–-]\s?\d[\d  ]*(?:,\d+)?\s?(?:%|pb))/g, (_, a, v) => `${a}<b style="color:${v[0] === "+" ? "#0f7b3e" : "#b42318"};white-space:nowrap;">${v}</b>`);

function titreMail(titre, n, st) {
  const police = `font-family:${POLICES_MAIL[st.police]};`, a = clair(st.carte) ? st.accent : "#f2f2f2";
  return st.titres === "numero" ? `<div style="${police}font-size:12px;font-weight:700;letter-spacing:2px;color:${st.lien};margin:0 0 4px;">${String(n).padStart(2, "0")}</div>
    <h2 style="${police}margin:0 0 12px;font-size:${st.taille + 6}px;line-height:1.25;color:${a};">${titre}</h2>` : habiller(`<h2>${titre}</h2>`, st);
}

function sectionMail(titre, corps, n, st) {
  const texte = texteMail(st), r = st.arrondis, police = POLICES_MAIL[st.police], ligne = clair(st.carte) ? melange(texte, .85) : "#333";
  if (titre === "L'essentiel") return `<div style="background:${melange(st.lien, .9)};border-left:4px solid ${st.lien};border-radius:${r}px;padding:16px 18px;">
    <div style="font-family:${police};font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:${clair(st.carte) ? st.accent : texte};margin-bottom:8px;">L'essentiel</div>${habiller(corps, st)}</div>`;
  let html;
  if (titre.startsWith("Les marchés") && st.marches === "tableau") {
    const rangs = [...corps.matchAll(/<li[^>]*>(.*?)<\/li>/gs)].map(([, l]) => `<tr><td style="padding:9px 10px 9px 0;border-bottom:1px solid ${ligne};font-family:${police};font-size:${st.taille - 1}px;font-weight:700;color:${texte};vertical-align:top;width:32%;">${sansBalises(l).split(" : ")[0]}</td>
      <td style="padding:9px 0;border-bottom:1px solid ${ligne};font-family:${police};font-size:${st.taille - 1}px;line-height:1.5;color:${texte};">${colorer(habiller(l.split(" : ").slice(1).join(" : ") || l, st))}</td></tr>`).join("");
    html = `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 14px;">${rangs}</table>${habiller(corps.replace(/<ul[^>]*>.*?<\/ul>/s, ""), st)}`;
  } else html = habiller(titre.startsWith("Les marchés") ? colorer(corps) : corps, st);
  let bloc = titreMail(titre, n, st) + html;
  const fort = corps.match(/<strong[^>]*>(.*?)<\/strong>/s);
  if (st.encadres && titre.startsWith("Le chiffre du jour") && fort)
    bloc = titreMail(titre, n, st) + `<div style="font-family:${police};font-size:40px;font-weight:800;line-height:1.1;color:${st.lien};margin:4px 0 10px;">${sansBalises(fort[1])}</div>` + habiller(corps.replace(fort[0], fort[1]), st);
  if (st.encadres && (titre.startsWith("Focus M2") || titre.startsWith("Le chiffre du jour")))
    bloc = `<div style="border:1px solid ${clair(st.carte) ? melange(st.accent, .8) : "#3a3a3a"};border-radius:${r}px;padding:18px 18px 4px;">${bloc}</div>`;
  return bloc;
}

function mailApercu(m) {
  const st = m.style, c = m.contenu, police = `font-family:${POLICES_MAIL[st.police]};`, texte = texteMail(st), plein = st.entete === "plein";
  const [marge, pad] = st.densite === "aere" ? [34, 28] : [22, 20];
  const [fondTete, texteTete] = plein ? [st.accent, clair(st.accent) ? "#111113" : "#ffffff"] : [st.carte, clair(st.carte) ? st.accent : texte];
  const liste = [...(c.essentiel ? ["L'essentiel"] : []), ...c.ordre.filter(t => !c.masquees.includes(t))];
  let n = 0;
  const exemple = t => t === "Focus M2" && c.question ? EXEMPLES[t] + "<p><strong>Question d'examen :</strong> pourquoi une obligation à duration longue perd-elle plus quand les taux montent ?</p>" : EXEMPLES[t];
  const rubriques = [...liste.map(t => [t, exemple(t)]), ...c.ajouts.filter(a => a.titre).map(a => [echap(a.titre), `<p>Environ ${a.mots} mots. ${echap(a.consigne || "Consigne à préciser.")}</p>`])]
    .map(([t, corps], i) => `<tr><td style="padding:${i ? marge : pad}px ${pad}px 0;">${sectionMail(t, corps, t === "L'essentiel" ? 0 : ++n, st)}</td></tr>`).join("");
  const pied = clair(st.carte) ? "#6b6b70" : "#a1a1aa";
  const question = c.question ? `<tr><td style="padding:${marge}px ${pad}px 0;"><div style="${police}font-size:${st.taille - 1}px;line-height:1.5;color:${texte};padding:14px 16px;border:1px dashed ${clair(st.carte) ? melange(texte, .7) : "#444"};border-radius:${st.arrondis}px;"><b>Question d'examen :</b> la réponse et le raisonnement sont sur le Coffre. <a href="#" style="color:${st.lien};">Voir la réponse</a></div></td></tr>` : "";
  const bouton = c.bouton ? `<tr><td style="padding:${marge}px ${pad}px 0;" align="center"><a href="#" style="display:inline-block;padding:13px 22px;border-radius:999px;background:${st.accent};color:${clair(st.accent) ? "#111113" : "#ffffff"};${police}font-size:15px;font-weight:700;text-decoration:none;">Lire l'édition complète et ses sources</a></td></tr>` : "";
  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><base target="_blank"></head><body style="margin:0;padding:0;background:${st.fond};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${st.fond};"><tr><td align="center" style="padding:20px 8px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:${st.largeur}px;background:${st.carte};border-radius:${st.arrondis}px;overflow:hidden;">
<tr><td style="padding:${pad + 4}px ${pad}px ${pad}px;background:${fondTete};${plein ? "" : `border-bottom:1px solid ${melange(texte, .85)};`}${police}">
<div style="font-size:13px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:${texteTete};"><span style="color:${plein ? "#ffb547" : st.lien};">◆</span> Le Coffre</div>
<div style="font-size:14px;color:${texteTete};opacity:.75;margin-top:6px;">Jeudi 29 octobre 2026</div>
<div style="display:inline-block;margin-top:12px;padding:6px 12px;border-radius:999px;background:${plein && !clair(st.accent) ? "rgba(255,255,255,.12)" : melange(st.lien, .88)};color:${texteTete};font-size:13px;font-weight:600;">Focus du jour : la duration d'une obligation</div></td></tr>
${rubriques}${question}${bouton}
<tr><td style="padding:${marge}px ${pad}px ${pad}px;${police}font-size:12px;line-height:1.6;color:${pied};">Cette newsletter est fournie à titre informatif et pédagogique. Elle ne constitue ni un conseil en investissement, ni un conseil fiscal ou juridique personnalisé.<br>
<a href="#" style="color:${pied};">Modifier le modèle du mail</a> · <a href="#" style="color:${pied};">Sources et vérifications</a></td></tr></table></td></tr></table></body></html>`;
}

const curseur = (nom, min, max, pas, libelle) => `<label class="champ">${libelle} <output id="v-${nom}"></output><input type="range" name="${nom}" min="${min}" max="${max}" step="${pas}"></label>`;
const segments = (nom, libelle, options) => `<div class="champ">${libelle}<div class="segments" style="grid-template-columns:repeat(${options.length},1fr)">${options.map(([v, l]) =>
  `<label><input type="radio" name="${nom}" value="${v}">${l}</label>`).join("")}</div></div>`;
const caseACocher = (nom, libelle) => `<label class="check"><input type="checkbox" name="${nom}">${libelle}</label>`;
const ligneOrdre = t => `<li data-r="${echap(t)}"><label class="check"><input type="checkbox" name="rubrique" value="${echap(t)}" ${OPTIONNELLES.includes(t) ? "" : "checked disabled"}>${t}</label>
  <span class="fleches"><button type="button" data-monter aria-label="Monter ${echap(t)}"><i class="ph ph-caret-up"></i></button><button type="button" data-descendre aria-label="Descendre ${echap(t)}"><i class="ph ph-caret-down"></i></button></span></li>`;

function vueModele() {
  return `<h1>Modèle du mail</h1><p class="lead">Règle l'apparence, la longueur et l'ordre de la newsletter. L'aperçu suit chaque réglage. Une fois enregistré, le modèle est repris par la routine dans l'heure, puis appliqué à l'édition suivante, préparée chaque matin à 7 h 25.</p>
  <div class="atelier" id="atelier"><form class="reglages" id="reglages" novalidate>
    <fieldset><legend>Envois</legend>
      <div class="champ">Jours de réception<div class="jours">${["L", "M", "M", "J", "V", "S", "D"].map((j, i) => `<label title="${JOURS[i]}"><input type="checkbox" name="jour" value="${i}">${j}</label>`).join("")}</div></div>
      ${segments("heure", "Heure de réception", [["08:00", "8 h"], ["08:30", "8 h 30"], ["09:00", "9 h"], ["09:30", "9 h 30"]])}
      <div class="champ">Pause (vacances, examens)<div class="pause"><input type="date" name="pause_du" aria-label="Début de la pause"><span>au</span><input type="date" name="pause_au" aria-label="Fin de la pause"></div></div>
      <p class="meta" id="v-envois"></p></fieldset>
    <fieldset><legend>Longueur et rubriques</legend>
      ${segments("format", "Longueur du mail", [["condense", "Condensé"], ["standard", "Standard"], ["complet", "Complet"]])}
      <p class="meta" id="v-format"></p>
      ${caseACocher("essentiel", "Bloc « L'essentiel » en tête : les trois faits à retenir")}${caseACocher("bouton", "Bouton vers l'édition complète et ses sources")}${caseACocher("question", "Question d'examen à la fin du Focus, réponse sur le Coffre")}
      <div class="champ">Rubriques : coche celles à garder, ordonne avec les flèches<ol class="ordre" id="ordre"></ol></div>
      <p class="meta">L'édito, la France et le Focus M2 restent toujours. Les sources sont sur le Coffre, plus dans le mail.</p></fieldset>
    <fieldset><legend>Couleurs</legend>
      <div class="palettes">${Object.entries(PALETTES).map(([n, c]) => `<button type="button" data-palette="${n}"><span style="background:linear-gradient(90deg, ${c[0]} 50%, ${c[1]} 50%)"></span>${n}</button>`).join("")}</div>
      <div class="couleurs">${[["accent", "En-tête"], ["lien", "Repères"], ["fond", "Fond"], ["carte", "Carte"]].map(([k, l]) => `<label><input type="color" name="${k}">${l}</label>`).join("")}</div>
      <p class="meta" id="lisibilite"></p></fieldset>
    <fieldset><legend>Mise en page</legend>
      ${segments("entete", "En-tête", [["plein", "Plein"], ["sobre", "Sobre"]])}
      ${segments("titres", "Titres de rubrique", [["numero", "Numérotés"], ["filet", "Filet"], ["bandeau", "Bandeau"], ["simple", "Simple"]])}
      ${segments("marches", "Marchés", [["tableau", "Tableau coloré"], ["liste", "Liste"]])}
      ${segments("densite", "Espacement", [["aere", "Aéré"], ["compact", "Compact"]])}
      ${caseACocher("encadres", "Focus M2 et chiffre du jour mis en valeur")}
      <label class="champ">Police<select name="police"><option value="sans">Sans moderne</option><option value="serif">Serif classique</option><option value="systeme">Police du système</option></select></label>
      ${curseur("taille", 15, 18, 1, "Taille du texte")}${curseur("largeur", 560, 720, 20, "Largeur sur ordinateur")}${curseur("arrondis", 0, 20, 2, "Arrondis")}</fieldset>
    <fieldset><legend>Rubriques ajoutées</legend>${[0, 1].map(i => `<div class="ajout"><input name="titre${i}" maxlength="60" placeholder="Titre, par exemple « Point SCPI »">
      <textarea name="consigne${i}" rows="2" maxlength="400" placeholder="Ce que la rubrique doit couvrir"></textarea>${curseur("mots" + i, 60, 250, 10, "Longueur")}</div>`).join("")}</fieldset>
    <fieldset><legend>Préférences de la rédaction</legend>
      <label class="champ">Sujets à suivre<input name="suivre" maxlength="300" placeholder="SCPI, PER, crypto, séparés par des virgules"></label>
      <label class="champ">Note pour la rédaction<textarea name="note" rows="3" maxlength="500" placeholder="Par exemple : plus d'exemples chiffrés, un ton plus direct"></textarea></label></fieldset>
    <div class="enregistrer"><label class="champ">Clé d'accès<input name="cle" type="password" autocomplete="current-password"></label>
      <div class="actions"><button class="btn primary" type="submit"><i class="ph ph-floppy-disk"></i>Enregistrer</button><button class="btn" type="button" id="origine">Modèle d'origine</button></div>
      <p class="meta" id="etat-modele" role="status"></p></div>
  </form><div class="apercu"><iframe id="apercu" title="Aperçu du mail"></iframe></div></div>`;
}

function lireForm() {
  const f = $("#reglages"), v = n => f.elements[n].value, coche = n => f.elements[n].checked, radio = n => f.querySelector(`[name=${n}]:checked`)?.value;
  modele = {style: {accent: v("accent"), lien: v("lien"), fond: v("fond"), carte: v("carte"), police: v("police"), taille: +v("taille"), largeur: +v("largeur"),
      arrondis: +v("arrondis"), titres: radio("titres"), entete: radio("entete"), marches: radio("marches"), densite: radio("densite"), encadres: coche("encadres")},
    contenu: {format: radio("format"), essentiel: coche("essentiel"), bouton: coche("bouton"), question: coche("question"), ordre: [...f.querySelectorAll("#ordre li")].map(li => li.dataset.r),
      masquees: OPTIONNELLES.filter(t => !f.querySelector(`[name=rubrique][value="${t}"]`).checked),
      ajouts: [0, 1].map(i => ({titre: v("titre" + i).trim(), consigne: v("consigne" + i).trim(), mots: +v("mots" + i)})).filter(a => a.titre),
      suivre: v("suivre").split(",").map(s => s.trim()).filter(Boolean), note: v("note").trim(),
      jours: [...f.querySelectorAll("[name=jour]:checked")].map(x => +x.value), heure: radio("heure"), pause_du: v("pause_du"), pause_au: v("pause_au")}};
}

const MOTS_FORMAT = {condense: "Environ 1 200 à 1 600 mots, 6 minutes de lecture.", standard: "Environ 1 800 à 2 100 mots, 9 minutes de lecture.",
  complet: "Environ 2 300 à 2 600 mots, 12 minutes de lecture."};

function majApercu() {
  lireForm();
  const s = modele.style, f = $("#reglages");
  $("#v-taille").textContent = `${s.taille} px`; $("#v-largeur").textContent = `${s.largeur} px`; $("#v-arrondis").textContent = `${s.arrondis} px`;
  $("#v-format").textContent = MOTS_FORMAT[modele.contenu.format];
  const c = modele.contenu, d = x => new Date(x + "T12:00:00").toLocaleDateString("fr-FR", {day: "numeric", month: "long"});
  $("#v-envois").textContent = !c.jours.length ? "Coche au moins un jour : sans jour coché, la newsletter arrive tous les jours."
    : `${c.jours.length === 7 ? "Tous les jours" : `${c.jours.length} jour${c.jours.length > 1 ? "s" : ""} par semaine`}, à ${c.heure.replace(/^0/, "").replace(":", " h ").replace(" h 00", " h")}.`
      + (c.pause_du && c.pause_au ? ` Pause du ${d(c.pause_du)} au ${d(c.pause_au)}.` : "");
  [0, 1].forEach(i => $(`#v-mots${i}`).textContent = `${f.elements["mots" + i].value} mots`);
  const mesures = [["texte", contraste(texteMail(s), s.carte)], ["repères", contraste(s.lien, s.carte)],
    ["en-tête", s.entete === "plein" ? contraste(clair(s.accent) ? "#111113" : "#ffffff", s.accent) : contraste(s.accent, s.carte)]];
  const faibles = mesures.filter(([, x]) => x < 4.5).map(([n]) => n);
  $("#lisibilite").innerHTML = `Lisibilité : ${mesures.map(([n, x]) => `${n} ${x.toFixed(1).replace(".", ",")}:1`).join(" · ")}`
    + (faibles.length ? `<br><span class="alerte">Contraste trop faible (${faibles.join(", ")}) : difficile à lire.</span>` : "");
  $("#apercu").srcdoc = mailApercu(modele);
}

function remplir() {
  const f = $("#reglages"), s = modele.style, c = modele.contenu;
  for (const k of ["accent", "lien", "fond", "carte", "police", "taille", "largeur", "arrondis"]) f.elements[k].value = s[k];
  for (const [k, v] of [["titres", s.titres], ["entete", s.entete], ["marches", s.marches], ["densite", s.densite], ["format", c.format]])
    f.querySelector(`[name=${k}][value=${v}]`).checked = true;
  for (const k of ["essentiel", "bouton", "question"]) f.elements[k].checked = c[k];
  f.elements.encadres.checked = s.encadres;
  $("#ordre").innerHTML = c.ordre.map(ligneOrdre).join("");
  f.querySelectorAll("[name=rubrique]:not(:disabled)").forEach(x => x.checked = !c.masquees.includes(x.value));
  [0, 1].forEach(i => { const a = c.ajouts[i] || {titre: "", consigne: "", mots: 120};
    f.elements["titre" + i].value = a.titre; f.elements["consigne" + i].value = a.consigne; f.elements["mots" + i].value = a.mots; });
  f.elements.suivre.value = c.suivre.join(", "); f.elements.note.value = c.note;
  f.querySelectorAll("[name=jour]").forEach(x => x.checked = c.jours.includes(+x.value));
  f.querySelector(`[name=heure][value="${c.heure}"]`).checked = true; f.elements.pause_du.value = c.pause_du; f.elements.pause_au.value = c.pause_au;
  if (!f.elements.cle.value) f.elements.cle.value = cleSession;
  majApercu();
}

const afficherEtat = (avant = "") => $("#etat-modele").textContent = avant + (modeleDate
  ? `En vigueur depuis le ${new Date(modeleDate).toLocaleString("fr-FR", {dateStyle: "long", timeStyle: "short"})}.` : "Modèle d'origine en vigueur.");

async function enregistrer(ev) {
  ev.preventDefault(); lireForm();
  const cle = $("#reglages").elements.cle.value.trim(), etat = $("#etat-modele");
  if (!cle) return void (etat.textContent = "Indique la clé d'accès pour enregistrer.");
  etat.textContent = "Enregistrement…";
  try {
    const r = await fetch(API_MODELE, {method: "POST", headers: {"content-type": "application/json"}, body: JSON.stringify({cle, modele})});
    const d = await r.json();
    if (!r.ok) return void (etat.textContent = d.erreur || "Enregistrement impossible.");
    cleSession = cle; modeleDate = d.date; modele = {style: d.style, contenu: d.contenu};
    remplir(); afficherEtat("Enregistré : repris par la routine dans l'heure. ");
  } catch { etat.textContent = "Connexion impossible. Réessaie dans un instant."; }
}

async function initModele() {
  const f = $("#reglages");
  f.addEventListener("input", majApercu);
  f.addEventListener("submit", enregistrer);
  $("#atelier").addEventListener("click", ev => {
    const p = ev.target.closest("[data-palette]"), li = ev.target.closest("#ordre li");
    if (p) { [modele.style.accent, modele.style.lien, modele.style.fond, modele.style.carte] = PALETTES[p.dataset.palette]; remplir(); }
    if (li && ev.target.closest("[data-monter]") && li.previousElementSibling) { li.previousElementSibling.before(li); majApercu(); }
    if (li && ev.target.closest("[data-descendre]") && li.nextElementSibling) { li.nextElementSibling.after(li); majApercu(); }
    if (ev.target.closest("#origine")) { modele = structuredClone(ORIGINE); remplir(); $("#etat-modele").textContent = "Modèle d'origine chargé : enregistre pour l'appliquer."; }
  });
  try {
    const d = await (await fetch(API_MODELE, {cache: "no-store"})).json();
    modele = {style: {...ORIGINE.style, ...d.style}, contenu: {...ORIGINE.contenu, ...d.contenu}}; modeleDate = d.date;
  } catch { modele = structuredClone(ORIGINE); }
  remplir(); afficherEtat();
}
