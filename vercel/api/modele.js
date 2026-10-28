// Le Coffre : modèle du mail. GET -> modèle en vigueur ; POST {cle, modele} -> enregistre après contrôle de la clé.
// Chaque version est un fichier modele/<horodatage>.json (jamais réécrit, donc jamais servi périmé) ; on garde les 20 dernières.
import { createHash } from "node:crypto";
import { put, list, del } from "@vercel/blob";

const EMPREINTE = "69fb66e50d0ebcb3350968790b452813613beddeeebb4e0e8ccb781b70da07f7"; // SHA-256 de la clé, en majuscules
const FIXES = ["L'édito", "France : épargne, fiscalité, immobilier", "Focus M2", "Sources"];
const OPTIONNELLES = ["Les marchés en un coup d'œil", "Banques centrales et macro", "Monde et sujets sensibles",
  "Le chiffre du jour", "À surveiller aujourd'hui"];
const ORDRE = ["L'édito", OPTIONNELLES[0], OPTIONNELLES[1], "France : épargne, fiscalité, immobilier", OPTIONNELLES[2], "Focus M2", OPTIONNELLES[3], OPTIONNELLES[4]];
const DEFAUT = {style: {accent: "#111113", lien: "#9a5b00", fond: "#f2f2f3", carte: "#ffffff", police: "sans", taille: 16, largeur: 680, titres: "numero",
    entete: "plein", arrondis: 12, densite: "aere", encadres: true, marches: "tableau"},
  contenu: {format: "condense", essentiel: true, bouton: true, ordre: ORDRE, masquees: [], ajouts: [], suivre: [], note: ""}};

const hex = (v, d) => /^#[0-9a-f]{6}$/i.test(v) ? v.toLowerCase() : d;
const borne = (v, a, b, d) => Number.isInteger(v) && v >= a && v <= b ? v : d;
const texte = (v, n) => String(v ?? "").replace(/[<>{}\u0000-\u001f]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);
const liste = v => Array.isArray(v) ? v : [];
const choix = (v, permis, d) => permis.includes(v) ? v : d;
const oui = (v, d) => typeof v === "boolean" ? v : d;

function valider(m) {
  const s = m?.style || {}, c = m?.contenu || {}, d = DEFAUT.style;
  const pris = [...FIXES, ...OPTIONNELLES].map(t => t.toLowerCase());
  return {
    style: {accent: hex(s.accent, d.accent), lien: hex(s.lien, d.lien), fond: hex(s.fond, d.fond), carte: hex(s.carte, d.carte),
      police: ["serif", "sans", "systeme"].includes(s.police) ? s.police : d.police, taille: borne(s.taille, 15, 18, d.taille),
      largeur: borne(s.largeur, 560, 720, d.largeur), titres: choix(s.titres, ["numero", "filet", "bandeau", "simple"], d.titres),
      entete: choix(s.entete, ["plein", "sobre"], d.entete), arrondis: borne(s.arrondis, 0, 20, d.arrondis),
      densite: choix(s.densite, ["aere", "compact"], d.densite), encadres: oui(s.encadres, d.encadres), marches: choix(s.marches, ["tableau", "liste"], d.marches)},
    contenu: {format: choix(c.format, ["condense", "standard", "complet"], "condense"), essentiel: oui(c.essentiel, true), bouton: oui(c.bouton, true),
      ordre: liste(c.ordre).length === ORDRE.length && [...c.ordre].sort().join("|") === [...ORDRE].sort().join("|") ? [...c.ordre] : ORDRE,
      masquees: OPTIONNELLES.filter(t => liste(c.masquees).includes(t)),
      ajouts: liste(c.ajouts).slice(0, 2).map(a => ({titre: texte(a?.titre, 60), consigne: texte(a?.consigne, 400), mots: borne(a?.mots, 60, 250, 120)}))
        .filter(a => a.titre && a.consigne && !pris.some(p => a.titre.toLowerCase().startsWith(p))),
      suivre: [...new Set(liste(c.suivre).map(t => texte(t, 40)).filter(Boolean))].slice(0, 8),
      note: texte(c.note, 500)},
  };
}

async function versions() {
  const {blobs} = await list({prefix: "modele/"});
  return blobs.sort((a, b) => b.pathname.localeCompare(a.pathname));
}

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "GET") {
    const [dernier] = await versions();
    const m = dernier ? await (await fetch(dernier.url)).json() : null;
    if (m?.version !== 2) return res.status(200).json({...DEFAUT, date: null}); // rien d'enregistré depuis le nouveau gabarit
    return res.status(200).json({...valider(m), date: m.date || null});
  }
  if (req.method !== "POST") return res.status(405).json({erreur: "Méthode non permise."});
  const {cle, modele} = req.body || {};
  if (createHash("sha256").update(String(cle || "").trim().toUpperCase()).digest("hex") !== EMPREINTE)
    return res.status(403).json({erreur: "Clé d'accès incorrecte."});
  const propre = {...valider(modele), version: 2, date: new Date().toISOString()};
  await put(`modele/${Date.now()}.json`, JSON.stringify(propre), {access: "public", contentType: "application/json", addRandomSuffix: false});
  const vieux = (await versions()).slice(20).map(b => b.url);
  if (vieux.length) await del(vieux);
  return res.status(200).json(propre);
}
