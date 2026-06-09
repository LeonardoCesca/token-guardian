from __future__ import annotations

import math
import re


WORD_RE = re.compile(r"\S+")
SENTENCE_RE = re.compile(r"[.!?]+")


def estimate_input_tokens(prompt: str) -> int:
    words = len(WORD_RE.findall(prompt))
    chars = len(prompt)
    lines = max(prompt.count("\n") + 1, 1)
    estimated = (chars / 4) + (words * 0.25) + (lines * 2)
    return max(1, math.ceil(estimated))


def estimate_output_tokens(prompt: str) -> int:
    sentences = max(len(SENTENCE_RE.findall(prompt)), 1)
    words = max(len(WORD_RE.findall(prompt)), 1)
    estimated = min(max(int(words * 0.45) + (sentences * 12), 128), 4096)
    return estimated

