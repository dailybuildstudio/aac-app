"""
Luke Scene Breakdown Builder
=============================
Manages scene-level data for the Gospel of Luke film project.
Each scene maps to: characters, location, Luke chapter/verse,
estimated runtime, target audience, and AI generation notes.

Usage:
    python build_scenes.py                  # list all scenes
    python build_scenes.py --episode nativity  # scene detail
    python build_scenes.py --audience women    # scenes for audience
"""

import json
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

SCENES = [
    {
        "scene_id": "annunciation_001",
        "title": "The Annunciation",
        "episode_label": "The Beginning",
        "luke_reference": "Luke 1:26-38",
        "characters": ["mary_mother_001"],
        "location": "Nazareth — Mary's home interior",
        "estimated_runtime_min": 4,
        "format": "short_film",
        "emotional_beat": "wonder, fear, surrender, courage",
        "key_moment": "Mary says 'Let it be to me according to your word' — the most consequential yes in history",
        "visual_direction": "Intimate interior. Oil lamp light. Young girl alone. The weight of what she's agreeing to must show on her face. No theatrical angel — the holiness is in her response.",
        "target_audiences": ["catholic", "hispanic_christian", "women", "evangelical_baptist"],
        "social_clip_moment": "The moment she says yes — 30 second clip, extreme close on face",
        "ai_generation_notes": {
            "primary_shot": "CU on Mary's face, oil lamp warm glow, eyes shifting from fear to resolve",
            "midjourney_scene_prompt": "1st century teenage Jewish girl age 14-16, olive warm skin, dark hair under blue-grey headscarf, oil lamp warm light, intimate interior room Nazareth, expression shifting from fear to courage, cinematic photoreal 8k --ar 16:9 --style raw --v 7",
            "runway_video_notes": "Slow push into face. Begin wide — small girl in a large decision. End tight on eyes. No cuts — let it breathe.",
            "audio_notes": "Near silence. Her breathing. Then her voice, quiet and firm."
        }
    },
    {
        "scene_id": "visitation_001",
        "title": "The Visitation — Mary and Elizabeth",
        "episode_label": "The Beginning",
        "luke_reference": "Luke 1:39-56",
        "characters": ["mary_mother_001", "elizabeth_001"],
        "location": "Hill country of Judea — Elizabeth's home",
        "estimated_runtime_min": 6,
        "format": "short_film",
        "emotional_beat": "joy, recognition, prophecy, solidarity between women",
        "key_moment": "Elizabeth cries out — the baby leaps — and then Mary's Magnificat explodes with prophetic fire",
        "visual_direction": "Two women, young and old, bound by impossible pregnancies. The Magnificat should feel like a declaration, not a lullaby — Mary is prophesying justice.",
        "target_audiences": ["women", "catholic", "hispanic_christian", "black_church"],
        "social_clip_moment": "Elizabeth's recognition cry — 20 seconds. Then the opening of the Magnificat — 45 seconds",
        "ai_generation_notes": {
            "primary_shot": "Two women embracing, young and old, both with child, hill country light",
            "midjourney_scene_prompt": "1st century Judean hillside home, teenage Jewish girl and elderly Jewish woman embracing, both pregnant, warm afternoon light through doorway, joy and awe on faces, cinematic photoreal 8k --ar 16:9 --style raw --v 7",
            "audio_notes": "The Magnificat in original Hebrew or Greek with subtitles — it hits differently"
        }
    },
    {
        "scene_id": "nativity_001",
        "title": "The Nativity",
        "episode_label": "The Nativity",
        "luke_reference": "Luke 2:1-20",
        "characters": ["mary_mother_001", "jesus_001"],
        "location": "Bethlehem — stable/cave, then fields with shepherds",
        "estimated_runtime_min": 18,
        "format": "special_episode",
        "emotional_beat": "exhaustion, wonder, the sacred in the ordinary",
        "key_moment": "Not the cleaned-up nativity. She's exhausted. It's cold. The manger is a feeding trough. And somehow — this is it.",
        "visual_direction": "Gritty and real. No glowing baby. The wonder is in the ordinariness of the setting vs the magnitude of what's happening. Shepherds arrive — rough, smelling of sheep, terrified and then laughing with joy.",
        "target_audiences": ["evangelical_baptist", "catholic", "hispanic_christian", "secular_curious", "women", "men"],
        "social_clip_moment": "The moment the baby is laid in the manger — extreme wide to extreme close",
        "ai_generation_notes": {
            "primary_shot": "New mother in rough stone stable, baby in stone feeding trough, single oil lamp, exhausted wonder on face",
            "midjourney_scene_prompt": "1st century Bethlehem stone stable cave interior, young Jewish mother wrapped in dark blue robe, newborn baby in stone manger, single oil lamp, deep shadow, exhausted tender expression, hay straw, cold breath visible, cinematic photoreal 8k --ar 16:9 --style raw --v 7",
            "runway_video_notes": "Begin outside the stable — sound of wind, city noise. Camera slowly moves through low doorway into warm lamplight. Find the mother first. Then the child.",
            "audio_notes": "No choir swell yet. Silence. Then one voice, a capella."
        }
    },
    {
        "scene_id": "baptism_001",
        "title": "The Baptism of Jesus",
        "episode_label": "The Launch",
        "luke_reference": "Luke 3:21-22",
        "characters": ["jesus_001", "john_baptist_001"],
        "location": "Jordan River — wilderness banks",
        "estimated_runtime_min": 5,
        "format": "short_film",
        "emotional_beat": "holy tension, surrender, divine affirmation",
        "key_moment": "John — who has been thundering at everyone — goes still and small when Jesus approaches. Then the voice from heaven.",
        "visual_direction": "The contrast between John's wild energy and Jesus' calm is cinematic gold. The descent of the Spirit as dove — subtle, real, not CGI spectacular.",
        "target_audiences": ["evangelical_baptist", "men", "secular_curious", "youth_gen_z"],
        "social_clip_moment": "John's recognition — 'I need to be baptized by you' — and Jesus' response. 40 seconds.",
        "ai_generation_notes": {
            "primary_shot": "Two men in the Jordan River, wild prophet and calm carpenter, sunlight breaking through clouds",
            "midjourney_scene_prompt": "1st century Jordan River, two Jewish men waist-deep in river water, one wild-haired lean desert prophet in camel hair, one calm bearded man in linen, shaft of light through clouds above, cinematic photoreal dramatic natural light 8k --ar 16:9 --style raw --v 7",
            "runway_video_notes": "Begin underwater — looking up at two pairs of feet. Rise to surface. Find faces."
        }
    },
    {
        "scene_id": "temptation_001",
        "title": "The Temptation in the Wilderness",
        "episode_label": "The Launch",
        "luke_reference": "Luke 4:1-13",
        "characters": ["jesus_001"],
        "location": "Judean wilderness — stark, isolated",
        "estimated_runtime_min": 8,
        "format": "short_film",
        "emotional_beat": "isolation, hunger, psychological warfare, victory",
        "key_moment": "40 days alone. Then the voice. Then the Word spoken back with precision.",
        "visual_direction": "The adversary is never shown as theatrical — the temptations come as thoughts, whispers, internal struggle made visual. Jesus is gaunt, cracked lips, genuinely suffering from fasting.",
        "target_audiences": ["men", "evangelical_baptist", "secular_curious", "youth_gen_z"],
        "social_clip_moment": "Jesus' final response: 'Away from me' — 15 seconds, absolute authority",
        "ai_generation_notes": {
            "primary_shot": "Gaunt bearded Jewish man alone in barren rocky wilderness, cracked lips, thousand-yard stare, spiritual intensity",
            "midjourney_scene_prompt": "1st century Jewish man age 30-33, deeply gaunt from 40-day fast, cracked lips, weathered skin, alone in barren Judean rocky wilderness, intense dark eyes, simple linen robe worn and dusty, harsh desert midday sun, cinematic photoreal 8k --ar 16:9 --style raw --v 7",
            "runway_video_notes": "Timelapse of days passing — light rotating over barren landscape. Find him smaller and smaller in the frame as days pass. Then the final confrontation — tight on eyes."
        }
    },
    {
        "scene_id": "good_samaritan_001",
        "title": "The Parable of the Good Samaritan",
        "episode_label": "The Parables",
        "luke_reference": "Luke 10:25-37",
        "characters": [],
        "location": "Road from Jerusalem to Jericho — rocky dangerous terrain",
        "estimated_runtime_min": 7,
        "format": "short_film",
        "emotional_beat": "indifference, suffering, shocking mercy, 'who is my neighbor?'",
        "key_moment": "The Samaritan stops. Everyone else kept walking. The camera holds on the man in the ditch — and then a shadow falls over him. And it's not who he expected.",
        "visual_direction": "Cast the Samaritan as visually and culturally 'other' to the Jewish audience — the hero is the outsider. Make the priest and Levite sympathetically cowardly, not cartoonishly evil.",
        "target_audiences": ["secular_curious", "black_church", "youth_gen_z", "men", "evangelical_baptist"],
        "social_clip_moment": "The Samaritan kneeling in the dust, pouring oil and wine — 30 seconds. No words.",
        "ai_generation_notes": {
            "primary_shot": "Samaritan man kneeling over wounded Jewish man on rocky road, genuine tender care, dusty landscape",
            "midjourney_scene_prompt": "1st century rocky road Jerusalem to Jericho, Samaritan man in distinctive Samaritan dress kneeling over wounded bloodied Jewish traveler, pouring oil on wounds, dusty arid landscape, late afternoon golden light, cinematic photoreal 8k --ar 16:9 --style raw --v 7",
            "casting_note": "Cast the Samaritan as visually distinct from Jewish characters — this is the entire point of the parable"
        }
    },
    {
        "scene_id": "prodigal_son_001",
        "title": "The Parable of the Prodigal Son",
        "episode_label": "The Parables",
        "luke_reference": "Luke 15:11-32",
        "characters": ["prodigal_father_001"],
        "location": "Judean farmstead, then far country city, then road home",
        "estimated_runtime_min": 14,
        "format": "short_episode",
        "emotional_beat": "entitlement, squandering, rock bottom, longing, the run, extravagant welcome",
        "key_moment": "The father sees him from far off — and runs. A wealthy elder man hiking up his robes and running down the road. Undignified. Doesn't care.",
        "visual_direction": "Three distinct visual worlds: 1) warm farmstead home, 2) cold glittering city that becomes squalor, 3) the long road home. The younger son should look destroyed — not just disheveled but hollowed out.",
        "target_audiences": ["men", "secular_curious", "evangelical_baptist", "hispanic_christian", "black_church"],
        "social_clip_moment": "The father running — wide shot, then close on his face. 45 seconds. This is your most viral clip.",
        "ai_generation_notes": {
            "primary_shot": "Elderly Jewish father hiking up his robes and running down a dusty road, joy and tears mixed, toward a distant disheveled figure",
            "midjourney_scene_prompt": "1st century elderly Jewish landowner age 60, silver beard, robes hiked up as he runs down dusty road toward distant figure, tears streaming, joy breaking through grief, golden sunset behind him, cinematic photoreal 8k --ar 16:9 --style raw --v 7",
            "runway_video_notes": "Begin extreme wide — tiny figure of father on large landscape. He begins to run. Camera SLOWLY zooms in. By the time they embrace we are on his face. No cuts.",
            "audio_notes": "Start in silence. Add music only when he starts running — and let it swell."
        }
    },
    {
        "scene_id": "zacchaeus_001",
        "title": "Zacchaeus in the Sycamore Tree",
        "episode_label": "The Road to Jerusalem",
        "luke_reference": "Luke 19:1-10",
        "characters": ["zacchaeus_001", "jesus_001"],
        "location": "Jericho street — sycamore tree",
        "estimated_runtime_min": 6,
        "format": "short_film",
        "emotional_beat": "desperation to see, public humiliation, unexpected invitation, transformation",
        "key_moment": "Jesus stops. Looks up. In a crowd of hundreds — calls him by name. The most hated man in Jericho. 'Come down. I'm going to your house today.'",
        "visual_direction": "Zacchaeus in the tree is visually comedic at first — powerful tax collector in a tree like a boy. Then Jesus looks up and the whole scene shifts. The crowd's disgust vs Jesus' warmth.",
        "target_audiences": ["men", "secular_curious", "evangelical_baptist", "youth_gen_z"],
        "social_clip_moment": "Jesus looking up into tree — 'Zacchaeus, come down.' His face in the tree. Then the crowd reaction. 30 seconds.",
        "ai_generation_notes": {
            "primary_shot": "Short wealthy Jewish man perched in sycamore tree looking down at crowd, then shocked expression as someone below calls his name",
            "midjourney_scene_prompt": "1st century Jericho crowded street, short stocky well-dressed Jewish tax collector perched awkwardly in sycamore fig tree, fine robes, surprised expression looking down, large crowd below, bright midday light, cinematic photoreal 8k --ar 16:9 --style raw --v 7"
        }
    },
    {
        "scene_id": "last_supper_001",
        "title": "The Last Supper",
        "episode_label": "The Passion",
        "luke_reference": "Luke 22:7-38",
        "characters": ["jesus_001", "peter_001", "judas_001"],
        "location": "Upper room Jerusalem — Passover evening",
        "estimated_runtime_min": 16,
        "format": "feature_sequence",
        "emotional_beat": "intimacy, foreshadowing, betrayal revealed, love persisting through it all",
        "key_moment": "He knows. He knows who will betray him. And he serves them all anyway. He washes feet. He breaks bread. He says 'Do this in remembrance of me.'",
        "visual_direction": "Oil lamp close quarters. Twelve men and the weight of history in one room. Intercutting between Judas's internal world and Jesus's tenderness. The bread — extreme close, his hands, the breaking.",
        "target_audiences": ["evangelical_baptist", "catholic", "men", "secular_curious"],
        "social_clip_moment": "The bread breaking — his hands, close. 15 seconds. Then the cup. Silence.",
        "ai_generation_notes": {
            "primary_shot": "Thirteen men around low table, oil lamps, Passover meal, bread and cup in center, faces half in shadow",
            "midjourney_scene_prompt": "1st century Jerusalem upper room Passover seder, thirteen Jewish men reclining around low table, oil lamps dramatic warm light, unleavened bread and wine cup center frame, faces in shadow and light, cinematic photoreal chiaroscuro 8k --ar 16:9 --style raw --v 7",
            "runway_video_notes": "Slow 360 around the table at table height. Find each face. Linger on Judas. Then return to Jesus."
        }
    },
    {
        "scene_id": "resurrection_001",
        "title": "The Empty Tomb",
        "episode_label": "The Resurrection",
        "luke_reference": "Luke 24:1-12",
        "characters": ["mary_magdalene_001", "peter_001"],
        "location": "Garden tomb Jerusalem — pre-dawn",
        "estimated_runtime_min": 10,
        "format": "feature_sequence",
        "emotional_beat": "grief, confusion, terror, dawning impossible hope",
        "key_moment": "They came to finish burying someone. The stone is moved. He is not there. 'Why do you look for the living among the dead?'",
        "visual_direction": "Pre-dawn blue light. Women moving through sleeping city. Their grief is real — they are not expecting resurrection. The stone moved is not triumphant yet — it's terrifying. Then the light shifts.",
        "target_audiences": ["evangelical_baptist", "women", "catholic", "secular_curious", "men"],
        "social_clip_moment": "Mary at the empty tomb — her face going from grief to confusion to dawning shock. 45 seconds. No words needed.",
        "ai_generation_notes": {
            "primary_shot": "Jewish women at pre-dawn tomb, stone rolled away, blue-grey light, faces of disbelief shifting to awe",
            "midjourney_scene_prompt": "1st century Jerusalem garden tomb pre-dawn, Jewish women in mourning robes, large stone rolled away from tomb entrance, cold blue-grey early morning light, spices and burial cloth in hands, expressions of grief turning to shock, cinematic photoreal 8k --ar 16:9 --style raw --v 7",
            "runway_video_notes": "Begin dark. Sound of sandals on stone. Pre-dawn cold blue. Camera behind women as they approach tomb. See the stone moved. Hold. Then slowly turn to face."
        }
    }
]


def load_characters_index() -> dict:
    """Load characters as a lookup dict by ID."""
    path = DATA_DIR / "characters.json"
    if not path.exists():
        return {}
    with open(path, "r") as f:
        raw = json.load(f)
    return {c["character_id"]: c["canonical_name"] for c in raw["characters"]}


def print_all_scenes(scenes: list, char_index: dict):
    total_runtime = sum(s["estimated_runtime_min"] for s in scenes)
    print(f"\n{'='*70}")
    print(f"  GOSPEL OF LUKE — SCENE BREAKDOWN")
    print(f"  {len(scenes)} scenes | Est. total runtime: {total_runtime} minutes")
    print(f"{'='*70}\n")

    episodes = {}
    for scene in scenes:
        ep = scene["episode_label"]
        episodes.setdefault(ep, []).append(scene)

    for ep, ep_scenes in episodes.items():
        ep_runtime = sum(s["estimated_runtime_min"] for s in ep_scenes)
        print(f"  [{ep.upper()}] — {ep_runtime} min total")
        for s in ep_scenes:
            chars = [char_index.get(c, c) for c in s["characters"]]
            char_str = ", ".join(chars) if chars else "parable characters"
            print(f"    • {s['title']:<40} {s['estimated_runtime_min']:>3} min  [{s['format']}]")
            print(f"      Luke {s['luke_reference']:<15} Characters: {char_str}")
        print()


def print_scene_detail(scene: dict, char_index: dict):
    chars = [char_index.get(c, c) for c in scene["characters"]]
    print(f"\n{'='*70}")
    print(f"  {scene['title'].upper()}")
    print(f"  {scene['luke_reference']} | {scene['estimated_runtime_min']} min | {scene['format']}")
    print(f"{'='*70}")
    print(f"\n  Location:       {scene['location']}")
    print(f"  Characters:     {', '.join(chars) if chars else 'Parable — new characters'}")
    print(f"  Emotional Beat: {scene['emotional_beat']}")
    print(f"\n  KEY MOMENT")
    print(f"  {scene['key_moment']}")
    print(f"\n  VISUAL DIRECTION")
    print(f"  {scene['visual_direction']}")
    print(f"\n  TARGET AUDIENCES: {', '.join(scene['target_audiences'])}")
    print(f"\n  SOCIAL CLIP: {scene['social_clip_moment']}")
    print(f"\n  AI GENERATION")
    ag = scene["ai_generation_notes"]
    print(f"  [Primary Shot] {ag['primary_shot']}")
    print(f"\n  [Midjourney]\n  {ag.get('midjourney_scene_prompt', 'See character prompts')}")
    if "runway_video_notes" in ag:
        print(f"\n  [Runway Notes] {ag['runway_video_notes']}")


def print_audience_scenes(scenes: list, segment: str, char_index: dict):
    matches = [s for s in scenes if segment in s["target_audiences"]]
    print(f"\n{'='*70}")
    print(f"  SCENES FOR: {segment.upper()} — {len(matches)} scenes")
    print(f"{'='*70}\n")
    total = sum(s["estimated_runtime_min"] for s in matches)
    for s in matches:
        print(f"  • {s['title']:<42} {s['estimated_runtime_min']:>3} min")
        print(f"    {s['social_clip_moment']}\n")
    print(f"  Total: {total} minutes of targeted content")


def main():
    parser = argparse.ArgumentParser(description="Luke Scene Breakdown Builder")
    parser.add_argument("--episode", type=str, help="Show detail for scene by id")
    parser.add_argument("--audience", type=str, help="Filter scenes by audience segment")
    args = parser.parse_args()

    char_index = load_characters_index()

    if args.episode:
        match = next((s for s in SCENES if s["scene_id"] == args.episode), None)
        if match:
            print_scene_detail(match, char_index)
        else:
            ids = [s["scene_id"] for s in SCENES]
            print(f"Scene '{args.episode}' not found.\nAvailable: {ids}")
    elif args.audience:
        print_audience_scenes(SCENES, args.audience, char_index)
    else:
        print_all_scenes(SCENES, char_index)
        print(f"  OPTIONS:")
        print(f"  python scripts/build_scenes.py --episode prodigal_son_001")
        print(f"  python scripts/build_scenes.py --audience secular_curious\n")


if __name__ == "__main__":
    main()
