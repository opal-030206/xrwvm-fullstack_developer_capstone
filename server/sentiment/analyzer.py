"""Sentiment analysis: local lexicon model used by both services.

The Flask microservice exposes this over HTTP; the Django app imports it as a
fallback so the application keeps working when only one process is running.
"""

import re

# Compact but effective English sentiment lexicon.  Values roughly follow the
# -4..+4 valence scale used by VADER.
_LEXICON = {
    "amazing": 3.2, "awesome": 3.2, "fantastic": 3.4, "excellent": 3.2,
    "outstanding": 3.4, "perfect": 3.2, "love": 3.1, "loved": 3.0,
    "great": 2.8, "superb": 3.1, "wonderful": 3.0, "best": 3.1,
    "brilliant": 3.0, "delightful": 2.9, "happy": 2.6, "pleased": 2.4,
    "glad": 2.2, "good": 1.9, "nice": 1.8, "friendly": 2.3,
    "helpful": 2.2, "recommend": 2.4, "recommended": 2.2, "satisfied": 2.2,
    "professional": 2.0, "smooth": 1.7, "easy": 1.6, "quick": 1.3,
    "fast": 1.2, "clean": 1.4, "fair": 1.5, "affordable": 1.7,
    "value": 1.4, "worth": 1.6, "impressed": 2.5, "impressive": 2.6,
    "courteous": 2.1, "responsive": 1.8, "reliable": 2.1, "trustworthy": 2.2,
    "thanks": 1.8, "thank": 1.8, "enjoyed": 2.3, "enjoy": 2.1,

    "bad": -2.5, "terrible": -3.2, "awful": -3.1, "horrible": -3.2,
    "worst": -3.3, "hate": -2.9, "hated": -2.8, "poor": -2.4,
    "disappointed": -2.6, "disappointing": -2.7, "unhappy": -2.4,
    "rude": -2.7, "slow": -1.7, "expensive": -1.6, "overpriced": -2.2,
    "waste": -2.5, "worried": -1.8, "problem": -1.6, "problems": -1.7,
    "issue": -1.4, "issues": -1.5, "broken": -2.1, "defective": -2.3,
    "refund": -1.2, "complaint": -1.8, "angry": -2.6, "frustrated": -2.3,
    "unprofessional": -2.6, "dishonest": -2.9, "scam": -3.2, "cheated": -2.9,
    "mediocre": -1.4, "average": -0.4, "okay": 0.2, "fine": 0.3,
    "acceptable": 0.4, "meh": -0.9,
}

_NEGATORS = {
    "not", "no", "never", "none", "nobody", "nothing", "neither", "nor",
    "cannot", "can't", "don't", "doesn't", "didn't", "won't", "wouldn't",
    "isn't", "aren't", "wasn't", "weren't", "hardly", "barely", "without",
}

_INTENSIFIERS = {
    "very": 1.4, "really": 1.3, "extremely": 1.6, "absolutely": 1.6,
    "totally": 1.4, "so": 1.2, "quite": 1.15, "super": 1.4, "highly": 1.3,
    "incredibly": 1.6, "truly": 1.3, "most": 1.3, "slightly": 0.7,
    "somewhat": 0.75, "little": 0.8,
}

_WORD_RE = re.compile(r"[a-zA-Z']+")


def _score_words(text):
    words = [w.lower().strip("'") for w in _WORD_RE.findall(text or "")]
    if not words:
        return 0.0

    total = 0.0
    hits = 0
    for index, word in enumerate(words):
        value = _LEXICON.get(word)
        if value is None:
            continue
        hits += 1

        # Look back two words for intensifiers and negators.
        window = words[max(0, index - 2):index]
        multiplier = 1.0
        negated = False
        for prev in window:
            if prev in _INTENSIFIERS:
                multiplier *= _INTENSIFIERS[prev]
            if prev in _NEGATORS:
                negated = True
        value *= multiplier
        if negated:
            value *= -0.85
        total += value

    if hits:
        # Dampen the raw sum so long reviews do not saturate the scale.
        total = total / (hits ** 0.5)
    return total


def _label(score):
    if score >= 0.6:
        return "positive"
    if score <= -0.6:
        return "negative"
    return "neutral"


def analyze(text):
    """Return ``{"text", "sentiment", "score", "confidence"}`` for *text*."""
    score = round(_score_words(text), 3)
    magnitude = min(abs(score) / 3.4, 1.0)
    return {
        "text": text,
        "sentiment": _label(score),
        "score": score,
        # Confidence blends magnitude with a floor so neutral text is not
        # reported as a high-confidence prediction.
        "confidence": round(0.5 + (magnitude * 0.5), 3),
    }
