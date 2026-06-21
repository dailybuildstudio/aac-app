from datetime import datetime
from typing import Optional
from ..models.production import ProductionLog, Asset, AssetStatus


def add_asset(log: ProductionLog, asset: Asset) -> None:
    log.assets.append(asset)
    log.last_updated = datetime.now().isoformat()


def update_status(log: ProductionLog, asset_id: str, new_status: str, notes: str = "") -> bool:
    for asset in log.assets:
        if asset.asset_id == asset_id:
            asset.status = new_status
            if notes:
                asset.review_notes = notes
            now = datetime.now().isoformat()
            log.last_updated = now
            if new_status == AssetStatus.APPROVED:
                asset.approved_at = now
            elif new_status == AssetStatus.PUBLISHED:
                asset.published_at = now
            return True
    return False


def set_file_path(log: ProductionLog, asset_id: str, file_path: str) -> bool:
    for asset in log.assets:
        if asset.asset_id == asset_id:
            asset.file_path = file_path
            asset.status = AssetStatus.GENERATED
            log.last_updated = datetime.now().isoformat()
            return True
    return False


def make_asset_id(book: str, asset_type: str, ref: str) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    ref_slug = ref.replace(" ", "_").lower()[:20]
    return f"{book}_{asset_type}_{ref_slug}_{ts}"


def print_dashboard(log: ProductionLog) -> None:
    summary = log.summary()
    total = summary["total"]
    print(f"\n{'='*70}")
    print(f"  PRODUCTION STATUS — {log.book.upper()}")
    print(f"  Last updated: {log.last_updated or 'never'}")
    print(f"{'='*70}")
    print(f"\n  Total assets tracked: {total}")
    print(f"  Completion:           {summary['completion_pct']}%\n")

    status_order = [
        "not_started", "prompt_ready", "generating",
        "generated", "in_review", "approved", "published", "rejected",
    ]
    by_status = summary["by_status"]
    for status in status_order:
        count = by_status.get(status, 0)
        if count == 0:
            continue
        bar = "█" * min(count, 30)
        print(f"  {status:<16} {count:>4}  {bar}")
    print()


def print_character_report(log: ProductionLog, character_id: str) -> None:
    assets = log.by_character(character_id)
    print(f"\n  CHARACTER: {character_id} — {len(assets)} assets\n")
    for a in assets:
        print(f"  [{a.status:<14}] {a.asset_type:<20} {a.platform:<12} {a.arc or ''}")
        if a.review_notes:
            print(f"               Note: {a.review_notes}")
    print()


def print_scene_report(log: ProductionLog, scene_id: str) -> None:
    assets = log.by_scene(scene_id)
    print(f"\n  SCENE: {scene_id} — {len(assets)} assets\n")
    for a in assets:
        print(f"  [{a.status:<14}] {a.asset_type:<20} {a.platform:<12}")
        if a.review_notes:
            print(f"               Note: {a.review_notes}")
    print()
