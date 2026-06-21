"""
Prompt Generator — Midjourney + Adobe Firefly + Runway
=======================================================
Generates ready-to-paste prompts for every character, arc, and scene.

Usage:
    python scripts/prompt_generator.py --list
    python scripts/prompt_generator.py --character jesus_001
    python scripts/prompt_generator.py --character jesus_001 --arc ministry
    python scripts/prompt_generator.py --character jesus_001 --platform firefly
    python scripts/prompt_generator.py --scene nativity_001
    python scripts/prompt_generator.py --scene nativity_001 --platform runway
    python scripts/prompt_generator.py --audience secular_curious
    python scripts/prompt_generator.py --export-characters
    python scripts/prompt_generator.py --export-scenes
    python scripts/prompt_generator.py --export-all
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.data_loader import load_book_characters, load_book_scenes
from src.pipeline.prompt_gen import (
    midjourney_character, firefly_character, runway_scene,
    elevenlabs_profile, all_character_prompts, all_scene_prompts,
)

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "prompts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def cmd_list(characters, scenes):
    print(f"\n{'='*70}")
    print(f"  LUKE PROJECT — PROMPT INVENTORY")
    print(f"  {len(characters)} characters | {len(scenes)} scenes")
    print(f"{'='*70}\n")
    print("  CHARACTERS:")
    for c in characters:
        arcs = list(c.visual_dna.wardrobe_by_arc.keys())
        print(f"    {c.character_id:<30} {c.canonical_name}")
        print(f"      arcs: {', '.join(arcs)}")
    print(f"\n  SCENES:")
    for s in scenes:
        print(f"    {s.scene_id:<35} {s.luke_reference:<15} {s.estimated_runtime_min}min")
    print()


def cmd_character(characters, character_id, arc=None, platform="all"):
    char = next((c for c in characters if c.character_id == character_id), None)
    if not char:
        ids = [c.character_id for c in characters]
        print(f"\nCharacter '{character_id}' not found.\nAvailable: {ids}")
        return

    print(f"\n{'='*70}")
    print(f"  PROMPTS — {char.canonical_name.upper()}")
    if arc:
        print(f"  Arc: {arc}")
    print(f"{'='*70}\n")

    if platform in ("all", "midjourney"):
        print("  [MIDJOURNEY]")
        print(f"  {midjourney_character(char, arc)}\n")

    if platform in ("all", "firefly"):
        print("  [ADOBE FIREFLY]")
        print(f"  Content class: {char.ai_generation.firefly_content_class}")
        print(f"  Style preset:  {char.ai_generation.firefly_style_preset}")
        print(f"  Prompt: {firefly_character(char, arc)}\n")

    if platform in ("all", "elevenlabs"):
        print("  [ELEVENLABS VOICE]")
        profile = elevenlabs_profile(char)
        print(f"  Register: {profile['voice_register']}")
        print(f"  Pace:     {profile['voice_pace']}")
        print(f"  Accent:   {profile['accent_note']}")
        print(f"  Notes:    {profile['notes']}\n")

    if arc is None and platform == "all":
        print("  [ARC PROMPTS]")
        for a, wardrobe in char.visual_dna.wardrobe_by_arc.items():
            print(f"\n  — {a.upper()}: {wardrobe}")
            print(f"    MJ:      {midjourney_character(char, a)}")
            print(f"    Firefly: {firefly_character(char, a)}")


def cmd_scene(scenes, scene_id, platform="all"):
    scene = next((s for s in scenes if s.scene_id == scene_id), None)
    if not scene:
        ids = [s.scene_id for s in scenes]
        print(f"\nScene '{scene_id}' not found.\nAvailable: {ids}")
        return

    print(f"\n{'='*70}")
    print(f"  PROMPTS — {scene.title.upper()}")
    print(f"  {scene.luke_reference} | {scene.estimated_runtime_min} min")
    print(f"{'='*70}\n")

    if platform in ("all", "midjourney"):
        print("  [MIDJOURNEY]")
        print(f"  {scene.ai_prompts.midjourney}\n")

    if platform in ("all", "firefly"):
        print("  [ADOBE FIREFLY]")
        print(f"  {scene.ai_prompts.firefly}\n")

    if platform in ("all", "runway"):
        print("  [RUNWAY GEN-4 VIDEO]")
        print(f"  {scene.ai_prompts.runway_video}\n")

    if scene.ai_prompts.audio_notes:
        print("  [AUDIO DIRECTION]")
        print(f"  {scene.ai_prompts.audio_notes}\n")

    if scene.social_clip_moments:
        print("  [SOCIAL CLIP MOMENTS]")
        for clip in scene.social_clip_moments:
            print(f"  — {clip.label} ({clip.duration_seconds}s)")
            print(f"    Hook: {clip.hook}")
            print(f"    Caption: {clip.caption_template}")
            print(f"    Platforms: {', '.join(clip.platform_targets)}\n")


def cmd_audience(characters, scenes, segment):
    print(f"\n{'='*70}")
    print(f"  PROMPT PACKAGE FOR: {segment.upper()}")
    print(f"{'='*70}\n")

    print("  TOP CHARACTERS:")
    seg_chars = []
    for c in characters:
        score = c.audience_targeting.score_dict().get(segment, 0)
        angle = getattr(c.audience_targeting, segment.replace("-", "_"), None)
        if score >= 4:
            seg_chars.append((score, c))
    seg_chars.sort(key=lambda x: -x[0])
    for score, c in seg_chars:
        bar = "█" * score + "░" * (5 - score)
        seg_obj = getattr(c.audience_targeting, segment.replace("-", "_"), None)
        angle = seg_obj.marketing_angle if seg_obj else ""
        print(f"  {bar} {score}/5  {c.canonical_name}")
        if angle:
            print(f"         → \"{angle}\"")
        print(f"         MJ: {midjourney_character(c)[:80]}...")
    print()

    print("  SCENES:")
    for s in scenes:
        if segment in s.target_audiences:
            print(f"  • {s.title} ({s.luke_reference})")
            for clip in s.social_clip_moments:
                print(f"    [{clip.duration_seconds}s] {clip.hook}")
    print()


def cmd_export_characters(characters):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out = {"generated": ts, "characters": []}

    mj_lines = [f"# MIDJOURNEY PROMPTS — LUKE\n# {ts}\n\n"]
    ff_lines = [f"# ADOBE FIREFLY PROMPTS — LUKE\n# {ts}\n\n"]
    el_profiles = []

    for c in characters:
        prompts = all_character_prompts(c)
        out["characters"].append(prompts)
        el_profiles.append(elevenlabs_profile(c))

        mj_lines.append(f"## {c.canonical_name}\n")
        mj_lines.append(f"### Base\n{prompts['midjourney_base']}\n\n")
        for arc, ap in prompts["arc_prompts"].items():
            mj_lines.append(f"### {arc}\n{ap['midjourney']}\n\n")
        mj_lines.append("---\n\n")

        ff_lines.append(f"## {c.canonical_name}\n")
        ff_lines.append(f"Content class: {c.ai_generation.firefly_content_class}\n")
        ff_lines.append(f"Style: {c.ai_generation.firefly_style_preset}\n")
        ff_lines.append(f"### Base\n{prompts['firefly_base']}\n\n")
        for arc, ap in prompts["arc_prompts"].items():
            ff_lines.append(f"### {arc}\n{ap['firefly']}\n\n")
        ff_lines.append("---\n\n")

    json_path = OUTPUT_DIR / f"character_prompts_{ts}.json"
    mj_path = OUTPUT_DIR / f"midjourney_characters_{ts}.md"
    ff_path = OUTPUT_DIR / f"firefly_characters_{ts}.md"
    el_path = OUTPUT_DIR / f"elevenlabs_profiles_{ts}.json"

    json_path.write_text(json.dumps(out, indent=2))
    mj_path.write_text("".join(mj_lines))
    ff_path.write_text("".join(ff_lines))
    el_path.write_text(json.dumps(el_profiles, indent=2))

    print(f"\n  Exported {len(characters)} characters:")
    for p in [json_path, mj_path, ff_path, el_path]:
        print(f"    {p.name}")


def cmd_export_scenes(scenes):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    mj_lines = [f"# MIDJOURNEY SCENE PROMPTS — LUKE\n# {ts}\n\n"]
    ff_lines = [f"# ADOBE FIREFLY SCENE PROMPTS — LUKE\n# {ts}\n\n"]
    rw_lines = [f"# RUNWAY VIDEO DIRECTION — LUKE\n# {ts}\n\n"]
    social_out = {"generated": ts, "clips": []}

    for s in scenes:
        mj_lines.append(f"## {s.title} ({s.luke_reference})\n{s.ai_prompts.midjourney}\n\n---\n\n")
        ff_lines.append(f"## {s.title} ({s.luke_reference})\n{s.ai_prompts.firefly}\n\n---\n\n")
        rw_lines.append(f"## {s.title} ({s.luke_reference})\n{s.ai_prompts.runway_video}\n")
        if s.ai_prompts.audio_notes:
            rw_lines.append(f"Audio: {s.ai_prompts.audio_notes}\n")
        rw_lines.append("\n---\n\n")
        for clip in s.social_clip_moments:
            social_out["clips"].append({
                "scene": s.scene_id,
                "scene_title": s.title,
                "label": clip.label,
                "duration_seconds": clip.duration_seconds,
                "hook": clip.hook,
                "caption_template": clip.caption_template,
                "platforms": clip.platform_targets,
            })

    mj_path = OUTPUT_DIR / f"midjourney_scenes_{ts}.md"
    ff_path = OUTPUT_DIR / f"firefly_scenes_{ts}.md"
    rw_path = OUTPUT_DIR / f"runway_direction_{ts}.md"
    social_path = OUTPUT_DIR / f"social_clips_{ts}.json"

    mj_path.write_text("".join(mj_lines))
    ff_path.write_text("".join(ff_lines))
    rw_path.write_text("".join(rw_lines))
    social_path.write_text(json.dumps(social_out, indent=2))

    print(f"\n  Exported {len(scenes)} scenes:")
    for p in [mj_path, ff_path, rw_path, social_path]:
        print(f"    {p.name}")


def main():
    parser = argparse.ArgumentParser(description="Bible Film Project — Prompt Generator")
    parser.add_argument("--book", default="luke", help="Book to load (default: luke)")
    parser.add_argument("--list", action="store_true", help="List all characters and scenes")
    parser.add_argument("--character", type=str, help="Generate prompts for character ID")
    parser.add_argument("--arc", type=str, help="Wardrobe arc for character prompt")
    parser.add_argument("--scene", type=str, help="Generate prompts for scene ID")
    parser.add_argument("--audience", type=str, help="Prompt package for audience segment")
    parser.add_argument("--platform", default="all",
                        choices=["all", "midjourney", "firefly", "runway", "elevenlabs"],
                        help="Filter output to specific platform")
    parser.add_argument("--export-characters", action="store_true", help="Export all character prompts")
    parser.add_argument("--export-scenes", action="store_true", help="Export all scene prompts")
    parser.add_argument("--export-all", action="store_true", help="Export everything")
    args = parser.parse_args()

    characters = load_book_characters(args.book)
    scenes = load_book_scenes(args.book)

    if not characters and not scenes:
        print(f"\nNo data found for book '{args.book}'.")
        print(f"Expected: data/characters/{args.book}/*.json and data/scenes/{args.book}/*.json")
        return

    if args.list:
        cmd_list(characters, scenes)
    elif args.character:
        cmd_character(characters, args.character, args.arc, args.platform)
    elif args.scene:
        cmd_scene(scenes, args.scene, args.platform)
    elif args.audience:
        cmd_audience(characters, scenes, args.audience)
    elif args.export_characters or args.export_all:
        cmd_export_characters(characters)
        if args.export_all:
            cmd_export_scenes(scenes)
    elif args.export_scenes:
        cmd_export_scenes(scenes)
    else:
        print(f"\nLoaded: {len(characters)} characters, {len(scenes)} scenes from '{args.book}'")
        print("\nOptions:")
        print("  --list")
        print("  --character jesus_001")
        print("  --character jesus_001 --arc ministry --platform firefly")
        print("  --scene nativity_001")
        print("  --audience secular_curious")
        print("  --export-all\n")


if __name__ == "__main__":
    main()
