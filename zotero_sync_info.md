# Zotero → extraction sync

[Python script](zotero_sync.py) pulls **item keys** and **notes** from your Zotero library into extraction Excel files.

## Why not `.bib`?

| Export | Contains |
|--------|----------|
| **`.bib`** (standard) | Bibliographic metadata; citation key only with [Better BibTeX](https://retorque.re/zotero-better-bibtex/) |
| **`.bib`** | Does **not** include Zotero notes or item keys (unless custom BBT fields) |
| **`zotero_sync.py`** | `Zotero_key` + `Notes` via Zotero API, matched by DOI (fallback: title) |

Use **`.bib`** for `review.qmd` citations (`references.bib`).  
Use **`zotero_sync.py`** for linking extraction tables to Zotero work.

## Setup (once)

1. `pip install -r requirements.txt`
2. Copy `zotero_config.example.json` → `zotero_config.json`
3. [Zotero API key](https://www.zotero.org/settings/keys) — allow library read access
4. **Library ID:** [zotero.org/settings](https://www.zotero.org/settings) (numeric user ID) or group ID
5. Optional `collection_key`: right-click collection → *Export Library* URL contains `/collections/XXXX` — use `XXXX`

Zotero desktop does not need to be open (uses web API).

## Usage

```bash
python zotero_sync.py
```

Or from **review_runner.py** → option `5`.

Updates `Zotero_key` when empty; fills `Notes` when empty (or overwrite if you choose `y`).

## Workflow

1. Import RIS into Zotero, add notes and PDFs there  
2. Run `extraction_templ.py` → Excel templates  
3. Run `zotero_sync.py` → fill keys and notes from Zotero  
4. Continue editing in Excel or in Zotero (re-run sync after major Zotero updates)  
5. Export `.bib` from Zotero for Quarto citations (separate step)
