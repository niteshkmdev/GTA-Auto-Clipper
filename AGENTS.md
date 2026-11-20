# Instructions for AI agents

Use this repository's commands as documented in [README.md](README.md). Keep all API keys in the local environment; never print, ask the user to paste, or write keys into prompts, logs, metadata, or tracked files.

## Channel & Caption Rules

1. **Only English videos should be captioned.**
2. **Never caption Hindi videos (`--channel hindi`):**
   - In GTA 6, in-game character dialogue is already in English with native in-game subtitles enabled by default.
   - Auto-transcribing Hindi/Hinglish speech adds visual clutter, clashes with game subtitles, and causes timing desync.
   - Hindi channel output must remain clean gameplay + streamer facecam with crisp native audio.
   - `clip.py` automatically skips subtitles when `--channel hindi` is selected (or when `--skip-captions` is passed).
3. **English videos (`--channel english`):**
   - Pop-up animated captions are burned into English clips by default using pause-aware timing.
4. **Titles, Descriptions & Hashtags:**
   - **All titles, descriptions, and hashtags must remain in English for BOTH channels.**
   - Do not invent reactions, events, creator approval, or viewership data.

## Video Resolution & Quality Rules

1. **Target 1440p Vertical (1440x2560):**
   - Always extract and render vertical clips in **1440p (1440x2560)** whenever source resolution is 1440p or higher.
2. **Fallback to 1080p Vertical (1080x1920):**
   - If 1440p is not available from the source stream/VOD, fall back cleanly to **1080p (1080x1920)**.
3. **Never go below 1080p:**
   - Output clips must never be rendered below 1080p under any circumstances.
4. **Framing & Layout Modes:**
   - `split`: Creator facecam on top, gameplay on bottom (ideal when streamer reaction is strong and persistent facecam is detected).
   - `fill`: Full 9:16 vertical gameplay centered on player/action (best for intense gameplay, driving, or streams without facecam).
   - `fit` / letterboxed: Entire source preserved with blurred backdrop padding (best for cinematic cutscenes or wide letterboxed sequences).

## Clip workflow

1. Run `python find_streams.py "GTA 6" --max 25 --json` and show the returned candidates. The ranking is YouTube's view-count search order, not current concurrent viewers.
2. Use a stream only when the user has authorized its use or has a standing source list that includes it. If rights are unclear, ask the user and do not capture it.
3. **Always ask the user what language the stream is (English or Hindi)** before starting capture.
   - For English: pass `--channel english` (saves to `output/english/<timestamp>_<streamer>_<id>/`).
   - For Hindi: pass `--channel hindi` (saves to `output/hindi/<timestamp>_<streamer>_<id>/`, captions automatically skipped).
4. Run clipping:
   - For live capture: `python clip.py URL --channel <english|hindi> --gameplay-confirmed --clip-len 30 --lead-in 6 --top 1`
   - For full ended streams / VODs: `python clip.py URL --vod --channel <english|hindi> --gameplay-confirmed --max-clips 5 --min-score 3.5` (downloads chat replay via yt-dlp, scans entire video, and globally ranks the Top 5 moments).
5. Inspect each MP4 and its JSON. Confirm the highlight includes its lead-in and payoff, gameplay is centered, captions (if English) are legible, pause-aware, and in sync, audio is intelligible, and metadata is accurate.
6. Draft truthful titles, descriptions, captions, and hashtags from the clip in English.
7. Run `zernio_publish.py` without `--publish` to preview (pass `--channel hindi` or `--channel english`, or let it auto-detect from the folder path). Publish only when the user authorized this specific clip or previously enabled unattended publishing for authorized sources.
   - English channel uses `ZERNIO_API_KEY`, `ZERNIO_YOUTUBE_ACCOUNT_ID`, and `ZERNIO_INSTAGRAM_ACCOUNT_ID`.
   - Hindi channel uses `HINDI_ZERNIO_API_KEY`, `HINDI_ZERNIO_YOUTUBE_ACCOUNT_ID`, and `HINDI_ZERNIO_INSTAGRAM_ACCOUNT_ID`.
8. After posting, report the Zernio post ID and status. If a request errors after upload, check Zernio before retrying.

## Learned Subtitle & Timing Rules (For English Channels)

1. **Pause-Aware Subtitle Timing:** Never extend subtitle duration across silences or speech pauses. A subtitle event must terminate within `0.20s - 0.35s` of speech cessation (`min(next_word_start, word_end + 0.35s)`). When a streamer pauses or stops speaking, the screen must immediately clear of subtitles so viewers see clean gameplay.
2. **FFmpeg Input Seeking vs Filter Complex (`-ss` before `-i`):** Always place `-ss <start>` before `-i <source>` when using `-filter_complex`. Output seeking (`-i <source> -ss <start>`) feeds un-seeked frames from source PTS 0 into libass, burning subtitles onto unseeked frames and discarding initial seconds, shifting all subtitles into the future by `start` seconds.
3. **Windows Drive Colon Parsing in FFmpeg ASS Filters:** Never pass absolute paths with drive colons (`C:\...`) to the `ass=` filter. FFmpeg treats `:` as a filter option separator (`key:value`), throwing `Unable to parse original_size`. Execute FFmpeg with `cwd=<output_dir>` and bare relative filenames.
4. **Folder Re-use on Retries:** When retrying or restarting clipping on a stream/VOD, reuse the existing timestamp folder for that stream (`find_existing_stream_folder()`) rather than generating empty duplicate folders.

The clipper itself never posts. A `--test` output is not publishable. The source allowlist was intentionally removed; the agent must still respect the user's rights policy.
