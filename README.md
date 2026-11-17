# Avarthana Website - complete project

Latest published website snapshot: 17 November 2026.
Source commit: abbe10c6611059489aba693608ac1d0960f55bac

## Run on Windows

1. Extract the entire ZIP first.
2. Install Python 3 if it is not already installed.
3. Double-click START_WEBSITE.bat.
4. Open http://localhost:8000 in your browser.
5. Keep the terminal window open; press Ctrl+C to stop.

## Run on macOS or Linux

Open a terminal in this folder and run:

    python3 -m http.server 8000 --directory dist

Then open http://localhost:8000.
Use a local server instead of opening index.html directly: product search loads JSON files.

## Edit and rebuild

- products.json: product data, specifications, filenames and download metadata.
- build.py: generates the HTML pages; run `python build.py` after editing content.
- restyle.py, refine.py, homepage_update.py, status_update.py, cohesion.py,
  interaction_theme.py: shared page and design generation stages called by build.py.
- dist/assets/: editable CSS, browser JavaScript, fonts and images.
- dist/assets/interaction-theme.css: latest button, focus, form and selection styling.
- dist/downloads/: product datasheets, separate block diagrams, ZIP packages and catalogue.

The normal build uses only the Python standard library. All final assets and downloads
are already included. There are 21 product pages, 21 datasheets and 20 block diagrams;
the radar support structure has no supplied block diagram.

Optional content-import helpers use Pillow and PyMuPDF. Install these with:

    python -m pip install -r requirements-optional.txt

These helpers are not required to run or rebuild the website. prepare_content.py is a
legacy initial importer that requires the original brochure PDF and resets product data;
do not run it for routine website updates. prepare_downloads.py is also a legacy helper
and can regenerate the earlier documentation. import_documents.py imports the updated
letterhead ZIP when explicitly supplied. Original import inputs are not required by the
normal build because the final product data and document files are included.

## Publish

Upload the CONTENTS of dist/ to any static website host. The project uses root-relative
URLs, so host it at the domain root. Subdirectory hosting needs URL/base-path changes.
.openai/hosting.json records the existing Sites project identity and static directory.
The original .git history, access tokens and runtime caches are intentionally excluded.

## Content notes

The enquiry form prepares an email in the visitor's email application; it does not run
an email delivery backend. Notifications describe download requests and email drafts,
not confirmed delivery. Product diagrams and datasheets remain downloadable only.
Original AI engineering illustrations are identified on the image-credits page.
Imported Rev 03 specifications are configurable design targets, and conceptual processor
diagrams are marked. See each product document for configuration details.

## Snapshot contents

This package includes source generators, ready-to-serve static pages, styles, scripts,
images, fonts, product data, and all currently linked PDF/PNG/ZIP downloads.
