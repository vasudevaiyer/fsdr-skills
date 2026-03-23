# FSDR Read Infrastructure

Use this skill when the user wants read-only OCI inventory needed before FSDR planning, validation, or protection-group design.

## Goal

Inspect workload infrastructure without changing OCI resources.

## Supported read-only tasks

- list compute instances in a compartment
- inspect a single compute instance
- show attached boot volumes
- show attached block volumes
- show VNIC attachments and IP context

## Inputs to collect

Collect only what is missing:

- tenancy context
- region
- compartment OCID
- optional instance OCID if the request targets one server

## Workflow

1. Confirm that the request is read-only.
2. Confirm the tenancy and region in scope.
3. Collect the compartment OCID.
4. If the user wants one server only, collect the instance OCID.
5. Run the inventory lookup.
6. Summarize the findings in plain language.
7. Suggest the next FSDR-relevant step, such as prerequisites, member preparation, or protection-group planning.

## Output format

Return:

- tenancy context
- region
- compartment
- instance count
- for each instance: state, shape, AD, boot volume, block volumes, VNICs
- next recommended action

## Guardrails

- Keep this workflow read-only.
- Do not create or modify OCI resources.
- If the compartment or instance identifier is missing, ask only for that missing input.
- If OCI access or region scope is unclear, return `blocked` and explain what is missing.
