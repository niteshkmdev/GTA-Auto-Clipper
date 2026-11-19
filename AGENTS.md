# Instructions for AI agents

Use this repository's commands as documented in [README.md](README.md). Keep all API keys in the local environment; never print, ask the user to paste, or write keys into prompts, logs, metadata, or tracked files.

## Clip workflow

1. Run `python find_streams.py "GTA 6" --max 25 --json` and show the returned candidates. The ranking is YouTube's view-count search order, not current concurrent viewers.
2. Use a stream only when the user has authorized its use or has a standing source list that includes it. If rights are unclear, ask the user and do not capture it.
3. **Always ask the user what language the stream is (English or Hindi)** before starting capture.
   - For English: pass `--channel english` (saves to `output/english/<timestamp>_<streamer>_<id>/`).
   - For Hindi: pass `--channel hindi` (saves to `output/hindi/<timestamp>_<streamer>_<id>/`).
4. Run clipping:
   - For live capture: `python clip.py URL --channel <english|hindi> --gameplay-confirmed --clip-len 30 --lead-in 6 --top 1`
   - For full ended streams / VODs: `python clip.py URL --vod --channel <english|hindi> --gameplay-confirmed --max-clips 5 --min-score 3.5` (downloads chat replay via yt-dlp, scans entire video, and globally ranks the Top 5 moments).
5. Inspect each MP4 and its JSON. Confirm the highlight includes its lead-in and payoff, gameplay is centered, captions are legible and in sync, the audio is intelligible, and metadata is accurate.
6. Draft truthful titles, descriptions, captions, and hashtags from the clip. **All titles, descriptions, and tags remain in English for both channels** (captions are Hinglish for Hindi streams). Do not invent reactions, events, creator approval, or viewership data.
7. Run `zernio_publish.py` without `--publish` to preview (pass `--channel hindi` or `--channel english`, or let it auto-detect from the folder path). Publish only when the user authorized this specific clip or previously enabled unattended publishing for authorized sources.
   - English channel uses `ZERNIO_API_KEY`, `ZERNIO_YOUTUBE_ACCOUNT_ID`, and `ZERNIO_INSTAGRAM_ACCOUNT_ID`.
   - Hindi channel uses `HINDI_ZERNIO_API_KEY`, `HINDI_ZERNIO_YOUTUBE_ACCOUNT_ID`, and `HINDI_ZERNIO_INSTAGRAM_ACCOUNT_ID`.
8. After posting, report the Zernio post ID and status. If a request errors after upload, check Zernio before retrying.

The clipper itself never posts. A `--test` output is not publishable. The source allowlist was intentionally removed; the agent must still respect the user's rights policy.
