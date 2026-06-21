from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VisualDNA:
    ethnicity: str
    skin_tone: str
    hair_color: str
    hair_texture: str
    eye_color: str
    height_build: str
    distinguishing_marks: list
    age_range: str = ""
    beard_style: str = ""
    wardrobe_by_arc: dict = field(default_factory=dict)


@dataclass
class VoiceProfile:
    register: str
    pace: str
    accent_note: str
    speech_mannerisms: list
    notes: str = ""


@dataclass
class EmotionalArc:
    opening: str
    midpoint: str
    climax: str
    resolution: str


@dataclass
class DemographicResonance:
    score: int  # 1-5
    notes: str = ""
    marketing_angle: str = ""


@dataclass
class AudienceTargeting:
    evangelical_baptist: DemographicResonance
    catholic: DemographicResonance
    black_church: DemographicResonance
    hispanic_christian: DemographicResonance
    secular_curious: DemographicResonance
    youth_gen_z: DemographicResonance
    jewish_american: DemographicResonance
    women: DemographicResonance
    men: DemographicResonance
    modern_parallel: str
    modern_parallel_detail: str = ""

    def top_segments(self, n: int = 3) -> list:
        segments = [
            ("evangelical_baptist", self.evangelical_baptist),
            ("catholic", self.catholic),
            ("black_church", self.black_church),
            ("hispanic_christian", self.hispanic_christian),
            ("secular_curious", self.secular_curious),
            ("youth_gen_z", self.youth_gen_z),
            ("jewish_american", self.jewish_american),
            ("women", self.women),
            ("men", self.men),
        ]
        return sorted(segments, key=lambda x: -x[1].score)[:n]

    def score_dict(self) -> dict:
        return {
            "evangelical_baptist": self.evangelical_baptist.score,
            "catholic": self.catholic.score,
            "black_church": self.black_church.score,
            "hispanic_christian": self.hispanic_christian.score,
            "secular_curious": self.secular_curious.score,
            "youth_gen_z": self.youth_gen_z.score,
            "jewish_american": self.jewish_american.score,
            "women": self.women.score,
            "men": self.men.score,
        }


@dataclass
class AIGenerationProfile:
    consistency_seed_prompt: str
    negative_prompt: str
    midjourney_style_params: str
    firefly_content_class: str  # photo | art | graphic
    firefly_style_preset: str
    firefly_prompt: str
    reference_films: list = field(default_factory=list)
    color_grading_notes: str = ""
    midjourney_version_params: str = "--ar 16:9 --style raw --v 7"


@dataclass
class Character:
    character_id: str
    canonical_name: str
    hebrew_name: str
    aliases: list
    role: str
    testament: str
    books_appearing_in: list
    book: str
    chapters_active: str
    era: str
    visual_dna: VisualDNA
    voice_profile: VoiceProfile
    emotional_arc: EmotionalArc
    audience_targeting: AudienceTargeting
    ai_generation: AIGenerationProfile
    production_notes: str = ""

    def midjourney_prompt(self, arc: Optional[str] = None) -> str:
        base = self.ai_generation.consistency_seed_prompt
        if arc and arc in self.visual_dna.wardrobe_by_arc:
            base = f"{base}, wearing {self.visual_dna.wardrobe_by_arc[arc]}"
        neg = f" --no {self.ai_generation.negative_prompt}"
        params = f" {self.ai_generation.midjourney_version_params}"
        return f"{base}{neg}{params}"

    def firefly_prompt(self, arc: Optional[str] = None) -> str:
        base = self.ai_generation.firefly_prompt
        if arc and arc in self.visual_dna.wardrobe_by_arc:
            base = f"{base}, wearing {self.visual_dna.wardrobe_by_arc[arc]}"
        return f"{base}, photorealistic, 8k, cinematic film quality"
