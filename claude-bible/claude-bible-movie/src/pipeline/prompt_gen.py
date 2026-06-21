from typing import Optional
from ..models.character import Character
from ..models.scene import Scene

MIDJOURNEY_DEFAULTS = "--ar 16:9 --style raw --v 7"
FIREFLY_SUFFIX = "photorealistic, 8k resolution, cinematic film quality, shallow depth of field"


def midjourney_character(char: Character, arc: Optional[str] = None) -> str:
    base = char.ai_generation.consistency_seed_prompt
    if arc and arc in char.visual_dna.wardrobe_by_arc:
        base = f"{base}, wearing {char.visual_dna.wardrobe_by_arc[arc]}"
    neg = f" --no {char.ai_generation.negative_prompt}"
    params = f" {char.ai_generation.midjourney_version_params}"
    return f"{base}{neg}{params}"


def firefly_character(char: Character, arc: Optional[str] = None) -> str:
    base = char.ai_generation.firefly_prompt
    if arc and arc in char.visual_dna.wardrobe_by_arc:
        base = f"{base}, wearing {char.visual_dna.wardrobe_by_arc[arc]}"
    return f"{base}, {FIREFLY_SUFFIX}"


def midjourney_scene(scene: Scene) -> str:
    return scene.ai_prompts.midjourney


def firefly_scene(scene: Scene) -> str:
    return scene.ai_prompts.firefly


def runway_scene(scene: Scene, char: Optional[Character] = None) -> str:
    lines = []
    if char:
        lines.append(f"Character: {char.canonical_name} — {char.ai_generation.consistency_seed_prompt}")
    lines.append(f"Scene: {scene.ai_prompts.runway_video}")
    lines.append(f"Style: cinematic photoreal, 24fps, shallow depth of field, film grain")
    lines.append(f"Audio: {scene.ai_prompts.audio_notes}")
    return "\n".join(lines)


def elevenlabs_profile(char: Character) -> dict:
    vp = char.voice_profile
    return {
        "character": char.canonical_name,
        "character_id": char.character_id,
        "voice_register": vp.register,
        "voice_pace": vp.pace,
        "accent_note": vp.accent_note,
        "speech_mannerisms": vp.speech_mannerisms,
        "notes": vp.notes,
        "emotional_arc": {
            "opening": char.emotional_arc.opening,
            "midpoint": char.emotional_arc.midpoint,
            "climax": char.emotional_arc.climax,
            "resolution": char.emotional_arc.resolution,
        },
        "recommended_settings": {
            "stability": 0.65,
            "similarity_boost": 0.80,
            "style_exaggeration": 0.30,
            "note": "Lower stability for emotional scenes, raise for authoritative speech",
        },
    }


def all_character_prompts(char: Character) -> dict:
    result = {
        "character_id": char.character_id,
        "character_name": char.canonical_name,
        "midjourney_base": midjourney_character(char),
        "firefly_base": firefly_character(char),
        "firefly_content_class": char.ai_generation.firefly_content_class,
        "firefly_style_preset": char.ai_generation.firefly_style_preset,
        "arc_prompts": {},
    }
    for arc in char.visual_dna.wardrobe_by_arc:
        result["arc_prompts"][arc] = {
            "midjourney": midjourney_character(char, arc),
            "firefly": firefly_character(char, arc),
        }
    return result


def all_scene_prompts(scene: Scene) -> dict:
    return {
        "scene_id": scene.scene_id,
        "title": scene.title,
        "luke_reference": scene.luke_reference,
        "midjourney": midjourney_scene(scene),
        "firefly": firefly_scene(scene),
        "runway": scene.ai_prompts.runway_video,
        "audio_notes": scene.ai_prompts.audio_notes,
        "social_clips": [
            {
                "label": sc.label,
                "duration_seconds": sc.duration_seconds,
                "hook": sc.hook,
                "caption_template": sc.caption_template,
                "platforms": sc.platform_targets,
            }
            for sc in scene.social_clip_moments
        ],
    }
