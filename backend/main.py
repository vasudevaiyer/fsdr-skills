from __future__ import annotations

import oci
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .models import (
    AuditEvent,
    Message,
    MessageCreate,
    ComputeInventoryResponse,
    Session,
    SessionCreate,
    SessionMessageResponse,
    SkillVersionResponse,
    TenancyProfile,
    TenancyProfileCreate,
    TenancyProfileUpdate,
)
from .oci_inventory import OciConfigError, OciDependencyError, OciInventoryError, OciInventoryService
from .router import build_assistant_message, route_request
from .store import DEFAULT_USER, STORE, utc_now


app = FastAPI(title="OCI FSDR Assistant API", version="0.1.0")
settings = get_settings()
frontend_dir = settings.repo_root / "frontend"
inventory_service = OciInventoryService(settings)

if frontend_dir.exists():
    app.mount("/ui-static", StaticFiles(directory=frontend_dir), name="ui-static")


def current_user():
    return DEFAULT_USER


def _clean_oci_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.split("#", 1)[0].strip().rstrip(",").strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    return cleaned or None


def _resolved_oci_classifier_status() -> tuple[str | None, str | None]:
    endpoint = _clean_oci_value(settings.ai_classifier_oci_genai_endpoint)
    model = _clean_oci_value(settings.ai_classifier_oci_model_id)

    if endpoint and model:
        return model, endpoint

    if not settings.oci_config_path.exists():
        return model, endpoint

    try:
        config = oci.config.from_file(str(settings.oci_config_path), settings.oci_config_profile)
    except Exception:
        return model, endpoint

    resolved_endpoint = endpoint or _clean_oci_value(config.get("oci_genai_endpoint"))
    resolved_model = (
        model
        or _clean_oci_value(config.get("model_id"))
        or _clean_oci_value(config.get("oci_model_ocid"))
    )
    return resolved_model, resolved_endpoint


def classifier_status_payload() -> dict[str, str | None]:
    if settings.ai_classifier_enabled:
        if settings.ai_classifier_oci_model_id or settings.ai_classifier_oci_genai_endpoint or settings.oci_config_path.exists():
            model, endpoint = _resolved_oci_classifier_status()
            return {
                "classifier_mode": "oci_inference",
                "classifier_model": model or 'config:model_id',
                "classifier_endpoint": endpoint or 'config:oci_genai_endpoint',
            }
        if settings.ai_classifier_oci_endpoint_id:
            return {
                "classifier_mode": "oci_agent_endpoint",
                "classifier_model": None,
                "classifier_endpoint": settings.ai_classifier_oci_endpoint_id,
            }
        if settings.ai_classifier_url and settings.ai_classifier_model:
            return {
                "classifier_mode": "http_ai",
                "classifier_model": settings.ai_classifier_model,
                "classifier_endpoint": settings.ai_classifier_url,
            }
    return {
        "classifier_mode": "heuristic",
        "classifier_model": None,
        "classifier_endpoint": None,
    }


def get_tenancy_or_404(tenancy_id: str) -> TenancyProfile:
    tenancy = STORE.tenancies.get(tenancy_id)
    if tenancy is not None:
        return tenancy

    for candidate in STORE.tenancies.values():
        if candidate.tenancy_ocid == tenancy_id:
            return candidate

    raise HTTPException(status_code=404, detail="tenancy not found")


def get_session_or_404(session_id: str) -> Session:
    session = STORE.sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session


def resolve_compartment_id(tenancy: TenancyProfile, compartment_id: str | None) -> str:
    if compartment_id:
        return compartment_id

    for candidate in tenancy.compartments_in_scope:
        if candidate.startswith("ocid1.compartment."):
            return candidate

    raise HTTPException(
        status_code=400,
        detail="compartment_id is required unless the tenancy profile already stores a compartment OCID in compartments_in_scope",
    )


def derive_onboarding_status(payload: TenancyProfileCreate | TenancyProfileUpdate, persona: str | None = None) -> str:
    current_persona = persona or getattr(payload, "persona", None)
    intended_use = getattr(payload, "intended_use", None)
    if current_persona == "viewer" and intended_use in {"configure", "start-drill", "stop-drill"}:
        return "needs approval"
    if current_persona == "operator" and intended_use == "configure":
        return "needs approval"
    return "ready"


@app.get("/")
def root():
    return {
        "name": "OCI FSDR Assistant API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "ui": "/ui",
    }


@app.get("/ui")
@app.get("/ui/")
def ui():
    return FileResponse(frontend_dir / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", **classifier_status_payload()}


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.get("/api/me")
def get_me():
    return current_user()


@app.get("/api/skills/version", response_model=SkillVersionResponse)
def get_skills_version():
    return SkillVersionResponse(
        repo_ref=settings.skill_repo_ref,
        router_file=settings.skill_router_file,
        loaded_at=settings.loaded_at,
        **classifier_status_payload(),
    )


@app.get("/api/tenancies")
def list_tenancies():
    user = current_user()
    return [tenancy for tenancy in STORE.tenancies.values() if tenancy.owner_user_id == user.id]


@app.post("/api/tenancies")
def create_tenancy(payload: TenancyProfileCreate):
    user = current_user()
    tenancy = TenancyProfile(
        owner_user_id=user.id,
        onboarding_status=derive_onboarding_status(payload),
        **payload.model_dump(),
    )
    STORE.tenancies[tenancy.id] = tenancy
    STORE.add_audit_event(
        AuditEvent(
            user_id=user.id,
            tenancy_profile_id=tenancy.id,
            event_type="tenancy_created",
            summary=f"Created tenancy profile {tenancy.tenancy_name}",
        )
    )
    return {"id": tenancy.id, "onboarding_status": tenancy.onboarding_status}


@app.get("/api/tenancies/{tenancy_id}")
def get_tenancy(tenancy_id: str):
    return get_tenancy_or_404(tenancy_id)


@app.get("/api/tenancies/{tenancy_id}/inventory/compute", response_model=ComputeInventoryResponse)
def get_compute_inventory(tenancy_id: str, compartment_id: str | None = None, region: str | None = None, instance_id: str | None = None):
    tenancy = get_tenancy_or_404(tenancy_id)
    resolved_compartment_id = resolve_compartment_id(tenancy, compartment_id)
    resolved_region = region or tenancy.home_region

    try:
        return inventory_service.get_compute_inventory(
            tenancy_id=tenancy.id,
            compartment_id=resolved_compartment_id,
            region=resolved_region,
            instance_id=instance_id,
        )
    except OciDependencyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except OciConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except OciInventoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OCI inventory lookup failed: {exc}") from exc


@app.patch("/api/tenancies/{tenancy_id}")
def update_tenancy(tenancy_id: str, payload: TenancyProfileUpdate):
    tenancy = get_tenancy_or_404(tenancy_id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(tenancy, key, value)
    if "onboarding_status" not in updates:
        tenancy.onboarding_status = derive_onboarding_status(tenancy, tenancy.persona)
    tenancy.updated_at = utc_now()
    STORE.add_audit_event(
        AuditEvent(
            user_id=tenancy.owner_user_id,
            tenancy_profile_id=tenancy.id,
            event_type="tenancy_updated",
            summary=f"Updated tenancy profile {tenancy.tenancy_name}",
        )
    )
    return tenancy


@app.post("/api/sessions")
def create_session(payload: SessionCreate):
    user = current_user()
    tenancy = get_tenancy_or_404(payload.tenancy_profile_id) if payload.tenancy_profile_id else None
    session = Session(
        user_id=user.id,
        tenancy_profile_id=tenancy.id if tenancy is not None else None,
        current_skill=settings.skill_router_file,
        skill_version=settings.skill_repo_ref,
    )
    STORE.sessions[session.id] = session
    STORE.add_audit_event(
        AuditEvent(
            user_id=user.id,
            tenancy_profile_id=tenancy.id if tenancy is not None else None,
            session_id=session.id,
            event_type="session_created",
            summary=(
                f"Created session for tenancy {tenancy.tenancy_name}"
                if tenancy is not None
                else "Created session without tenancy context"
            ),
        )
    )
    return {"id": session.id, "current_skill": session.current_skill, "skill_version": session.skill_version}


@app.get("/api/sessions")
def list_sessions():
    user = current_user()
    return [session for session in STORE.sessions.values() if session.user_id == user.id]


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    session = get_session_or_404(session_id)
    return {
        "session": session,
        "messages": STORE.messages.get(session_id, []),
    }


@app.post("/api/sessions/{session_id}/messages", response_model=SessionMessageResponse)
def post_session_message(session_id: str, payload: MessageCreate):
    user = current_user()
    session = get_session_or_404(session_id)
    tenancy = get_tenancy_or_404(session.tenancy_profile_id) if session.tenancy_profile_id else None
    decision = route_request(payload.message, tenancy)

    user_message = Message(session_id=session.id, role="user", content=payload.message, routing_reason=decision.reason)
    assistant_text = build_assistant_message(decision, tenancy, session)
    assistant_message = Message(session_id=session.id, role="assistant", content=assistant_text, routing_reason=decision.reason)

    STORE.add_message(user_message)
    STORE.add_message(assistant_message)
    STORE.touch_session(session.id, current_skill=decision.skill)
    STORE.add_audit_event(
        AuditEvent(
            user_id=user.id,
            tenancy_profile_id=tenancy.id if tenancy is not None else None,
            session_id=session.id,
            event_type="message_posted",
            summary=f"Routed message to {decision.skill}",
        )
    )

    return SessionMessageResponse(
        session_id=session.id,
        selected_skill=decision.skill,
        routing_reason=decision.reason,
        assistant_message=assistant_text,
        skill_version=session.skill_version,
        execution_mode=decision.execution_mode,
        invoked_skills=list(decision.invoked_skills),
        member_types=list(decision.member_types),
        **classifier_status_payload(),
    )


@app.get("/api/sessions/{session_id}/messages")
def list_messages(session_id: str):
    get_session_or_404(session_id)
    return STORE.messages.get(session_id, [])


@app.get("/api/audit")
def list_audit_events():
    return STORE.audit_events
