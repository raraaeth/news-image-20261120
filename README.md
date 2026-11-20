# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/raraaeth/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/raraaeth/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

**The World in One Picture — Friday, 20 November 2026.** A newspaper-style front page that sums up one day's world news in a single 1024×1024 image: the date set large in the masthead, one lead story, and five further stories from five different beats, each with a small flat illustration, a headline and a one-line summary.

The lead is the day's biggest story — hours after the Shenzhen peace summit, Russia's massive missile and drone strike on Kyiv, drawn as an original night skyline of towers, a river bridge and missile trails (no news photography, logos or artwork). Below it: the three-power peace pledge in Shenzhen (diplomacy), GTA VI's record-smashing launch-day sales (culture), Cyclone Akvan's landfall in Odisha (Asia), a tanker ablaze near Hormuz (Middle East), and Taiwan's plunging stock market (markets).

## How it was made

- `stories.json` holds the editorial content — kicker, headline and sublabel for every panel — so the words can be refreshed by editing data only. Every story is an event of 20 November 2026 as reported that day; nothing is invented, and the date is named in the image itself.
- `render_image.py` composes `entry.png` from that data with Python/PIL: it draws the masthead, the lead illustration and each panel's icon scene from flat vector-style primitives, and renders every text string itself (DejaVu and Liberation fonts), so no text can come out garbled. It renders at 2× and downscales for clean edges.
- `main.ts` is the entry program the grader runs. The rules allow shipping the finished image with a program that copies it, so `main.ts` verifies `entry.png` (present, PNG signature, IHDR dimensions within 1024×1024, within the 1 MiB cap) and copies its bytes unchanged to the output directory — two runs therefore write identical bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

To rebuild the artwork after editing the stories: `python3 render_image.py` (needs Pillow).

---

<sub>Entered on [make.fun](https://make.fun/?ref=ainur-irawan&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
