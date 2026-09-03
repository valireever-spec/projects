"""
Founder-fit scoring — the edge-first ranking engine.

Inverts the original "trending + low-competition" oracle. Instead of ranking
domains by market heat and hoping the founder has an edge, this ranks domains by
how well they match *this founder's* edge and constraints, and demotes market
heat to a small tiebreaker.

Weighting (0-100):
    skill_match       35   overlap of founder skills with what the domain needs
    channel_match     15   can the founder actually reach these customers?
    language_leverage  5   founder speaks a non-German language the domain rewards
    constraint_fit    30   operational drag / capital / remote vs founder limits
    market_signal     15   the old composite market score, demoted to a tiebreaker

Pure functions, no I/O — matches the analytics/ convention.
"""

from typing import NamedTuple

# Weight budget per component (sums to 100).
W_SKILL = 35
W_CHANNEL = 15
W_LANGUAGE = 5
W_CONSTRAINT = 30
W_MARKET = 15

# Constraint sub-budget (sums to W_CONSTRAINT).
W_DRAG = 12
W_CAPITAL = 10
W_REMOTE = 8

_LEVEL = {"low": 0, "medium": 1, "high": 2}
# Anything not clearly German counts as a leverageable second language.
_GERMAN = {"de", "ger", "deu", "german", "deutsch"}


class FitScore(NamedTuple):
    slug: str
    name_de: str
    name_en: str
    fit_score: float
    fit_grade: str
    skill_match: float
    channel_match: float
    language_leverage: float
    constraint_fit: float
    market_signal: float
    matched_skills: list
    matched_channels: list
    reasons: list


def score_founder_fit(
    profile: dict,
    domains: list,
    market_scores: dict,
) -> list[FitScore]:
    """
    Rank domains by fit to a founder profile.

    Args:
        profile: {
            skills: list[str],           # controlled vocab (see german_domains.json skill_tags)
            channels: list[str],         # content|network|local|cold_outreach|marketplace|paid_ads
            languages: list[str],        # e.g. ["de", "ro"] — a non-German entry unlocks leverage
            capital_level: "low"|"medium"|"high",
            maintenance_preference: "low"|"medium"|"high",  # low = wants a low-maintenance business
            remote_only: bool,
        }
        domains: list of domain dicts (must carry the edge tags added to german_domains.json)
        market_scores: {slug: composite_market_score(0-100)} from the original domain_scorer

    Returns:
        List of FitScore, highest fit first.
    """
    skills = {s.strip().lower() for s in profile.get("skills", []) if s.strip()}
    channels = {c.strip().lower() for c in profile.get("channels", []) if c.strip()}
    languages = {l.strip().lower() for l in profile.get("languages", []) if l.strip()}
    has_second_language = bool(languages - _GERMAN)
    capital_level = profile.get("capital_level", "medium")
    maintenance_pref = profile.get("maintenance_preference", "medium")
    remote_only = bool(profile.get("remote_only", False))

    results = []
    for domain in domains:
        slug = domain.get("slug", "")
        domain_skills = [s.lower() for s in domain.get("skill_tags", [])]
        domain_channels = [c.lower() for c in domain.get("channels", [])]

        matched_skills = sorted(skills & set(domain_skills))
        matched_channels = sorted(channels & set(domain_channels))

        skill_match = _skill_score(matched_skills, domain_skills)
        channel_match = _channel_score(matched_channels)
        language_leverage = (
            W_LANGUAGE if (has_second_language and domain.get("language_leverage")) else 0
        )
        constraint_fit, constraint_reasons = _constraint_score(
            domain, capital_level, maintenance_pref, remote_only
        )
        market_signal = round(market_scores.get(slug, 0) / 100 * W_MARKET, 1)

        fit = round(
            skill_match + channel_match + language_leverage + constraint_fit + market_signal, 1
        )

        results.append(
            FitScore(
                slug=slug,
                name_de=domain.get("name_de", ""),
                name_en=domain.get("name_en", ""),
                fit_score=fit,
                fit_grade=_fit_grade(fit),
                skill_match=round(skill_match, 1),
                channel_match=round(channel_match, 1),
                language_leverage=round(language_leverage, 1),
                constraint_fit=round(constraint_fit, 1),
                market_signal=market_signal,
                matched_skills=matched_skills,
                matched_channels=matched_channels,
                reasons=_build_reasons(
                    matched_skills, matched_channels, language_leverage, constraint_reasons
                ),
            )
        )

    results.sort(key=lambda x: x.fit_score, reverse=True)
    return results


def _skill_score(matched: list, domain_skills: list) -> float:
    """Fraction of the domain's required skills the founder actually has."""
    if not domain_skills:
        return 0.0
    return W_SKILL * (len(matched) / len(domain_skills))


def _channel_score(matched: list) -> float:
    """Reward having at least one viable channel; two or more is full credit."""
    if not matched:
        return 0.0
    return W_CHANNEL * min(1.0, len(matched) / 2)


def _constraint_score(
    domain: dict,
    capital_level: str,
    maintenance_pref: str,
    remote_only: bool,
) -> tuple[float, list]:
    """Score how well the domain fits the founder's hard constraints."""
    reasons = []

    # Operational drag vs how much maintenance the founder will tolerate.
    drag = domain.get("operational_drag", "medium")
    drag_table = {
        "low":    {"low": 12, "medium": 6, "high": 0},
        "medium": {"low": 12, "medium": 10, "high": 5},
        "high":   {"low": 12, "medium": 11, "high": 10},
    }
    drag_score = drag_table.get(maintenance_pref, drag_table["medium"]).get(drag, 6)
    if maintenance_pref == "low" and drag == "high":
        reasons.append("High operational drag — clashes with your low-maintenance goal")
    elif drag == "low":
        reasons.append("Low operational drag — easy to run part-time")

    # Capital intensity the founder can cover.
    capital = domain.get("capital_intensity", "medium")
    gap = _LEVEL.get(capital, 1) - _LEVEL.get(capital_level, 1)
    if gap <= 0:
        capital_score = W_CAPITAL
    elif gap == 1:
        capital_score = 4
        reasons.append(f"Needs more capital ({capital}) than you flagged ({capital_level})")
    else:
        capital_score = 0
        reasons.append(f"Capital-intensive ({capital}) — well above your {capital_level} budget")

    # Remote requirement.
    remote_capable = bool(domain.get("remote_capable", True))
    if remote_only and not remote_capable:
        remote_score = 0
        reasons.append("Requires on-site/local work — you asked for remote-only")
    else:
        remote_score = W_REMOTE

    return drag_score + capital_score + remote_score, reasons


def _fit_grade(fit: float) -> str:
    if fit >= 75:
        return "Strong fit"
    elif fit >= 55:
        return "Good fit"
    elif fit >= 35:
        return "Possible"
    else:
        return "Weak fit"


def _build_reasons(
    matched_skills: list,
    matched_channels: list,
    language_leverage: float,
    constraint_reasons: list,
) -> list:
    reasons = []
    if matched_skills:
        reasons.append("Uses your skills: " + ", ".join(matched_skills))
    else:
        reasons.append("None of your listed skills apply here")
    if matched_channels:
        reasons.append("You can reach customers via: " + ", ".join(matched_channels))
    if language_leverage:
        reasons.append("Your second language is a real advantage in this domain")
    reasons.extend(constraint_reasons)
    return reasons
