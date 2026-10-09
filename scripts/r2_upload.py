#!/usr/bin/env python3
"""
Carica file nei bucket R2 e aggiorna r2-manifest.json (stdlib only, ma
richiede la CLI `wrangler` autenticata: `wrangler login` una tantum).

I bucket vivono SOLO su R2, mai nel repo: .gitignore + check_site.py
rifiutano PDF/audio committati per sbaglio.

Uso:
  python3 scripts/r2_upload.py documents <file-locale> [chiave]
  python3 scripts/r2_upload.py audio <file-locale> [chiave]
  python3 scripts/r2_upload.py --migrate-document
      carica tutto ciò che è in document/ preservando i sotto-path
      (document/poster/X.pdf -> chiave poster/X.pdf), per la migrazione
      una tantum. Dopo la verifica, document/ si rimuove dal repo.

Regole (vedi CLAUDE.md "File pesanti e R2"):
- la chiave (nome nello bucket) è IMMUTABILE: mai sovrascrivere una chiave
  esistente con contenuto diverso (la cache edge è immutable a un anno).
  Nuova versione = nuovo nome. Lo script rifiuta le chiavi già nel manifest,
  salvo --force (migrazione/ricarichi identici).
- se la chiave non è data, si usa il basename del file.
"""
import mimetypes
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "r2-manifest.json")

BUCKETS = {
    "documents": "stefanocosta-documents",
    "audio": "stefanocosta-audio",
}

# mimetypesstdlib non conosce tutti i tipi audio: fallback espliciti.
CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".opus": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
}


def content_type(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in CONTENT_TYPES:
        return CONTENT_TYPES[ext]
    guessed, _ = mimetypes.guess_type(path)
    return guessed or "application/octet-stream"


def load_manifest():
    import json
    with open(MANIFEST, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("documents", [])
    data.setdefault("audio", [])
    return data


def save_manifest(data):
    import json
    data["documents"] = sorted(set(data["documents"]))
    data["audio"] = sorted(set(data["audio"]))
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def upload(kind, local_path, key, force=False):
    import json
    bucket = BUCKETS[kind]
    if not os.path.isfile(local_path):
        sys.exit(f"file inesistente: {local_path}")
    manifest = load_manifest()
    if key in manifest[kind] and not force:
        sys.exit(f"ERRORE: la chiave {kind}/{key} esiste già nel manifest — "
                 "le chiavi sono immutabili, usa un nuovo nome "
                 "(vedi CLAUDE.md 'File pesanti e R2').")
    # --remote è obbligatorio: senza, wrangler v4 scrive nello storage LOCALE
    # (~/.wrangler) fingendo successo, e il bucket remoto resta vuoto.
    cmd = ["wrangler", "r2", "object", "put", f"{bucket}/{key}",
           f"--file={local_path}",
           f"--content-type={content_type(local_path)}",
           "--remote"]
    print("+ " + " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, cwd=ROOT)
    except FileNotFoundError:
        sys.exit("ERRORE: `wrangler` non trovato. Installa con `npm i -g wrangler` e poi `wrangler login`.")
    except subprocess.CalledProcessError:
        sys.exit("ERRORE: upload fallito (wrangler non loggato? `wrangler login`).")
    manifest[kind].append(key)
    save_manifest(manifest)
    size = os.path.getsize(local_path)
    print(f"ok: {kind}/{key} ({size // 1024}KB) — manifest aggiornato.")
    print("URL pubblico: https://stefanocosta.me/"
          f"{'document' if kind == 'documents' else 'audio'}/{key}")


def migrate_document():
    docdir = os.path.join(ROOT, "document")
    if not os.path.isdir(docdir):
        sys.exit("niente da migrare: document/ non esiste più nel repo.")
    files = []
    for dirpath, _, filenames in os.walk(docdir):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            key = os.path.relpath(full, docdir).replace(os.sep, "/")
            files.append((full, key))
    files.sort(key=lambda t: t[1])
    print(f"{len(files)} file da caricare nel bucket documents.")
    for full, key in files:
        # force: la migrazione riconcilia disco -> bucket nuovo; ricaricare
        # lo stesso contenuto sotto la stessa chiave è innocuo (il divieto
        # di sovrascrittura vale per contenuti DIVERSI sotto la stessa chiave).
        upload("documents", full, key, force=True)


def main():
    args = sys.argv[1:]
    if args == ["--migrate-document"]:
        migrate_document()
        return
    force = "--force" in args
    args = [a for a in args if a != "--force"]
    if len(args) not in (2, 3) or args[0] not in BUCKETS:
        sys.exit("uso: r2_upload.py [--force] (documents|audio) <file> [chiave]  "
                 "oppure  r2_upload.py --migrate-document")
    kind, local = args[0], args[1]
    key = args[2] if len(args) == 3 else os.path.basename(local)
    upload(kind, local, key, force=force)


if __name__ == "__main__":
    main()
