#!/usr/bin/env python3
"""Render cv/_cv.html to a PDF with headless Chromium. Stdlib only.

    python3 scripts/build_cv.py                 # → ~/Downloads/Stefano_Costa_CV.pdf
    python3 scripts/build_cv.py -o out.pdf

The PDF is written OUTSIDE the repo on purpose: check_site.py fails on any
PDF in the working tree, even a gitignored one.

The page is served over a local HTTP server rooted at the repo, because
base.css loads fonts with root-absolute URLs (/style/fonts/...) that a
file:// URL would resolve against the filesystem root.

Chromium is looked up in $CHROME, then PATH, then the Playwright cache.
To publish it, upload it to R2 under a NEW key (keys are immutable), e.g.
    python3 scripts/r2_upload.py documents ~/Downloads/Stefano_Costa_CV.pdf Stefano_Costa_CV_2026-11.pdf
"""
import argparse
import functools
import glob
import http.server
import os
import shutil
import subprocess
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "cv/_cv.html"


def find_chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        if shutil.which(name):
            return shutil.which(name)
    cands = sorted(glob.glob(os.path.expanduser(
        "~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")))
    if cands:
        return cands[-1]
    sys.exit("Chromium non trovato: installalo o imposta $CHROME")


def main():
    ap = argparse.ArgumentParser()
    downloads = os.path.expanduser("~/Downloads")
    default_dir = downloads if os.path.isdir(downloads) else os.path.expanduser("~")
    ap.add_argument("-o", "--output", default=os.path.join(default_dir, "Stefano_Costa_CV.pdf"))
    args = ap.parse_args()

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Quiet, directory=ROOT)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/{SRC}"

    out = os.path.abspath(os.path.expanduser(args.output))
    if out.startswith(ROOT + os.sep):
        sys.exit("Output dentro il repo: check_site.py bloccherebbe il commit. Usa un path esterno.")
    try:
        subprocess.run([
            find_chrome(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
            "--virtual-time-budget=5000",  # let webfonts load before printing
            f"--print-to-pdf={out}", url,
        ], check=True, capture_output=True)
    finally:
        srv.shutdown()
    print(f"PDF scritto in {out}")


if __name__ == "__main__":
    main()
