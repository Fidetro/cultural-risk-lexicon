#!/usr/bin/env python3
"""查询中文文化与历史风险关联库。"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = [ROOT / "data" / "entities.json", ROOT / "data" / "events.json"]

CHINESE_DIGITS = {
    "零": "0",
    "〇": "0",
    "○": "0",
    "一": "1",
    "二": "2",
    "两": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
}


@dataclass(frozen=True)
class Candidate:
    entry: dict[str, Any]
    alias: str
    alias_kind: str
    normalized: str


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.strip().lower()
    translated = "".join(CHINESE_DIGITS.get(char, char) for char in text)
    return re.sub(r"[\s\-_./:：,，。·'\"“”‘’（）()\[\]{}]+", "", translated)


def compact_digit_variant(value: str) -> str:
    if value.isdigit() and len(value) > 1:
        return value.lstrip("0") or "0"
    return value


def query_variants(query: str) -> set[str]:
    base = normalize(query)
    variants = {base, compact_digit_variant(base)}
    digits_only = re.sub(r"\D+", "", base)
    if digits_only:
        variants.add(digits_only)
        variants.add(compact_digit_variant(digits_only))
    return {item for item in variants if item}


def load_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for data_file in DATA_FILES:
        with data_file.open("r", encoding="utf-8") as handle:
            entries.extend(json.load(handle))
    return entries


def candidates(entries: Iterable[dict[str, Any]]) -> list[Candidate]:
    result: list[Candidate] = []
    for entry in entries:
        values = [entry["canonical"], entry.get("date", "")]
        values.extend(entry.get("aliases", []))
        for alias in values:
            if alias:
                result.append(Candidate(entry, alias, "alias", normalize(alias)))
                compact = compact_digit_variant(normalize(alias))
                if compact != normalize(alias):
                    result.append(Candidate(entry, alias, "alias", compact))
        for alias in entry.get("fuzzy_aliases", []):
            result.append(Candidate(entry, alias, "fuzzy_alias", normalize(alias)))
            compact = compact_digit_variant(normalize(alias))
            if compact != normalize(alias):
                result.append(Candidate(entry, alias, "fuzzy_alias", compact))
    return result


def score_match(query: str, variants: set[str], candidate: Candidate) -> tuple[str, float] | None:
    if candidate.normalized in variants:
        if candidate.alias_kind == "fuzzy_alias":
            return ("listed-near-match", 0.90)
        return ("exact", 1.0)

    best_ratio = max(SequenceMatcher(None, variant, candidate.normalized).ratio() for variant in variants)
    if best_ratio >= 0.88:
        return ("near-exact", round(best_ratio, 2))

    query_digits = re.sub(r"\D+", "", normalize(query))
    candidate_digits = re.sub(r"\D+", "", candidate.normalized)
    if query_digits and candidate_digits and sorted(query_digits) == sorted(candidate_digits):
        ratio = SequenceMatcher(None, query_digits, candidate_digits).ratio()
        if ratio >= 0.66:
            return ("digit-transposition", round(ratio, 2))

    if best_ratio >= 0.66 and len(normalize(query)) >= 3 and len(candidate.normalized) >= 3:
        return ("fuzzy", round(best_ratio, 2))

    return None


def search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    entries = load_entries()
    variants = query_variants(query)
    matches: dict[str, dict[str, Any]] = {}

    for candidate in candidates(entries):
        scored = score_match(query, variants, candidate)
        if not scored:
            continue

        match_type, confidence = scored
        entry = candidate.entry
        current = matches.get(entry["id"])
        if current and current["confidence"] >= confidence:
            continue

        matches[entry["id"]] = {
            "id": entry["id"],
            "canonical": entry["canonical"],
            "type": entry["type"],
            "date": entry.get("date"),
            "matched_alias": candidate.alias,
            "match_type": match_type,
            "confidence": confidence,
            "risk_categories": entry.get("risk_categories", []),
            "review_note": entry.get("review_note", ""),
            "sources": entry.get("sources", []),
        }

    ordered = sorted(matches.values(), key=lambda item: item["confidence"], reverse=True)
    if any(item["match_type"] == "exact" for item in ordered):
        ordered = [item for item in ordered if item["match_type"] == "exact"]
    return ordered[:limit]


def print_text(results: list[dict[str, Any]], query: str) -> None:
    if not results:
        print(f"未找到匹配：{query}")
        return

    for index, item in enumerate(results, start=1):
        print(f"{index}. 可能关联：{item['canonical']}")
        print(f"   匹配：{query} -> {item['matched_alias']} ({item['match_type']})")
        if item.get("date"):
            print(f"   日期：{item['date']}")
        print(f"   风险类别：{', '.join(item['risk_categories'])}")
        print(f"   置信度：{item['confidence']:.2f}")
        print(f"   复核说明：{item['review_note']}")
        if item["sources"]:
            print(f"   来源：{', '.join(item['sources'])}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="查询中文文化与历史风险关联库。")
    parser.add_argument("query", help="要查询的词、编号、拼音或日期。")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果。")
    parser.add_argument("--limit", type=int, default=5, help="最大匹配数量。")
    args = parser.parse_args(argv)

    results = search(args.query, limit=args.limit)
    if args.json:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print_text(results, args.query)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
