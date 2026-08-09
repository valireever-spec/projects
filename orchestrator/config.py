"""Configuration management for orchestrator."""

from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from pydantic import BaseModel, Field
from orchestrator.schemas import FrameworkType


class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    enabled: bool = True
    model: str = Field(default="claude-opus-4-8", description="Claude model ID or ollama:model_name")
    timeout_seconds: int = Field(default=300, ge=10)
    context_window_tokens: Optional[int] = None


class GateConfig(BaseModel):
    """Configuration for workflow gates."""
    design_blockers: List[str] = Field(
        default_factory=lambda: ["security", "architecture"],
        description="Gate halts workflow if these blocker types found"
    )
    implementation_blockers: List[str] = Field(
        default_factory=lambda: ["security", "test_coverage"],
        description="Gate halts workflow if these blocker types found"
    )
    verification_blockers: List[str] = Field(
        default_factory=lambda: ["requirement_validation", "security"],
        description="Gate halts workflow if these blocker types found"
    )


class CSFConfig(BaseModel):
    """CSF framework configuration."""
    include_pillars: List[int] = Field(
        default_factory=lambda: list(range(1, 24)),
        description="Pillar IDs to include (1-23)"
    )
    focus_pillars: List[str] = Field(
        default_factory=list,
        description="Pillars to focus design on"
    )
    minimum_score: int = Field(default=70, ge=0, le=100, description="Target score per pillar")


class PillarConfig(BaseModel):
    """8-pillar framework configuration."""
    scoring_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "Architecture Discipline & Traceability": 0.15,
            "Build Quality In / Error-Proofing": 0.15,
            "Verification & Validation": 0.15,
            "Continuous Integration & Safe Delivery": 0.15,
            "Root-Cause Driven Improvement": 0.10,
            "Security & Privacy by Design": 0.15,
            "Observability & Telemetry": 0.10,
            "Maintainability & Sustainable Pace": 0.05,
        }
    )


class TrackerConfig(BaseModel):
    """Tracker integration configuration."""
    url: str = Field(default="http://localhost:8000", description="Tracker API base URL")
    project_id: Optional[int] = None
    api_key: Optional[str] = Field(default=None, description="API key if required")
    auto_create_requirements: bool = True
    auto_create_gaps: bool = True
    timeout_seconds: int = Field(default=30, ge=5)


class NotificationConfig(BaseModel):
    """Notification settings."""
    on_design_complete: List[str] = Field(default_factory=list, description="e.g., ['slack', 'email']")
    on_implementation_complete: List[str] = Field(default_factory=list)
    on_verification_blocker: List[str] = Field(default_factory=list)


class OrchestratorConfig(BaseModel):
    """Main orchestrator configuration."""
    project_name: str
    project_path: str
    framework: FrameworkType = FrameworkType.CSF_21

    agents: Dict[str, AgentConfig] = Field(
        default_factory=lambda: {
            "designer": AgentConfig(timeout_seconds=300),
            "implementer": AgentConfig(timeout_seconds=600),
            "verifier": AgentConfig(timeout_seconds=600),
        }
    )

    gates: GateConfig = Field(default_factory=GateConfig)
    csf: CSFConfig = Field(default_factory=CSFConfig)
    pillars_8: PillarConfig = Field(default_factory=PillarConfig)
    tracker: TrackerConfig = Field(default_factory=TrackerConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)

    class Config:
        """Pydantic config."""
        use_enum_values = True


class ConfigLoader:
    """Load orchestrator configuration from YAML or JSON."""

    @staticmethod
    def load_yaml(path: Path) -> OrchestratorConfig:
        """Load config from YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError("pyyaml required for YAML config. Install: pip install pyyaml")

        with open(path) as f:
            data = yaml.safe_load(f)

        return OrchestratorConfig(**data)

    @staticmethod
    def load_json(path: Path) -> OrchestratorConfig:
        """Load config from JSON file."""
        with open(path) as f:
            data = json.load(f)

        return OrchestratorConfig(**data)

    @staticmethod
    def load(path: Path) -> OrchestratorConfig:
        """Auto-detect and load config (YAML or JSON)."""
        if path.suffix == ".yaml" or path.suffix == ".yml":
            return ConfigLoader.load_yaml(path)
        elif path.suffix == ".json":
            return ConfigLoader.load_json(path)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}. Use .yaml or .json")

    @staticmethod
    def default() -> OrchestratorConfig:
        """Return default configuration."""
        return OrchestratorConfig(
            project_name="default",
            project_path="/home/vali/projects/default"
        )
