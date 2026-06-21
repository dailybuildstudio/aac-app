"""
Bible Film Project - Luke Character Builder & AI Prompt Generator
=================================================================
Run this script to:
  1. Load and validate all character data
  2. Generate AI image/video prompts per character and scene
  3. Export production packages for Midjourney, Runway, ElevenLabs

Usage:
    python build_characters.py                  # validate + summary
    python build_characters.py --prompts        # generate all AI prompts
    python build_characters.py --export         # full production export
    python build_characters.py --character jesus_001  # single character report
    python build_characters.py --audience secular_curious  # filter by audience
"""

import json
import os
import sys
import argparse
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
OUTPUT_DIR = BASE_DIR / "output" / "prompts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class VisualDNA:
    age_range_in_luke: str
    ethnicity: str
    skin_tone: str
    hair_color: str
    eye_color: str
    height_build: str
    distinguishing_marks: str
    wardrobe_by_arc: dict
    hair_texture: str = ""
    beard_style: str = ""
    primary_age_for_ministry: str = ""
    primary_age_for_annunciation_nativity: str = ""


@dataclass
class VoicePersonality:
    speech_style: str
    personality_traits: list
    emotional_arc: str
    voice_profile_notes: str


@dataclass
class AudienceTargeting:
    demographic_resonance: dict          # segment → 1-5 score
    modern_parallel: str
    marketing_angles: dict               # segment → angle string


@dataclass
class AIGeneration:
    consistency_seed_prompt: str
    negative_prompt: str
    style_preset: str
    reference_films: list = field(default_factory=list)


@dataclass
class Character:
    character_id: str
    canonical_name: str
    aliases: list
    role: str
    testament: str
    books_appearing_in: list
    luke_chapters_active: str
    era: str
    visual_dna: VisualDNA
    voice_personality: VoicePersonality
    audience_targeting: AudienceTargeting
    ai_generation: AIGeneration


# ── Loaders ──────────────────────────────────────────────────────────────────

def load_characters() -> list[Character]:
    """Load all characters from JSON and parse into dataclasses."""
    path = DATA_DIR / "characters.json"
    with open(path, "r") as f:
        raw = json.load(f)

    characters = []
    for c in raw["characters"]:
        vd = c["visual_dna"]
        vp = c["voice_personality"]
        at = c["audience_targeting"]
        ag = c["ai_generation"]

        char = Character(
            character_id=c["character_id"],
            canonical_name=c["canonical_name"],
            aliases=c.get("aliases", []),
            role=c["role"],
            testament=c["testament"],
            books_appearing_in=c["books_appearing_in"],
            luke_chapters_active=c["luke_chapters_active"],
            era=c["era"],
            visual_dna=VisualDNA(
                age_range_in_luke=vd.get("age_range_in_luke", ""),
                ethnicity=vd.get("ethnicity", ""),
                skin_tone=vd.get("skin_tone", ""),
                hair_color=vd.get("hair_color", ""),
                hair_texture=vd.get("hair_texture", ""),
                beard_style=vd.get("beard_style", ""),
                eye_color=vd.get("eye_color", ""),
                height_build=vd.get("height_build", ""),
                distinguishing_marks=vd.get("distinguishing_marks", ""),
                wardrobe_by_arc=vd.get("wardrobe_by_arc", {}),
                primary_age_for_ministry=vd.get("primary_age_for_ministry", ""),
                primary_age_for_annunciation_nativity=vd.get("primary_age_for_annunciation_nativity", ""),
            ),
            voice_personality=VoicePersonality(
                speech_style=vp.get("speech_style", ""),
                personality_traits=vp.get("personality_traits", []),
                emotional_arc=vp.get("emotional_arc", ""),
                voice_profile_notes=vp.get("voice_profile_notes", ""),
            ),
            audience_targeting=AudienceTargeting(
                demographic_resonance=at.get("demographic_resonance", {}),
                modern_parallel=at.get("modern_parallel", ""),
                marketing_angles=at.get("marketing_angles", {}),
            ),
            ai_generation=AIGeneration(
                consistency_seed_prompt=ag.get("consistency_seed_prompt", ""),
                negative_prompt=ag.get("negative_prompt", ""),
                style_preset=ag.get("style_preset", ""),
                reference_films=ag.get("reference_films", []),
            ),
        )
        characters.append(char)
    return characters


def load_style_guide() -> dict:
    path = CONFIG_DIR / "style_guide.json"
    with open(path, "r") as f:
        return json.load(f)


# ── Validators ───────────────────────────────────────────────────────────────

REQUIRED_FIELDS = [
    "character_id", "canonical_name", "role", "era",
    "luke_chapters_active",
]

def validate_characters(characters: list[Character]) -> dict:
    """Check all characters for completeness. Returns {id: [issues]}."""
    issues = {}
    for char in characters:
        char_issues = []

        if not char.ai_generation.consistency_seed_prompt:
            char_issues.append("MISSING: consistency_seed_prompt")
        if not char.ai_generation.negative_prompt:
            char_issues.append("MISSING: negative_prompt")
        if not char.visual_dna.skin_tone:
            char_issues.append("MISSING: visual_dna.skin_tone")
        if not char.visual_dna.distinguishing_marks:
            char_issues.append("MISSING: visual_dna.distinguishing_marks")
        if not char.audience_targeting.modern_parallel:
            char_issues.append("MISSING: audience_targeting.modern_parallel")
        if not char.voice_personality.emotional_arc:
            char_issues.append("MISSING: voice_personality.emotional_arc")
        if len(char.audience_targeting.demographic_resonance) == 0:
            char_issues.append("MISSING: demographic_resonance scores")

        if char_issues:
            issues[char.character_id] = char_issues

    return issues


# ── Prompt Generators ────────────────────────────────────────────────────────

def generate_midjourney_prompt(char: Character, arc: Optional[str] = None) -> str:
    """
    Generate a Midjourney-ready prompt for a character.
    Optionally target a specific wardrobe arc.
    """
    base = char.ai_generation.consistency_seed_prompt

    if arc and arc in char.visual_dna.wardrobe_by_arc:
        wardrobe = char.visual_dna.wardrobe_by_arc[arc]
        base = base.replace("cinematic photoreal", f"{wardrobe}, cinematic photoreal")

    negative = f" --no {char.ai_generation.negative_prompt}"
    params = " --ar 16:9 --style raw --v 7"

    return f"{base}{negative}{params}"


def generate_runway_prompt(char: Character, scene_description: str, arc: Optional[str] = None) -> str:
    """
    Generate a Runway Gen-4 video prompt for a character in a scene.
    """
    base = char.ai_generation.consistency_seed_prompt

    wardrobe_note = ""
    if arc and arc in char.visual_dna.wardrobe_by_arc:
        wardrobe_note = f" Wearing: {char.visual_dna.wardrobe_by_arc[arc]}."

    camera = "Slow cinematic push-in. Shallow depth of field. 24fps film look."

    return (
        f"Scene: {scene_description}\n"
        f"Character: {char.canonical_name} — {base}{wardrobe_note}\n"
        f"Style: {char.ai_generation.style_preset}\n"
        f"Camera: {camera}\n"
        f"Avoid: {char.ai_generation.negative_prompt}"
    )


def generate_elevenlabs_profile(char: Character) -> dict:
    """Generate an ElevenLabs voice configuration dict."""
    vp = char.voice_personality
    return {
        "character": char.canonical_name,
        "character_id": char.character_id,
        "voice_description": vp.voice_profile_notes,
        "speech_style": vp.speech_style,
        "personality_traits": vp.personality_traits,
        "emotional_arc": vp.emotional_arc,
        "recommended_voice_settings": {
            "stability": 0.65,
            "similarity_boost": 0.80,
            "style_exaggeration": 0.30,
            "notes": "Adjust stability down for emotional scenes, up for authoritative speeches"
        }
    }


# ── Reports ──────────────────────────────────────────────────────────────────

def print_character_summary(characters: list[Character]):
    print("\n" + "="*70)
    print(f"  LUKE FILM PROJECT — CHARACTER BIBLE")
    print(f"  {len(characters)} Characters Loaded")
    print("="*70)

    roles = {}
    for char in characters:
        roles.setdefault(char.role, []).append(char.canonical_name)

    for role, names in sorted(roles.items()):
        print(f"\n  [{role.upper()}]")
        for name in names:
            print(f"    • {name}")

    print("\n" + "="*70)


def print_character_report(char: Character):
    """Full single-character report."""
    print(f"\n{'='*70}")
    print(f"  {char.canonical_name.upper()}")
    print(f"  ID: {char.character_id} | Role: {char.role}")
    print(f"  Luke Chapters: {char.luke_chapters_active}")
    print(f"  Era: {char.era}")
    print(f"{'='*70}")

    print(f"\n  VISUAL DNA")
    print(f"  Age in Luke:   {char.visual_dna.age_range_in_luke}")
    print(f"  Ethnicity:     {char.visual_dna.ethnicity}")
    print(f"  Skin Tone:     {char.visual_dna.skin_tone}")
    print(f"  Hair:          {char.visual_dna.hair_color} | {char.visual_dna.hair_texture}")
    print(f"  Beard:         {char.visual_dna.beard_style or 'N/A'}")
    print(f"  Eyes:          {char.visual_dna.eye_color}")
    print(f"  Build:         {char.visual_dna.height_build}")
    print(f"  Marks:         {char.visual_dna.distinguishing_marks}")

    print(f"\n  WARDROBE ARCS")
    for arc, desc in char.visual_dna.wardrobe_by_arc.items():
        print(f"    [{arc}] {desc}")

    print(f"\n  PERSONALITY")
    print(f"  Speech:        {char.voice_personality.speech_style}")
    print(f"  Traits:        {', '.join(char.voice_personality.personality_traits)}")
    print(f"  Arc:           {char.voice_personality.emotional_arc}")

    print(f"\n  AUDIENCE TARGETING")
    print(f"  Modern Parallel: {char.audience_targeting.modern_parallel}")
    print(f"\n  Demographic Scores (1-5):")
    for seg, score in sorted(char.audience_targeting.demographic_resonance.items(),
                              key=lambda x: -x[1]):
        bar = "█" * score + "░" * (5 - score)
        print(f"    {seg:<25} {bar} {score}/5")

    print(f"\n  AI PROMPTS")
    print(f"\n  [Midjourney]")
    print(f"  {generate_midjourney_prompt(char)}")
    print(f"\n  [Style Preset] {char.ai_generation.style_preset}")


def print_audience_filter(characters: list[Character], segment: str, min_score: int = 4):
    """Show characters most relevant to a given audience segment."""
    print(f"\n{'='*70}")
    print(f"  CHARACTERS FOR SEGMENT: {segment.upper()} (score >= {min_score})")
    print(f"{'='*70}\n")

    matches = []
    for char in characters:
        score = char.audience_targeting.demographic_resonance.get(segment, 0)
        if score >= min_score:
            angle = char.audience_targeting.marketing_angles.get(segment, "")
            matches.append((score, char.canonical_name, angle, char.character_id))

    matches.sort(reverse=True)
    for score, name, angle, cid in matches:
        print(f"  {'█'*score}{'░'*(5-score)} {score}/5  {name} ({cid})")
        if angle:
            print(f"              → \"{angle}\"")
        print()


# ── Exporters ────────────────────────────────────────────────────────────────

def export_all_prompts(characters: list[Character]):
    """Write all prompt files to output/prompts/."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # Master Midjourney prompt file
    mj_lines = [f"# MIDJOURNEY PROMPTS — LUKE PROJECT\n# Generated {timestamp}\n\n"]
    for char in characters:
        mj_lines.append(f"## {char.canonical_name}\n")
        # Base prompt
        mj_lines.append(f"### Base\n{generate_midjourney_prompt(char)}\n\n")
        # Per-arc prompts
        for arc in char.visual_dna.wardrobe_by_arc:
            mj_lines.append(f"### Arc: {arc}\n{generate_midjourney_prompt(char, arc)}\n\n")
        mj_lines.append("---\n\n")

    mj_path = OUTPUT_DIR / f"midjourney_prompts_{timestamp}.md"
    with open(mj_path, "w") as f:
        f.writelines(mj_lines)
    print(f"  ✓ Midjourney prompts → {mj_path}")

    # ElevenLabs voice profiles
    voice_profiles = [generate_elevenlabs_profile(c) for c in characters]
    el_path = OUTPUT_DIR / f"elevenlabs_profiles_{timestamp}.json"
    with open(el_path, "w") as f:
        json.dump(voice_profiles, f, indent=2)
    print(f"  ✓ ElevenLabs profiles → {el_path}")

    # Audience matrix CSV
    segments = list(characters[0].audience_targeting.demographic_resonance.keys())
    csv_lines = ["character," + ",".join(segments) + "\n"]
    for char in characters:
        scores = [str(char.audience_targeting.demographic_resonance.get(s, 0)) for s in segments]
        csv_lines.append(f"{char.canonical_name}," + ",".join(scores) + "\n")

    matrix_path = OUTPUT_DIR / f"audience_matrix_{timestamp}.csv"
    with open(matrix_path, "w") as f:
        f.writelines(csv_lines)
    print(f"  ✓ Audience matrix → {matrix_path}")

    return mj_path, el_path, matrix_path


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bible Film Project — Luke Character Builder")
    parser.add_argument("--prompts", action="store_true", help="Generate all AI prompts")
    parser.add_argument("--export", action="store_true", help="Full production export")
    parser.add_argument("--character", type=str, help="Show report for single character ID")
    parser.add_argument("--audience", type=str, help="Filter characters by audience segment")
    parser.add_argument("--validate", action="store_true", help="Validate all character data")
    args = parser.parse_args()

    print("\nLoading character data...")
    characters = load_characters()
    style = load_style_guide()

    # Always validate
    issues = validate_characters(characters)
    if issues:
        print(f"\n⚠️  VALIDATION ISSUES FOUND:")
        for cid, char_issues in issues.items():
            print(f"  {cid}:")
            for issue in char_issues:
                print(f"    → {issue}")
    else:
        print(f"  ✓ All {len(characters)} characters passed validation")

    # Route to requested action
    if args.character:
        match = next((c for c in characters if c.character_id == args.character), None)
        if match:
            print_character_report(match)
        else:
            print(f"\n❌ Character '{args.character}' not found.")
            print(f"   Available IDs: {[c.character_id for c in characters]}")

    elif args.audience:
        print_audience_filter(characters, args.audience)

    elif args.prompts or args.export:
        print(f"\n📤 Exporting production package...")
        export_all_prompts(characters)
        print(f"\n✓ Export complete.")

    else:
        # Default: summary view
        print_character_summary(characters)
        print(f"\n  RUN OPTIONS:")
        print(f"  python scripts/build_characters.py --validate")
        print(f"  python scripts/build_characters.py --character jesus_001")
        print(f"  python scripts/build_characters.py --audience secular_curious")
        print(f"  python scripts/build_characters.py --export\n")


if __name__ == "__main__":
    main()
