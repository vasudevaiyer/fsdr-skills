# FSDR Setup Reference

Use this reference when the user needs one Oracle-aligned summary of:

- prerequisites to start OCI Full Stack Disaster Recovery
- IAM policy expectations
- DR Protection Group setup inputs
- supported member types
- member preparation notes that affect readiness and drill workflows

## Prerequisites and IAM policy guidance

- Confirm the tenancy, compartments, and regions that will be part of the DR scope.
- Confirm the user or team can inspect and manage Full Stack DR resources in the target compartments.
- Plan for policies not only for Full Stack DR itself, but also for the managed services that Full Stack DR operates on.
- Resource principal based authentication is the preferred pattern for Full Stack DR when additional service integrations are needed.
- Before creating a DR Protection Group, make sure object storage and tag-related policies are accounted for because DR plan execution logs use an Object Storage bucket.
- For workload-specific automation, expect additional service policies. Common examples are:
  - Vault access for Oracle Database related workflows
  - Oracle Cloud Agent or Run Command access for compute workflows

## Starter IAM policy statements

Use these as Oracle-documented starter examples and replace group names and compartment names for your tenancy.

### Full DR administration in the tenancy

```text
Allow group DRUberAdmins to manage disaster-recovery-family in tenancy
```

### Create DR configurations and execute prechecks in one compartment

```text
Allow group DRMonitors to manage disaster-recovery-protection-groups in compartment ApplicationERP
Allow group DRMonitors to manage disaster-recovery-plans in compartment ApplicationERP
Allow group DRMonitors to manage disaster-recovery-prechecks in compartment ApplicationERP
```

### Create DR configurations in one compartment

```text
Allow group DRConfig to manage disaster-recovery-protection-groups in compartment ApplicationERP
Allow group DRConfig to manage disaster-recovery-plans in compartment ApplicationERP
```

## IAM resource type notes

- `disaster-recovery-family` is the family-level resource type.
- The individual resource types listed by Oracle include:
  - `disaster-recovery-protection-groups`
  - `disaster-recovery-plans`
  - `disaster-recovery-plan-prechecks`
  - `disaster-recovery-plan-executions`
  - `disaster-recovery-workrequests`

## Protection group creation checklist

Use this checklist before saying a protection group is ready to create:

- tenancy onboarding is complete
- prerequisite and IAM policy status is not blocked
- application or environment scope is identified
- source region and target region are identified
- Object Storage bucket for DR plan execution logs is identified
- peer relationship choices are understood:
  - role in the peer relationship
  - peer region
  - peer DR Protection Group if already created

Important operating note:

- Adding or removing members requires a refresh and verification of existing DR plans in the standby region. If the user already has custom plans, call this out explicitly before changing membership.

## Supported DR Protection Group member types

Use this as the default summary of what Full Stack DR can add as DR Protection Group members.

- Compute
  - moving instance
  - non-moving instance
- Oracle Database
  - Autonomous container database
  - Autonomous database
  - Oracle Base Database
  - Oracle Exadata on Oracle Public Cloud
  - Oracle Exadata on Cloud@Customer
  - Oracle Exadata on Exascale Infrastructure
- Database
  - MySQL DB System
- Storage
  - File System
  - Volume group
  - Object Storage bucket
- Networking
  - Load Balancer
  - Network Load Balancer
- Platform and developer services
  - Kubernetes Engine (OKE)
  - Integration instance

## Member preparation notes

Use these as concise guidance before deeper product-specific instructions are needed.

### Compute instances

- Prepare a block storage volume group in the same AD as the compute instance.
- Add the boot volume and attached block volumes to the volume group for moving-instance style recovery.
- If the workflow needs user-defined scripts or commands, plan for Oracle Cloud Agent Run Command access and any required `sudo` model.

### Volume groups and block storage

- Configure either cross-region replication or backups to the standby region.
- Make sure the standby replica or backup exists and is usable before treating the member as ready.
- Be explicit about whether the workload is using moving or non-moving compute, because the boot-volume expectation changes.

### Oracle databases

- Confirm the database and peer database are in the expected role relationship.
- Confirm Data Guard or remote peer configuration is already in place where required.
- Confirm any required secret or Vault references are available to Full Stack DR.

### Autonomous Database and Autonomous Container Database

- Confirm remote standby configuration exists where required.
- Confirm the primary and remote peer are mapped into the associated DR Protection Groups.

### File systems

- Confirm mount targets, export paths, and mount points are consistent with the target DR design.
- Treat file-system mount details as part of precheck readiness, not as a last-minute drill task.

### Object Storage buckets

- Confirm the source and target bucket relationship matches the intended peer-region design.
- Treat replication assumptions as an explicit part of the member design.

### OKE

- Confirm namespace, backup target bucket, and any load balancer mappings are identified before calling the member ready.

### Integration instance and other newer member types

- Verify the exact workload-specific preparation topic before claiming readiness, because newer member types can have additional service-specific requirements.

## Readiness interpretation

When using this reference inside `fsdr-dr-readiness`, treat the environment as:

- `ready` only if prerequisites, IAM policies, protection group design, and member preparation are all clear
- `partially ready` if some member-specific preparation is still open
- `blocked` if access, policy, region, or core dependency questions are still unresolved

## Start drill guidance

Use this when the user wants to understand what a Start drill plan does and what to confirm before running it.

- A Start drill plan is used to validate that the standby stack can be brought up successfully without interrupting the production environment.
- It creates a replica of the production stack in the standby DR Protection Group.
- DR Plan Executions are launched only from the standby DR Protection Group.
- Before calling the environment ready for Start drill, confirm:
  - prerequisites and IAM policies are clear
  - DR Protection Groups are associated correctly
  - the standby DR Protection Group has the relevant DR plan
  - member preparation for the workload types in scope is complete
  - any workload-specific prechecks are expected to pass
- Once Start drill begins, both the primary and standby DR Protection Groups transition into a drill-in-progress state.
- While the environment is in drill-in-progress state, Start drill, Switchover, and Failover operations should not be treated as available until Stop drill is completed.
- Built-in Start drill behavior varies by member type. Examples include:
  - Autonomous Database can convert to snapshot standby or create a clone depending on the drill option selected
  - MySQL DB System Start drill creates a clone
  - Volume groups restore in the standby region
  - File systems restore in the standby region
  - Load balancers add standby-region backend servers
  - OKE restores resources and scales up the standby node pools

## Stop drill guidance

Use this when the user wants to end a drill and clean up the replica drill stack.

- A Stop drill plan removes the replica of the production stack that was created by Start drill.
- A replica drill stack must already exist in the standby DR Protection Group before Stop drill can run.
- Do not treat Stop drill as available unless Start drill has already executed successfully.
- Before Stop drill, confirm:
  - the target drill context is identified clearly
  - the standby DR Protection Group is still in drill-in-progress context
  - the team understands what standby-side resources will be removed or terminated
- Built-in Stop drill behavior varies by member type. Examples include:
  - Autonomous Database can convert back to physical standby or delete the clone
  - MySQL DB System Stop drill terminates the clone
  - Volume groups terminate in the standby region
  - File systems unmount and terminate in the standby region
  - Load balancers remove standby-region backend servers
  - OKE performs standby cleanup and scale-down actions
