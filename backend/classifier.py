from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Literal
from urllib import error as urllib_error
from urllib import request as urllib_request

import oci
from oci.generative_ai_agent_runtime.models import ChatDetails as AgentChatDetails, CreateSessionDetails
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import (
    ChatDetails as InferenceChatDetails,
    CohereChatRequestV2,
    CohereSystemMessageV2,
    CohereTextContentV2,
    CohereUserMessageV2,
    GenericChatRequest,
    OnDemandServingMode,
    SystemMessage,
    TextContent,
    UserMessage,
)

from .config import get_settings
from .skill_catalog import skill_for_intent

Intent = Literal[
    "introduction",
    "tenancy_onboarding",
    "prerequisites",
    "member_preparation",
    "readiness",
    "create_protection_group",
    "read_inventory",
    "read_protection_group",
    "explore_plans",
    "run_prechecks",
    "start_drill",
    "stop_drill",
    "troubleshooting",
    "unsupported",
]
SubjectType = Literal["general", "tenancy", "member", "protection_group", "drill", "infrastructure"]
MemberType = Literal[
    "none",
    "compute",
    "block_volume",
    "volume_group",
    "file_system",
    "database",
    "autonomous_database",
    "oke",
    "integration_instance",
    "load_balancer",
    "application",
    "custom",
]

VALID_INTENTS: tuple[Intent, ...] = (
    "introduction",
    "tenancy_onboarding",
    "prerequisites",
    "member_preparation",
    "readiness",
    "create_protection_group",
    "read_inventory",
    "read_protection_group",
    "explore_plans",
    "run_prechecks",
    "start_drill",
    "stop_drill",
    "troubleshooting",
    "unsupported",
)
VALID_SUBJECT_TYPES: tuple[SubjectType, ...] = (
    "general",
    "tenancy",
    "member",
    "protection_group",
    "drill",
    "infrastructure",
)
VALID_MEMBER_TYPES: tuple[MemberType, ...] = (
    "none",
    "compute",
    "block_volume",
    "volume_group",
    "file_system",
    "database",
    "autonomous_database",
    "oke",
    "integration_instance",
    "load_balancer",
    "application",
    "custom",
)
TENANCY_REQUIRED_INTENTS = {
    "readiness",
    "create_protection_group",
    "read_inventory",
    "read_protection_group",
    "explore_plans",
    "run_prechecks",
    "start_drill",
    "stop_drill",
    "troubleshooting",
}
AI_CLASSIFIER_SYSTEM_PROMPT = """You classify OCI Full Stack Disaster Recovery requests into a fixed taxonomy. Return JSON only with keys: intent, subject_type, member_type, confidence, reason. Do not include markdown. Use only the allowed values below.

Allowed intents:
- introduction
- tenancy_onboarding
- prerequisites
- member_preparation
- readiness
- create_protection_group
- read_inventory
- read_protection_group
- explore_plans
- run_prechecks
- start_drill
- stop_drill
- troubleshooting
- unsupported

Allowed subject_type values:
- general
- tenancy
- member
- protection_group
- drill
- infrastructure

Allowed member_type values:
- none
- compute
- block_volume
- volume_group
- file_system
- database
- autonomous_database
- oke
- integration_instance
- load_balancer
- application
- custom

Rules:
- Use member_preparation for planning or prerequisite questions about supported FSDR members.
- Use member_preparation when the user asks whether a specific member type can be added to a DRPG or protection group, or what must be done before adding it.
- Use tenancy_onboarding for questions about getting started in a tenancy.
- Use prerequisites for IAM, policy, or prerequisite guidance.
- Use read_protection_group only for inspection, status, or detail questions about an existing DRPG.
- Do not use read_protection_group for member-addition or member-eligibility questions.
- Use explore_plans for DR plan exploration questions.
- Use run_prechecks for precheck execution or evaluation questions.
- Use readiness for broader readiness questions.
- Use unsupported if the request does not fit the taxonomy.
- confidence must be a number between 0 and 1.
"""


@dataclass(frozen=True)
class RouteClassification:
    intent: Intent
    subject_type: SubjectType
    member_type: MemberType
    needs_tenancy_context: bool
    needs_inventory_lookup: bool
    best_skill: str
    confidence: float
    missing_context: list[str] = field(default_factory=list)
    reason: str = ""


INTRO_TERMS = (
    "what is fsdr", "what is oci fsdr", "intro to fsdr", "introduction to fsdr",
    "what fsdr is not", "what can fsdr do", "what can this assistant do", "what is full stack disaster recovery",
)
INVENTORY_TERMS = (
    "compute instance", "compute instances", "boot volume", "block volume", "attached volumes",
    "infrastructure inventory", "instance inventory", "server inventory", "list instances", "show instances",
)
START_DRILL_TERMS = ("start drill", "start a drill", "run drill", "exercise failover")
STOP_DRILL_TERMS = ("stop drill", "stop a drill", "end drill", "terminate drill")
READINESS_TERMS = ("ready for a drill", "readiness", "validate readiness", "is this ready")
PRECHECK_TERMS = ("precheck", "prechecks", "run precheck", "run prechecks", "execute prechecks")
PLAN_TERMS = ("dr plan", "dr plans", "plan steps", "explore plans", "show plans")
DRPG_TERMS = ("drpg", "dr protection group", "protection group details", "inspect protection group", "read protection group")
CREATE_PG_TERMS = ("create protection group", "create drpg", "set up protection group", "build protection group")
PREREQ_TERMS = ("iam polic", "prereq", "policy", "policies", "permissions", "prerequisites")
POLICY_TAILORING_TERMS = ("tailor", "tailored", "customize", "customise", "scope", "operator group", "compartment scope")
POLICY_SCOPE_TERMS = ("policy", "policies", "iam", "permission", "permissions", "access")
TROUBLESHOOTING_TERMS = ("failed", "error", "blocked", "why did", "troubleshoot", "diagnose")
MEMBER_PREP_TERMS = (
    "prepare", "preparation", "before adding", "before add", "member prep", "supported member", "what members can"
)
MEMBER_ADD_TERMS = (
    "add ", "add to", "can i add", "what can i do to add", "before adding", "eligible", "supported"
)
MEMBER_SCOPE_TERMS = ("drpg", "dr protection group", "protection group", "member", "members")


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _strip_json_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def _clean_oci_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.split("#", 1)[0].strip().rstrip(",").strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    return cleaned or None


def _default_subject_for_intent(intent: Intent) -> SubjectType:
    return {
        "introduction": "general",
        "tenancy_onboarding": "tenancy",
        "prerequisites": "tenancy",
        "member_preparation": "member",
        "readiness": "drill",
        "create_protection_group": "protection_group",
        "read_inventory": "infrastructure",
        "read_protection_group": "protection_group",
        "explore_plans": "protection_group",
        "run_prechecks": "drill",
        "start_drill": "drill",
        "stop_drill": "drill",
        "troubleshooting": "drill",
        "unsupported": "general",
    }[intent]


def _build_classification(
    intent: Intent,
    subject_type: SubjectType,
    member_type: MemberType,
    confidence: float,
    has_tenancy_context: bool,
    reason: str,
) -> RouteClassification:
    needs_tenancy_context = intent in TENANCY_REQUIRED_INTENTS
    needs_inventory_lookup = intent == "read_inventory"
    best_skill = skill_for_intent(intent, member_type)
    missing_context: list[str] = []

    if needs_tenancy_context and not has_tenancy_context:
        missing_context.append("selected tenancy")
    if intent == "read_inventory":
        missing_context.append("compartment OCID or instance OCID")
    if intent in {"create_protection_group", "read_protection_group", "explore_plans"}:
        missing_context.append("application or protection group scope")
    if intent in {"readiness", "run_prechecks"}:
        missing_context.append("readiness inputs and protection group status")
    if intent == "member_preparation" and member_type == "none":
        missing_context.append("member type in scope")

    return RouteClassification(
        intent=intent,
        subject_type=subject_type,
        member_type=member_type,
        needs_tenancy_context=needs_tenancy_context,
        needs_inventory_lookup=needs_inventory_lookup,
        best_skill=best_skill,
        confidence=max(0.0, min(confidence, 1.0)),
        missing_context=missing_context,
        reason=reason,
    )


def classify_member_type(message: str) -> MemberType:
    text = message.lower()
    if any(term in text for term in ("oke", "kubernetes", "cluster", "k8s")):
        return "oke"
    if any(term in text for term in ("autonomous database", "autonomous db", "adb", "adw", "atp")):
        return "autonomous_database"
    if any(term in text for term in ("integration instance", "oic", "integration")):
        return "integration_instance"
    if any(term in text for term in ("boot volume", "block volume", "volume group")):
        return "block_volume"
    if any(term in text for term in ("compute", "instance", "vm", "server")):
        return "compute"
    if any(term in text for term in ("database", "dbcs", "data guard", "exadata", "exacc")):
        return "database"
    if any(term in text for term in ("load balancer", "lb", "nlb")):
        return "load_balancer"
    if any(term in text for term in ("application", "app", "workload")):
        return "application"
    return "none"


def _classify_request_heuristic(message: str, has_tenancy_context: bool = False) -> RouteClassification:
    text = " ".join(message.lower().split())
    member_type = classify_member_type(text)

    if _contains_any(text, INTRO_TERMS):
        intent: Intent = "introduction"
        subject_type: SubjectType = "general"
        confidence = 0.99
        reason = "heuristic classifier: The request asks for a high-level FSDR explanation."
    elif _contains_any(text, INVENTORY_TERMS):
        intent = "read_inventory"
        subject_type = "infrastructure"
        confidence = 0.98
        reason = "heuristic classifier: The request is a read-only OCI infrastructure inventory lookup."
    elif _contains_any(text, STOP_DRILL_TERMS):
        intent = "stop_drill"
        subject_type = "drill"
        confidence = 0.97
        reason = "heuristic classifier: The request asks to stop a drill workflow."
    elif _contains_any(text, START_DRILL_TERMS):
        intent = "start_drill"
        subject_type = "drill"
        confidence = 0.97
        reason = "heuristic classifier: The request asks to start a drill workflow."
    elif _contains_any(text, PRECHECK_TERMS):
        intent = "run_prechecks"
        subject_type = "drill"
        confidence = 0.90
        reason = "heuristic classifier: The request asks to run or inspect FSDR prechecks."
    elif _contains_any(text, PLAN_TERMS):
        intent = "explore_plans"
        subject_type = "protection_group"
        confidence = 0.88
        reason = "heuristic classifier: The request asks to inspect DR plans or plan steps."
    elif member_type != "none" and _contains_any(text, MEMBER_ADD_TERMS) and _contains_any(text, MEMBER_SCOPE_TERMS):
        intent = "member_preparation"
        subject_type = "member"
        confidence = 0.93
        member_label = member_type.replace("_", " ")
        reason = f"heuristic classifier: The request asks what is required before adding the {member_label} member type to a DR Protection Group."
    elif _contains_any(text, DRPG_TERMS):
        intent = "read_protection_group"
        subject_type = "protection_group"
        confidence = 0.90
        reason = "heuristic classifier: The request asks to inspect a DR Protection Group."
    elif _contains_any(text, CREATE_PG_TERMS):
        intent = "create_protection_group"
        subject_type = "protection_group"
        confidence = 0.95
        reason = "heuristic classifier: The request asks to create or design a DR Protection Group."
    elif _contains_any(text, POLICY_TAILORING_TERMS) and (_contains_any(text, POLICY_SCOPE_TERMS) or "fsdr" in text):
        intent = "prerequisites"
        subject_type = "tenancy"
        confidence = 0.95
        reason = "heuristic classifier: The request asks to tailor OCI FSDR IAM policy guidance to a tenancy or compartment scope."
    elif _contains_any(text, PREREQ_TERMS):
        intent = "prerequisites"
        subject_type = "tenancy"
        confidence = 0.94
        reason = "heuristic classifier: The request asks about tenancy prerequisites or IAM policies."
    elif _contains_any(text, MEMBER_PREP_TERMS) or member_type != "none":
        intent = "member_preparation"
        subject_type = "member"
        confidence = 0.91 if member_type != "none" else 0.72
        if member_type != "none":
            member_label = member_type.replace("_", " ")
            reason = f"heuristic classifier: The request asks how to prepare the {member_label} member type for FSDR."
        else:
            reason = "heuristic classifier: The request asks about supported members or how to prepare them for FSDR."
    elif _contains_any(text, READINESS_TERMS):
        intent = "readiness"
        subject_type = "drill"
        confidence = 0.86
        reason = "heuristic classifier: The request asks for a readiness or validation assessment."
    elif _contains_any(text, TROUBLESHOOTING_TERMS):
        intent = "troubleshooting"
        subject_type = "drill"
        confidence = 0.68
        reason = "heuristic classifier: The request appears to be troubleshooting a DR workflow or validation issue."
    elif any(term in text for term in ("onboard", "new to oci fsdr", "get started", "tenancy")):
        intent = "tenancy_onboarding"
        subject_type = "tenancy"
        confidence = 0.80
        reason = "heuristic classifier: The request is about onboarding or selecting tenancy context."
    else:
        intent = "unsupported"
        subject_type = "general"
        confidence = 0.40
        reason = "heuristic classifier: The request does not map cleanly to the current FSDR taxonomy."

    return _build_classification(intent, subject_type, member_type, confidence, has_tenancy_context, reason)


def _parse_ai_classification_payload(classification: dict, has_tenancy_context: bool, source: str) -> RouteClassification | None:
    intent = classification.get("intent")
    if intent not in VALID_INTENTS:
        return None
    subject_type = classification.get("subject_type") or _default_subject_for_intent(intent)
    if subject_type not in VALID_SUBJECT_TYPES:
        subject_type = _default_subject_for_intent(intent)
    member_type = classification.get("member_type") or "none"
    if member_type not in VALID_MEMBER_TYPES:
        member_type = "none"

    try:
        confidence = float(classification.get("confidence", 0.75))
    except (TypeError, ValueError):
        confidence = 0.75

    reason_detail = classification.get("reason") or f"classified by {source}"
    return _build_classification(
        intent=intent,
        subject_type=subject_type,
        member_type=member_type,
        confidence=confidence,
        has_tenancy_context=has_tenancy_context,
        reason=f"ai classifier: {reason_detail}",
    )


def _resolve_oci_inference_settings(settings) -> tuple[dict, str | None, str | None, str | None]:
    config = oci.config.from_file(str(settings.oci_config_path), settings.oci_config_profile)
    endpoint = _clean_oci_value(settings.ai_classifier_oci_genai_endpoint) or _clean_oci_value(config.get("oci_genai_endpoint"))
    model_id = (
        _clean_oci_value(settings.ai_classifier_oci_model_id)
        or _clean_oci_value(config.get("model_id"))
        or _clean_oci_value(config.get("oci_model_ocid"))
    )
    compartment_id = _clean_oci_value(settings.ai_classifier_oci_compartment_id) or _clean_oci_value(config.get("oci_compartment_ocid"))
    return config, endpoint, model_id, compartment_id


def _build_oci_inference_request(model_id: str, message: str, has_tenancy_context: bool):
    prompt = "Classify this request and return JSON only:\n" + json.dumps(
        {"message": message, "has_tenancy_context": has_tenancy_context}
    )
    normalized_model_id = model_id.lower()
    if "cohere" in normalized_model_id or "command" in normalized_model_id:
        return CohereChatRequestV2(
            messages=[
                CohereSystemMessageV2(content=[CohereTextContentV2(text=AI_CLASSIFIER_SYSTEM_PROMPT)]),
                CohereUserMessageV2(content=[CohereTextContentV2(text=prompt)]),
            ],
            max_tokens=300,
            temperature=0,
            top_p=0.9,
        )
    return GenericChatRequest(
        messages=[
            SystemMessage(content=[TextContent(text=AI_CLASSIFIER_SYSTEM_PROMPT)]),
            UserMessage(content=[TextContent(text=prompt)]),
        ],
        temperature=0,
        top_p=0.9,
        max_tokens=300,
    )


def _classify_request_with_oci_inference(message: str, has_tenancy_context: bool = False) -> RouteClassification | None:
    settings = get_settings()
    if not settings.ai_classifier_enabled:
        return None

    try:
        config, endpoint, model_id, compartment_id = _resolve_oci_inference_settings(settings)
        if not endpoint or not model_id or not compartment_id:
            return None

        client = GenerativeAiInferenceClient(config, service_endpoint=endpoint)
        response = client.chat(
            InferenceChatDetails(
                compartment_id=compartment_id,
                serving_mode=OnDemandServingMode(model_id=model_id),
                chat_request=_build_oci_inference_request(model_id, message, has_tenancy_context),
            )
        )
        chat_response = response.data.chat_response
        text_parts: list[str] = []
        choices = getattr(chat_response, "choices", None) or []
        if choices:
            message_content = getattr(getattr(choices[0], "message", None), "content", None) or []
            text_parts = [part.text for part in message_content if getattr(part, "text", None)]
        else:
            message = getattr(chat_response, "message", None)
            message_content = getattr(message, "content", None) or []
            text_parts = [part.text for part in message_content if getattr(part, "text", None)]
        if not text_parts:
            return None
        classification = json.loads(_strip_json_fence("\n".join(text_parts)))
    except Exception:
        return None

    return _parse_ai_classification_payload(classification, has_tenancy_context, "OCI inference endpoint")


def _classify_request_with_oci_agent(message: str, has_tenancy_context: bool = False) -> RouteClassification | None:
    settings = get_settings()
    if not settings.ai_classifier_enabled or not settings.ai_classifier_oci_endpoint_id:
        return None

    try:
        config = oci.config.from_file(str(settings.oci_config_path), settings.oci_config_profile)
        client = oci.generative_ai_agent_runtime.GenerativeAiAgentRuntimeClient(config, timeout=(5, int(settings.ai_classifier_timeout_seconds)))
        client.base_client.set_region(settings.oci_region)
        session = client.create_session(
            CreateSessionDetails(display_name="FSDR AI Classifier"),
            agent_endpoint_id=settings.ai_classifier_oci_endpoint_id,
        ).data
        prompt = (
            AI_CLASSIFIER_SYSTEM_PROMPT
            + "\n\nClassify this request and return JSON only:\n"
            + json.dumps({"message": message, "has_tenancy_context": has_tenancy_context})
        )
        result = client.chat(
            agent_endpoint_id=settings.ai_classifier_oci_endpoint_id,
            chat_details=AgentChatDetails(
                user_message=prompt,
                session_id=session.id,
                should_stream=False,
                performed_actions=[],
            ),
        ).data
        content = getattr(getattr(getattr(result, "message", None), "content", None), "text", "") or ""
        classification = json.loads(_strip_json_fence(content))
    except Exception:
        return None

    return _parse_ai_classification_payload(classification, has_tenancy_context, "OCI agent endpoint")


def _classify_request_with_http_ai(message: str, has_tenancy_context: bool = False) -> RouteClassification | None:
    settings = get_settings()
    if not settings.ai_classifier_enabled:
        return None
    if not settings.ai_classifier_url or not settings.ai_classifier_model:
        return None

    payload = {
        "model": settings.ai_classifier_model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": AI_CLASSIFIER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "message": message,
                        "has_tenancy_context": has_tenancy_context,
                    }
                ),
            },
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if settings.ai_classifier_api_key:
        headers["Authorization"] = f"Bearer {settings.ai_classifier_api_key}"

    request = urllib_request.Request(settings.ai_classifier_url, data=body, headers=headers, method="POST")

    try:
        with urllib_request.urlopen(request, timeout=settings.ai_classifier_timeout_seconds) as response:
            parsed = json.loads(response.read().decode("utf-8"))
        content = parsed["choices"][0]["message"]["content"]
        classification = json.loads(_strip_json_fence(content))
    except (urllib_error.URLError, TimeoutError, ValueError, OSError, KeyError, IndexError, TypeError):
        return None

    return _parse_ai_classification_payload(classification, has_tenancy_context, "HTTP AI endpoint")


def _classify_request_with_ai(message: str, has_tenancy_context: bool = False) -> RouteClassification | None:
    settings = get_settings()
    if not settings.ai_classifier_enabled:
        return None

    oci_inference_result = _classify_request_with_oci_inference(message, has_tenancy_context=has_tenancy_context)
    if oci_inference_result is not None:
        return oci_inference_result

    oci_agent_result = _classify_request_with_oci_agent(message, has_tenancy_context=has_tenancy_context)
    if oci_agent_result is not None:
        return oci_agent_result

    return _classify_request_with_http_ai(message, has_tenancy_context=has_tenancy_context)


def classify_request(message: str, has_tenancy_context: bool = False) -> RouteClassification:
    normalized = " ".join(message.lower().split())
    ai_result = _classify_request_with_ai(normalized, has_tenancy_context=has_tenancy_context)
    if ai_result is not None:
        return ai_result
    return _classify_request_heuristic(normalized, has_tenancy_context=has_tenancy_context)
