from flask import Blueprint

from fetusapp.storage_client import list_patient_blobs

documents = Blueprint("documents", __name__, url_prefix="/patient")


@documents.get("/<pid>/documents/_ping")
def docs_ping(pid: str) -> tuple[dict, int] | dict:
    try:
        blobs = list_patient_blobs(pid)
        return {"ok": True, "count": len(blobs)}
    except Exception as e:
        return {"ok": False, "error": str(e)}, 500
