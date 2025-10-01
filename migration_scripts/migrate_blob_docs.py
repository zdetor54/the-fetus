# scripts/migrate_blob_docs.py
import os
from datetime import timezone

from azure.identity import InteractiveBrowserCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

from fetusapp import app, db
from fetusapp.models import Patient, PatientDocument  # your existing model

ACCOUNT_URL = os.environ["AZURE_STORAGE_ACCOUNT_URL"]
CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "patient-docs")
TENANT_ID = os.environ["AZURE_TENANT_ID"]


def _cred() -> ManagedIdentityCredential | InteractiveBrowserCredential:
    if os.getenv("WEBSITE_HOSTNAME"):
        return ManagedIdentityCredential()
    # force the login to *your* tenant, allow any sub-resource tenants
    return InteractiveBrowserCredential(
        tenant_id=TENANT_ID, additionally_allowed_tenants=["*"]
    )


def run() -> None:
    svc = BlobServiceClient(ACCOUNT_URL, credential=_cred())
    cc = svc.get_container_client(CONTAINER)

    inserted = skipped = 0
    with app.app_context():
        for b in cc.list_blobs(name_starts_with="patient_files/"):
            parts = b.name.split("/")
            # structure is: patient_files/<pid>/<filename>
            if len(parts) < 3:
                continue
            try:
                pid = int(parts[1])  # 2nd segment is patient_id
            except ValueError:
                continue

            if not Patient.query.get(pid):
                continue

            if PatientDocument.query.filter_by(
                patient_id=pid, blob_path=b.name
            ).first():
                continue

            doc = PatientDocument(
                patient_id=pid,
                created_by=1,  # system user id or admin
                blob_path=b.name,
                original_filename=parts[-1],
                content_type=b.content_settings.content_type
                or "application/octet-stream",
                size_bytes=b.size,
                status="migrated",
            )
            if getattr(b, "last_modified", None):
                doc.created_on = b.last_modified.astimezone(timezone.utc).replace(
                    tzinfo=None
                )

            db.session.add(doc)
            inserted += 1
        db.session.commit()
    print(f"Inserted {inserted}, skipped(no patient) {skipped}")


if __name__ == "__main__":
    run()
