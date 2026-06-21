from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AssetStatus(str, Enum):
    NOT_STARTED = "not_started"
    PROMPT_READY = "prompt_ready"
    GENERATING = "generating"
    GENERATED = "generated"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"


class AssetType(str, Enum):
    CHARACTER_IMAGE = "character_image"
    SCENE_IMAGE = "scene_image"
    SCENE_VIDEO = "scene_video"
    SOCIAL_CLIP = "social_clip"
    VOICE_PROFILE = "voice_profile"
    BEHIND_SCENES = "behind_scenes"


class Platform(str, Enum):
    MIDJOURNEY = "midjourney"
    FIREFLY = "firefly"
    RUNWAY = "runway"
    ELEVENLABS = "elevenlabs"
    SORA = "sora"


@dataclass
class Asset:
    asset_id: str
    asset_type: str            # AssetType value
    platform: str              # Platform value
    status: str                # AssetStatus value
    prompt_used: str
    character_id: str = ""
    scene_id: str = ""
    arc: str = ""
    file_path: str = ""
    review_notes: str = ""
    created_at: str = ""
    approved_at: str = ""
    published_at: str = ""
    published_url: str = ""


@dataclass
class ProductionLog:
    book: str
    last_updated: str
    assets: list = field(default_factory=list)  # list of Asset

    def by_status(self, status: str) -> list:
        return [a for a in self.assets if a.status == status]

    def by_scene(self, scene_id: str) -> list:
        return [a for a in self.assets if a.scene_id == scene_id]

    def by_character(self, character_id: str) -> list:
        return [a for a in self.assets if a.character_id == character_id]

    def summary(self) -> dict:
        from collections import Counter
        counts = Counter(a.status for a in self.assets)
        total = len(self.assets)
        approved_published = counts.get("approved", 0) + counts.get("published", 0)
        return {
            "total": total,
            "by_status": dict(counts),
            "completion_pct": round(approved_published / max(total, 1) * 100, 1),
        }
