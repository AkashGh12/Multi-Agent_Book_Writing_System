"""
orchestrator.py — The central controller for the multi-agent book pipeline.

Run this script to produce the complete 3-chapter book:
    python orchestrator.py

The orchestrator calls each agent in the correct order, passes outputs
between agents, manages revision rounds, and writes the final book to disk.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Optional

from agents import (
    # Agents
    PlannerAgent,
    ResearcherAgent,
    WriterAgent,
    FactCheckerAgent,
    EditorAgent,
    # Data structures
    BookOutline,
    ChapterDraft,
    ChapterOutline,
    EditResult,
    FactCheckResult,
    ResearchPackage,
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def safe_print(msg: str = "") -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_REVISION_ROUNDS = 2   # How many times the Writer may revise a chapter
OUTPUT_FILE = Path(__file__).parent / "final_book.md"

BRIEF = {
    "title": "Pay Me on UPI: How Digital Payments Changed Small Business in India",
    "audience": "First-time small-business owners in India",
    "tone": (
        "Friendly, clear and encouraging, as if a mentor is explaining things "
        "to a new shop owner. Plain English with no jargon; explain any "
        "technical term the first time it appears."
    ),
}


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class Orchestrator:
    """
    Coordinates all five agents to produce the final book.

    Pipeline per chapter:
        1. Planner  -> BookOutline
        2. Researcher -> ResearchPackage   (one per chapter)
        3. Writer   -> ChapterDraft
        4. Fact-Checker + Editor in parallel (simulated sequentially here)
        5. If issues: Writer revises (up to MAX_REVISION_ROUNDS)
        6. Compile final_book.md
    """

    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.fact_checker = FactCheckerAgent()
        self.editor = EditorAgent()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        safe_print("\n" + "=" * 60)
        safe_print("  MULTI-AGENT BOOK PIPELINE")
        safe_print("  'Pay Me on UPI'")
        safe_print("=" * 60 + "\n")

        # -- Stage 1: Planning -----------------------------------------
        safe_print("STAGE 1 - PLANNING")
        safe_print("-" * 40)
        outline: BookOutline = self.planner.run(BRIEF)
        safe_print()

        # -- Stage 2-5: Research -> Write -> Check -> Edit per chapter --
        final_chapters: List[str] = []

        for chapter_outline in outline.chapters:
            chapter_text = self._process_chapter(chapter_outline)
            final_chapters.append(chapter_text)
            safe_print()

        # -- Stage 6: Compile final book -------------------------------
        safe_print("STAGE 6 - COMPILING FINAL BOOK")
        safe_print("-" * 40)
        self._compile_book(outline, final_chapters)

    # ------------------------------------------------------------------
    # Per-chapter pipeline
    # ------------------------------------------------------------------

    def _process_chapter(self, chapter_outline: ChapterOutline) -> str:
        """Run the full pipeline for one chapter. Returns final chapter text."""
        n = chapter_outline.number
        safe_print(f"\nSTAGES 2-5 - CHAPTER {n}: '{chapter_outline.title}'")
        safe_print("-" * 40)

        # Stage 2: Research
        safe_print(f"\n  [Stage 2] Research")
        research: ResearchPackage = self.researcher.run(chapter_outline)

        # Stage 3: Write
        safe_print(f"\n  [Stage 3] Writing")
        draft: ChapterDraft = self.writer.run(chapter_outline, research)

        # Stage 4-5: Fact-check + Edit loop
        for revision_round in range(MAX_REVISION_ROUNDS + 1):
            safe_print(f"\n  [Stage 4] Fact-checking (round {revision_round})")
            fc_result: FactCheckResult = self.fact_checker.run(draft, research)

            safe_print(f"  [Stage 5] Editing (round {revision_round})")
            edit_result: EditResult = self.editor.run(draft)

            # Collect all issues from both agents
            all_issues: List[str] = fc_result.issues + edit_result.issues

            if not all_issues:
                # Both agents approved — chapter is done
                safe_print(f"  [SUCCESS] Chapter {n} approved after {revision_round} revision round(s).")
                return edit_result.edited_text  # type: ignore[return-value]

            # If there are issues and we still have revision rounds left
            if revision_round < MAX_REVISION_ROUNDS:
                safe_print(
                    f"\n  [WARN] Issues found ({len(all_issues)}). "
                    f"Sending back to Writer for revision {revision_round + 1}..."
                )
                for issue in all_issues:
                    safe_print(f"     * {issue}")
                draft = self.writer.run(
                    chapter_outline,
                    research,
                    revision_notes=all_issues,
                    previous_draft=draft,
                )
            else:
                # Exhausted revision rounds — flag in output but continue
                safe_print(
                    f"\n  [WARN] Chapter {n}: max revision rounds reached. "
                    f"Remaining issues will be noted in the book."
                )
                note = (
                    f"\n\n> **Editorial note:** This chapter has {len(all_issues)} "
                    f"unresolved issue(s) after {MAX_REVISION_ROUNDS} revision round(s): "
                    + "; ".join(all_issues)
                )
                return (edit_result.edited_text or self._format_draft(draft)) + note

        # Should not reach here, but satisfy type checker
        return self._format_draft(draft)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _format_draft(self, draft: ChapterDraft) -> str:
        """Formats a ChapterDraft as a markdown string."""
        return (
            f"## Chapter {draft.chapter_number}: {draft.title}\n\n"
            + draft.body
            + f"\n\n{draft.takeaway}\n\n"
            + "### References\n\n"
            + "\n".join(draft.references)
        )

    def _compile_book(self, outline: BookOutline, chapters: List[str]) -> None:
        """Writes the complete book to final_book.md."""
        book_title = BRIEF["title"]
        book_subtitle = "A Guide for First-Time Small-Business Owners in India"

        front_matter = textwrap.dedent(f"""\
        # {book_title}
        ### {book_subtitle}

        ---

        {outline.summary}

        ---

        """)

        full_book = front_matter + "\n\n---\n\n".join(chapters)

        OUTPUT_FILE.write_text(full_book, encoding="utf-8")
        print(f"\n✅ Book written to: {OUTPUT_FILE}")
        print(f"   Chapters: {len(chapters)}")
        print(f"   Total size: {OUTPUT_FILE.stat().st_size:,} bytes")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        Orchestrator().run()
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user.")
        sys.exit(1)
