"""Integration tests for export endpoints."""
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.core.config import SESSIONS_DIR


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_session(tmp_path, monkeypatch):
    """Create a sample session with minimal data."""
    # Mock SESSIONS_DIR
    monkeypatch.setattr("backend.core.config.SESSIONS_DIR", tmp_path)
    monkeypatch.setattr("backend.api.routers.export.SESSIONS_DIR", tmp_path)
    monkeypatch.setattr("backend.services.plan_service.SESSIONS_DIR", tmp_path)

    session_id = "test-session-001"
    session_file = tmp_path / f"{session_id}.json"

    session_data = {
        "session_id": session_id,
        "profile": {
            "business_name": "Test Business",
            "domain_slug": "online-consulting",
            "city": "Berlin",
            "legal_form": "Einzelunternehmen",
            "target_market": "Small businesses",
            "unique_value_proposition": "Quick consulting",
            "founder_background": "10 years experience",
        },
        "market_analysis": {
            "market": {
                "market_size_estimate": "€50M",
                "growth_rate_pct": 15,
                "market_maturity": "Growing"
            },
            "competition": {
                "level": "medium",
                "main_players": ["Competitor A", "Competitor B"],
                "barriers_to_entry": ["High expertise required"],
                "differentiation_opportunities": ["Better pricing"]
            }
        },
        "financial_projection": {
            "startup_costs": {"total": 25000, "office": 5000, "equipment": 10000},
            "revenue_model": "Project-based pricing",
            "monthly_revenue_estimate": 5000,
            "break_even_month": 6,
            "break_even_achievable": True,
            "break_even_monthly_revenue": 3000,
            "key_metrics": {
                "year_1": {
                    "total_revenue": 60000,
                    "net_income": 15000,
                    "ebitda_margin_pct": 25.0
                },
                "year_3": {
                    "total_revenue": 180000,
                    "net_income": 60000,
                }
            },
            "scenarios": {
                "conservative": {
                    "year_1": {"total_revenue": 40000, "ebitda_margin_pct": 15.0},
                    "year_3": {"total_revenue": 120000}
                },
                "base": {
                    "year_1": {"total_revenue": 60000, "ebitda_margin_pct": 25.0},
                    "year_3": {"total_revenue": 180000}
                },
                "optimistic": {
                    "year_1": {"total_revenue": 80000, "ebitda_margin_pct": 35.0},
                    "year_3": {"total_revenue": 240000}
                }
            },
            "months_1_12": [],
            "months_13_24": [],
            "months_25_36": []
        },
        "risk_assessment": {
            "overall_risk_level": "medium",
            "risk_score": 45,
            "risk_factors": [
                {"name": "Market Saturation", "score": 5, "description": "Low saturation"}
            ],
            "top_3_risks": [
                {"title": "Cash flow risk", "score": 8, "description": "Early stage"}
            ]
        }
    }

    with open(session_file, "w") as f:
        json.dump(session_data, f)

    return session_id, session_file


class TestExportMarkdown:
    def test_export_markdown_success(self, client, sample_session):
        """Test successful markdown export."""
        session_id, _ = sample_session

        response = client.get(f"/export/plan/{session_id}/markdown")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "Test_Business_plan.md" in response.headers["content-disposition"]

        content = response.text
        assert "Geschäftsplan: Test Business" in content
        assert "Executive Summary" in content
        assert "Test Business" in content
        assert "Berlin" in content

    def test_export_markdown_session_not_found(self, client):
        """Test markdown export with non-existent session."""
        response = client.get("/export/plan/nonexistent/markdown")

        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]


class TestExportHTML:
    def test_export_html_success(self, client, sample_session):
        """Test successful HTML export."""
        session_id, _ = sample_session

        response = client.get(f"/export/plan/{session_id}/html")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "Geschäftsplan" in content
        assert "Test Business" in content
        assert "Executive Summary" in content

    def test_export_html_session_not_found(self, client):
        """Test HTML export with non-existent session."""
        response = client.get("/export/plan/nonexistent/html")

        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_export_html_contains_styling(self, client, sample_session):
        """Test that HTML export contains styling."""
        session_id, _ = sample_session

        response = client.get(f"/export/plan/{session_id}/html")

        assert response.status_code == 200
        content = response.text

        # Check for CSS styling
        assert "<style>" in content
        assert "font-family" in content
        assert "@media print" in content

    def test_export_html_contains_all_sections(self, client, sample_session):
        """Test that HTML export contains all plan sections."""
        session_id, _ = sample_session

        response = client.get(f"/export/plan/{session_id}/html")

        assert response.status_code == 200
        content = response.text

        # Check for all major sections
        sections = [
            "Executive Summary",
            "Unternehmensbeschreibung",
            "Marktanalyse",
            "Finanzplan",
            "Risikobewertung",
            "Regulatorische Anforderungen",
            "Wettbewerbsvorteile",
            "90-Tage-Aktionsplan",
        ]

        for section in sections:
            assert section in content


class TestExportSummary:
    def test_export_summary_success(self, client, sample_session):
        """Test export summary endpoint."""
        session_id, _ = sample_session

        response = client.get(f"/export/{session_id}/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == session_id
        assert data["business_name"] == "Test Business"
        assert data["domain"] == "online-consulting"
        assert data["city"] == "Berlin"
        assert data["legal_form"] == "Einzelunternehmen"

        # Check export options
        assert len(data["export_options"]) == 2
        assert data["export_options"][0]["format"] == "markdown"
        assert data["export_options"][1]["format"] == "html"

    def test_export_summary_session_not_found(self, client):
        """Test export summary with non-existent session."""
        response = client.get("/export/nonexistent/summary")

        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]


class TestExportIntegration:
    def test_full_export_workflow(self, client, sample_session):
        """Test complete export workflow from summary to download."""
        session_id, _ = sample_session

        # 1. Get export summary
        summary_response = client.get(f"/export/{session_id}/summary")
        assert summary_response.status_code == 200

        summary_data = summary_response.json()
        assert summary_data["business_name"] == "Test Business"

        # 2. Export markdown
        md_response = client.get(f"/export/plan/{session_id}/markdown")
        assert md_response.status_code == 200
        assert "# Geschäftsplan:" in md_response.text

        # 3. Export HTML
        html_response = client.get(f"/export/plan/{session_id}/html")
        assert html_response.status_code == 200
        assert "<!DOCTYPE html>" in html_response.text

    def test_export_handles_missing_optional_fields(self, client, tmp_path, monkeypatch):
        """Test export with minimal session data."""
        monkeypatch.setattr("backend.core.config.SESSIONS_DIR", tmp_path)
        monkeypatch.setattr("backend.api.routers.export.SESSIONS_DIR", tmp_path)
        monkeypatch.setattr("backend.services.plan_service.SESSIONS_DIR", tmp_path)

        session_id = "minimal-session"
        session_file = tmp_path / f"{session_id}.json"

        # Minimal session data
        minimal_session = {
            "session_id": session_id,
            "profile": {"business_name": "Minimal Business"}
        }

        with open(session_file, "w") as f:
            json.dump(minimal_session, f)

        # Should not crash with missing data
        response = client.get(f"/export/plan/{session_id}/markdown")
        assert response.status_code == 200

        response = client.get(f"/export/plan/{session_id}/html")
        assert response.status_code == 200

    def test_markdown_file_download_headers(self, client, sample_session):
        """Test that markdown export has correct download headers."""
        session_id, _ = sample_session

        response = client.get(f"/export/plan/{session_id}/markdown")

        # Check download headers
        assert "attachment" in response.headers["content-disposition"]
        assert ".md" in response.headers["content-disposition"]
        assert response.headers["content-type"].startswith("text/markdown")

    def test_html_export_printable(self, client, sample_session):
        """Test that HTML export includes print-friendly CSS."""
        session_id, _ = sample_session

        response = client.get(f"/export/plan/{session_id}/html")

        assert response.status_code == 200
        content = response.text

        # Should include print media queries
        assert "@media print" in content
        # Should include page break styles
        assert "page-break" in content or "break" in content.lower()
