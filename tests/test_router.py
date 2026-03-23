import backend.router as router_module
from backend.models import Session, TenancyProfile
from backend.router import build_assistant_message, route_request


def make_tenancy() -> TenancyProfile:
    return TenancyProfile(
        owner_user_id="user_demo",
        tenancy_name="demo-tenancy",
        tenancy_ocid="ocid1.tenancy.oc1..demo",
        home_region="us-ashburn-1",
        target_regions=["us-ashburn-1", "us-phoenix-1"],
        compartments_in_scope=["ocid1.compartment.oc1..demo"],
        persona="operator",
        intended_use="readiness",
        onboarding_status="ready",
        application_name="payroll",
        environment_name="prod",
    )


def test_prepare_oke_routes_without_tenancy_requirement() -> None:
    decision = route_request("How do I prepare OKE clusters for FSDR?")

    assert decision.skill == "skills/prerequisites/members/fsdr-prepare-oke.md"
    assert decision.intent == "member_preparation"
    assert decision.requires_tenancy_context is False
    assert "selected tenancy" not in (decision.missing_context or [])


def test_prepare_oke_message_stays_instruction_only_without_tenancy() -> None:
    decision = route_request("How do I prepare OKE clusters for FSDR?")
    message = build_assistant_message(decision, None, Session(user_id="user_demo", current_skill="SKILL.md", skill_version="dev"))

    assert "instruction-only guidance" in message
    assert "tenancy selection or registration" not in message


def test_autonomous_database_routes_to_specific_member_skill() -> None:
    decision = route_request("How do I prepare Autonomous Database for FSDR?")

    assert decision.skill == "skills/prerequisites/members/fsdr-prepare-autonomous-database.md"
    assert decision.member_type == "autonomous_database"


def test_read_drpg_requires_tenancy() -> None:
    decision = route_request("Read DRPG for payroll")

    assert decision.skill == "skills/operations/fsdr-tenancy-operations.md"
    assert decision.requires_tenancy_context is True
    assert "selected tenancy" in (decision.missing_context or [])


def test_run_prechecks_uses_readiness_skill() -> None:
    decision = route_request("Run prechecks for payroll", make_tenancy())

    assert decision.skill == "skills/operations/fsdr-dr-readiness.md"
    assert decision.intent == "run_prechecks"
    assert decision.requires_tenancy_context is True


def test_policy_tailoring_routes_to_tenancy_skill() -> None:
    decision = route_request("Can you tailor FSDR IAM policies for my tenancy?")

    assert decision.skill == "skills/tenancy/fsdr-policy-tailoring.md"
    assert decision.intent == "prerequisites"
    assert decision.requires_tenancy_context is False


def test_policy_tailoring_routes_for_customize_compartments_prompt() -> None:
    decision = route_request("Can you customize FSDR policies for these compartments?")

    assert decision.skill == "skills/tenancy/fsdr-policy-tailoring.md"
    assert decision.intent == "prerequisites"
    assert decision.requires_tenancy_context is False


def test_route_request_uses_classifier_result(monkeypatch) -> None:
    class DummyClassification:
        intent = "member_preparation"
        member_type = "database"
        confidence = 0.93
        best_skill = "skills/prerequisites/members/fsdr-prepare-database.md"
        missing_context = []
        reason = "ai classifier: database member preparation request"

    monkeypatch.setattr(router_module, "classify_request", lambda *_args, **_kwargs: DummyClassification())

    decision = route_request("What can I do to add database to a DRPG?")

    assert decision.skill == "skills/prerequisites/members/fsdr-prepare-database.md"
    assert decision.intent == "member_preparation"
    assert decision.member_type == "database"
    assert decision.reason == "ai classifier: database member preparation request"


def test_member_preparation_uses_prompt_context_to_reduce_missing_inputs() -> None:
    decision = route_request(
        "Prepare the payroll database member for FSDR. The primary database is in us-ashburn-1, the standby peer is in us-phoenix-1, Data Guard replication is configured, and Vault secrets are already in place.",
        make_tenancy(),
    )

    assert decision.skill == "skills/prerequisites/members/fsdr-prepare-database.md"
    assert decision.intent == "member_preparation"
    assert "primary and peer role mapping" not in (decision.missing_context or [])
    assert "replication and peer relationship status" not in (decision.missing_context or [])
    assert "vault and secret dependencies" not in (decision.missing_context or [])


def test_multi_member_request_uses_generic_orchestration_skill() -> None:
    decision = route_request("How do I prepare OKE and Database for FSDR?")

    assert decision.skill == "skills/operations/fsdr-member-preparation.md"
    assert decision.intent == "member_preparation"
    assert decision.execution_mode == "multi_skill"
    assert decision.member_types == ("oke", "database")
    assert decision.invoked_skills == (
        "skills/prerequisites/members/fsdr-prepare-oke.md",
        "skills/prerequisites/members/fsdr-prepare-database.md",
    )


def test_multi_member_message_aggregates_member_skills() -> None:
    decision = route_request("How do I prepare OKE and Database for FSDR?")
    message = build_assistant_message(decision, None, Session(user_id="user_demo", current_skill="SKILL.md", skill_version="dev"))

    assert "multi_skill" in message
    assert "Member types in scope: `oke`, `database`." in message
    assert "skills/prerequisites/members/fsdr-prepare-oke.md" in message
    assert "skills/prerequisites/members/fsdr-prepare-database.md" in message
    assert "Overall status:" in message


def test_generic_member_question_returns_supported_member_summary() -> None:
    decision = route_request("What members can I add to a protection group?")
    message = build_assistant_message(decision, None, Session(user_id="user_demo", current_skill="SKILL.md", skill_version="dev"))

    assert decision.skill == "skills/operations/fsdr-member-preparation.md"
    assert "Supported member types in this prototype:" in message
    assert "database: skills/prerequisites/members/fsdr-prepare-database.md" in message
    assert "Missing context:" not in message


def test_policy_tailoring_message_uses_policy_pack_output() -> None:
    tenancy = make_tenancy()
    decision = route_request("Please tailor the FSDR IAM policies for my tenancy", tenancy)
    message = build_assistant_message(decision, tenancy, Session(user_id="user_demo", current_skill="SKILL.md", skill_version="dev"))

    assert "Policy pack status:" in message
    assert "ready to review" in message
    assert "Suggested IAM principals:" in message
    assert "FSDROperators" in message
    assert "Dynamic group candidates:" in message
    assert "payroll-fsdr-dg" in message
    assert "Dependency policy templates to validate:" in message
    assert "Oracle-aligned starter references:" in message


def test_policy_tailoring_message_uses_placeholders_without_tenancy() -> None:
    decision = route_request("Please tailor the FSDR IAM policies for my tenancy")
    message = build_assistant_message(decision, None, Session(user_id="user_demo", current_skill="SKILL.md", skill_version="dev"))

    assert "Policy pack status:" in message
    assert "template-only" in message
    assert "<compartment_name>" in message
    assert "Dynamic group candidates:" in message
    assert "selected tenancy" in message
