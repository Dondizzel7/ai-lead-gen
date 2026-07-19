# Voiceover Script — Social Media Autopilot Tutorial (`social-autopilot-demo.html`)

Voice: "Sterling" (Higgsfield seed_audio preset `dc382508-c8bd-443c-8cb2-46e57b8d2e6f`).
Scene duration = 400ms + clip + 1300ms. VO offset = scene start + 0.4s.
All 9 clips pending (Higgsfield daily limit reached 2026-07-13 UTC).

1. "What if your business showed up on social media every single day, with zero ad spend and zero effort from you? That's the Social Media Autopilot: daily branded posts, plus automated D M follow ups that turn attention into booked appointments. Here's how it works."
2. "It starts with a one time setup. We load your brand: your services, your service area, your offers, and your voice. From that moment, every post is created to sound and look exactly like you."
3. "Then the system generates a full month of content in one click. Tips, before and afters, customer reviews, and offers, scheduled to post automatically every single day."
4. "Each post is written and designed for your brand, then published natively to Facebook, Instagram, and your Google Business Profile, at the time your local audience is most active."
5. "Day after day, the queue publishes itself. No logging in, no thinking about what to post. Your business simply shows up, everywhere, consistently."
6. "And here's where it turns into leads: when someone comments or sends a message, the system follows up instantly with an automated D M, while their interest is hot."
7. "The AI carries the conversation. It answers questions, qualifies the lead, and books them straight onto your calendar, then adds them to your pipeline, tagged as an organic social lead."
8. "The result: a page that posts every day, thousands of local people reached, every D M answered, and dozens of booked leads each month, all without spending a dollar on ads."
9. "That's the Social Media Autopilot by High-Rise Solution. Always visible, always following up, always booking. Ready to put your social media on autopilot? Let's talk."

## Progress (2026-07-19)

Generated individually (Sterling seed_audio):
- Beat 1: 17.03s — https://d8j0ntlcm91z4.cloudfront.net/user_2vdkYecoxD7UgVFOoH1GqkisXdC/hf_20260719_050204_5f57d926-3328-4654-b554-747a659b1ca0.wav
- Beat 2: 13.655s — https://d8j0ntlcm91z4.cloudfront.net/user_2vdkYecoxD7UgVFOoH1GqkisXdC/hf_20260719_050211_87c7b759-bbab-4402-a1d8-74ee4cdc7757.wav
- Beat 3: pending job 59ce594d-703c-456d-ae51-dc4f46780cfc (check show_generations for URL/duration)

## Plan for beats 4-9 (single-clip strategy, daily cap ≈ 3 jobs)

Generate ONE seed_audio clip containing beats 4-9 verbatim (in order). Then:
1. Import that WAV into a temp Descript project (import_media, no compositions needed)
2. export_transcript (srt) → parse caption start times; find beat boundaries by opening words:
   "Each post is written" (4), "Day after day" (5), "And here's where" (6),
   "The AI carries" (7), "The result" (8), "That's the Social Media Autopilot" (9)
3. Scene durations: s1..s3 = 400 + dur*1000 + 1300 each; s4..s8 = beat_{i+1}_start - beat_i_start;
   s9 = clip_end - beat9_start + 1700. Long clip placed at scene4_start + 400ms.
4. Render social-autopilot-demo.html with frames.mjs, then standard Descript assemble/publish/
   watermark-strip/GHL-encode/MP3/commit/deliver pipeline (see reactivation for reference).
