---
name: client-demo-video
description: Create a narrated, client-ready demo video of the automated lead follow-up workflow (lead capture → instant SMS/email → nurture → quote → booked appointment → dashboard). Use when the user asks for a demo video for a client or niche (e.g. "make a demo video for a roofing client"), wants to re-render or customize the existing demo, or wants a new industry-specific version.
---

# Client Demo Video Pipeline

Produces a ~2 minute, 1280×720, 30 fps narrated screen-capture-style video that walks a
prospective client through the automated lead follow-up system. All assets live in `demo/`.
The reference build (kitchen-remodel example, "BrightBuild Remodeling") shipped as
`demo/lead-followup-demo-narrated.mp4`; share link: https://share.descript.com/view/zBBNUk2ezZP

## Pipeline overview

1. **Customize** `demo/ghl-followup-demo.html` for the client's niche
2. **Generate voiceover** clips with Higgsfield MCP (`generate_audio`, model `seed_audio`)
3. **Size scene durations** to the narration clip lengths
4. **Render deterministically** with `demo/frames.mjs` (virtual-time, frame-exact)
5. **Assemble + publish** narrated video in Descript MCP (video + VO tracks at offsets)
6. **Download, commit, deliver** the final MP4

## Step 1 — Customize the HTML

`demo/ghl-followup-demo.html` is self-contained (no network deps). It has 9 scenes
(`#s1`…`#s9`): intro, pipeline capture, instant response, nurture sequence, lead reply,
quote, calendar booking, dashboard, outro CTA. Things to swap per client:

- Example business name (`BrightBuild Remodeling`), lead name/service, SMS copy
- Sidebar brand (`Follow-Up Engine`) — or the agency's own brand
- Quote line items and total; pipeline card values
- Dashboard stats (`data-count` attrs) and chart bars (`data-h` attrs)

Animation engine notes (already handled, don't regress):
- Elements with `data-t="ms"` reveal at that time into their scene (class `on` added)
- `data-lite`/`data-done` light up workflow nodes; sub-steps must finish by ~7 s into a scene
- `animateCount` steps by rAF-delta with a per-frame fallback — rAF timestamps are frozen
  under virtual time, so never use `performance.now()` deltas alone for JS animation
- `window.startDemo(durationsArrayMs)` schedules everything; returns total ms

## Step 2 — Voiceover (Higgsfield MCP)

Script template is in `demo/narration-script.md` — keep the 9-beat structure, adapt niche
wording. Generate one clip per scene:

- Tool: `generate_audio`, params `{model: "seed_audio", voice_type: "preset", voice_id: "dc382508-c8bd-443c-8cb2-46e57b8d2e6f"}` (voice "Sterling"; ~1.5 credits/clip)
- Backend allows only ~2 concurrent jobs — submit sequentially, retry on 429 after the
  pending ones finish
- Poll results with `show_generations` (type `audio`); each result has `rawUrl` (WAV on
  CloudFront) and `durationSec` — record both for every clip

## Step 3 — Scene durations

`scene_ms[i] = 400 + durationSec[i]*1000 + 1300` (VO starts 0.4 s into each scene, ~1.3 s
breathing room after). Narration offset for Descript: `offset[i] = scene_start[i] + 0.4`
where `scene_start` is the cumulative sum of scene durations.

## Step 4 — Render

Do NOT use Playwright's `recordVideo` screencast — its timebase assumes 25 fps and drifts
~5%, which breaks narration sync (this was measured; `record.mjs` is kept only as a
reference/anti-pattern). Use the deterministic renderer:

```bash
cd demo && mkdir -p node_modules \
  && ln -sfn "$(npm root -g)/playwright" node_modules/playwright \
  && ln -sfn "$(npm root -g)/playwright-core" node_modules/playwright-core
node frames.mjs '[<9 scene durations in ms>]' lead-followup-demo.mp4
```

It drives CDP `Emulation.setVirtualTimePolicy` in 1/30 s budgets and pipes JPEG frames into
ffmpeg — output duration exactly matches the timeline. Requires ffmpeg (`apt-get install -y
ffmpeg`; retry once if apt indexes are stale). Spot-check frames afterwards:
`ffmpeg -ss <t> -i out.mp4 -frames:v 1 f.png` at a scene boundary +0.7 s and at the dashboard
(~scene8 +3 s, counters must show final values, not 0 or negatives).

## Step 5 — Assemble in Descript (MCP, runs server-side)

The container egress blocks CloudFront and most hosts (GitHub + storage.googleapis.com are
allowed), so the WAVs can't be downloaded locally — Descript fetches them by URL instead:

1. Push the silent MP4 to the repo (public), get its `raw.githubusercontent.com` URL
2. `import_media` into a new project: the video URL, the 9 CloudFront WAV URLs, plus a
   `"final-sequence"` entry with `tracks: [{media: video, offset: 0}, {media: vo_i, offset: offset_i}, …]`
   and `add_compositions: [{name, clips: [{media: "final-sequence"}], width: 1280, height: 720, fps: 30}]`
3. `wait_for_job`, then `publish_project` (`media_type: "Video"`, `resolution: "720p"`), `wait_for_job`
4. Download the `download_url` (storage.googleapis.com — allowed), verify audio placement
   (`volumedetect` on a narration window ≈ −18 dB, on a gap window ≈ −91 dB)
5. Commit the narrated MP4, push, send to the user with `SendUserFile`, and report the
   Descript `share_url`

## Constraints recap

- No GoHighLevel connector exists — never claim to record inside the user's real GHL
  account; this simulated UI is the deliverable (white-label friendly by design)
- Keep videos at 1280×720/30 fps unless asked otherwise; H.264 `crf 21`, `+faststart`
- Total credits per video: ~13.5 Higgsfield (9 VO clips) + Descript media-import minutes
