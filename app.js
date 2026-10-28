// Le Café Patrimoine : archives. Application d'une page, navigation par #/vue.
const THEMES = ["Fiscalité IR", "IS et sociétés", "Immobilier", "Gestion de portefeuille", "Transmission", "Cas pratique", "Marchés et macro"];
const JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];
const DEMO = new URLSearchParams(location.search).has("demo");
let entrees = null, erreur = false;
const filtre = {theme: "Tous", q: ""};

const $ = s => document.querySelector(s);
const echap = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const sansAccents = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const titreEdito = e => echap((e.objet.split(" : ").slice(1).join(" : ") || e.objet).trim());
const dateCourte = d => new Date(d + "T12:00:00").toLocaleDateString("fr-FR", {day: "numeric", month: "short", year: "numeric"});
const jourLong = e => echap(e.jour.charAt(0).toUpperCase() + e.jour.slice(1));
const compte = t => entrees.filter(e => e.theme === t).length;

function donneesDemo() { // aperçu de mise en page seulement, activé par ?demo
  const sujets = ["PFU ou barème : l'option pour l'imposition des dividendes", "Régime mère-fille : conditions et quote-part de frais",
    "LMNP : réintégration des amortissements dans la plus-value", "Duration et convexité d'une obligation",
    "Démembrement de propriété : le barème de l'art. 669 CGI", "Cas transversal : cession d'entreprise et donation",
    "Courbe des taux : lire une inversion"];
  const editos = ["La BCE ne bouge pas, les taux si", "Ménages au plus bas, marchés sereins", "L'OAT frôle les 5 %", "Le pétrole dicte le tempo"];
  const fin = new Date("2026-10-28T12:00:00");
  return Array.from({length: 26}, (_, i) => {
    const d = new Date(fin); d.setDate(fin.getDate() - i);
    const n = (d.getDay() + 6) % 7;
    return {date: d.toISOString().slice(0, 10), theme: THEMES[n], focus: sujets[n],
            jour: d.toLocaleDateString("fr-FR", {weekday: "long", day: "numeric", month: "long", year: "numeric"}),
            objet: `Démonstration : ${editos[i % editos.length]}`};
  });
}

function route() {
  const [vue, arg] = location.hash.replace(/^#\/?/, "").split("/");
  const actif = {fiches: "fiches", historique: "historique", "a-propos": "a-propos", n: "historique"}[vue] || "accueil";
  document.querySelectorAll(".nav a").forEach(a => a.dataset.vue === actif ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  if (entrees === null) return;
  const vues = {fiches, historique, "a-propos": aPropos, n: () => lecteur(arg)};
  $("#contenu").innerHTML = `<div class="view">${(vues[vue] || accueil)()}</div>`;
  if (vue === "fiches") majFiches();
  document.title = `${$("#contenu h1")?.textContent || "Archives"} | Le Café Patrimoine`;
  window.scrollTo(0, 0);
}

function clic(ev) {
  const el = ev.target.closest("[data-n], [data-theme], [data-chip]");
  if (!el) return;
  if (el.dataset.n) location.hash = `#/n/${el.dataset.n}`;
  else if (el.dataset.theme) { filtre.theme = el.dataset.theme; filtre.q = ""; location.hash === "#/fiches" ? route() : (location.hash = "#/fiches"); }
  else {
    filtre.theme = el.dataset.chip;
    document.querySelectorAll("[data-chip]").forEach(b => b.setAttribute("aria-pressed", b.dataset.chip === filtre.theme));
    majFiches();
  }
}

function saisie(ev) {
  if (ev.target.id !== "q") return;
  filtre.q = ev.target.value;
  majFiches();
}

async function init() {
  addEventListener("hashchange", route);
  document.addEventListener("click", clic);
  document.addEventListener("input", saisie);
  try {
    entrees = DEMO ? donneesDemo() : await (await fetch("archives/index.json", {cache: "no-store"})).json();
  } catch {
    entrees = []; erreur = true;
  }
  entrees.sort((a, b) => b.date.localeCompare(a.date));
  $("#themes-lateraux").innerHTML = "<p>Thèmes</p>" + THEMES.map(t =>
    `<button data-theme="${t}"><span>${t}</span><span class="mono">${compte(t)}</span></button>`).join("");
  route();
}

const ligne = e => `<button data-n="${e.date}"><span class="mono meta">${dateCourte(e.date)}</span>
  <strong>${echap(e.focus)}</strong><span class="meta">${e.theme}</span></button>`;
const programme = () => `<div class="theme-grid">${JOURS.map((j, i) =>
  `<button data-theme="${THEMES[i]}"><span>${j}</span><span class="meta">${THEMES[i]}</span></button>`).join("")}</div>`;

function accueil() {
  if (!entrees.length) return `<h1>${erreur ? "Archives indisponibles" : "Bienvenue"}</h1>
    <p class="lead">${erreur ? "Les archives n'ont pas pu être chargées. Réessaie dans un instant."
      : "La première édition arrive à 9 h et apparaîtra ici automatiquement, avec sa fiche Focus."}</p>
    <h2>Une fiche par jour, un thème par jour</h2>${programme()}`;
  const e = entrees[0], premier = entrees[entrees.length - 1];
  return `<h1>Dernière édition</h1><p class="lead">${jourLong(e)}</p>
    <section class="hero">
      <div class="hero-main"><span class="meta">Édito</span><h2>${titreEdito(e)}</h2>
        <div><a class="btn primary" href="#/n/${e.date}"><i class="ph ph-book-open"></i>Lire l'édition</a></div></div>
      <div class="hero-focus"><span class="tag">Focus M2 : ${e.theme}</span><strong>${echap(e.focus)}</strong>
        <p class="meta">Principe, texte de référence, exemple chiffré et piège d'examen.</p></div>
    </section>
    <div class="stats">
      <div><b>${entrees.length}</b><span class="meta">éditions archivées</span></div>
      <div><b>${THEMES.filter(t => compte(t)).length}/7</b><span class="meta">thèmes couverts</span></div>
      <div><b>${dateCourte(premier.date)}</b><span class="meta">première édition</span></div>
    </div>
    <h2>Réviser par thème</h2>
    <div class="theme-grid">${THEMES.map(t => `<button data-theme="${t}"><span>${t}</span><span class="mono">${compte(t)}</span></button>`).join("")}</div>
    <h2>Dernières fiches</h2><div class="rows">${entrees.slice(0, 6).map(ligne).join("")}</div>`;
}

function fiches() {
  return `<h1>Fiches Focus</h1>
    <p class="lead">Chaque édition contient une fiche de révision : principe, texte de référence, exemple chiffré et piège classique.</p>
    <div class="tools"><label for="q">Rechercher une notion</label>
      <input id="q" type="search" autocomplete="off" placeholder="PFU, démembrement, art. 150 VC, duration…" value="${echap(filtre.q)}">
      <div class="chips" role="group" aria-label="Filtrer par thème">${["Tous", ...THEMES].map(t =>
        `<button data-chip="${t}" aria-pressed="${filtre.theme === t}">${t}</button>`).join("")}</div></div>
    <p class="meta" id="compte" aria-live="polite"></p><div class="cards" id="cartes"></div>`;
}

function majFiches() {
  const q = sansAccents(filtre.q.trim());
  const liste = entrees.filter(e => (filtre.theme === "Tous" || e.theme === filtre.theme)
    && (!q || sansAccents(`${e.focus} ${e.objet} ${e.jour} ${e.theme}`).includes(q)));
  $("#compte").textContent = `${liste.length} fiche${liste.length > 1 ? "s" : ""}`;
  $("#cartes").innerHTML = liste.length ? liste.map(e => `<button class="card" data-n="${e.date}">
      <span class="meta"><span class="tag">${e.theme}</span> · ${dateCourte(e.date)}</span>
      <strong>${echap(e.focus)}</strong><p>${titreEdito(e)}</p></button>`).join("")
    : `<p class="empty">${entrees.length ? "Aucune fiche ne correspond. Essaie un autre mot ou un autre thème." : "Les fiches apparaîtront ici dès la première édition."}</p>`;
}

function historique() {
  if (!entrees.length) return `<h1>Historique</h1><p class="empty">L'historique commencera avec la première édition.</p>`;
  const parMois = {};
  entrees.forEach(e => (parMois[e.date.slice(0, 7)] ??= {})[e.date] = e);
  const dows = ["L", "M", "M", "J", "V", "S", "D"].map(d => `<span class="dow">${d}</span>`).join("");
  return `<h1>Historique</h1><p class="lead">Toutes les éditions, jour par jour. Chaque case colorée ouvre l'édition du jour.</p>
    <div class="months">${Object.keys(parMois).sort().reverse().map(m => {
      const [a, mo] = m.split("-").map(Number), nb = new Date(a, mo, 0).getDate();
      const vides = (new Date(a, mo - 1, 1).getDay() + 6) % 7;
      const jours = Array.from({length: nb}, (_, i) => {
        const iso = `${m}-${String(i + 1).padStart(2, "0")}`, e = parMois[m][iso];
        return e ? `<button data-n="${iso}" title="${echap(e.focus)}" aria-label="${jourLong(e)} : ${echap(e.focus)}">${i + 1}</button>` : `<span>${i + 1}</span>`;
      }).join("");
      return `<section class="month"><h2>${new Date(a, mo - 1, 1).toLocaleDateString("fr-FR", {month: "long", year: "numeric"})}</h2>
        <div class="cal">${dows}${"<span></span>".repeat(vides)}${jours}</div></section>`;
    }).join("")}</div>`;
}

function lecteur(date) {
  const i = entrees.findIndex(e => e.date === date);
  if (i < 0) return `<h1>Édition introuvable</h1><p class="empty">Cette date n'a pas d'édition. <a href="#/historique">Voir l'historique</a></p>`;
  const e = entrees[i], prec = entrees[i + 1], suiv = entrees[i - 1];
  return `<div class="reader-bar"><a class="btn" href="#/historique"><i class="ph ph-arrow-left"></i>Historique</a>
      <div class="group">${prec ? `<a class="btn" href="#/n/${prec.date}"><i class="ph ph-caret-left"></i>Précédente</a>` : ""}
        ${suiv ? `<a class="btn" href="#/n/${suiv.date}">Suivante<i class="ph ph-caret-right"></i></a>` : ""}
        <a class="btn" href="archives/${e.date}.html" target="_blank" rel="noopener"><i class="ph ph-arrow-square-out"></i>Ouvrir seule</a></div></div>
    <h1>${titreEdito(e)}</h1><p class="lead">${jourLong(e)}. Focus : ${echap(e.focus)}</p>
    ${DEMO ? `<p class="empty" style="margin-top:20px">Mode démonstration : le texte de l'édition s'affiche ici.</p>`
      : `<iframe class="frame" style="margin-top:20px" src="archives/${e.date}.html" title="${titreEdito(e)}"></iframe>`}`;
}

function aPropos() {
  return `<div class="about"><h1>À propos</h1>
    <p class="lead">Le Café Patrimoine est une newsletter quotidienne pour suivre l'actualité patrimoniale et réviser le M2 Gestion de patrimoine. Elle arrive chaque matin à 9 h.</p>
    <h2>Une fiche par jour, un thème par jour</h2>${programme()}
    <h2>Comment elle est préparée</h2>
    <p>Chaque édition s'appuie sur des recherches faites le matin même et sur des sources primaires (BCE, INSEE, Légifrance, BOFiP). Les chiffres sont recoupés avant l'envoi.</p>
    <p class="meta">Contenu informatif et pédagogique. Il ne constitue ni un conseil en investissement, ni un conseil fiscal ou juridique personnalisé.</p></div>`;
}

init();
