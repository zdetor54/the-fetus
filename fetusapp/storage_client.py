# fetusapp/storage_client.py
import os
from functools import lru_cache
from typing import Tuple

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import InteractiveBrowserCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

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


def ensure_patient_folder(patient_id: int) -> str:
    """
    Ensures that the folder structure exists for a patient's documents.
    Note: In Azure Blob Storage, folders are virtual - they're created implicitly
    when you upload a blob with a path containing slashes.

    Args:
        patient_id: The patient's ID

    Returns:
        The folder path for the patient's documents (e.g., "patient_files/123")
    """
    # Azure Blob Storage uses flat namespace, so we just return the path pattern
    # The folder will be created when the first blob is uploaded
    return f"patient_files/{patient_id}"


def check_blob_exists(blob_path: str) -> bool:
    """
    Check if a blob already exists at the given path.

    Args:
        blob_path: The full path to the blob (e.g., "patients/123/documents/file.pdf")

    Returns:
        True if blob exists, False otherwise
    """
    try:
        blob_client = _blob().get_blob_client(container=CONTAINER, blob=blob_path)
        blob_client.get_blob_properties()
        return True
    except ResourceNotFoundError:
        return False
    except Exception as e:
        # In production, use proper logging
        print(f"Error checking blob existence: {str(e)}")
        return False


def upload_blob(
    file_data: bytes, blob_path: str, content_type: str, check_duplicate: bool = True
) -> Tuple[str, int]:
    """
    Upload a file to Azure Blob Storage.

    Args:
        file_data: The file content as bytes
        blob_path: The full path where the blob should be stored
        content_type: The MIME type of the file
        check_duplicate: Whether to check for existing file (default True)

    Returns:
        Tuple of (blob_url, file_size_bytes)

    Raises:
        FileExistsError: If file already exists and check_duplicate is True
        Exception: If upload fails
    """
    try:
        # Check if blob already exists
        if check_duplicate and check_blob_exists(blob_path):
            filename = blob_path.split("/")[-1]
            raise FileExistsError(f"Υπάρχει ήδη αρχείο με το όνομα: {filename}")

        # Get blob client
        blob_client = _blob().get_blob_client(container=CONTAINER, blob=blob_path)

        # Upload the blob with content type
        content_settings = ContentSettings(content_type=content_type)
        blob_client.upload_blob(
            file_data,
            overwrite=False,  # Don't overwrite if exists (safety check)
            content_settings=content_settings,
        )

        # Get the blob URL
        blob_url = blob_client.url

        # Get file size
        file_size = len(file_data)

        return blob_url, file_size

    except FileExistsError:
        # Re-raise our custom error
        raise
    except Exception as e:
        raise Exception(f"Failed to upload file: {str(e)}")


def delete_blob(blob_path: str) -> bool:
    """
    Delete a blob from Azure Blob Storage.

    Args:
        blob_path: The full path to the blob to delete

    Returns:
        True if deletion was successful

    Raises:
        Exception: If deletion fails
    """
    try:
        blob_client = _blob().get_blob_client(container=CONTAINER, blob=blob_path)
        blob_client.delete_blob()
        return True
    except ResourceNotFoundError:
        # Blob doesn't exist - consider it already deleted
        print(f"Blob not found (already deleted?): {blob_path}")
        return True
    except Exception as e:
        raise Exception(f"Failed to delete blob: {str(e)}")
