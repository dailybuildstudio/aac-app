import json
from pathlib import Path
from dataclasses import asdict
from typing import Optional
from ..models.character import (
    Character, VisualDNA, VoiceProfile, EmotionalArc,
    AudienceTargeting, DemographicResonance, AIGenerationProfile,
)
from ..models.scene import Scene, Shot, SocialClipMoment, AIScenePrompts
from ..models.production import ProductionLog, Asset

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"


# ── Characters ────────────────────────────────────────────────────────────────

def _parse_segment(seg_dict: dict) -> DemographicResonance:
    return DemographicResonance(
        score=seg_dict.get("score", 0),
        notes=seg_dict.get("notes", ""),
        marketing_angle=seg_dict.get("marketing_angle", ""),
    )


def character_from_dict(data: dict) -> Character:
    vd = data["visual_dna"]
    vp = data["voice_profile"]
    ea = data["emotional_arc"]
    at = data["audience_targeting"]
    ag = data["ai_generation"]
    segs = at.get("segments", {})

    return Character(
        character_id=data["character_id"],
        canonical_name=data["canonical_name"],
        hebrew_name=data.get("hebrew_name", ""),
        aliases=data.get("aliases", []),
        role=data["role"],
        testament=data["testament"],
        books_appearing_in=data.get("books_appearing_in", []),
        book=data.get("book", "luke"),
        chapters_active=data.get("chapters_active", ""),
        era=data.get("era", ""),
        visual_dna=VisualDNA(
            age_range=vd.get("age_range", ""),
            ethnicity=vd.get("ethnicity", ""),
            skin_tone=vd.get("skin_tone", ""),
            hair_color=vd.get("hair_color", ""),
            hair_texture=vd.get("hair_texture", ""),
            beard_style=vd.get("beard_style", ""),
            eye_color=vd.get("eye_color", ""),
            height_build=vd.get("height_build", ""),
            distinguishing_marks=vd.get("distinguishing_marks", []),
            wardrobe_by_arc=vd.get("wardrobe_by_arc", {}),
        ),
        voice_profile=VoiceProfile(
            register=vp.get("register", ""),
            pace=vp.get("pace", ""),
            accent_note=vp.get("accent_note", ""),
            speech_mannerisms=vp.get("speech_mannerisms", []),
            notes=vp.get("notes", ""),
        ),
        emotional_arc=EmotionalArc(
            opening=ea.get("opening", ""),
            midpoint=ea.get("midpoint", ""),
            climax=ea.get("climax", ""),
            resolution=ea.get("resolution", ""),
        ),
        audience_targeting=AudienceTargeting(
            evangelical_baptist=_parse_segment(segs.get("evangelical_baptist", {})),
            catholic=_parse_segment(segs.get("catholic", {})),
            black_church=_parse_segment(segs.get("black_church", {})),
            hispanic_christian=_parse_segment(segs.get("hispanic_christian", {})),
            secular_curious=_parse_segment(segs.get("secular_curious", {})),
            youth_gen_z=_parse_segment(segs.get("youth_gen_z", {})),
            jewish_american=_parse_segment(segs.get("jewish_american", {})),
            women=_parse_segment(segs.get("women", {})),
            men=_parse_segment(segs.get("men", {})),
            modern_parallel=at.get("modern_parallel", ""),
            modern_parallel_detail=at.get("modern_parallel_detail", ""),
        ),
        ai_generation=AIGenerationProfile(
            consistency_seed_prompt=ag.get("consistency_seed_prompt", ""),
            negative_prompt=ag.get("negative_prompt", ""),
            midjourney_style_params=ag.get("midjourney_style_params", ""),
            firefly_content_class=ag.get("firefly_content_class", "photo"),
            firefly_style_preset=ag.get("firefly_style_preset", "cinematic"),
            firefly_prompt=ag.get("firefly_prompt", ""),
            reference_films=ag.get("reference_films", []),
            color_grading_notes=ag.get("color_grading_notes", ""),
            midjourney_version_params=ag.get("midjourney_version_params", "--ar 16:9 --style raw --v 7"),
        ),
        production_notes=data.get("production_notes", ""),
    )


def load_book_characters(book: str = "luke") -> list:
    """Load all per-character JSON files for a book."""
    book_dir = DATA_DIR / "characters" / book
    characters = []
    if not book_dir.exists():
        return characters
    for path in sorted(book_dir.glob("*.json")):
        with open(path) as f:
            data = json.load(f)
        characters.append(character_from_dict(data))
    return characters


def load_character(book: str, character_id: str) -> Optional[Character]:
    book_dir = DATA_DIR / "characters" / book
    for path in book_dir.glob("*.json"):
        with open(path) as f:
            data = json.load(f)
        if data.get("character_id") == character_id:
            return character_from_dict(data)
    return None


# ── Scenes ────────────────────────────────────────────────────────────────────

def scene_from_dict(data: dict) -> Scene:
    ap = data.get("ai_prompts", {})
    shot_list = [Shot(**s) for s in data.get("shot_list", [])]
    clips = [SocialClipMoment(**c) for c in data.get("social_clip_moments", [])]
    return Scene(
        scene_id=data["scene_id"],
        title=data["title"],
        episode_label=data.get("episode_label", ""),
        act=data.get("act", ""),
        book=data.get("book", "luke"),
        luke_reference=data.get("luke_reference", ""),
        chapter_start=data.get("chapter_start", 0),
        verse_start=data.get("verse_start", 0),
        chapter_end=data.get("chapter_end", 0),
        verse_end=data.get("verse_end", 0),
        characters=data.get("characters", []),
        location=data.get("location", ""),
        time_of_day=data.get("time_of_day", ""),
        estimated_runtime_min=data.get("estimated_runtime_min", 0),
        format=data.get("format", ""),
        emotional_beat=data.get("emotional_beat", ""),
        key_moment=data.get("key_moment", ""),
        visual_direction=data.get("visual_direction", ""),
        shot_list=shot_list,
        social_clip_moments=clips,
        target_audiences=data.get("target_audiences", []),
        ai_prompts=AIScenePrompts(
            midjourney=ap.get("midjourney", ""),
            firefly=ap.get("firefly", ""),
            runway_video=ap.get("runway_video", ""),
            audio_notes=ap.get("audio_notes", ""),
        ),
        production_notes=data.get("production_notes", ""),
    )


def load_book_scenes(book: str = "luke") -> list:
    """Load all scene JSON files for a book (organized by act files)."""
    book_dir = DATA_DIR / "scenes" / book
    scenes = []
    if not book_dir.exists():
        return scenes
    for path in sorted(book_dir.glob("*.json")):
        with open(path) as f:
            data = json.load(f)
        for s in data.get("scenes", []):
            scenes.append(scene_from_dict(s))
    return scenes


# ── Production ────────────────────────────────────────────────────────────────

def load_production_log(book: str = "luke") -> ProductionLog:
    path = DATA_DIR / "production" / f"{book}_status.json"
    if not path.exists():
        return ProductionLog(book=book, last_updated="", assets=[])
    with open(path) as f:
        data = json.load(f)
    assets = [Asset(**a) for a in data.get("assets", [])]
    return ProductionLog(
        book=data.get("book", book),
        last_updated=data.get("last_updated", ""),
        assets=assets,
    )


def save_production_log(log: ProductionLog, book: str = "luke") -> None:
    path = DATA_DIR / "production" / f"{book}_status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "book": log.book,
        "last_updated": log.last_updated,
        "assets": [asdict(a) for a in log.assets],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
