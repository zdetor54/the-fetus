# fetusapp/storage_client.py
import os
from functools import lru_cache

from azure.identity import InteractiveBrowserCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

ACCOUNT_URL = os.environ["AZURE_STORAGE_ACCOUNT_URL"]
CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "patient-docs")
TENANT_ID = os.getenv("AZURE_TENANT_ID")


def _in_azure() -> bool:
    return bool(os.getenv("WEBSITE_HOSTNAME"))


@lru_cache(maxsize=1)
def _blob() -> BlobServiceClient:
    if _in_azure():
        cred = ManagedIdentityCredential()
    else:
        cred = InteractiveBrowserCredential(
            tenant_id=TENANT_ID, additionally_allowed_tenants=["*"]
        )
    return BlobServiceClient(account_url=ACCOUNT_URL, credential=cred)


def list_patient_blobs(patient_id: str) -> list[str]:
    prefix = f"patients/{patient_id}/"
    return [
        b.name
        for b in _blob()
        .get_container_client(CONTAINER)
        .list_blobs(name_starts_with=prefix)
    ]


def download_blob(blob_path: str) -> tuple[bytes, str]:
    """
    Download a blob from Azure Storage and return its content and content type.

    Args:
        blob_path: The path to the blob in the container

    Returns:
        Tuple of (blob_content as bytes, content_type as string)
    """
    blob_client = _blob().get_blob_client(container=CONTAINER, blob=blob_path)
    blob_data = blob_client.download_blob()
    content = blob_data.readall()

    # Get content type from blob properties
    properties = blob_client.get_blob_properties()
    content_type = (
        properties.content_settings.content_type or "application/octet-stream"
    )

    return content, content_type
