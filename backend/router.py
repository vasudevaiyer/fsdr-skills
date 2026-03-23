from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from .classifier import (
    CREATE_PG_TERMS,
    DRPG_TERMS,
    INTRO_TERMS,
    INVENTORY_TERMS,
    PLAN_TERMS,
    PRECHECK_TERMS,
    PREREQ_TERMS,
    READINESS_TERMS,
    START_DRILL_TERMS,
    STOP_DRILL_TERMS,
    TROUBLESHOOTING_TERMS,
    classify_member_type,
    classify_request,
)
from .models import Session, TenancyProfile
from .skill_catalog import (
    ALLOWED_SKILLS,
    CREATE_PROTECTION_GROUP_SKILL,
    DEFAULT_ROUTER_SKILL,
    GENERIC_MEMBER_PREPARATION_SKILL,
    INTRO_SKILL,
    MEMBER_PREPARATION_SKILLS,
    POLICY_TAILORING_SKILL,
    PREREQUISITES_SKILL,
    READINESS_SKILL,
    READ_INFRASTRUCTURE_SKILL,
    START_DRILL_SKILL,
    STOP_DRILL_SKILL,
    TENANCY_ONBOARD_SKILL,
    TENANCY_OPERATIONS_SKILL,
    skill_for_member_preparation,
    skill_requires_tenancy,
)


@dataclass(frozen=True)
class RouteDecision:
    skill: str
    reason: str
    intent: str = "unsupported"
    member_type: str = "none"
    confidence: float = 0.0
    requires_tenancy_context: bool = False
    missing_context: list[str] | None = None
    member_types: tuple[str, ...] = ()
    execution_mode: str = "single_skill"
    invoked_skills: tuple[str, ...] = ()
    request_text: str = ""


REPO_ROOT = Path(__file__).resolve().parent.parent
_MEMBER_LABEL_TO_TYPE = {
    "oke": "oke",
    "kubernetes": "oke",
    "cluster": "oke",
    "database": "database",
    "db": "database",
    "autonomous database": "autonomous_database",
    "adb": "autonomous_database",
    "compute": "compute",
    "vm": "compute",
    "instance": "compute",
    "integration": "integration_instance",
    "integration instance": "integration_instance",
    "oic": "integration_instance",
    "application": "application",
    "app": "application",
}
_MEMBER_TYPE_TO_LABEL = {member_type: member_type.replace("_", " ") for member_type in MEMBER_PREPARATION_SKILLS}


_MEMBER_EXTRACTION_PATTERNS = (
    (r"\bautonomous database\b", "autonomous_database"),
    (r"\bautonomous db\b", "autonomous_database"),
    (r"\badb\b", "autonomous_database"),
    (r"\badw\b", "autonomous_database"),
    (r"\batp\b", "autonomous_database"),
    (r"\bintegration instance\b", "integration_instance"),
    (r"\boic\b", "integration_instance"),
    (r"\bintegration\b", "integration_instance"),
    (r"\bkubernetes\b", "oke"),
    (r"\bk8s\b", "oke"),
    (r"\boke\b", "oke"),
    (r"\bcluster\b", "oke"),
    (r"\bdatabase\b", "database"),
    (r"\bdbcs\b", "database"),
    (r"\bdb\b", "database"),
    (r"\bcompute\b", "compute"),
    (r"\bvm\b", "compute"),
    (r"\binstance\b", "compute"),
    (r"\bapplication\b", "application"),
    (r"\bapp\b", "application"),
)
_MULTI_MEMBER_APP_SCOPE_TYPES = {"oke", "database", "autonomous_database", "integration_instance", "application"}
_POLICY_TAILORING_TERMS = (
    "tailor",
    "tailored",
    "customize",
    "customise",
    "scope",
    "scope the policy",
    "scope these policies",
    "for my tenancy",
    "for this tenancy",
    "for these compartments",
    "operator group",
)
_POLICY_SCOPE_TERMS = ("policy", "policies", "iam", "permission", "permissions", "access")

_MEMBER_CONTEXT_TERM_GROUPS: dict[str, tuple[tuple[str, ...], ...]] = {
    "application boundary and critical components": (("application", "app", "component", "components", "service", "services", "tier", "tiers"),),
    "dependency order for recovery readiness": (("dependency", "dependencies", "order", "sequence", "sequencing"),),
    "known blockers by member type": (("blocker", "blockers", "gap", "gaps", "issue", "issues", "risk", "risks"),),
    "autonomous database scope": (("autonomous", "adb", "adw", "atp"),),
    "remote peer and standby mapping": (("peer", "remote", "standby", "target"),),
    "database type and deployment model": (("database", "db", "dbcs", "exadata", "rac", "autonomous"), ("deployment", "model", "single instance", "single-instance", "rac", "exadata", "vm", "bare metal")),
    "primary and peer role mapping": (("primary", "source"), ("peer", "standby", "target", "remote")),
    "replication and peer relationship status": (("replication", "data guard", "dataguard", "peer", "standby", "remote"),),
    "vault and secret dependencies": (("vault", "secret", "secrets", "wallet", "wallets", "key", "keys"),),
    "instance scope and recovery style": (("instance", "vm", "compute", "server"), ("recovery", "moving", "non-moving", "nonmoving", "restore", "rehost")),
    "boot and block volume dependencies": (("boot volume", "block volume", "volume", "volumes"),),
    "volume group preparation status": (("volume group", "consistency group"),),
    "automation script and run-command dependencies": (("script", "scripts", "run command", "run-command", "automation", "ansible"),),
    "source and standby integration scope": (("integration", "integration instance", "oic"), ("source", "standby", "target", "peer")),
    "source and standby cluster scope": (("cluster", "oke", "kubernetes", "k8s"), ("source", "standby", "target", "peer")),
    "namespace and workload scope": (("namespace", "workload", "deployment", "service", "app", "application"),),
    "ingress and load balancer dependencies": (("ingress", "load balancer", "load-balancer", "lb"),),
}
_APP_SCOPE_TERMS = ("application", "app", "environment", "env", "workload", "namespace", "service")
_REGION_SCOPE_TERMS = ("source region", "target region", "region pair", "primary region", "standby region", "ashburn", "phoenix", "frankfurt", "london", "region")
_CHECKLIST_REVIEW_TERMS = ("checklist", "reviewed", "validated", "documented", "confirmed", "configured", "mapped", "complete", "completed", "ready")
_NETWORK_DEPENDENCY_TERMS = ("network", "networking", "subnet", "subnets", "nsg", "nsgs", "vcn", "private endpoint")
_POLICY_DEPENDENCY_TERMS = ("policy", "policies", "iam", "permission", "permissions")
_SECRET_DEPENDENCY_TERMS = ("secret", "secrets", "vault", "wallet", "wallets", "key", "keys")


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def _extract_member_types(text: str) -> list[str]:
    working = text
    member_types: list[str] = []

    for pattern, member_type in _MEMBER_EXTRACTION_PATTERNS:
        if member_type not in MEMBER_PREPARATION_SKILLS:
            continue
        if re.search(pattern, working):
            member_types.append(member_type)
            working = re.sub(pattern, " ", working)

    if member_types:
        return _dedupe(member_types)

    classified = classify_member_type(text)
    if classified in MEMBER_PREPARATION_SKILLS:
        return [classified]
    return []


def extract_reference_section(reference_path: str, heading: str) -> str | None:
    path = REPO_ROOT / reference_path
    if not path.exists():
        return None

    lines = path.read_text(encoding="utf-8").splitlines()
    target = f"## {heading}"
    start_index = None

    for index, line in enumerate(lines):
        if line.strip() == target:
            start_index = index + 1
            break

    if start_index is None:
        return None

    collected: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("## "):
            break
        if line.strip():
            collected.append(line)

    return "\n".join(collected).strip() or None


def extract_policy_lines(section: str | None) -> list[str]:
    if not section:
        return []
    return [line.strip() for line in section.splitlines() if line.strip().startswith("Allow group ")]


def _normalize_bullet_item(item: str) -> str:
    stripped = item.strip()
    return stripped[2:].strip() if stripped.startswith("- ") else stripped


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {_normalize_bullet_item(item)}" for item in items)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _normalize(message: str) -> str:
    return " ".join(message.lower().split())


def _groups_match(text: str, groups: tuple[tuple[str, ...], ...]) -> bool:
    return all(any(term in text for term in group) for group in groups)


def _has_application_scope_context(text: str, tenancy: TenancyProfile | None = None) -> bool:
    if tenancy is not None and (tenancy.application_name or tenancy.environment_name):
        return True
    return any(term in text for term in _APP_SCOPE_TERMS)


def _has_region_pair_context(text: str, tenancy: TenancyProfile | None = None) -> bool:
    if tenancy is not None and len(tenancy.target_regions) >= 2:
        return True
    if any(term in text for term in _REGION_SCOPE_TERMS) and any(term in text for term in ("source", "target", "primary", "standby", "peer")):
        return True
    return len(re.findall(r"\b[a-z]{2}-[a-z-]+-\d\b", text)) >= 2


def _has_checklist_review_context(text: str) -> bool:
    return any(term in text for term in _CHECKLIST_REVIEW_TERMS)


def _member_context_item_present(item: str, text: str, tenancy: TenancyProfile | None, member_type: str) -> bool:
    normalized_item = _normalize_bullet_item(item)

    if normalized_item == "member types involved":
        return bool(_extract_member_types(text)) or "member type" in text or "members" in text
    if normalized_item == "region mapping for primary and standby":
        return _has_region_pair_context(text, tenancy) and any(term in text for term in ("primary", "standby", "peer", "source", "target"))
    if normalized_item == "backup bucket and restore ownership":
        return ("bucket" in text or "object storage" in text) and ("backup" in text or "restore" in text)
    if normalized_item == "networking, policy, and secret dependencies":
        hits = sum(
            any(term in text for term in terms)
            for terms in (_NETWORK_DEPENDENCY_TERMS, _POLICY_DEPENDENCY_TERMS, _SECRET_DEPENDENCY_TERMS)
        )
        return hits >= 2

    groups = _MEMBER_CONTEXT_TERM_GROUPS.get(normalized_item)
    if groups is not None:
        return _groups_match(text, groups)

    fallback_terms = [token for token in re.split(r"[^a-z0-9]+", normalized_item) if len(token) > 3]
    return any(term in text for term in fallback_terms)


def _member_preparation_known_context(skill: str, tenancy: TenancyProfile | None, request_text: str) -> list[str]:
    text = _normalize(request_text)
    member_type, checklist, required_context = _member_skill_summary(skill)
    known: list[str] = []

    if member_type in {"oke", "database", "autonomous_database", "integration_instance", "application"} and _has_application_scope_context(text, tenancy):
        known.append("application or environment scope")
    if _has_region_pair_context(text, tenancy):
        known.append("source and target region pair")

    for item in required_context:
        if _member_context_item_present(item, text, tenancy, member_type):
            known.append(item)

    if checklist and _has_checklist_review_context(text):
        known.append("member-specific checklist review")

    return _dedupe(known)


def _resolve_member_preparation_missing_context(skill: str, tenancy: TenancyProfile | None, request_text: str) -> list[str]:
    text = _normalize(request_text)
    member_type, checklist, required_context = _member_skill_summary(skill)
    missing: list[str] = []

    if member_type in {"oke", "database", "autonomous_database", "integration_instance", "application"} and not _has_application_scope_context(text, tenancy):
        missing.append("application or environment scope")
    if not _has_region_pair_context(text, tenancy):
        missing.append("source and target region pair")

    for item in required_context:
        if not _member_context_item_present(item, text, tenancy, member_type):
            missing.append(item)

    if checklist and not _has_checklist_review_context(text):
        missing.append("member-specific checklist review")

    return _dedupe(missing)


def _is_policy_tailoring_request(text: str, intent: str) -> bool:
    if not any(term in text for term in _POLICY_TAILORING_TERMS):
        return False
    return intent == "prerequisites" or any(term in text for term in _POLICY_SCOPE_TERMS) or "fsdr" in text


def _member_type_from_text(text: str) -> str:
    member_types = _extract_member_types(text)
    if member_types:
        return member_types[0]

    classified = classify_member_type(text)
    if classified in MEMBER_PREPARATION_SKILLS:
        return classified

    for term, member_type in _MEMBER_LABEL_TO_TYPE.items():
        if term in text and member_type in MEMBER_PREPARATION_SKILLS:
            return member_type
    return "none"


def _finalize_decision(
    skill: str,
    reason: str,
    intent: str,
    member_type: str,
    confidence: float,
    tenancy: TenancyProfile | None,
    missing_context: list[str] | None = None,
    member_types: tuple[str, ...] = (),
    execution_mode: str = "single_skill",
    invoked_skills: tuple[str, ...] = (),
    request_text: str = "",
) -> RouteDecision:
    selected_skill = skill if skill in ALLOWED_SKILLS else DEFAULT_ROUTER_SKILL
    requires_tenancy = skill_requires_tenancy(selected_skill)
    unresolved = list(missing_context or [])
    if requires_tenancy and tenancy is None and "selected tenancy" not in unresolved:
        unresolved.append("selected tenancy")
    return RouteDecision(
        skill=selected_skill,
        reason=reason,
        intent=intent,
        member_type=member_type,
        confidence=confidence,
        requires_tenancy_context=requires_tenancy,
        missing_context=unresolved,
        member_types=member_types,
        execution_mode=execution_mode,
        invoked_skills=invoked_skills,
        request_text=request_text,
    )


def _deterministic_route(text: str, tenancy: TenancyProfile | None) -> RouteDecision | None:
    if _contains_any(text, INTRO_TERMS):
        return _finalize_decision(INTRO_SKILL, "deterministic match for fsdr introduction", "introduction", "none", 0.99, tenancy)

    if _contains_any(text, INVENTORY_TERMS):
        return _finalize_decision(
            READ_INFRASTRUCTURE_SKILL,
            "deterministic match for read-only inventory",
            "read_inventory",
            "none",
            0.98,
            tenancy,
            ["compartment OCID or instance OCID"],
        )

    if _contains_any(text, STOP_DRILL_TERMS):
        return _finalize_decision(STOP_DRILL_SKILL, "deterministic match for stop-drill workflow", "stop_drill", "none", 0.97, tenancy)

    if _contains_any(text, START_DRILL_TERMS):
        return _finalize_decision(START_DRILL_SKILL, "deterministic match for start-drill workflow", "start_drill", "none", 0.97, tenancy)

    if _contains_any(text, PRECHECK_TERMS):
        return _finalize_decision(
            READINESS_SKILL,
            "deterministic match for readiness precheck",
            "run_prechecks",
            "none",
            0.92,
            tenancy,
            ["readiness inputs and protection group status"],
        )

    if _contains_any(text, READINESS_TERMS):
        return _finalize_decision(
            READINESS_SKILL,
            "deterministic match for readiness assessment",
            "readiness",
            "none",
            0.9,
            tenancy,
            ["readiness inputs and protection group status"],
        )

    if _contains_any(text, PLAN_TERMS):
        return _finalize_decision(
            TENANCY_OPERATIONS_SKILL,
            "deterministic match for DR plan exploration",
            "explore_plans",
            "none",
            0.9,
            tenancy,
            ["application or protection group scope"],
        )

    if _contains_any(text, DRPG_TERMS):
        return _finalize_decision(
            TENANCY_OPERATIONS_SKILL,
            "deterministic match for DR protection group inspection",
            "read_protection_group",
            "none",
            0.9,
            tenancy,
            ["application or protection group scope"],
        )

    if _contains_any(text, CREATE_PG_TERMS):
        return _finalize_decision(
            CREATE_PROTECTION_GROUP_SKILL,
            "deterministic match for protection group creation",
            "create_protection_group",
            "none",
            0.95,
            tenancy,
            ["application or protection group scope"],
        )

    if _contains_any(text, PREREQ_TERMS):
        return _finalize_decision(PREREQUISITES_SKILL, "deterministic match for prerequisites and IAM policies", "prerequisites", "none", 0.94, tenancy)

    member_type = _member_type_from_text(text)
    if "prepare" in text and member_type != "none":
        member_skill = skill_for_member_preparation(member_type)
        return _finalize_decision(
            member_skill,
            f"deterministic member preparation route for {member_type.replace('_', ' ')}",
            "member_preparation",
            member_type,
            0.94,
            tenancy,
        )

    if any(term in text for term in ("member", "members", "member prep", "supported member", "before adding")):
        if member_type != "none":
            member_skill = skill_for_member_preparation(member_type)
            return _finalize_decision(
                member_skill,
                f"deterministic member preparation route for {member_type.replace('_', ' ')}",
                "member_preparation",
                member_type,
                0.9,
                tenancy,
            )
        return _finalize_decision(
            skill_for_member_preparation("none"),
            "deterministic generic member preparation route",
            "member_preparation",
            "none",
            0.84,
            tenancy,
            ["member type in scope"],
        )

    if _contains_any(text, TROUBLESHOOTING_TERMS):
        return _finalize_decision(TENANCY_OPERATIONS_SKILL, "deterministic route for troubleshooting operations", "troubleshooting", "none", 0.7, tenancy)

    if any(term in text for term in ("onboard", "new to oci fsdr", "get started", "tenancy")):
        return _finalize_decision(TENANCY_ONBOARD_SKILL, "deterministic tenancy onboarding route", "tenancy_onboarding", "none", 0.8, tenancy)

    return None


def _extract_titled_block(path: Path, title: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == title:
            start = idx + 1
            break
    if start is None:
        return []

    block: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped and block:
            break
        if not stripped:
            continue
        if stripped.endswith(":") and not stripped.startswith("-"):
            break
        if stripped in {"Goal", "Preconditions", "Required context", "Workflow", "Output format", "Guardrails", "Supporting files"}:
            break
        block.append(stripped)
    return block


def _member_skill_summary(skill: str) -> tuple[str, list[str], list[str]]:
    path = REPO_ROOT / skill
    member_type = "unknown"
    checklist: list[str] = []
    required_context: list[str] = []

    for key, mapped_skill in MEMBER_PREPARATION_SKILLS.items():
        if mapped_skill == skill:
            member_type = key
            break

    if path.exists():
        checklist = _extract_titled_block(path, "Preparation checklist")
        required_context = _extract_titled_block(path, "Required context")
    return member_type, checklist, required_context


def tenancy_context_summary(tenancy: TenancyProfile | None, skill: str, request_text: str = "") -> str:
    if tenancy is None:
        if skill_requires_tenancy(skill):
            return 'Known context:\n- no tenancy selected yet\n\nStill needed:\n- tenancy selection or registration'
        if skill in MEMBER_PREPARATION_SKILLS.values():
            known = ["no tenancy selected yet", "this request can be handled as instruction-only guidance"]
            known.extend(_member_preparation_known_context(skill, tenancy, request_text))
            missing = _resolve_member_preparation_missing_context(skill, tenancy, request_text)
            if not missing:
                missing.append("no unresolved member-preparation context captured yet")
            return f'Known context:\n{bullet_list(known)}\n\nStill needed:\n{bullet_list(missing)}'
        return (
            'Known context:\n- no tenancy selected yet\n- this request can be handled as instruction-only guidance\n\nStill needed:\n- workload-specific scope details for the current question'
        )

    known = [
        f"tenancy name: {tenancy.tenancy_name}",
        f"home region: {tenancy.home_region}",
        f"onboarding status: {tenancy.onboarding_status}",
        f"persona: {tenancy.persona}",
        f"intended use: {tenancy.intended_use}",
    ]

    if tenancy.target_regions:
        known.append(f"target regions: {', '.join(tenancy.target_regions)}")
    if tenancy.compartments_in_scope:
        known.append(f"compartments: {', '.join(tenancy.compartments_in_scope)}")
    if tenancy.application_name:
        known.append(f"application: {tenancy.application_name}")
    if tenancy.environment_name:
        known.append(f"environment: {tenancy.environment_name}")

    if skill in MEMBER_PREPARATION_SKILLS.values():
        known.extend(_member_preparation_known_context(skill, tenancy, request_text))
        missing = _resolve_member_preparation_missing_context(skill, tenancy, request_text)
        if not missing:
            missing.append("no unresolved member-preparation context captured yet")
        return f'Known context:\n{bullet_list(_dedupe(known))}\n\nStill needed:\n{bullet_list(missing)}'

    missing: list[str] = []

    if skill == PREREQUISITES_SKILL:
        if not tenancy.target_regions:
            missing.append("target regions for FSDR scope")
        if not tenancy.compartments_in_scope:
            missing.append("compartments in scope")
    elif skill == POLICY_TAILORING_SKILL:
        if not tenancy.target_regions:
            missing.append("target regions for FSDR scope")
        if not tenancy.compartments_in_scope:
            missing.append("compartments in scope")
        if not tenancy.persona:
            missing.append("persona or operator role")
        if not tenancy.application_name and not tenancy.environment_name:
            missing.append("workload or application scope when policy scope depends on the protected stack")
    elif skill == CREATE_PROTECTION_GROUP_SKILL:
        if not tenancy.application_name:
            missing.append("application or environment scope")
        if len(tenancy.target_regions) < 2:
            missing.append("source and target region pair")
        missing.append("Object Storage bucket for DR plan logs")
        missing.append("peer role and peer protection group plan")
    elif skill == READINESS_SKILL:
        missing.append("prerequisite and IAM policy status")
        missing.append("protection group status")
        missing.append("member preparation status")
    elif skill == READ_INFRASTRUCTURE_SKILL:
        missing.append("compartment OCID for inventory lookup")
        missing.append("optional instance OCID if the request is for a single server")
    elif skill == START_DRILL_SKILL:
        if not tenancy.application_name:
            missing.append("application or protection group scope")
        missing.append("standby DR Protection Group and DR plan context")
        missing.append("readiness confirmation for the selected workload")
        missing.append("explicit confirmation to create the standby drill stack")
    elif skill == STOP_DRILL_SKILL:
        if not tenancy.application_name:
            missing.append("application or drill scope")
        missing.append("active drill context in the standby DR Protection Group")
        missing.append("confirmation that the standby drill stack should be removed")
    elif skill == TENANCY_ONBOARD_SKILL:
        if not tenancy.tenancy_ocid:
            missing.append("tenancy OCID")
        if not tenancy.home_region:
            missing.append("home region")
        if not tenancy.target_regions:
            missing.append("target regions")
        if not tenancy.compartments_in_scope:
            missing.append("compartments in scope")
        if not tenancy.persona:
            missing.append("persona")
        if not tenancy.intended_use:
            missing.append("intended use")

    if not missing:
        missing.append("no additional context captured yet in this prototype")

    return f'Known context:\n{bullet_list(known)}\n\nStill needed:\n{bullet_list(missing)}'

def route_request(message: str, tenancy: TenancyProfile | None = None) -> RouteDecision:
    text = _normalize(message)
    member_types = tuple(_extract_member_types(text))

    classified = classify_request(text, has_tenancy_context=tenancy is not None)

    if _is_policy_tailoring_request(text, classified.intent):
        return _finalize_decision(
            skill=POLICY_TAILORING_SKILL,
            reason=f"{classified.reason} Policy tailoring override for tenancy-scoped IAM guidance.",
            intent="prerequisites",
            member_type="none",
            confidence=classified.confidence,
            tenancy=tenancy,
            missing_context=classified.missing_context,
            request_text=text,
        )

    if classified.intent == "member_preparation" and len(member_types) > 1:
        invoked_skills = tuple(skill_for_member_preparation(member_type) for member_type in member_types)
        multi_reason = f"{classified.reason} Multi-member orchestration for: {', '.join(member_types)}."
        missing_context = [item for item in (classified.missing_context or []) if item != "member type in scope"]
        for skill in invoked_skills:
            missing_context.extend(_resolve_member_preparation_missing_context(skill, tenancy, text))
        return _finalize_decision(
            skill=GENERIC_MEMBER_PREPARATION_SKILL,
            reason=multi_reason,
            intent=classified.intent,
            member_type="none",
            confidence=classified.confidence,
            tenancy=tenancy,
            missing_context=_dedupe(missing_context),
            member_types=member_types,
            execution_mode="multi_skill",
            invoked_skills=invoked_skills,
            request_text=text,
        )

    finalized_member_types = member_types if classified.intent == "member_preparation" else ()
    invoked_skills = ()
    resolved_missing_context = classified.missing_context
    if classified.intent == "member_preparation" and classified.best_skill in MEMBER_PREPARATION_SKILLS.values():
        invoked_skills = (classified.best_skill,)
        resolved_missing_context = _resolve_member_preparation_missing_context(classified.best_skill, tenancy, text)

    return _finalize_decision(
        skill=classified.best_skill,
        reason=classified.reason,
        intent=classified.intent,
        member_type=classified.member_type,
        confidence=classified.confidence,
        tenancy=tenancy,
        missing_context=resolved_missing_context,
        member_types=finalized_member_types,
        invoked_skills=invoked_skills,
        request_text=text,
    )

def build_assistant_message(decision: RouteDecision, tenancy: TenancyProfile | None, session: Session) -> str:
    tenancy_text = "No tenancy selected yet."
    if tenancy is not None:
        tenancy_text = (
            f"Tenancy `{tenancy.tenancy_name}` in `{tenancy.home_region}` "
            f"with onboarding status `{tenancy.onboarding_status}`."
        )

    if decision.skill == INTRO_SKILL:
        next_step = (
            "If you want to continue, I can move next into prerequisites, onboarding, or protection group setup."
            if tenancy is not None
            else "If you want to continue, I can start with tenancy onboarding or prerequisite guidance."
        )
        return (
            "OCI Full Stack Disaster Recovery (FSDR) is an OCI service and operating model for "
            "organizing disaster recovery preparation, readiness validation, and drill workflows for supported workloads.\n\n"
            "What it can help with:\n"
            "- explain FSDR concepts in plain language\n"
            "- guide tenancy onboarding and prerequisite checks\n"
            "- explain IAM and approval expectations\n"
            "- help with protection groups, member preparation, readiness, and drill lifecycle guidance\n\n"
            "What it is not:\n"
            "- not a replacement for OCI product documentation\n"
            "- not an automatic executor of OCI changes by default in this prototype\n"
            "- not proof that a tenancy is ready unless the required context and checks are present\n"
            "- not a bypass for governance, approvals, or role boundaries\n\n"
            f"{tenancy_text}\n\n"
            f"Session `{session.id}` is using `{decision.skill}`.\n\n"
            f"{next_step}"
        )

    if decision.execution_mode == "multi_skill" and decision.intent == "member_preparation":
        member_types = list(decision.member_types)
        invoked_skills = list(decision.invoked_skills)
        member_labels = [f"`{_MEMBER_TYPE_TO_LABEL.get(member_type, member_type)}`" for member_type in member_types]
        common_requirements = [
            "tenancy onboarding is ready",
            "the relevant protection group or application scope is identified",
            "the resource types in scope are confirmed",
        ]
        if any(member_type in _MULTI_MEMBER_APP_SCOPE_TYPES for member_type in member_types):
            common_requirements.append("application or environment scope is known")
        common_requirements.append("source and target region pair is known")

        common_missing: list[str] = []
        if tenancy is None:
            common_missing.append("selected tenancy is optional for instruction-only planning, but required for validated readiness")
        if not _has_region_pair_context(decision.request_text, tenancy):
            common_missing.append("source and target region pair")
        if any(member_type in _MULTI_MEMBER_APP_SCOPE_TYPES for member_type in member_types) and not _has_application_scope_context(decision.request_text, tenancy):
            common_missing.append("application or environment scope")

        member_sections: list[str] = []
        overall_blockers: list[str] = []
        for skill in invoked_skills:
            member_type, checklist, required_context = _member_skill_summary(skill)
            member_label = _MEMBER_TYPE_TO_LABEL.get(member_type, member_type)
            member_missing = _resolve_member_preparation_missing_context(skill, tenancy, decision.request_text)
            overall_blockers.extend([f"{member_label}: {_normalize_bullet_item(item)}" for item in member_missing])
            checklist_text = bullet_list(checklist) if checklist else "- checklist not found in skill file"
            context_text = bullet_list(required_context) if required_context else "- scope details from the member skill"
            member_sections.append(
                f"Member `{member_label}` using `{skill}`:\n"
                f"Required context:\n{context_text}\n\n"
                f"Preparation checklist:\n{checklist_text}"
            )

        consolidated_blockers = _dedupe(common_missing + overall_blockers)
        blockers_text = bullet_list(consolidated_blockers) if consolidated_blockers else "- no blockers captured yet in this prototype"
        invoked_skill_text = bullet_list(invoked_skills)
        member_section_text = "\n\n".join(member_sections)
        return (
            f"{tenancy_text} Session `{session.id}` is using `{decision.skill}` in `{decision.execution_mode}` mode.\n\n"
            f"Member types in scope: {', '.join(member_labels)}.\n\n"
            "Invoked skills:\n"
            f"{invoked_skill_text}\n\n"
            "Common preparation gates:\n"
            f"{bullet_list(common_requirements)}\n\n"
            f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
            f"{member_section_text}\n\n"
            "Overall status:\n"
            "- needs preparation\n\n"
            "Aggregated blockers or missing inputs:\n"
            f"{blockers_text}\n\n"
            "Recommended next action:\n"
            "- complete the member-specific preparation items, then return to readiness once the member set is defined"

        )

    if decision.skill == READ_INFRASTRUCTURE_SKILL:
        tenancy_id = tenancy.id if tenancy is not None else "<tenancy_id>"
        return (
            f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
            "This read-only workflow can inspect:\n"
            "- compute instances in a compartment\n"
            "- attached boot volumes\n"
            "- attached block volumes\n"
            "- VNIC attachments and IP context\n\n"
            f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
            "API to use in this prototype:\n"
            f"- `GET /api/tenancies/{tenancy_id}/inventory/compute?compartment_id=<compartment_ocid>`\n"
            f"- `GET /api/tenancies/{tenancy_id}/inventory/compute?compartment_id=<compartment_ocid>&instance_id=<instance_ocid>`\n\n"
            "If your tenancy profile already stores a compartment OCID in `compartments_in_scope`, the `compartment_id` query parameter can be omitted."
        )

    if decision.skill in MEMBER_PREPARATION_SKILLS.values():
        member_type, checklist, required_context = _member_skill_summary(decision.skill)
        member_label = _MEMBER_TYPE_TO_LABEL.get(member_type, member_type)
        checklist_text = bullet_list(checklist) if checklist else "- checklist not found in skill file"
        context_text = bullet_list(required_context) if required_context else "- scope details from the member skill"
        return (
            f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
            f"Member preparation scope: `{member_label}`.\n\n"
            "Required context:\n"
            f"{context_text}\n\n"
            "Preparation checklist:\n"
            f"{checklist_text}\n\n"
            f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
            "Response contract:\n"
            "- member type\n"
            "- known scope\n"
            "- preparation checklist\n"
            "- blockers\n"
            "- readiness state\n"
            "- next action"
        )

    if decision.skill == GENERIC_MEMBER_PREPARATION_SKILL:
        supported_members = bullet_list([
            f"{_MEMBER_TYPE_TO_LABEL.get(member_type, member_type)}: {skill}"
            for member_type, skill in MEMBER_PREPARATION_SKILLS.items()
        ])
        common_gates = _extract_titled_block(REPO_ROOT / decision.skill, "Preconditions")
        common_gates_text = bullet_list(common_gates) if common_gates else (
            "- tenancy onboarding is ready\n"
            "- the relevant protection group or application scope is identified\n"
            "- the user knows which workload or resource types are in scope"
        )
        return (
            f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
            "This is the generic member-preparation overview.\n\n"
            "Supported member types in this prototype:\n"
            f"{supported_members}\n\n"
            "Common preparation gates:\n"
            f"{common_gates_text}\n\n"
            "What this question can answer now:\n"
            "- which member types are supported in the current prototype\n"
            "- the common preparation gates before add-member decisions\n"
            "- the next member-specific skill to use for deeper readiness guidance\n\n"
            "Recommended next action:\n"
            "- ask for a specific member type such as `database`, `oke`, `compute`, `autonomous database`, `integration instance`, or `application` if you want detailed preparation steps"
        )

    if decision.skill == TENANCY_ONBOARD_SKILL:
        onboarding_status = tenancy.onboarding_status if tenancy is not None else "blocked"
        next_step = (
            "Move to prerequisites and IAM policies."
            if tenancy is not None and tenancy.onboarding_status == "ready"
            else "Capture the missing tenancy context fields first."
        )
        return (
            f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
            "Goal:\n"
            "- establish a reusable tenancy context for later FSDR operations\n\n"
            f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
            "Onboarding result for this prototype:\n"
            f"- status: {onboarding_status}\n"
            "- output needed: selected tenancy identifier, onboarding status, missing prerequisites, next step\n\n"
            "What this skill validates:\n"
            "- tenancy identity and access context\n"
            "- region scope\n"
            "- compartments in scope\n"
            "- persona and intended use\n"
            "- whether the tenancy can move into prerequisites and policy checks\n\n"
            f"Recommended next step:\n- {next_step}"
        )

    if decision.skill == PREREQUISITES_SKILL:
        policy_guidance = extract_reference_section("references/fsdr-setup-reference.md", "Prerequisites and IAM policy guidance")
        starter_policies = extract_reference_section("references/fsdr-setup-reference.md", "Starter IAM policy statements")
        if policy_guidance:
            extra = ""
            policy_lines = extract_policy_lines(starter_policies)
            if policy_lines:
                extra = f"\n\nStarter IAM policy statements:\n{bullet_list(policy_lines)}"
            return (
                f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
                f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
                "Here is the current OCI FSDR prerequisite and IAM policy guidance:\n"
                f"{policy_guidance}{extra}\n\n"
                "If you want, the next step is to tailor this to your tenancy, regions, and compartments."
            )

    if decision.skill == POLICY_TAILORING_SKILL:
        starter_policies = extract_reference_section("references/fsdr-setup-reference.md", "Starter IAM policy statements")
        policy_guidance = extract_reference_section("references/fsdr-setup-reference.md", "Prerequisites and IAM policy guidance")

        persona = tenancy.persona if tenancy is not None and tenancy.persona else "operator"
        group_name = {
            "admin": "FSDRAdmins",
            "operator": "FSDROperators",
            "viewer": "FSDRViewers",
        }.get(persona, "FSDROperators")
        compartment_scope = tenancy.compartments_in_scope[0] if tenancy is not None and tenancy.compartments_in_scope else "<compartment_name>"
        workload_scope = (
            tenancy.application_name
            if tenancy is not None and tenancy.application_name
            else tenancy.environment_name
            if tenancy is not None and tenancy.environment_name
            else "<workload_name>"
        )
        dynamic_group_slug = re.sub(r"[^a-z0-9-]+", "-", workload_scope.lower()).strip("-") or "fsdr-workload"
        dynamic_group_name = f"{dynamic_group_slug}-fsdr-dg"
        log_bucket_name = f"{dynamic_group_slug}-drplan-logs"

        missing_tailoring_context: list[str] = []
        if tenancy is None:
            missing_tailoring_context.extend(["selected tenancy", "compartments in scope", "target regions for FSDR scope", "persona or operator group"])
        else:
            if not tenancy.compartments_in_scope:
                missing_tailoring_context.append("compartments in scope")
            if not tenancy.target_regions:
                missing_tailoring_context.append("target regions for FSDR scope")
            if not tenancy.persona:
                missing_tailoring_context.append("persona or operator group")

        policy_pack_status = "ready to review" if not missing_tailoring_context else "template-only"

        core_fsdr_policies = [
            f"Allow group {group_name} to manage disaster-recovery-protection-groups in compartment {compartment_scope}",
            f"Allow group {group_name} to manage disaster-recovery-plans in compartment {compartment_scope}",
            f"Allow group {group_name} to manage disaster-recovery-prechecks in compartment {compartment_scope}",
        ]
        if persona == "admin":
            core_fsdr_policies.insert(0, f"Allow group {group_name} to manage disaster-recovery-family in tenancy")

        dependency_policy_templates = [
            f"Allow group {group_name} to read buckets in compartment {compartment_scope}",
            f"Allow group {group_name} to manage objects in compartment {compartment_scope} where target.bucket.name = '{log_bucket_name}'",
            f"Allow group {group_name} to use tag-namespaces in tenancy",
        ]
        if persona in {"admin", "operator"}:
            dependency_policy_templates.extend([
                f"Allow dynamic-group {dynamic_group_name} to use keys in compartment <security_compartment_name>",
                f"Allow dynamic-group {dynamic_group_name} to read secret-bundles in compartment <security_compartment_name>",
            ])

        dynamic_group_templates = [
            f"Dynamic group name: {dynamic_group_name}",
            "Matching rule template: ALL {resource.type = '<workload_resource_type>', resource.compartment.id = '<compartment_ocid>'}",
            f"Allow dynamic-group {dynamic_group_name} to manage objects in compartment {compartment_scope} where target.bucket.name = '{log_bucket_name}'",
        ]

        workload_review_points = [
            "database workflows: validate Vault, key, and secret access requirements",
            "compute workflows: validate Oracle Cloud Agent or Run Command access requirements",
            "all workloads: validate Object Storage log bucket and tag-governance requirements",
        ]

        starter_text = bullet_list(extract_policy_lines(starter_policies)) if starter_policies else "- starter policy statements unavailable"
        guidance_text = policy_guidance or "Use the Oracle-aligned starter statements as the base and then scope them to the tenancy, compartments, and operator intent."
        missing_text = bullet_list(missing_tailoring_context) if missing_tailoring_context else "- no required placeholders remain"

        return (
            f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
            f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
            "Policy pack status:\n"
            f"- {policy_pack_status}\n\n"
            "Suggested IAM principals:\n"
            f"- human group: {group_name}\n"
            f"- dynamic group: {dynamic_group_name}\n"
            f"- log bucket placeholder: {log_bucket_name}\n\n"
            "Core FSDR policies:\n"
            f"{bullet_list(core_fsdr_policies)}\n\n"
            "Dependency policy templates to validate:\n"
            f"{bullet_list(dependency_policy_templates)}\n\n"
            "Dynamic group candidates:\n"
            f"{bullet_list(dynamic_group_templates)}\n\n"
            "Workload-specific review points:\n"
            f"{bullet_list(workload_review_points)}\n\n"
            "Oracle-aligned starter references:\n"
            f"{starter_text}\n\n"
            "Additional policy guidance:\n"
            f"{guidance_text}\n\n"
            "Still to replace or confirm:\n"
            f"{missing_text}\n\n"
            "Recommended next action:\n"
            "- review the draft policy pack, replace placeholders, and then use it as the input for a later policy-creation skill"
        )

    if decision.skill == CREATE_PROTECTION_GROUP_SKILL:
        protection_group_guidance = extract_reference_section("references/fsdr-setup-reference.md", "Protection group creation checklist")
        if protection_group_guidance:
            return (
                f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
                f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
                "Here is the current DR Protection Group setup guidance:\n"
                f"{protection_group_guidance}\n\n"
                "If you want, the next step is to provide the application scope, source region, target region, and bucket details."
            )

    if decision.skill == READINESS_SKILL:
        readiness_guidance = extract_reference_section("references/fsdr-setup-reference.md", "Readiness interpretation")
        if readiness_guidance:
            return (
                f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
                f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
                "Here is the current readiness interpretation for this prototype:\n"
                f"{readiness_guidance}\n\n"
                "To assess your readiness, I need the prerequisite status, protection group status, and member preparation status."
            )

    if decision.skill == START_DRILL_SKILL:
        start_drill_guidance = extract_reference_section("references/fsdr-setup-reference.md", "Start drill guidance")
        if start_drill_guidance:
            return (
                f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
                f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
                "Here is the current Start drill guidance for this prototype:\n"
                f"{start_drill_guidance}\n\n"
                "To continue, confirm the target protection group or application scope and that the team wants to create the standby drill stack."
            )

    if decision.skill == STOP_DRILL_SKILL:
        stop_drill_guidance = extract_reference_section("references/fsdr-setup-reference.md", "Stop drill guidance")
        if stop_drill_guidance:
            return (
                f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n\n"
                f"{tenancy_context_summary(tenancy, decision.skill, decision.request_text)}\n\n"
                "Here is the current Stop drill guidance for this prototype:\n"
                f"{stop_drill_guidance}\n\n"
                "To continue, identify the active drill context and confirm that the standby drill stack should be removed."
            )

    unresolved = decision.missing_context or []
    unresolved_text = bullet_list(unresolved) if unresolved else "- no additional context required"
    return (
        f"{tenancy_text} Session `{session.id}` is using `{decision.skill}`.\n"
        f"Routing intent: `{decision.intent}` (confidence `{decision.confidence:.2f}`).\n"
        f"Reason: {decision.reason}\n\n"
        "Missing context:\n"
        f"{unresolved_text}"
    )
