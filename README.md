# Покриви & Дърво – website

Website for a roofing and timber construction company in Pazardzhik and Plovdiv,
built from the Stitch design in `DESIGN.md`.

## What's in this repository

| Path | What it is |
|---|---|
| `docs/` | The multi-page website: 8 pages, `assets/styles.css`, `assets/app.js`, photos in `assets/img/` |
| `server.py` | Local Python server for the site, with the inquiry form API |
| `single-page/pokrivi-darvo.html` | The whole site as one file with the photos built in. Opens in any browser on its own |
| `DESIGN.md` | Design tokens and guidelines (colours, fonts, spacing) |

Pages: `index.html` (Начало), `za-nas.html` (За нас), `uslugi.html` (Услуги),
`galeriya.html` (Галерия), `regioni.html` (Региони), `kontakti.html` (Контакти),
`privacy.html` (Политика за поверителност), `terms.html` (Общи условия).

## Run it locally

Needs Python 3, no extra packages.

```bash
python3 server.py
```

Open http://localhost:3000. Form submissions are saved to `data/inquiries.json`
and listed at http://localhost:3000/api/inquiries.

## Publish with GitHub Pages

Settings → Pages → Source: "Deploy from a branch" → Branch: `main`, folder: `/docs` → Save.

GitHub Pages only serves static files, so the inquiry form cannot save submissions there.
On Pages the form shows an error asking visitors to call instead. To receive inquiries
online, connect the form to a form service or host `server.py` on a server.

## Before going live

- Replace the placeholder company details (ЕИК 123456789, address) in the footer,
  `privacy.html` and `terms.html`.
- The gallery and service photos are Stitch-generated stand-ins; replace them with photos of real jobs.
- Have a lawyer review the privacy policy and terms.
