# FSDR Introduction

Use this skill when the user wants a brief explanation of OCI Full Stack Disaster Recovery (FSDR), what it is for, what this assistant can help with, or what falls outside scope.

## Goal

Give a short, plain-language orientation before moving into onboarding, policy, or operations workflows.

## What to explain

Keep the answer brief and structured around three points:

1. What OCI FSDR is
2. What users typically do with it
3. What it is not

## Core message

- OCI Full Stack Disaster Recovery (FSDR) is an OCI service and operating model used to organize disaster recovery preparation, orchestration, readiness validation, and drill execution for supported application stacks.
- It helps teams define recovery workflows, protection-group structure, and operational steps for DR events and DR drills.
- In this skill library, FSDR work usually progresses from tenancy onboarding to prerequisites and IAM validation, then protection-group and member preparation, then readiness checks and drill lifecycle guidance.

## What this assistant can do

- explain FSDR in plain language
- describe the typical onboarding and readiness flow
- explain prerequisites, IAM expectations, protection groups, and drills
- route the user into the correct FSDR workflow

## What this assistant is not

- not a replacement for OCI product documentation
- not an automatic executor of OCI changes by default
- not proof that a tenancy is ready unless the required context and validation are present
- not a bypass for approvals, governance, or role boundaries

## Follow-up routing

- If the user asks how to begin, route to [fsdr-tenancy-onboard.md](fsdr-tenancy-onboard.md).
- If the user asks about prerequisites or IAM, route to [fsdr-prerequisites-and-policies.md](fsdr-prerequisites-and-policies.md).
- If the user asks about protection groups, readiness, or drills in a known tenancy, route to the matching operations skill.
