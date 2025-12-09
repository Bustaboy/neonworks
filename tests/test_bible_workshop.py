from __future__ import annotations

from pathlib import Path

from neonworks.agents.llm_backend import DummyBackend
from neonworks.bible.storage import load_bible
from neonworks.bible.workshop import BibleWorkshop
from neonworks.cli import NeonWorksCLI


def _scripted_answers() -> list[str]:
    # Order matches BibleWorkshop.questions
    return [
        "Skyward Isles, a floating-archipelago adventure about rebuilding a shattered sky nation",
        "Hopeful, adventurous, a little wistful",
        "Action RPG / top-down 3/4 camera",
        "Glide between islands, befriend skywhales, clear storm dungeons, upgrade your glider/ship",
        "Traversal flow; Found family; Light survival, heavy vibes",
        "Airi the wind courier; Toma the tinkerer; Elder Mira the guide",
        "Storm barons; Sky pirates; Collapsing weather machine",
        "Sunrise market isle; Cracked lighthouse; Storm-forged ruins",
        "Find the lost songstones; Rebuild the lighthouse; Calm the skywhale",
        "Painterly pixels with soft gradients; Studio Ghibli skies; Teal and amber palette",
        "Teens+ who love cozy adventures; ESRB E10+ vibe",
        "No grimdark gore; Keep combat light; Accessibility first",
        "A skywhale rescue set piece; Glider race through a storm tunnel",
    ]


def test_workshop_creates_graph_and_files(tmp_path):
    workshop = BibleWorkshop(backend=DummyBackend())
    answers = _scripted_answers()

    result = workshop.run(scripted_answers=answers)
    assert result.graph.nodes, "Graph should contain nodes from the brainstorm"

    result.save(tmp_path)

    bible_dir = tmp_path / "bible"
    persisted = load_bible(bible_dir / "bible.json")
    assert persisted.nodes, "Persisted bible should round-trip nodes"

    summary_text = (bible_dir / "summary.md").read_text(encoding="utf-8")
    assert "Skyward Isles" in summary_text
    assert "Glider race" in summary_text

    transcript_text = (bible_dir / "transcript.md").read_text(encoding="utf-8")
    assert "Glide between islands" in transcript_text

    for fname in ("characters.json", "locations.json", "quests.json", "pillars.json"):
        assert (bible_dir / fname).is_file(), f"{fname} should be scaffolded"


def test_cli_guided_bible_automation(tmp_path):
    script = tmp_path / "answers.txt"
    script.write_text("\n".join(_scripted_answers()), encoding="utf-8")

    cli = NeonWorksCLI()
    # Redirect projects root to the temp dir for test isolation.
    cli.projects_root = tmp_path / "projects"
    cli.project_manager.projects_root = cli.projects_root

    success = cli.create_project(
        "guided_demo",
        template="basic_game",
        guided_bible=True,
        guided_script=script,
    )
    assert success

    project_dir = cli.projects_root / "guided_demo"
    bible_path = project_dir / "bible" / "bible.json"
    assert bible_path.is_file()

    graph = load_bible(bible_path)
    assert graph.nodes, "Guided project should have a bible graph"
