# Voiceover Script — Reputation & Review Automation Tutorial (`review-automation-demo.html`)

Voice: "Sterling" (Higgsfield seed_audio preset `dc382508-c8bd-443c-8cb2-46e57b8d2e6f`).
Scene duration = 400ms + clip + 1300ms. VO offset = scene start + 0.4s.

1. "Your best customers are walking out the door happy every single day — but most of them never leave a review, unless you ask at exactly the right moment. That's what Reputation Automation does. Let me show you how it works."
2. "The moment a job is marked complete in your pipeline, the automation kicks in — no one has to remember to ask for a review ever again."
3. "A friendly text goes out asking how the job went, with one simple tap to rate the experience from one to five stars."
4. "Here's the smart part: happy customers, four or five stars, get sent straight to your Google or Facebook page to post a public review. Anything three stars or below gets routed somewhere else entirely — a private feedback form, so an unhappy customer never becomes a public one star review."
5. "When a happy customer taps five stars, they're one click away from posting a glowing public review, and you get notified the moment it goes live."
6. "But if someone's unhappy, you find out first, privately. You get an instant alert with exactly what went wrong, so you can make it right before they ever think about going public."
7. "If a customer doesn't respond right away, a gentle reminder goes out a few days later, because most reviews come from a nudge, not the first ask."
8. "The results speak for themselves: dozens of new five star reviews every month, unhappy customers caught and saved instead of posted publicly, and your average rating climbing steadily over time."
9. "That's Reputation Automation by High-Rise Solution. More five star reviews, fewer public complaints, and a reputation that keeps building itself. Ready to protect and grow yours? Let's talk."

## Progress (2026-07-28)

Generated individually (Sterling seed_audio):
- Beat 1: 20.925s — https://d8j0ntlcm91z4.cloudfront.net/user_2vdkYecoxD7UgVFOoH1GqkisXdC/hf_20260728_232323_48454d0c-090d-4dc2-82de-d2f145837e9b.wav
- Beat 2: 10.055s — https://d8j0ntlcm91z4.cloudfront.net/user_2vdkYecoxD7UgVFOoH1GqkisXdC/hf_20260728_232341_775965fa-f7e0-4903-b68c-9d0abc7ff5b9.wav
- Beat 3: pending job 92a318bc-815d-4adf-932b-98ef9e116b48 (check job_display for URL/duration when done)

Hit grace_daily_limit_reached generating beat 4. Same pattern as social-autopilot video.

## Plan for beats 4-9 (single-clip strategy)

Generate ONE seed_audio clip containing beats 4-9 verbatim (in order, exact text from the
numbered list above). Then:
1. Import that WAV into a temp Descript project (import_media + composition)
2. export_transcript (srt) → find beat boundaries by opening words:
   "Here's the smart part" (4), "When a happy customer" (5), "But if someone's unhappy" (6),
   "If a customer doesn't respond" (7), "The results speak" (8), "That's Reputation Automation" (9)
3. Scene durations: s1..s3 = 400 + dur*1000 + 1300 each (per-beat clips);
   s4..s8 = beat_{i+1}_start - beat_i_start (from srt, in ms);
   s9 = clip_end - beat9_start + 1700.
   Long clip placed at offset = scene4_start/1000 - beat4_start_in_clip + 0.4 (seconds).
4. Render review-automation-demo.html via frames.mjs with the 9 durations (ms).
5. Standard finish: push silent master, Descript assemble (beat1/2/3 WAVs + long clip at
   computed offset, video track, 1280x720 30fps), publish 720p, download, mux clean video +
   Descript audio (ffmpeg -map 0:v -map 1:a -c copy) to strip watermark, encode
   review-ghl-720p.mp4 + review-ghl-480p-sms.mp4 + review-audio.mp3, commit to
   claude/ghl-workflow-demo-video-b9hp4l, SendUserFile + share links.
