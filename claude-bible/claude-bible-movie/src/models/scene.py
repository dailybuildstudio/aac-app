from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Shot:
    shot_type: str   # ECU, CU, MS, WS, EWS
    description: str
    camera_movement: str = ""
    lens_note: str = ""


@dataclass
class SocialClipMoment:
    label: str
    duration_seconds: int
    hook: str
    caption_template: str
    platform_targets: list = field(default_factory=list)


@dataclass
class AIScenePrompts:
    midjourney: str
    firefly: str
    runway_video: str
    audio_notes: str = ""


@dataclass
class Scene:
    scene_id: str
    title: str
    episode_label: str
    act: str
    book: str
    luke_reference: str
    chapter_start: int
    verse_start: int
    chapter_end: int
    verse_end: int
    characters: list            # character_ids
    location: str
    time_of_day: str
    estimated_runtime_min: int
    format: str                 # short_film | short_episode | feature_sequence | special_episode
    emotional_beat: str
    key_moment: str
    visual_direction: str
    shot_list: list             # list of Shot
    social_clip_moments: list   # list of SocialClipMoment
    target_audiences: list
    ai_prompts: AIScenePrompts
    production_notes: str = ""
