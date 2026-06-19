"""
Portfolio-level analytics: aggregate requirement health across all projects.
"""

from typing import Dict, List


class PortfolioAnalytics:
    """Analyzes requirement health across entire portfolio."""

    @staticmethod
    def aggregate_requirement_health(projects_health: Dict[str, List[Dict]]) -> Dict:
        """
        Aggregate health metrics across all projects.

        Args:
            projects_health: Dict mapping project_id -> list of health dicts

        Returns:
            Portfolio-level metrics
        """
        total_requirements = 0
        healthy_count = 0
        at_risk_count = 0
        unvalidated_count = 0
        total_gaps = 0
        critical_risk_count = 0

        all_requirements = []

        for project_id, requirements in projects_health.items():
            for req in requirements:
                total_requirements += 1
                all_requirements.append({
                    "project_id": project_id,
                    **req
                })

                if req["health"] == "Healthy":
                    healthy_count += 1
                elif req["health"] == "At Risk":
                    at_risk_count += 1
                else:  # Unvalidated
                    unvalidated_count += 1

                if req.get("risk_level") == "Critical":
                    critical_risk_count += 1

                total_gaps += req.get("gap_count", 0)

        coverage_percent = (healthy_count / total_requirements * 100) if total_requirements > 0 else 0
        at_risk_percent = (at_risk_count / total_requirements * 100) if total_requirements > 0 else 0

        return {
            "total_requirements": total_requirements,
            "healthy": healthy_count,
            "at_risk": at_risk_count,
            "unvalidated": unvalidated_count,
            "coverage_percent": round(coverage_percent, 1),
            "at_risk_percent": round(at_risk_percent, 1),
            "total_gaps": total_gaps,
            "critical_risk_count": critical_risk_count,
            "all_requirements": all_requirements
        }

    @staticmethod
    def get_top_at_risk_requirements(portfolio_metrics: Dict, limit: int = 10) -> List[Dict]:
        """Get most at-risk requirements across portfolio."""
        at_risk = [r for r in portfolio_metrics["all_requirements"] if r["health"] == "At Risk"]
        # Sort by gap count descending
        at_risk.sort(key=lambda x: x.get("gap_count", 0), reverse=True)
        return at_risk[:limit]

    @staticmethod
    def get_by_project_summary(projects_health: Dict[str, List[Dict]]) -> List[Dict]:
        """Get summary metrics per project."""
        summary = []

        for project_id, requirements in projects_health.items():
            total = len(requirements)
            healthy = sum(1 for r in requirements if r["health"] == "Healthy")
            at_risk = sum(1 for r in requirements if r["health"] == "At Risk")
            total_gaps = sum(r.get("gap_count", 0) for r in requirements)

            coverage = (healthy / total * 100) if total > 0 else 0

            summary.append({
                "project_id": project_id,
                "total_requirements": total,
                "healthy": healthy,
                "at_risk": at_risk,
                "coverage_percent": round(coverage, 1),
                "total_gaps": total_gaps,
                "health_status": "Healthy" if coverage >= 80 else "At Risk" if coverage >= 50 else "Critical"
            })

        # Sort by coverage descending (best projects first)
        summary.sort(key=lambda x: x["coverage_percent"], reverse=True)
        return summary

    @staticmethod
    def get_requirement_category_breakdown(all_requirements: List[Dict]) -> Dict:
        """Break down requirements by category."""
        breakdown = {}

        for req in all_requirements:
            category = req.get("category", "Uncategorized")
            if category not in breakdown:
                breakdown[category] = {
                    "total": 0,
                    "healthy": 0,
                    "at_risk": 0,
                    "unvalidated": 0
                }

            breakdown[category]["total"] += 1
            if req["health"] == "Healthy":
                breakdown[category]["healthy"] += 1
            elif req["health"] == "At Risk":
                breakdown[category]["at_risk"] += 1
            else:
                breakdown[category]["unvalidated"] += 1

        return breakdown

    @staticmethod
    def get_requirement_type_breakdown(all_requirements: List[Dict]) -> Dict:
        """Break down requirements by type (Functional vs Non-Functional)."""
        functional = {
            "total": 0,
            "healthy": 0,
            "at_risk": 0,
            "unvalidated": 0,
            "coverage_percent": 0
        }
        nonfunctional = {
            "total": 0,
            "healthy": 0,
            "at_risk": 0,
            "unvalidated": 0,
            "coverage_percent": 0
        }

        for req in all_requirements:
            req_type = req.get("req_type", "Functional")
            target = functional if req_type == "Functional" else nonfunctional

            target["total"] += 1
            if req["health"] == "Healthy":
                target["healthy"] += 1
            elif req["health"] == "At Risk":
                target["at_risk"] += 1
            else:
                target["unvalidated"] += 1

        # Calculate coverage percentages
        if functional["total"] > 0:
            functional["coverage_percent"] = round(functional["healthy"] / functional["total"] * 100, 1)
        if nonfunctional["total"] > 0:
            nonfunctional["coverage_percent"] = round(nonfunctional["healthy"] / nonfunctional["total"] * 100, 1)

        return {
            "functional": functional,
            "nonfunctional": nonfunctional
        }

    @staticmethod
    def calculate_portfolio_health_score(metrics: Dict) -> Dict:
        """Calculate overall portfolio health score (0-100)."""
        # Formula: (healthy / total) * 100
        score = metrics.get("coverage_percent", 0)

        if score >= 90:
            grade = "A"
            status = "Excellent"
        elif score >= 80:
            grade = "B"
            status = "Good"
        elif score >= 70:
            grade = "C"
            status = "Fair"
        elif score >= 60:
            grade = "D"
            status = "Poor"
        else:
            grade = "F"
            status = "Critical"

        return {
            "score": round(score, 1),
            "grade": grade,
            "status": status,
            "total_requirements": metrics["total_requirements"],
            "met": metrics["healthy"],
            "at_risk": metrics["at_risk"],
            "gaps": metrics["total_gaps"]
        }
