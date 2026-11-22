from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN = re.compile(r"[a-z0-9][a-z0-9+.#-]{1,}")
_STOP = {
    "the",
    "and",
    "for",
    "with",
    "you",
    "our",
    "are",
    "this",
    "that",
    "will",
    "have",
    "from",
    "your",
    "job",
    "role",
    "team",
    "work",
    "about",
    "into",
    "able",
}


def cosine_similarity(left: str, right: str) -> float:
    left_vec = _vector(left)
    right_vec = _vector(right)
    if not left_vec or not right_vec:
        return 0.0
    keys = set(left_vec) | set(right_vec)
    dot = sum(left_vec[key] * right_vec.get(key, 0) for key in keys)
    left_norm = math.sqrt(sum(value * value for value in left_vec.values()))
    right_norm = math.sqrt(sum(value * value for value in right_vec.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (left_norm * right_norm)))


def _vector(text: str) -> Counter[str]:
    tokens = [token for token in _TOKEN.findall((text or "").lower()) if token not in _STOP]
    return Counter(tokens)
