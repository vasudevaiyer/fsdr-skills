from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OperationType = Literal["instruction", "read_only", "validate", "mutating"]

INTRO_SKILL = "skills/tenancy/fsdr-introduction.md"
TENANCY_ONBOARD_SKILL = "skills/tenancy/fsdr-tenancy-onboard.md"
PREREQUISITES_SKILL = "skills/tenancy/fsdr-prerequisites-and-policies.md"
POLICY_TAILORING_SKILL = "skills/tenancy/fsdr-policy-tailoring.md"
TENANCY_OPERATIONS_SKILL = "skills/operations/fsdr-tenancy-operations.md"
READINESS_SKILL = "skills/operations/fsdr-dr-readiness.md"
READ_INFRASTRUCTURE_SKILL = "skills/operations/fsdr-read-infrastructure.md"
CREATE_PROTECTION_GROUP_SKILL = "skills/operations/fsdr-create-protection-group.md"
GENERIC_MEMBER_PREPARATION_SKILL = "skills/operations/fsdr-member-preparation.md"
START_DRILL_SKILL = "skills/operations/fsdr-start-drill.md"
STOP_DRILL_SKILL = "skills/operations/fsdr-stop-drill.md"
DEFAULT_ROUTER_SKILL = "SKILL.md"

MEMBER_PREPARATION_SKILLS = {
    "compute": "skills/prerequisites/members/fsdr-prepare-compute.md",
    "database": "skills/prerequisites/members/fsdr-prepare-database.md",
    "autonomous_database": "skills/prerequisites/members/fsdr-prepare-autonomous-database.md",
    "oke": "skills/prerequisites/members/fsdr-prepare-oke.md",
    "integration_instance": "skills/prerequisites/members/fsdr-prepare-integration-instance.md",
    "application": "skills/prerequisites/members/fsdr-prepare-application.md",
}

INTENT_DEFAULT_SKILLS = {
    "introduction": INTRO_SKILL,
    "tenancy_onboarding": TENANCY_ONBOARD_SKILL,
    "prerequisites": PREREQUISITES_SKILL,
    "member_preparation": GENERIC_MEMBER_PREPARATION_SKILL,
    "readiness": READINESS_SKILL,
    "create_protection_group": CREATE_PROTECTION_GROUP_SKILL,
    "read_inventory": READ_INFRASTRUCTURE_SKILL,
    "read_protection_group": TENANCY_OPERATIONS_SKILL,
    "explore_plans": TENANCY_OPERATIONS_SKILL,
    "run_prechecks": READINESS_SKILL,
    "start_drill": START_DRILL_SKILL,
    "stop_drill": STOP_DRILL_SKILL,
    "troubleshooting": TENANCY_OPERATIONS_SKILL,
    "unsupported": DEFAULT_ROUTER_SKILL,
}


@dataclass(frozen=True)
class SkillSpec:
    skill: str
    intent: str
    operation_type: OperationType
    requires_tenancy_context: bool
    description: str
    member_type: str = "none"


SKILL_CATALOG = {
    INTRO_SKILL: SkillSpec(INTRO_SKILL, "introduction", "instruction", False, "Explain OCI FSDR basics, scope, and boundaries."),
    TENANCY_ONBOARD_SKILL: SkillSpec(TENANCY_ONBOARD_SKILL, "tenancy_onboarding", "instruction", False, "Capture or validate tenancy context."),
    PREREQUISITES_SKILL: SkillSpec(PREREQUISITES_SKILL, "prerequisites", "instruction", False, "Explain tenancy prerequisites and IAM policies."),
    POLICY_TAILORING_SKILL: SkillSpec(POLICY_TAILORING_SKILL, "prerequisites", "instruction", False, "Tailor OCI FSDR starter IAM policy guidance to a tenancy, scope, and persona."),
    TENANCY_OPERATIONS_SKILL: SkillSpec(TENANCY_OPERATIONS_SKILL, "troubleshooting", "validate", True, "Inspect DR resources, plans, and operations in a validated tenancy."),
    READINESS_SKILL: SkillSpec(READINESS_SKILL, "readiness", "validate", True, "Assess readiness and precheck status before drill or DR operations."),
    READ_INFRASTRUCTURE_SKILL: SkillSpec(READ_INFRASTRUCTURE_SKILL, "read_inventory", "read_only", True, "Read compute, volume, and VNIC inventory."),
    CREATE_PROTECTION_GROUP_SKILL: SkillSpec(CREATE_PROTECTION_GROUP_SKILL, "create_protection_group", "mutating", True, "Guide DR Protection Group creation."),
    GENERIC_MEMBER_PREPARATION_SKILL: SkillSpec(GENERIC_MEMBER_PREPARATION_SKILL, "member_preparation", "instruction", False, "Explain supported member types and preparation guidance."),
    START_DRILL_SKILL: SkillSpec(START_DRILL_SKILL, "start_drill", "mutating", True, "Start a drill in a validated tenancy."),
    STOP_DRILL_SKILL: SkillSpec(STOP_DRILL_SKILL, "stop_drill", "mutating", True, "Stop a drill in a validated tenancy."),
}

for member_type, skill in MEMBER_PREPARATION_SKILLS.items():
    SKILL_CATALOG[skill] = SkillSpec(
        skill=skill,
        intent="member_preparation",
        operation_type="instruction",
        requires_tenancy_context=False,
        description=f"Prepare {member_type.replace('_', ' ')} resources for OCI FSDR membership.",
        member_type=member_type,
    )

ALLOWED_SKILLS = set(SKILL_CATALOG) | {DEFAULT_ROUTER_SKILL}


def skill_for_member_preparation(member_type: str) -> str:
    return MEMBER_PREPARATION_SKILLS.get(member_type, GENERIC_MEMBER_PREPARATION_SKILL)


def skill_for_intent(intent: str, member_type: str = "none") -> str:
    if intent == "member_preparation":
        return skill_for_member_preparation(member_type)
    return INTENT_DEFAULT_SKILLS.get(intent, DEFAULT_ROUTER_SKILL)


def skill_requires_tenancy(skill: str) -> bool:
    spec = SKILL_CATALOG.get(skill)
    return spec.requires_tenancy_context if spec else False
