# WNBA Stats (simple version)

Defense-vs-position matchup app for the WNBA. No database — the
sync script writes a single JSON file, and the site reads it directly.

## How it works

```
python data/sync.py          (run on your own machine)
        |
        v
  data/dvp.json               (committed to the repo)
        |
        v
  app/page.tsx imports it directly at build time
        |
        v
  Vercel builds + deploys the site with that data baked in
```

To update the numbers: re-run `sync.py`, commit the updated
`data/dvp.json`, push. Vercel redeploys automatically.

## Setup

1. `pip install nba_api` (only needed to run the sync script)
2. `python data/sync.py` — this fetches WNBA box scores and writes
   `data/dvp.json`. Takes a few minutes; it's polite-rate-limited.
3. `npm install`
4. `npm run dev` to preview locally at `localhost:3000`

## Deploying

1. Push this repo to GitHub (or update your existing one)
2. In Vercel, set **Framework Preset** to **Next.js** under
   Settings → Build and Deployment
3. Deploy. No environment variables needed — there's no database.

## No database, no API route, no query console

This version intentionally skips Postgres entirely. The tradeoff:
you have to re-run `sync.py` and push whenever you want fresh
numbers, rather than data updating live. For a project like this,
that's a fine tradeoff — much less to set up and maintain.
