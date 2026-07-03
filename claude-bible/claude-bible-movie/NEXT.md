# Where We Left Off

## Current Status
- 22 characters built (data/characters/luke/)
- 30 scenes built covering all of Luke 1-24 (data/scenes/luke/)
- 299 production assets tracked
- All prompts ready to paste into Midjourney and Firefly
- Everything saved to GitHub (dailybuildstudio/aac-app)

## Next Action — DO THIS FIRST
Open Midjourney and paste this prompt:

```
1st century Jewish man age 30-33, warm olive-brown sun-weathered skin, dark wavy shoulder-length hair, full natural beard, dark brown eyes with depth and calm authority, lean strong build from years of walking, simple undyed linen tunic and outer robe with tassels, worn leather sandals, cinematic photoreal, golden hour natural light, 8k, film grain --no blue eyes, blonde hair, European features, white skin, halo, glowing body, cartoonish, painted illustration, modern clothing, medieval costume, muscular bodybuilder physique, long flowing luxurious hair --ar 16:9 --style raw --v 7
```

Generate 20-30 variations. Pick the face that looks right. Save that image.
That becomes the visual reference for everything else in the film.

## After Jesus Is Locked
Run this to get the next character prompts:
```bash
python3 scripts/prompt_generator.py --character peter_001 --platform midjourney
python3 scripts/prompt_generator.py --character mary_magdalene_001 --platform midjourney
python3 scripts/prompt_generator.py --character john_baptist_001 --platform midjourney
```

## Quick Commands
```bash
# See everything in the project
python3 scripts/prompt_generator.py --list

# See production status
python3 scripts/production_tracker.py --dashboard

# Get any character prompt
python3 scripts/prompt_generator.py --character jesus_001 --platform midjourney

# Get any scene prompt
python3 scripts/prompt_generator.py --scene transfiguration_001

# Export everything at once
python3 scripts/prompt_generator.py --export-all
```

## Production Phase Plan
1. Style lock (Jesus face) — IN PROGRESS
2. Character library — 22 characters, all arcs
3. Scene images — 30 scenes, hero shots
4. Video — Runway Gen-4 direction notes already written
5. Voice — ElevenLabs profiles already written
6. Social clips — 69 clips with hooks and captions ready to post
7. Feature cut — edit into film or 7-episode series

## Tool Costs (~$152/mo total)
- Midjourney Pro: $60/mo
- Adobe Firefly (Creative Cloud): $55/mo
- Runway Gen-4 Standard: $15/mo
- ElevenLabs Creator: $22/mo
