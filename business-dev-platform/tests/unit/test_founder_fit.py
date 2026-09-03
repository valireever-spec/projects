"""Unit tests for the edge-first founder-fit scorer."""
import pytest
from backend.analytics.founder_fit import score_founder_fit, W_MARKET


def _domain(slug, skills, channels, remote, capital, drag, lang):
    return {
        "slug": slug,
        "name_de": slug,
        "name_en": slug,
        "skill_tags": skills,
        "channels": channels,
        "remote_capable": remote,
        "capital_intensity": capital,
        "operational_drag": drag,
        "language_leverage": lang,
    }


WRITER_DOMAIN = _domain(
    "copywriting", ["writing", "marketing"], ["content", "network"],
    True, "low", "low", True,
)
FARM_DOMAIN = _domain(
    "pflanzenzucht", ["agriculture", "science"], ["local"],
    False, "high", "high", False,
)

WRITER_PROFILE = {
    "skills": ["writing", "marketing"],
    "channels": ["content", "network"],
    "languages": ["de", "ro"],
    "capital_level": "low",
    "maintenance_preference": "low",
    "remote_only": False,
}


class TestStructure:
    def test_returns_sorted_by_fit_desc(self):
        results = score_founder_fit(
            WRITER_PROFILE, [FARM_DOMAIN, WRITER_DOMAIN], {"copywriting": 50, "pflanzenzucht": 50}
        )
        scores = [r.fit_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_all_fields_present_and_bounded(self):
        results = score_founder_fit(WRITER_PROFILE, [WRITER_DOMAIN], {"copywriting": 100})
        r = results[0]
        assert 0 <= r.fit_score <= 100
        assert r.fit_grade in {"Strong fit", "Good fit", "Possible", "Weak fit"}
        assert r.reasons  # non-empty explanation


class TestEdgeDrivesRanking:
    def test_matching_skills_beats_market_heat(self):
        # Farm domain has a huge market score; writer domain has none.
        # Edge-first ranking must still put the fitting domain first.
        results = score_founder_fit(
            WRITER_PROFILE, [FARM_DOMAIN, WRITER_DOMAIN],
            {"copywriting": 0, "pflanzenzucht": 100},
        )
        assert results[0].slug == "copywriting"

    def test_skill_score_is_fractional_coverage(self):
        profile = {**WRITER_PROFILE, "skills": ["writing"]}  # only half the domain's skills
        r = score_founder_fit(profile, [WRITER_DOMAIN], {"copywriting": 0})[0]
        assert r.skill_match == pytest.approx(17.5)  # 35 * 1/2

    def test_no_matching_skills_scores_zero_skill(self):
        profile = {**WRITER_PROFILE, "skills": ["hardware"]}
        r = score_founder_fit(profile, [WRITER_DOMAIN], {"copywriting": 0})[0]
        assert r.skill_match == 0
        assert "None of your listed skills apply" in " ".join(r.reasons)


class TestConstraintFit:
    def test_low_maintenance_pref_penalizes_high_drag(self):
        low = _domain("low", ["writing"], ["content"], True, "low", "low", False)
        high = _domain("high", ["writing"], ["content"], True, "low", "high", False)
        profile = {**WRITER_PROFILE, "maintenance_preference": "low"}
        res = {r.slug: r for r in score_founder_fit(profile, [low, high], {"low": 0, "high": 0})}
        assert res["low"].constraint_fit > res["high"].constraint_fit

    def test_remote_only_penalizes_onsite_domain(self):
        profile = {**WRITER_PROFILE, "remote_only": True}
        onsite = _domain("onsite", ["writing"], ["content"], False, "low", "low", False)
        r = score_founder_fit(profile, [onsite], {"onsite": 0})[0]
        assert "remote-only" in " ".join(r.reasons)

    def test_capital_over_budget_reduces_fit(self):
        profile = {**WRITER_PROFILE, "capital_level": "low"}
        cheap = _domain("cheap", ["writing"], ["content"], True, "low", "low", False)
        pricey = _domain("pricey", ["writing"], ["content"], True, "high", "low", False)
        res = {r.slug: r for r in score_founder_fit(profile, [cheap, pricey], {"cheap": 0, "pricey": 0})}
        assert res["cheap"].constraint_fit > res["pricey"].constraint_fit


class TestMarketDemotion:
    def test_market_signal_capped_at_weight(self):
        r_hi = score_founder_fit(WRITER_PROFILE, [WRITER_DOMAIN], {"copywriting": 100})[0]
        r_lo = score_founder_fit(WRITER_PROFILE, [WRITER_DOMAIN], {"copywriting": 0})[0]
        assert r_hi.market_signal == W_MARKET  # 15
        assert r_lo.market_signal == 0
        # Market can only ever swing the total by its weight.
        assert r_hi.fit_score - r_lo.fit_score == pytest.approx(W_MARKET)

    def test_perfect_edge_fit_scores_85_without_market(self):
        # Full skill + full channel + language + full constraint, zero market.
        r = score_founder_fit(WRITER_PROFILE, [WRITER_DOMAIN], {"copywriting": 0})[0]
        assert r.fit_score == pytest.approx(85.0)


class TestLanguageLeverage:
    def test_second_language_adds_bonus_on_leverage_domain(self):
        bilingual = {**WRITER_PROFILE, "languages": ["de", "ro"]}
        monolingual = {**WRITER_PROFILE, "languages": ["de"]}
        r_bi = score_founder_fit(bilingual, [WRITER_DOMAIN], {"copywriting": 0})[0]
        r_mono = score_founder_fit(monolingual, [WRITER_DOMAIN], {"copywriting": 0})[0]
        assert r_bi.language_leverage == 5
        assert r_mono.language_leverage == 0

    def test_no_leverage_when_domain_does_not_benefit(self):
        no_lang_domain = _domain("x", ["writing"], ["content"], True, "low", "low", False)
        bilingual = {**WRITER_PROFILE, "languages": ["de", "ro"]}
        r = score_founder_fit(bilingual, [no_lang_domain], {"x": 0})[0]
        assert r.language_leverage == 0
