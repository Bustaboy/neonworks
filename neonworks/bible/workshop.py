from __future__ import annotations

"""
Conversational Bible workshop for guided project creation.

This module provides a light, friendly Q&A flow that feels like a
brainstorming session instead of a form. It captures a draft game bible,
turns it into a Graph, and writes reviewable artifacts (JSON + markdown)
so teams can review before diving into subsystem generation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from neonworks.agents.llm_backend import DummyBackend, LLMBackend

from .schema import Character, GameplayRule, Graph, Location, Quest, StyleGuide
from .storage import PathLike, save_bible


def _slugify(text: str, fallback: str) -> str:
    """Create a simple slug usable as an ID."""
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in text)
    cleaned = "_".join(filter(None, cleaned.split("_")))
    return cleaned or fallback


def _split_list(text: str) -> List[str]:
    """
    Split a free-form answer into a list, accepting commas, semicolons,
    or newlines as separators.
    """
    if not text:
        return []
    parts: List[str] = []
    for chunk in text.replace(";", "\n").replace(",", "\n").splitlines():
        item = chunk.strip()
        if item:
            parts.append(item)
    return parts


@dataclass
class WorkshopQuestion:
    """Lightweight question definition."""

    key: str
    prompt: str
    vibe: str


@dataclass
class WorkshopTurn:
    """One question/answer turn."""

    question: str
    answer: str


@dataclass
class BibleDraft:
    """
    Structured snapshot of the brainstorm results.
    """

    title: str
    pitch: str
    tone: str
    genre: str
    camera: str
    core_loop: str
    pillars: List[str]
    main_characters: List[str]
    antagonists: List[str]
    locations: List[str]
    quest_seeds: List[str]
    art_style: str
    inspirations: List[str]
    audience: str
    constraints: str
    setpieces: List[str]

    def to_graph(self) -> Graph:
        """
        Convert the draft into a Bible Graph.
        """
        graph = Graph()

        style_id = _slugify(self.title or "style_guide", "style_guide")
        style_node = StyleGuide(
            id=style_id,
            props={
                "title": self.title,
                "pitch": self.pitch,
                "tone": self.tone,
                "genre": self.genre,
                "camera": self.camera,
                "core_loop": self.core_loop,
                "pillars": self.pillars,
                "art_style": self.art_style,
                "inspirations": self.inspirations,
                "audience": self.audience,
                "constraints": self.constraints,
                "setpieces": self.setpieces,
            },
        )
        graph.add_node(style_node)

        # Pillars become gameplay rules linked to the style guide.
        for idx, pillar in enumerate(self.pillars or [], start=1):
            pillar_id = _slugify(pillar, f"pillar_{idx}")
            node = GameplayRule(id=pillar_id, props={"summary": pillar})
            graph.add_node(node)
            graph.add_edge(style_node.id, "pillar", node.id)

        # Characters (heroes + antagonists) share the Character type but keep role info in props.
        for idx, hero in enumerate(self.main_characters or [], start=1):
            char_id = _slugify(hero, f"hero_{idx}")
            node = Character(id=char_id, props={"name": hero, "role": "hero"})
            graph.add_node(node)
            graph.add_edge(style_node.id, "cast", node.id)

        for idx, foe in enumerate(self.antagonists or [], start=1):
            char_id = _slugify(foe, f"foe_{idx}")
            node = Character(id=char_id, props={"name": foe, "role": "antagonist"})
            graph.add_node(node)
            graph.add_edge(style_node.id, "foe", node.id)

        for idx, loc in enumerate(self.locations or [], start=1):
            loc_id = _slugify(loc, f"location_{idx}")
            node = Location(id=loc_id, props={"name": loc})
            graph.add_node(node)
            graph.add_edge(style_node.id, "set_in", node.id)

        for idx, quest in enumerate(self.quest_seeds or [], start=1):
            quest_id = _slugify(quest, f"quest_{idx}")
            node = Quest(id=quest_id, props={"seed": quest})
            graph.add_node(node)
            graph.add_edge(style_node.id, "quest_seed", node.id)

        return graph

    def to_summary_markdown(self, turns: List[WorkshopTurn]) -> str:
        """Render a human-readable summary."""
        lines = [
            f"# Game Bible Overview: {self.title or 'Untitled'}",
            "",
            f"**Pitch:** {self.pitch}",
            f"**Tone/Feel:** {self.tone}",
            f"**Genre + Camera:** {self.genre} / {self.camera}",
            f"**Core Loop:** {self.core_loop}",
            f"**Art Style:** {self.art_style or 'TBD'}",
            f"**Audience:** {self.audience or 'TBD'}",
            "",
            "## Pillars",
        ]
        lines += [f"- {pillar}" for pillar in (self.pillars or ["TBD"])]
        lines += [
            "",
            "## Cast",
        ]
        lines += [f"- Hero: {name}" for name in (self.main_characters or ["TBD"])]
        lines += [f"- Antagonist: {name}" for name in (self.antagonists or [])]
        lines += [
            "",
            "## Places",
        ]
        lines += [f"- {name}" for name in (self.locations or ["TBD"])]
        lines += [
            "",
            "## Quest Seeds",
        ]
        lines += [f"- {seed}" for seed in (self.quest_seeds or ["TBD"])]
        lines += [
            "",
            "## Inspirations",
        ]
        lines += [f"- {name}" for name in (self.inspirations or ["TBD"])]
        lines += [
            "",
            "## Constraints / Must-Avoid",
            self.constraints or "None noted yet.",
            "",
            "## Set Pieces",
        ]
        lines += [f"- {item}" for item in (self.setpieces or ["TBD"])]
        lines += [
            "",
            "## Conversation Transcript",
        ]
        for turn in turns:
            lines.append(f"**Q:** {turn.question}")
            lines.append(f"**A:** {turn.answer or '(left blank)'}")
            lines.append("")
        return "\n".join(lines)


@dataclass
class BibleWorkshopResult:
    """Outcome of a workshop session."""

    draft: BibleDraft
    graph: Graph
    turns: List[WorkshopTurn]
    summary_md: str

    def save(self, project_root: PathLike) -> None:
        """
        Persist the bible graph and review docs under the project root.
        """
        root = Path(project_root)
        bible_dir = root / "bible"
        bible_dir.mkdir(parents=True, exist_ok=True)

        save_bible(self.graph, bible_dir / "bible.json")

        # Write summary and transcript for review.
        (bible_dir / "summary.md").write_text(self.summary_md, encoding="utf-8")
        transcript_lines = []
        for turn in self.turns:
            transcript_lines.append(f"Q: {turn.question}")
            transcript_lines.append(f"A: {turn.answer or '(left blank)'}")
            transcript_lines.append("")
        (bible_dir / "transcript.md").write_text("\n".join(transcript_lines), encoding="utf-8")

        # Lightweight scaffolds the rest of the pipeline can consume.
        def _write_list(filename: str, nodes: List[Any]) -> None:
            payload = [{"id": node.id, "props": dict(node.props)} for node in nodes]
            (bible_dir / filename).write_text(
                json_dumps(payload), encoding="utf-8"
            )

        from neonworks.bible.schema import Character, Location, Quest, GameplayRule

        _write_list("characters.json", [n for n in self.graph.nodes.values() if isinstance(n, Character)])
        _write_list("locations.json", [n for n in self.graph.nodes.values() if isinstance(n, Location)])
        _write_list("quests.json", [n for n in self.graph.nodes.values() if isinstance(n, Quest)])
        _write_list(
            "pillars.json", [n for n in self.graph.nodes.values() if isinstance(n, GameplayRule)]
        )


def json_dumps(payload: Any) -> str:
    """
    Tiny wrapper to avoid a hard dependency on json at import time for callers
    that want a fast path.
    """
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)


class BibleWorkshop:
    """
    Friendly, conversational bible builder.

    The workshop runs through a handful of cozy prompts, gathers answers,
    and emits structured outputs without forcing the user through rigid forms.
    """

    def __init__(self, backend: Optional[LLMBackend] = None):
        # Backend can be a real LLM; defaults to Dummy for offline/deterministic runs.
        self.backend = backend or DummyBackend()

        self.questions: List[WorkshopQuestion] = [
            WorkshopQuestion(
                key="pitch",
                prompt="What's the spark of this game? Give me the one-sentence fantasy or elevator pitch.",
                vibe="Keep it playful; imagine you are pitching a friend.",
            ),
            WorkshopQuestion(
                key="tone",
                prompt="How should it feel moment-to-moment? Cozy, heroic, grim, slapstick, contemplative?",
                vibe="Think about pacing and emotional beats.",
            ),
            WorkshopQuestion(
                key="genre_camera",
                prompt="What's the genre and camera vibe? (e.g., SNES JRPG with top-down 3/4, 2.5D action-platformer, tactics isometric).",
                vibe="Camera, perspective, and genre tags are all fair game.",
            ),
            WorkshopQuestion(
                key="core_loop",
                prompt="Describe the main loop players repeat that makes this fun.",
                vibe="Collect -> upgrade -> tackle a boss? Social -> quest -> narrative beat?",
            ),
            WorkshopQuestion(
                key="pillars",
                prompt="Name 3-ish design pillars that must stay true.",
                vibe="Short phrases, one per idea.",
            ),
            WorkshopQuestion(
                key="heroes",
                prompt="Who are the heroes/crew and what makes them tick?",
                vibe="List names or archetypes; quick descriptors encouraged.",
            ),
            WorkshopQuestion(
                key="foes",
                prompt="Who's pushing back? Rival factions, villains, or forces of nature?",
                vibe="Give me a few troublemakers.",
            ),
            WorkshopQuestion(
                key="world",
                prompt="Where does this unfold? Key locations, biomes, or hubs.",
                vibe="Paint a quick postcard tour.",
            ),
            WorkshopQuestion(
                key="quests",
                prompt="Pitch a few quest seeds or story beats you know you want.",
                vibe="Short hooks are perfect.",
            ),
            WorkshopQuestion(
                key="art",
                prompt="What's the art direction? Style tags, inspirations, palette ideas.",
                vibe="Think mood board in a sentence.",
            ),
            WorkshopQuestion(
                key="audience",
                prompt="Who is this for, and what rating/age vibe fits?",
                vibe="Player fantasy, accessibility, rating targets.",
            ),
            WorkshopQuestion(
                key="constraints",
                prompt="Any hard constraints or off-limits topics?",
                vibe="What should we avoid or keep minimal?",
            ),
            WorkshopQuestion(
                key="setpieces",
                prompt="Any must-have set pieces or moments you already imagine?",
                vibe="Flashbulb scenes or boss encounters.",
            ),
        ]

    def _compose_question(self, question: WorkshopQuestion, turns: List[WorkshopTurn]) -> str:
        """
        Compose a conversational question, lightly contextualized.
        """
        intro = ""
        if turns:
            last_answer = turns[-1].answer
            if last_answer:
                intro = f"Got it about '{last_answer[:80]}'. "
            else:
                intro = "Thanks. "
        base = f"{intro}{question.prompt} ({question.vibe})"
        # Allow backend to rewrite the tone if desired.
        try:
            return self.backend.generate(base)
        except Exception:
            # Fallback to the base prompt if backend fails.
            return base

    def run(
        self,
        scripted_answers: Optional[Iterable[str]] = None,
        input_fn: Callable[[str], str] = input,
    ) -> BibleWorkshopResult:
        """
        Run the workshop. If `scripted_answers` is provided, it will be
        consumed in order for non-interactive use (tests/automation).
        """
        turns: List[WorkshopTurn] = []
        answer_iter = iter(scripted_answers) if scripted_answers is not None else None

        captured: Dict[str, str] = {}
        for question in self.questions:
            prompt = self._compose_question(question, turns)
            if answer_iter is not None:
                try:
                    raw_answer = next(answer_iter)
                except StopIteration:
                    raw_answer = ""
            else:
                raw_answer = input_fn(f"\n{prompt}\n> ").strip()

            captured[question.key] = raw_answer
            turns.append(WorkshopTurn(question=prompt, answer=raw_answer))

        draft = self._build_draft(captured)
        graph = draft.to_graph()
        summary_md = draft.to_summary_markdown(turns)
        return BibleWorkshopResult(draft=draft, graph=graph, turns=turns, summary_md=summary_md)

    def _build_draft(self, captured: Dict[str, str]) -> BibleDraft:
        """
        Map raw answers into a structured draft.
        """
        pitch = captured.get("pitch", "").strip()
        title = pitch[:60] or "New Game"

        genre_camera = captured.get("genre_camera", "")
        if "/" in genre_camera:
            genre, camera = [part.strip() for part in genre_camera.split("/", 1)]
        else:
            genre = genre_camera.strip()
            camera = ""

        draft = BibleDraft(
            title=title,
            pitch=pitch,
            tone=captured.get("tone", "").strip(),
            genre=genre,
            camera=camera,
            core_loop=captured.get("core_loop", "").strip(),
            pillars=_split_list(captured.get("pillars", "")),
            main_characters=_split_list(captured.get("heroes", "")),
            antagonists=_split_list(captured.get("foes", "")),
            locations=_split_list(captured.get("world", "")),
            quest_seeds=_split_list(captured.get("quests", "")),
            art_style=captured.get("art", "").strip(),
            inspirations=_split_list(captured.get("art", "")),
            audience=captured.get("audience", "").strip(),
            constraints=captured.get("constraints", "").strip(),
            setpieces=_split_list(captured.get("setpieces", "")),
        )
        return draft


def run_workshop_and_save(
    project_root: PathLike,
    backend: Optional[LLMBackend] = None,
    scripted_answers: Optional[Iterable[str]] = None,
) -> BibleWorkshopResult:
    """
    Helper for CLI/editor flows: run a workshop and persist outputs.
    """
    workshop = BibleWorkshop(backend=backend)
    result = workshop.run(scripted_answers=scripted_answers)
    result.save(project_root)
    return result
