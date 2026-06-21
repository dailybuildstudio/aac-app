"""
Production Status Tracker — Bible Film Project
===============================================
Track every asset (images, video clips, voice profiles) through the pipeline.

Usage:
    python scripts/production_tracker.py --dashboard
    python scripts/production_tracker.py --character jesus_001
    python scripts/production_tracker.py --scene nativity_001
    python scripts/production_tracker.py --filter approved
    python scripts/production_tracker.py --add --type character_image --character jesus_001 --platform midjourney --prompt "1st century..."
    python scripts/production_tracker.py --update ASSET_ID --status approved --notes "Approved by director"
    python scripts/production_tracker.py --file ASSET_ID --path output/images/jesus_ministry_01.png
    python scripts/production_tracker.py --seed-luke
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.data_loader import load_book_characters, load_book_scenes, load_production_log, save_production_log
from src.pipeline.status_tracker import (
    add_asset, update_status, set_file_path,
    make_asset_id, print_dashboard, print_character_report, print_scene_report,
)
from src.models.production import Asset, AssetStatus, AssetType, Platform


VALID_STATUSES = [s.value for s in AssetStatus]
VALID_TYPES = [t.value for t in AssetType]
VALID_PLATFORMS = [p.value for p in Platform]


def cmd_dashboard(log):
    print_dashboard(log)
    summary = log.summary()
    if summary["total"] == 0:
        print("  No assets tracked yet. Run --seed-luke to initialize from existing data.")
        print("  Or use --add to register individual assets.\n")


def cmd_filter(log, status):
    assets = log.by_status(status)
    print(f"\n  STATUS: {status.upper()} — {len(assets)} assets\n")
    for a in assets:
        ref = a.character_id or a.scene_id or "?"
        print(f"  {a.asset_id}")
        print(f"    type:     {a.asset_type}")
        print(f"    platform: {a.platform}")
        print(f"    ref:      {ref}")
        if a.file_path:
            print(f"    file:     {a.file_path}")
        if a.review_notes:
            print(f"    notes:    {a.review_notes}")
        print()


def cmd_add(log, args):
    asset_id = make_asset_id(args.book, args.type, args.character or args.scene or "unknown")
    asset = Asset(
        asset_id=asset_id,
        asset_type=args.type,
        platform=args.platform,
        status=AssetStatus.PROMPT_READY,
        prompt_used=args.prompt or "",
        character_id=args.character or "",
        scene_id=args.scene or "",
        arc=args.arc or "",
        created_at=datetime.now().isoformat(),
    )
    add_asset(log, asset)
    save_production_log(log, args.book)
    print(f"\n  Added: {asset_id}")
    print(f"  Status: {asset.status}")
    print(f"  Ref: {asset.character_id or asset.scene_id}\n")


def cmd_update(log, asset_id, status, notes, args):
    if status not in VALID_STATUSES:
        print(f"\nInvalid status '{status}'. Valid: {VALID_STATUSES}\n")
        return
    ok = update_status(log, asset_id, status, notes)
    if ok:
        save_production_log(log, args.book)
        print(f"\n  Updated {asset_id} → {status}\n")
    else:
        print(f"\n  Asset '{asset_id}' not found.\n")


def cmd_file(log, asset_id, file_path, args):
    ok = set_file_path(log, asset_id, file_path)
    if ok:
        save_production_log(log, args.book)
        print(f"\n  Set file path for {asset_id}: {file_path}\n")
    else:
        print(f"\n  Asset '{asset_id}' not found.\n")


def cmd_seed_luke(book="luke"):
    """Initialize production log with all characters and scenes at not_started."""
    characters = load_book_characters(book)
    scenes = load_book_scenes(book)
    log = load_production_log(book)

    existing_ids = {a.asset_id for a in log.assets}
    added = 0

    for char in characters:
        for arc in (list(char.visual_dna.wardrobe_by_arc.keys()) or ["base"]):
            for platform in ["midjourney", "firefly"]:
                aid = f"{book}_character_image_{char.character_id}_{arc}_{platform}"
                if aid not in existing_ids:
                    prompt = (char.midjourney_prompt(arc if arc != "base" else None)
                              if platform == "midjourney"
                              else char.firefly_prompt(arc if arc != "base" else None))
                    asset = Asset(
                        asset_id=aid,
                        asset_type=AssetType.CHARACTER_IMAGE,
                        platform=platform,
                        status=AssetStatus.PROMPT_READY,
                        prompt_used=prompt,
                        character_id=char.character_id,
                        arc=arc,
                        created_at=datetime.now().isoformat(),
                    )
                    log.assets.append(asset)
                    added += 1

        # Voice profile
        vid = f"{book}_voice_profile_{char.character_id}_elevenlabs"
        if vid not in existing_ids:
            log.assets.append(Asset(
                asset_id=vid,
                asset_type=AssetType.VOICE_PROFILE,
                platform=Platform.ELEVENLABS,
                status=AssetStatus.NOT_STARTED,
                prompt_used=char.voice_profile.notes,
                character_id=char.character_id,
                created_at=datetime.now().isoformat(),
            ))
            added += 1

    for scene in scenes:
        for platform in ["midjourney", "firefly"]:
            sid = f"{book}_scene_image_{scene.scene_id}_{platform}"
            if sid not in existing_ids:
                prompt = scene.ai_prompts.midjourney if platform == "midjourney" else scene.ai_prompts.firefly
                log.assets.append(Asset(
                    asset_id=sid,
                    asset_type=AssetType.SCENE_IMAGE,
                    platform=platform,
                    status=AssetStatus.PROMPT_READY,
                    prompt_used=prompt,
                    scene_id=scene.scene_id,
                    created_at=datetime.now().isoformat(),
                ))
                added += 1

        vid_id = f"{book}_scene_video_{scene.scene_id}_runway"
        if vid_id not in existing_ids:
            log.assets.append(Asset(
                asset_id=vid_id,
                asset_type=AssetType.SCENE_VIDEO,
                platform=Platform.RUNWAY,
                status=AssetStatus.NOT_STARTED,
                prompt_used=scene.ai_prompts.runway_video,
                scene_id=scene.scene_id,
                created_at=datetime.now().isoformat(),
            ))
            added += 1

        for clip in scene.social_clip_moments:
            cid = f"{book}_social_clip_{scene.scene_id}_{clip.label[:20].replace(' ', '_').lower()}"
            if cid not in existing_ids:
                log.assets.append(Asset(
                    asset_id=cid,
                    asset_type=AssetType.SOCIAL_CLIP,
                    platform=Platform.RUNWAY,
                    status=AssetStatus.NOT_STARTED,
                    prompt_used=clip.hook,
                    scene_id=scene.scene_id,
                    created_at=datetime.now().isoformat(),
                ))
                added += 1

    log.last_updated = datetime.now().isoformat()
    save_production_log(log, book)
    print(f"\n  Seeded {added} assets into production log for '{book}'.")
    print_dashboard(log)


def main():
    parser = argparse.ArgumentParser(description="Bible Film Project — Production Tracker")
    parser.add_argument("--book", default="luke")
    parser.add_argument("--dashboard", action="store_true")
    parser.add_argument("--character", type=str, help="Report for character ID")
    parser.add_argument("--scene", type=str, help="Report for scene ID")
    parser.add_argument("--filter", type=str, metavar="STATUS", help=f"Filter by status: {VALID_STATUSES}")
    parser.add_argument("--add", action="store_true", help="Register a new asset")
    parser.add_argument("--type", choices=VALID_TYPES, help="Asset type")
    parser.add_argument("--platform", choices=VALID_PLATFORMS, help="Platform")
    parser.add_argument("--prompt", type=str, help="Prompt used to generate asset")
    parser.add_argument("--arc", type=str, help="Wardrobe arc (for character images)")
    parser.add_argument("--update", type=str, metavar="ASSET_ID", help="Update asset status")
    parser.add_argument("--status", type=str, help="New status")
    parser.add_argument("--notes", type=str, default="", help="Review notes")
    parser.add_argument("--file", type=str, metavar="ASSET_ID", help="Set file path for asset")
    parser.add_argument("--path", type=str, help="File path to set")
    parser.add_argument("--seed-luke", action="store_true", help="Initialize from all characters + scenes")
    args = parser.parse_args()

    if args.seed_luke:
        cmd_seed_luke(args.book)
        return

    log = load_production_log(args.book)

    if args.add:
        if not args.type or not args.platform:
            print("\n--add requires --type and --platform\n")
            return
        cmd_add(log, args)
    elif args.update:
        if not args.status:
            print("\n--update requires --status\n")
            return
        cmd_update(log, args.update, args.status, args.notes, args)
    elif args.file:
        if not args.path:
            print("\n--file requires --path\n")
            return
        cmd_file(log, args.file, args.path, args)
    elif args.character:
        print_character_report(log, args.character)
    elif args.scene:
        print_scene_report(log, args.scene)
    elif args.filter:
        cmd_filter(log, args.filter)
    else:
        cmd_dashboard(log)


if __name__ == "__main__":
    main()
