#!/usr/bin/env python3
"""
News Summary Agent for make.fun news-summary-01 competition.
Compiles and writes a structured summary of world news for November 11, 2026
to /output/entry.txt (or a configured output path).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPORT_TITLE = "WORLD NEWS: Wednesday, November 11, 2026"
REPORT_DATE = "2026-11-11"
VERSION = "1.1.0"
MAX_WORD_BUDGET = 1000

SECTIONS: list[tuple[str, str]] = [
    (
        "THE BIG PICTURE",
        "A day of mixed signals in global affairs: US-mediated Russia-Ukraine peace talks "
        "resumed in Abu Dhabi for the first time in nine months, yielding an agreement in "
        "principle on a major prisoner exchange but no breakthrough on ending the five-year "
        'war. Meanwhile, President Trump declared the Iran conflict "over in military terms" '
        "while simultaneously threatening strikes on Iranian sites, as Nvidia's Jensen Huang "
        "faced an FBI investigation and lawsuit over an alleged affair with a Chinese spy "
        "that erased $430 billion from the company's value.",
    ),
    (
        "AMERICAS",
        "The US House voted 211-204 to block impeachment charges against Defense Secretary "
        "Pete Hegseth, with Republicans burying the resolution in committee. Eleven "
        'Democrats skipped the vote, including Nancy Pelosi. Trump hailed the outcome as '
        '"exoneration." The White House countered Democratic oversight plans with a warning '
        'letter claiming such probes could constitute "blatant criminality." Consumer prices '
        "rose 0.4% in October, exceeding forecasts.",
    ),
    (
        "EUROPE & UK",
        "A US Army soldier was arrested in Britain on suspicion of attempting to steal NATO "
        "secrets for Russia—the Kremlin denied involvement. In a separate case, the US "
        "charged three men linked to Iran over plotted attacks including an incident at "
        "RAF Fairford. The UK probed the base plot as House GOP selected new leadership. "
        "Portugal canceled over 300 flights and closed schools as Storm Charles approached. "
        "Schools across Italy evacuated after email bomb threats.",
    ),
    (
        "MIDDLE EAST",
        "Israeli forces killed at least eight Palestinians in Gaza, including a father and "
        "his 13-year-old son, despite a US-brokered ceasefire. Since the deal took effect "
        "last October, over 1,600 Palestinians have been killed. Yemen's Houthis claimed "
        "missile and drone strikes on Saudi airports and oil facilities; Saudi defenses "
        "intercepted seven projectiles including cruise missiles aimed at Riyadh. Iran "
        'designated Argentina\'s navy and air force as "terrorist organizations" in '
        "reciprocal move.",
    ),
    (
        "CLIMATE & ENVIRONMENT",
        "COP31 opened in Antalya, Turkey, with a notable absence: leaders from the US, "
        "China, and India—the world's top three emitters—skipped the summit. Turkish "
        "President Erdogan simultaneously celebrated new oil fields in the Gabar Mountains. "
        "Greta Thunberg attended her first climate summit since 2021. The Global Carbon "
        "Project reported fossil fuel emissions are projected to decline 0.4% in 2026, "
        "attributed to Iran conflict disruptions and clean energy expansion.",
    ),
    (
        "HEALTH & HUMANITARIAN",
        "The Democratic DRC Ebola outbreak surpassed 11,000 cases with "
        "5,387 deaths—the country's deadliest ever. The Bundibugyo virus strain has no "
        "known vaccine and has spread to Uganda, Kenya, and Nigeria. Kenya discharged its "
        "last Ebola patient from a separate outbreak. A migrant boat capsized off Senegal, "
        "killing at least 39. Over one million Lebanese face acute food shortages.",
    ),
    (
        "TECH & BUSINESS",
        "Anthropic set an IPO price range valuing the company at $1.4 trillion. Oura "
        "acquired medical AI chatbot firm Counsel Health for $625 million. Paul McCartney "
        "became a billionaire according to Forbes, with net worth of $1.4 billion, ranking "
        "as the world's third richest musician behind Jay-Z and Taylor Swift. The SS United "
        "States, the historic ocean liner, will sink off Florida to become the world's "
        "largest artificial reef. WuXi AppTec was removed from the US list of Chinese "
        "military companies.",
    ),
    (
        "OTHER NOTABLE",
        "Trinidad and Tobago's highest court decriminalized same-sex relations. Indonesia's "
        "Vice President Gibran Rakabuming Raka resigned. Eleven Pakistani police officers "
        "were killed in an attack in Kohat. A 3.9 magnitude earthquake struck Shimla, India. "
        "India simplified its visa regime, cutting categories from 13 to 9. The EU enacted "
        "the Digital Fairness Act targeting loot boxes and addictive features in gaming and "
        "social platforms. Russia's ambassador to the US, Alexander Darchiev, died suddenly "
        "at age 66. Brent crude settled at $92.76 as the Nasdaq gained 1.6% on AI stock rally.",
    ),
]


def render_summary(
    title: str = REPORT_TITLE,
    sections: list[tuple[str, str]] = SECTIONS,
) -> str:
    """Format the title and news sections into the final report text."""
    blocks = [title]
    for heading, body in sections:
        blocks.append(f"{heading}\n{body}")
    return "\n\n".join(blocks) + "\n"


def compute_metrics(text: str) -> dict[str, int]:
    """Calculate character, word, and line counts for the rendered summary."""
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines()),
    }


def resolve_output_path(cli_output: str | None) -> Path:
    """Resolve the target output file path from CLI arg, env var, or default."""
    if cli_output:
        return Path(cli_output)
    env_file = os.environ.get("NEWS_OUTPUT_FILE")
    if env_file:
        return Path(env_file)
    output_dir = os.environ.get("OUTPUT_DIR", "/output")
    return Path(output_dir) / "entry.txt"


def write_summary(output_path: Path, content: str) -> None:
    """Write the rendered summary to disk as UTF-8."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def validate_sections(sections: list[tuple[str, str]]) -> None:
    """Ensure every section has a non-empty heading and body."""
    if not sections:
        raise ValueError("At least one news section is required.")
    for heading, body in sections:
        if not heading.strip() or not body.strip():
            raise ValueError(f"Invalid empty section detected: {heading!r}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write the November 11, 2026 world news summary."
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (defaults to $NEWS_OUTPUT_FILE or $OUTPUT_DIR/entry.txt).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the rendered summary to stdout without writing a file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output metadata and sections as JSON to stdout.",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Display summary metrics without printing full text.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point for generating and writing the news summary."""
    args = parse_args(argv)
    validate_sections(SECTIONS)
    summary = render_summary()
    metrics = compute_metrics(summary)

    if args.json:
        payload = {
            "title": REPORT_TITLE,
            "report_date": REPORT_DATE,
            "version": VERSION,
            "section_count": len(SECTIONS),
            "char_count": metrics["characters"],
            "word_count": metrics["words"],
            "line_count": metrics["lines"],
            "sections": [{"heading": h, "body": b} for h, b in SECTIONS],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.stats_only:
        print(f"Report: {REPORT_TITLE} (v{VERSION})")
        print(f"Sections: {len(SECTIONS)}")
        print(f"Words: {metrics['words']}")
        print(f"Characters: {metrics['characters']}")
        return 0

    if args.dry_run:
        sys.stdout.write(summary)
        return 0

    output_path = resolve_output_path(args.output)
    write_summary(output_path, summary)
    print(f"Summary written to {output_path}")
    print(
        f"Stats: {len(SECTIONS)} sections, {metrics['words']} words, "
        f"{metrics['characters']} characters"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
