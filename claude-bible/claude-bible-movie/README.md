# Bible Film Project — Gospel of Luke
## AI-Powered Photoreal Video Series

### Project Vision
A multi-format, demographically-targeted photoreal video series covering the Gospel of Luke,
produced using AI image and video generation tools for the US market.

---

## Directory Structure

```
bible_film_project/
├── data/
│   └── characters.json          ← All character records (edit here to add characters)
├── config/
│   └── style_guide.json         ← Visual style constants + audience segment definitions
├── scripts/
│   ├── build_characters.py      ← Character loader, validator, AI prompt generator
│   └── build_scenes.py          ← Scene breakdown builder
└── output/
    └── prompts/                 ← Generated AI prompt files (created on export)
```

---

## Quick Start

```bash
# No dependencies needed beyond Python 3.10+

# Validate all characters and see summary
python scripts/build_characters.py

# Full character report for Jesus
python scripts/build_characters.py --character jesus_001

# See which characters resonate most with secular audience
python scripts/build_characters.py --audience secular_curious

# Export all AI prompts (Midjourney, ElevenLabs, audience matrix)
python scripts/build_characters.py --export

# See all scenes
python scripts/build_scenes.py

# Deep dive on the Prodigal Son scene
python scripts/build_scenes.py --episode prodigal_son_001

# Find best scenes for women's ministry content
python scripts/build_scenes.py --audience women
```

---

## Characters in the Bible (Luke)

| ID | Name | Role | Luke Chapters |
|---|---|---|---|
| jesus_001 | Jesus of Nazareth | Protagonist | 1-24 |
| mary_mother_001 | Mary of Nazareth | Supporting Major | 1-2, 8, 11 |
| john_baptist_001 | John the Baptist | Supporting Major | 1, 3, 7 |
| peter_001 | Simon Peter | Supporting Major | 4-9, 18, 22, 24 |
| mary_magdalene_001 | Mary Magdalene | Supporting Major | 8, 23-24 |
| judas_001 | Judas Iscariot | Supporting Major | 6, 22 |
| zacchaeus_001 | Zacchaeus | Supporting Minor | 19 |
| elizabeth_001 | Elizabeth | Supporting Minor | 1 |
| pilate_001 | Pontius Pilate | Antagonist Secondary | 3, 13, 23 |
| prodigal_father_001 | The Father (Prodigal Son) | Parable Character | 15 |

**Characters to add next:**
- zechariah_001 (Luke 1) — Elizabeth's husband, struck mute
- herod_antipas_001 (Luke 3, 9, 23) — the political threat
- the_prodigal_son_001 (Luke 15) — the younger brother
- the_elder_brother_001 (Luke 15) — the resentful one
- the_good_samaritan_001 (Luke 10) — cast carefully
- lazarus_poor_001 (Luke 16) — the Rich Man parable

---

## Scenes Breakdown (10 scenes, ~94 min total)

| Scene | Format | Runtime | Top Audiences |
|---|---|---|---|
| The Annunciation | Short | 4 min | Catholic, Women, Hispanic |
| The Visitation | Short | 6 min | Women, Catholic, Hispanic |
| The Nativity | Special | 18 min | Everyone |
| The Baptism | Short | 5 min | Evangelical, Men |
| The Temptation | Short | 8 min | Men, Secular, Youth |
| The Good Samaritan | Short | 7 min | Secular, Black Church, Youth |
| The Prodigal Son | Episode | 14 min | Men, Secular, Hispanic |
| Zacchaeus | Short | 6 min | Men, Secular, Youth |
| The Last Supper | Feature seq | 16 min | Evangelical, Catholic |
| The Empty Tomb | Feature seq | 10 min | Evangelical, Women, Secular |

---

## AI Tools Stack

| Purpose | Tool | Notes |
|---|---|---|
| Character stills | Midjourney v7 | Use character reference for consistency |
| Video generation | Runway Gen-4 | Scene-by-scene clips |
| Alternative video | Kling 2.0 | Good for longer sequences |
| Voice acting | ElevenLabs | One voice profile per character |
| Video editing | DaVinci Resolve | Free version sufficient to start |
| Social clips | CapCut | Fast mobile editing |

---

## Workflow: From Data to First Clip

1. **Validate** — `python scripts/build_characters.py --validate`
2. **Export prompts** — `python scripts/build_characters.py --export`
3. **Generate character reference images** — Run Midjourney prompts for your 5 priority characters
4. **Lock the look** — Iterate until you have a consistent face for each character
5. **Save as character reference** — Use Midjourney's `--cref` parameter for scene generation
6. **Generate first scene stills** — Annunciation or Prodigal Son (highest impact, simplest cast)
7. **Bring into Runway** — Generate 4-10 second video clips from the best stills
8. **Assemble in DaVinci** — First rough cut
9. **Add voice** — ElevenLabs for character dialogue
10. **Post first clip** — The Prodigal Son running scene. That's your first viral moment.

---

## Distribution Strategy (US)

### Phase 1 — Proof of concept (3 clips)
- Prodigal Son running scene (60 sec) → YouTube, Instagram, TikTok
- The Annunciation (full 4 min) → YouTube
- Zacchaeus in the tree (90 sec clip) → TikTok/Reels

### Phase 2 — Series launch
- Release Luke as episodic series on YouTube (ad-supported)
- License individual parables to church platforms (RightNow Media, FORMED)
- Spanish dub for Hispanic Christian market

### Phase 3 — Theatrical / Streaming
- Full passion/resurrection feature cut for streaming pitch
- Church theatrical screening partnerships

---

## Adding a New Character

Edit `data/characters.json` and add a new object to the `"characters"` array.
Copy an existing character block as your template.
Then run `python scripts/build_characters.py --validate` to check for missing fields.

---

*"The Son of Man came to seek and to save the lost." — Luke 19:10*
