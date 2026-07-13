# Lead Follow-Up Workflow — Client Demo Video

A narrated, screen-capture-style demo video that walks prospective clients through the
automated lead follow-up system (instant response → multi-day nurture → quote → booked
appointment → results dashboard). Built to be sent to clients instead of a live Zoom
walkthrough.

## Files

| File | What it is |
|---|---|
| `lead-followup-demo-narrated.mp4` | **The client-ready video** — full voiceover, 1280×720 @ 30 fps, 2:05. Send this one to clients. |
| `lead-followup-demo.mp4` | Silent master render (narration is layered on top in Descript). |
| `ghl-followup-demo.html` | The animated demo itself — a self-contained HTML page that plays through 9 scenes (pipeline, SMS, workflow builder, quote, calendar, dashboard). Open in a browser and run `startDemo()` in the console to watch it live. |
| `frames.mjs` | Deterministic renderer: drives the page frame-by-frame with Chrome DevTools virtual time and pipes exact 30 fps frames into ffmpeg. No wall-clock drift, so narration stays in sync. |
| `record.mjs` | Simpler real-time Playwright screen recorder (kept for reference; the screencast timebase drifts, so `frames.mjs` is the one to use). |
| `narration-script.md` | The full voiceover script with per-scene timings and audio offsets. |

## Re-rendering

```bash
npm i playwright   # or link a global install
node frames.mjs '[16200,12800,18800,10900,13800,11300,12900,14100,13800]' lead-followup-demo.mp4
```

The JSON array is the 9 scene durations in ms — each is sized to its narration clip
(clip length + ~1.7 s breathing room). If you regenerate the voiceover, update these.

## Customizing for a specific client

Everything client-facing lives in `ghl-followup-demo.html`:

- **Brand name** — search for `Follow-Up Engine` (sidebar logo) and `BrightBuild Remodeling` (the example business in the SMS/quote scenes).
- **Industry example** — the sample lead is a $12,400 kitchen remodel; swap the pipeline cards, SMS copy, and quote line items for the client's trade.
- **Stats** — the scene 8 dashboard numbers (`data-count` attributes) and chart bars (`data-h`).
