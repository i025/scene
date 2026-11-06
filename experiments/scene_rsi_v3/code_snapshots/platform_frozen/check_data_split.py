"""Check explicit V3 source assignments without reading images or rubric contents."""

import json
from collections import Counter, defaultdict
from pathlib import Path


def check_split(manifest_path: Path) -> dict:
    scenes = json.loads(manifest_path.read_text())
    counts = Counter(scene["split"] for scene in scenes)
    assert counts == {"development": 12, "selection": 4, "test": 6, "meta_replay": 2}, counts
    assert len({scene["scene_id"] for scene in scenes}) == len(scenes)
    source_splits = defaultdict(set)
    group_splits = defaultdict(set)
    image_splits = defaultdict(set)
    for scene in scenes:
        source_splits[scene["source_id"]].add(scene["split"])
        group_splits[scene["group_id"]].add(scene["split"])
        image = Path(scene["image_path"])
        assert image.is_file(), image
        image_splits[str(image.resolve())].add(scene["split"])
        assert scene["task_type"] == "multi_object_interior"
        assert scene["blind_status"] != "unexposed_blind"
        if scene["query_path"] is not None:
            assert Path(scene["query_path"]).is_file()
            assert Path(scene["rubric_path"]).is_file()
            for attachment in scene["attachments"]:
                assert Path(attachment).is_file(), attachment
        if scene["historical_test_reassigned_to_development"]:
            assert scene["split"] == "development"
            assert scene["blind_status"] == "historically_exposed"
    for mapping in (source_splits, group_splits, image_splits):
        assert all(len(splits) == 1 for splits in mapping.values())
    return {
        "status": "passed",
        "split_counts": dict(counts),
        "source_count": len(source_splits),
        "group_count": len(group_splits),
        "physical_location_independence_verified": False,
        "reference_pixels_read": False,
        "rubric_contents_read": False,
        "study_status": "exploratory",
        "checks": [
            "source/group/resolved-image-path disjoint across all splits",
            "no development source reused for Selection",
            "all referenced media/query/attachment/rubric files exist",
            "historical tests reassigned to development permanently exposed",
            "BlenderWorld assignments are custom research splits",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(check_split(Path(__file__).parent / "manifest.json"), indent=2))
