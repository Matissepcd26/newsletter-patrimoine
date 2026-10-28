// Le Coffre : réglage du modèle du mail. L'aperçu reprend routine/outils.py (styles, gabarit) : garder les deux alignés.
const API_MODELE = "api/modele";
const OPTIONNELLES = ["Les marchés en un coup d'œil", "Banques centrales et macro", "Monde et sujets sensibles", "Le chiffre du jour", "À surveiller aujourd'hui"];
const RUBRIQUES = ["L'édito", OPTIONNELLES[0], OPTIONNELLES[1], "France : épargne, fiscalité, immobilier", OPTIONNELLES[2], "Focus M2", OPTIONNELLES[3], OPTIONNELLES[4]];
const POLICES_MAIL = {serif: "Georgia,'Times New Roman',serif", sans: "'Helvetica Neue',Helvetica,Arial,sans-serif",
  systeme: "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif"};
const PALETTES = {Classique: ["#1a2b4c", "#1a5fb4", "#f4f1ea", "#ffffff"], Encre: ["#09090b", "#9a5b00", "#f4f4f5", "#ffffff"],
  Forêt: ["#1f4d3a", "#1f6f8b", "#eef2ec", "#ffffff"], Bordeaux: ["#6b1d2a", "#8a2a3a", "#f6f0ee", "#ffffff"], Nuit: ["#ffb547", "#7cb4ff", "#0b0b0d", "#16161a"]};
const ORIGINE = {style: {accent: "#1a2b4c", lien: "#1a5fb4", fond: "#f4f1ea", carte: "#ffffff", police: "serif", taille: 16, largeur: 640, titres: "filet"},
  contenu: {masquees: [], ajouts: [], suivre: [], note: ""}};
const EXEMPLES = {
  "L'édito": "<p><strong>Texte d'exemple.</strong> L'édito résume en quelques lignes ce qui compte ce matin pour l'épargne, les marchés et tes révisions.</p>",
  "Les marchés en un coup d'œil": "<ul><li>CAC 40 : 0 000,00 pts ; +0,00 % sur la séance ; clôture du jj/mm/aaaa</li><li>OAT 10 ans : 0,000 % ; +0,0 pb</li></ul><p>Chaque mouvement est expliqué et daté.</p>",
  "Banques centrales et macro": "<p>Décisions de la BCE et de la Fed, inflation, emploi : les chiffres viennent des sites des institutions.</p>",
  "France : épargne, fiscalité, immobilier": "<p>Livret A, PER, assurance vie, crédit immobilier, budget : chaque mesure indique son stade (projet, voté, en vigueur).</p>",
  "Monde et sujets sensibles": "<p>Les sujets disputés sont présentés avec chaque lecture et son auteur.</p>",
  "Focus M2": "<p><strong>Principe, texte de référence, exemple chiffré et piège d'examen</strong>, avec les liens Légifrance et BOFiP.</p>",
  "Le chiffre du jour": "<p><strong>0,0 %</strong> : un chiffre, sa source et pourquoi il compte.</p>",
  "À surveiller aujourd'hui": "<ul><li>10 h 00 : publication attendue, avec l'heure de Paris</li></ul>",
};
let modele = null, modeleDate = null, cleSession = "";

const melange = (h, t) => "#" + [1, 3, 5].map(i => { const v = parseInt(h.slice(i, i + 2), 16); return Math.round(v + (255 - v) * t).toString(16).padStart(2, "0"); }).join("");
const luminance = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255).map(v => v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
  .reduce((s, v, i) => s + v * [.2126, .7152, .0722][i], 0);
const contraste = (a, b) => { const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p); return (x + .05) / (y + .05); };
const clair = h => { const [r, g, b] = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)); return .299 * r + .587 * g + .114 * b > 140; };
const texteMail = st => clair(st.carte) ? "#2b2b2b" : "#ececec";

function stylesMail(st) {
  const police = `font-family:${POLICES_MAIL[st.police]};`, t = st.taille, texte = texteMail(st);
  const titre = {filet: `padding-bottom:6px;border-bottom:2px solid ${melange(st.accent, .75)};color:${st.accent};`,
    bandeau: `padding:8px 12px;border-radius:4px;background:${st.accent};color:${st.carte};`, simple: `color:${st.accent};`}[st.titres];
  return {h2: police + `margin:32px 0 12px;font-size:${t + 5}px;line-height:1.3;` + titre,
    p: police + `margin:0 0 14px;font-size:${t}px;line-height:1.65;color:${texte};`, ul: "margin:0 0 16px;padding-left:20px;",
    li: police + `margin:0 0 8px;font-size:${t}px;line-height:1.6;color:${texte};`, a: `color:${st.lien};text-decoration:underline;`,
    strong: `color:${clair(st.carte) ? st.accent : texte};`};
}

function mailApercu(m) {
  const st = m.style, c = m.contenu, sombre = !clair(st.carte);
  let f = RUBRIQUES.filter(t => !c.masquees.includes(t)).map(t => `<h2>${t}</h2>${EXEMPLES[t]}`).join("")
    + c.ajouts.filter(a => a.titre).map(a => `<h2>${echap(a.titre)}</h2><p>Environ ${a.mots} mots. ${echap(a.consigne || "Consigne à préciser.")}</p>`).join("")
    + `<h2>Sources</h2><ul><li><a href="#">Banque centrale européenne : décisions de politique monétaire</a></li></ul>
      <p>Cette newsletter est fournie à titre informatif et pédagogique. Elle ne constitue ni un conseil en investissement, ni un conseil fiscal ou juridique personnalisé.</p>`;
  for (const [tag, s] of Object.entries(stylesMail(st))) f = f.replace(new RegExp(`<${tag}(\\s[^>]*)?>`, "g"), (_, at) => `<${tag} style="${s}"${at || ""}>`);
  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><base target="_blank"></head><body style="margin:0;padding:0;background:${st.fond};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${st.fond};"><tr><td align="center" style="padding:24px 10px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:${st.largeur}px;background:${st.carte};border-radius:8px;">
<tr><td style="padding:28px 24px 4px;font-family:${POLICES_MAIL[st.police]};">
<div style="font-size:13px;letter-spacing:1px;text-transform:uppercase;color:${sombre ? "#ececec" : st.accent};">☕ Le Café Patrimoine</div>
<div style="font-size:14px;color:${sombre ? "#b5b5b5" : "#6b6b6b"};margin-top:4px;">Jeudi 29 octobre 2026 · Focus M2 du jour : le démembrement de propriété</div></td></tr>
<tr><td style="padding:0 24px 28px;">${f}</td></tr></table></td></tr></table></body></html>`;
}

const curseur = (nom, min, max, pas, libelle) => `<label class="champ">${libelle} <output id="v-${nom}"></output><input type="range" name="${nom}" min="${min}" max="${max}" step="${pas}"></label>`;

function vueModele() {
  return `<h1>Modèle du mail</h1><p class="lead">Règle l'apparence et le contenu de la newsletter. L'aperçu suit chaque réglage ; l'enregistrement s'applique dès la prochaine édition, préparée à 7 h 25.</p>
  <div class="atelier" id="atelier"><form class="reglages" id="reglages" novalidate>
    <fieldset><legend>Esthétique</legend>
      <div class="palettes">${Object.entries(PALETTES).map(([n, c]) => `<button type="button" data-palette="${n}"><span style="background:linear-gradient(90deg, ${c[0]} 50%, ${c[3]} 50%)"></span>${n}</button>`).join("")}</div>
      <div class="couleurs">${[["accent", "Titres"], ["lien", "Liens"], ["fond", "Fond"], ["carte", "Carte"]].map(([k, l]) => `<label><input type="color" name="${k}">${l}</label>`).join("")}</div>
      <label class="champ">Police<select name="police"><option value="serif">Serif classique</option><option value="sans">Sans moderne</option><option value="systeme">Police du système</option></select></label>
      ${curseur("taille", 15, 18, 1, "Taille du texte")}${curseur("largeur", 560, 720, 20, "Largeur")}
      <div class="champ">Titres de rubrique<div class="segments">${["filet", "bandeau", "simple"].map(v => `<label><input type="radio" name="titres" value="${v}">${v[0].toUpperCase() + v.slice(1)}</label>`).join("")}</div></div>
      <p class="meta" id="lisibilite"></p></fieldset>
    <fieldset><legend>Rubriques</legend>${[...RUBRIQUES, "Sources"].map(t => `<label class="check"><input type="checkbox" name="rubrique" value="${t}" ${OPTIONNELLES.includes(t) ? "" : "checked disabled"}>${t}</label>`).join("")}
      <p class="meta">L'édito, la France, le Focus M2 et les Sources restent toujours.</p></fieldset>
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
  const f = $("#reglages"), v = n => f.elements[n].value;
  modele = {style: {accent: v("accent"), lien: v("lien"), fond: v("fond"), carte: v("carte"), police: v("police"), taille: +v("taille"), largeur: +v("largeur"),
      titres: f.querySelector("[name=titres]:checked")?.value || "filet"},
    contenu: {masquees: OPTIONNELLES.filter(t => !f.querySelector(`[name=rubrique][value="${t}"]`).checked),
      ajouts: [0, 1].map(i => ({titre: v("titre" + i).trim(), consigne: v("consigne" + i).trim(), mots: +v("mots" + i)})).filter(a => a.titre),
      suivre: v("suivre").split(",").map(s => s.trim()).filter(Boolean), note: v("note").trim()}};
}

function majApercu() {
  lireForm();
  const s = modele.style, f = $("#reglages");
  $("#v-taille").textContent = `${s.taille} px`; $("#v-largeur").textContent = `${s.largeur} px`;
  [0, 1].forEach(i => $(`#v-mots${i}`).textContent = `${f.elements["mots" + i].value} mots`);
  const mesures = [["texte", contraste(texteMail(s), s.carte)], ["liens", contraste(s.lien, s.carte)],
    ["titres", s.titres === "bandeau" ? contraste(s.carte, s.accent) : contraste(s.accent, s.carte)]];
  const faibles = mesures.filter(([, x]) => x < 4.5).map(([n]) => n);
  $("#lisibilite").innerHTML = `Lisibilité : ${mesures.map(([n, x]) => `${n} ${x.toFixed(1).replace(".", ",")}:1`).join(" · ")}`
    + (faibles.length ? `<br><span class="alerte">Contraste trop faible pour les ${faibles.join(" et les ")} : ils seront difficiles à lire.</span>` : "");
  $("#apercu").srcdoc = mailApercu(modele);
}

function remplir() {
  const f = $("#reglages"), s = modele.style, c = modele.contenu;
  for (const k of ["accent", "lien", "fond", "carte", "police", "taille", "largeur"]) f.elements[k].value = s[k];
  f.querySelector(`[name=titres][value=${s.titres}]`).checked = true;
  f.querySelectorAll("[name=rubrique]:not(:disabled)").forEach(x => x.checked = !c.masquees.includes(x.value));
  [0, 1].forEach(i => { const a = c.ajouts[i] || {titre: "", consigne: "", mots: 120};
    f.elements["titre" + i].value = a.titre; f.elements["consigne" + i].value = a.consigne; f.elements["mots" + i].value = a.mots; });
  f.elements.suivre.value = c.suivre.join(", "); f.elements.note.value = c.note;
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
    remplir(); afficherEtat("Enregistré. Appliqué dès la prochaine édition. ");
  } catch { etat.textContent = "Connexion impossible. Réessaie dans un instant."; }
}

async function initModele() {
  const f = $("#reglages");
  f.addEventListener("input", majApercu);
  f.addEventListener("submit", enregistrer);
  $("#atelier").addEventListener("click", ev => {
    const p = ev.target.closest("[data-palette]");
    if (p) { [modele.style.accent, modele.style.lien, modele.style.fond, modele.style.carte] = PALETTES[p.dataset.palette]; remplir(); }
    if (ev.target.closest("#origine")) { modele = structuredClone(ORIGINE); remplir(); $("#etat-modele").textContent = "Modèle d'origine chargé : enregistre pour l'appliquer."; }
  });
  try {
    const d = await (await fetch(API_MODELE, {cache: "no-store"})).json();
    modele = {style: d.style, contenu: d.contenu}; modeleDate = d.date;
  } catch { modele = structuredClone(ORIGINE); }
  remplir(); afficherEtat();
}
