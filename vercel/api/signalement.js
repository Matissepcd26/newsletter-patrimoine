// Le Coffre : signalements d'erreur. GET -> les 50 derniers ; POST {cle, signalement} -> enregistre après contrôle de la clé.
// La routine les vérifie chaque matin (copie horaire dans config/signalements.json) et publie un rectificatif si l'erreur est confirmée.
import { createHash } from "node:crypto";
import { put, list } from "@vercel/blob";

const EMPREINTE = "69fb66e50d0ebcb3350968790b452813613beddeeebb4e0e8ccb781b70da07f7"; // SHA-256 de la clé, en majuscules
const texte = (v, n) => String(v ?? "").replace(/[<>{}\u0000-\u001f]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "GET") {
    const {blobs} = await list({prefix: "signalements/"});
    const recents = blobs.sort((a, b) => b.pathname.localeCompare(a.pathname)).slice(0, 50);
    return res.status(200).json(await Promise.all(recents.map(async b => (await fetch(b.url)).json())));
  }
  if (req.method !== "POST") return res.status(405).json({erreur: "Méthode non permise."});
  const {cle, signalement: s} = req.body || {};
  if (createHash("sha256").update(String(cle || "").trim().toUpperCase()).digest("hex") !== EMPREINTE)
    return res.status(403).json({erreur: "Clé d'accès incorrecte."});
  const propre = {id: String(Date.now()), date: /^\d{4}-\d{2}-\d{2}$/.test(s?.date) ? s.date : "", rubrique: texte(s?.rubrique, 80),
    texte: texte(s?.texte, 600), source: /^https?:\/\/\S+$/.test(s?.source || "") ? String(s.source).slice(0, 300) : "", recu: new Date().toISOString()};
  if (!propre.date || propre.texte.length < 10) return res.status(400).json({erreur: "Choisis l'édition et décris l'erreur en une phrase au moins."});
  await put(`signalements/${propre.id}.json`, JSON.stringify(propre), {access: "public", contentType: "application/json", addRandomSuffix: false});
  return res.status(200).json(propre);
}
