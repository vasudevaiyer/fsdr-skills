from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import os


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    skill_repo_ref: str
    skill_router_file: str
    loaded_at: str
    oci_config_path: Path
    oci_config_profile: str
    oci_region: str
    oci_auth_type: str
    ai_classifier_enabled: bool
    ai_classifier_url: str | None
    ai_classifier_model: str | None
    ai_classifier_api_key: str | None
    ai_classifier_timeout_seconds: float
    ai_classifier_oci_endpoint_id: str | None
    ai_classifier_oci_genai_endpoint: str | None
    ai_classifier_oci_model_id: str | None
    ai_classifier_oci_compartment_id: str | None


def get_settings() -> Settings:
    repo_root = Path(__file__).resolve().parent.parent
    return Settings(
        repo_root=Path(os.getenv("SKILL_REPO_PATH", repo_root)),
        skill_repo_ref=os.getenv("SKILL_REPO_REF", "main"),
        skill_router_file=os.getenv("SKILL_ROUTER_FILE", "SKILL.md"),
        loaded_at=datetime.now(timezone.utc).isoformat(),
        oci_config_path=Path(os.getenv("OCI_CONFIG_PATH", Path.home() / ".oci" / "config")),
        oci_config_profile=os.getenv("OCI_PROFILE", "DEFAULT"),
        oci_region=os.getenv("OCI_REGION", "us-chicago-1"),
        oci_auth_type=os.getenv("OCI_AUTH_TYPE", "api_key"),
        ai_classifier_enabled=_env_bool("AI_CLASSIFIER_ENABLED", False),
        ai_classifier_url=os.getenv("AI_CLASSIFIER_URL"),
        ai_classifier_model=os.getenv("AI_CLASSIFIER_MODEL"),
        ai_classifier_api_key=os.getenv("AI_CLASSIFIER_API_KEY"),
        ai_classifier_timeout_seconds=float(os.getenv("AI_CLASSIFIER_TIMEOUT_SECONDS", "10")),
        ai_classifier_oci_endpoint_id=os.getenv("AI_CLASSIFIER_OCI_ENDPOINT_ID") or os.getenv("SOLUTION_COPILOT_ENDPOINT_ID"),
        ai_classifier_oci_genai_endpoint=os.getenv("AI_CLASSIFIER_OCI_GENAI_ENDPOINT") or os.getenv("OCI_GENAI_ENDPOINT"),
        ai_classifier_oci_model_id=os.getenv("AI_CLASSIFIER_OCI_MODEL_ID") or os.getenv("OCI_MODEL_OCID") or os.getenv("OCI_CHAT_MODEL_ID"),
        ai_classifier_oci_compartment_id=os.getenv("AI_CLASSIFIER_OCI_COMPARTMENT_ID") or os.getenv("OCI_COMPARTMENT_OCID"),
    )
