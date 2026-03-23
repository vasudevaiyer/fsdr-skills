from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import Settings
from .models import ComputeInstanceInventory, ComputeInventoryResponse, VnicInfo, VolumeAttachmentInfo

try:
    import oci
except ImportError:  # pragma: no cover - validated at runtime if dependency missing
    oci = None


class OciInventoryError(RuntimeError):
    pass


class OciDependencyError(OciInventoryError):
    pass


class OciConfigError(OciInventoryError):
    pass


@dataclass
class OciInventoryService:
    settings: Settings

    def _load_config(self, region: str | None = None) -> dict[str, Any]:
        if oci is None:
            raise OciDependencyError(
                "The oci Python SDK is not installed. Install backend requirements before using OCI inventory endpoints."
            )

        config_path = Path(self.settings.oci_config_path).expanduser()
        if not config_path.exists():
            raise OciConfigError(f"OCI config file not found at {config_path}")

        config = oci.config.from_file(
            file_location=str(config_path),
            profile_name=self.settings.oci_config_profile,
        )
        if region:
            config["region"] = region
        return config

    def get_compute_inventory(
        self,
        *,
        compartment_id: str,
        region: str | None = None,
        instance_id: str | None = None,
        tenancy_id: str | None = None,
    ) -> ComputeInventoryResponse:
        config = self._load_config(region)
        resolved_region = config["region"]

        compute_client = oci.core.ComputeClient(config)
        blockstorage_client = oci.core.BlockstorageClient(config)
        network_client = oci.core.VirtualNetworkClient(config)

        list_kwargs: dict[str, Any] = {"compartment_id": compartment_id}
        if instance_id:
            instance = compute_client.get_instance(instance_id).data
            if instance.compartment_id != compartment_id:
                raise OciInventoryError("instance_id does not belong to the requested compartment")
            instances = [instance]
        else:
            instances = oci.pagination.list_call_get_all_results(
                compute_client.list_instances,
                **list_kwargs,
            ).data

        inventory_items: list[ComputeInstanceInventory] = []
        for instance in instances:
            boot_volume = self._get_boot_volume(
                compute_client=compute_client,
                blockstorage_client=blockstorage_client,
                compartment_id=compartment_id,
                instance=instance,
            )
            block_volumes = self._get_block_volumes(
                compute_client=compute_client,
                blockstorage_client=blockstorage_client,
                compartment_id=compartment_id,
                instance_id=instance.id,
            )
            vnics = self._get_vnics(
                compute_client=compute_client,
                network_client=network_client,
                compartment_id=compartment_id,
                instance_id=instance.id,
            )
            inventory_items.append(
                ComputeInstanceInventory(
                    instance_id=instance.id,
                    display_name=instance.display_name,
                    lifecycle_state=instance.lifecycle_state,
                    shape=instance.shape,
                    availability_domain=instance.availability_domain,
                    fault_domain=getattr(instance, "fault_domain", None),
                    compartment_id=instance.compartment_id,
                    region=resolved_region,
                    boot_volume=boot_volume,
                    block_volumes=block_volumes,
                    vnics=vnics,
                )
            )

        return ComputeInventoryResponse(
            tenancy_id=tenancy_id,
            compartment_id=compartment_id,
            region=resolved_region,
            instance_count=len(inventory_items),
            instances=inventory_items,
        )

    def _get_boot_volume(
        self,
        *,
        compute_client: Any,
        blockstorage_client: Any,
        compartment_id: str,
        instance: Any,
    ) -> VolumeAttachmentInfo | None:
        attachments = oci.pagination.list_call_get_all_results(
            compute_client.list_boot_volume_attachments,
            availability_domain=instance.availability_domain,
            compartment_id=compartment_id,
            instance_id=instance.id,
        ).data
        if not attachments:
            return None

        attachment = attachments[0]
        boot_volume = blockstorage_client.get_boot_volume(attachment.boot_volume_id).data
        return VolumeAttachmentInfo(
            attachment_id=attachment.id,
            volume_id=boot_volume.id,
            display_name=boot_volume.display_name,
            volume_type="boot",
            lifecycle_state=boot_volume.lifecycle_state,
            size_in_gbs=getattr(boot_volume, "size_in_gbs", None),
            device=getattr(attachment, "device", None),
            attachment_type=getattr(attachment, "attachment_type", None),
            is_read_only=getattr(attachment, "is_read_only", None),
            is_shareable=getattr(attachment, "is_shareable", None),
        )

    def _get_block_volumes(
        self,
        *,
        compute_client: Any,
        blockstorage_client: Any,
        compartment_id: str,
        instance_id: str,
    ) -> list[VolumeAttachmentInfo]:
        attachments = oci.pagination.list_call_get_all_results(
            compute_client.list_volume_attachments,
            compartment_id=compartment_id,
            instance_id=instance_id,
        ).data

        volumes: list[VolumeAttachmentInfo] = []
        for attachment in attachments:
            if not getattr(attachment, "volume_id", None):
                continue
            volume = blockstorage_client.get_volume(attachment.volume_id).data
            volumes.append(
                VolumeAttachmentInfo(
                    attachment_id=attachment.id,
                    volume_id=volume.id,
                    display_name=volume.display_name,
                    volume_type="block",
                    lifecycle_state=volume.lifecycle_state,
                    size_in_gbs=getattr(volume, "size_in_gbs", None),
                    device=getattr(attachment, "device", None),
                    attachment_type=getattr(attachment, "attachment_type", None),
                    is_read_only=getattr(attachment, "is_read_only", None),
                    is_shareable=getattr(attachment, "is_shareable", None),
                )
            )
        return volumes

    def _get_vnics(
        self,
        *,
        compute_client: Any,
        network_client: Any,
        compartment_id: str,
        instance_id: str,
    ) -> list[VnicInfo]:
        attachments = oci.pagination.list_call_get_all_results(
            compute_client.list_vnic_attachments,
            compartment_id=compartment_id,
            instance_id=instance_id,
        ).data

        vnics: list[VnicInfo] = []
        for attachment in attachments:
            if not getattr(attachment, "vnic_id", None):
                continue
            vnic = network_client.get_vnic(attachment.vnic_id).data
            vnics.append(
                VnicInfo(
                    vnic_id=vnic.id,
                    display_name=vnic.display_name,
                    private_ip=vnic.private_ip,
                    public_ip=getattr(vnic, "public_ip", None),
                    subnet_id=vnic.subnet_id,
                    nsg_ids=list(getattr(vnic, "nsg_ids", []) or []),
                    hostname_label=getattr(vnic, "hostname_label", None),
                )
            )
        return vnics
