from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


Role = Literal["viewer", "operator", "admin"]
OnboardingStatus = Literal["ready", "blocked", "needs approval"]
IntendedUse = Literal["onboarding", "readiness", "configure", "start-drill", "stop-drill"]
SessionStatus = Literal["active", "completed"]
MessageRole = Literal["user", "assistant"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


class User(BaseModel):
    id: str = Field(default_factory=lambda: new_id("user"))
    email: str
    display_name: str
    role: Role
    created_at: datetime = Field(default_factory=utc_now)


class TenancyProfileBase(BaseModel):
    tenancy_name: str
    tenancy_ocid: str
    home_region: str
    target_regions: list[str]
    compartments_in_scope: list[str]
    persona: Role
    intended_use: IntendedUse
    application_name: str | None = None
    environment_name: str | None = None


class TenancyProfileCreate(TenancyProfileBase):
    pass


class TenancyProfileUpdate(BaseModel):
    tenancy_name: str | None = None
    tenancy_ocid: str | None = None
    home_region: str | None = None
    target_regions: list[str] | None = None
    compartments_in_scope: list[str] | None = None
    persona: Role | None = None
    intended_use: IntendedUse | None = None
    application_name: str | None = None
    environment_name: str | None = None
    onboarding_status: OnboardingStatus | None = None


class TenancyProfile(TenancyProfileBase):
    id: str = Field(default_factory=lambda: new_id("tenancy"))
    owner_user_id: str
    onboarding_status: OnboardingStatus
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class SessionCreate(BaseModel):
    tenancy_profile_id: str | None = None


class Session(BaseModel):
    id: str = Field(default_factory=lambda: new_id("session"))
    user_id: str
    tenancy_profile_id: str | None = None
    current_skill: str
    skill_version: str
    status: SessionStatus = "active"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class MessageCreate(BaseModel):
    message: str


class Message(BaseModel):
    id: str = Field(default_factory=lambda: new_id("msg"))
    session_id: str
    role: MessageRole
    content: str
    routing_reason: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("audit"))
    user_id: str
    tenancy_profile_id: str | None = None
    session_id: str | None = None
    event_type: str
    summary: str
    created_at: datetime = Field(default_factory=utc_now)


class SkillVersionResponse(BaseModel):
    repo_ref: str
    router_file: str
    loaded_at: str
    classifier_mode: str | None = None
    classifier_model: str | None = None
    classifier_endpoint: str | None = None


class SessionMessageResponse(BaseModel):
    session_id: str
    selected_skill: str
    routing_reason: str
    assistant_message: str
    skill_version: str
    execution_mode: str | None = None
    invoked_skills: list[str] = Field(default_factory=list)
    member_types: list[str] = Field(default_factory=list)
    classifier_mode: str | None = None
    classifier_model: str | None = None
    classifier_endpoint: str | None = None


class VolumeAttachmentInfo(BaseModel):
    attachment_id: str | None = None
    volume_id: str
    display_name: str
    volume_type: Literal["boot", "block"]
    lifecycle_state: str | None = None
    size_in_gbs: int | None = None
    device: str | None = None
    attachment_type: str | None = None
    is_read_only: bool | None = None
    is_shareable: bool | None = None


class VnicInfo(BaseModel):
    vnic_id: str
    display_name: str
    private_ip: str | None = None
    public_ip: str | None = None
    subnet_id: str | None = None
    nsg_ids: list[str] = Field(default_factory=list)
    hostname_label: str | None = None


class ComputeInstanceInventory(BaseModel):
    instance_id: str
    display_name: str
    lifecycle_state: str
    shape: str
    availability_domain: str
    fault_domain: str | None = None
    compartment_id: str
    region: str
    boot_volume: VolumeAttachmentInfo | None = None
    block_volumes: list[VolumeAttachmentInfo] = Field(default_factory=list)
    vnics: list[VnicInfo] = Field(default_factory=list)


class ComputeInventoryResponse(BaseModel):
    tenancy_id: str | None = None
    compartment_id: str
    region: str
    instance_count: int
    instances: list[ComputeInstanceInventory]
