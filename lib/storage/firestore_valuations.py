"""
Firestore-backed valuation storage. Pure Python — NO streamlit imports.

Collection structure: users/{uid}/valuations/{auto_id}
Each document stores _meta fields at top level (for listing) and the full
session data as a JSON string blob (avoids Firestore reserved field names
like __dataclass__, __set__, __df__ used by session_collector).
"""

import json
import logging

from lib.auth.firebase_init import get_firestore_client

logger = logging.getLogger(__name__)

_MAX_DOC_BYTES = 1_000_000  # Firestore 1MB limit


def save_valuation(uid: str, data: dict) -> str:
    """Save a valuation dict to Firestore.

    Stores _meta as native fields (for queries/listing) and the full
    data dict as a JSON string in the 'payload' field.

    Returns the Firestore document ID.
    """
    db = get_firestore_client()

    json_str = json.dumps(data, default=str)
    size = len(json_str.encode("utf-8"))
    logger.info(f"Valuation size: {size:,} bytes")

    if size > _MAX_DOC_BYTES:
        raise ValueError(
            f"Valuation data too large ({size:,} bytes). "
            f"Maximum is {_MAX_DOC_BYTES:,} bytes."
        )

    # Store meta as native fields, full data as JSON blob
    meta = data.get("_meta", {})
    doc_data = dict(meta)
    doc_data["payload"] = json_str

    doc_ref = (
        db.collection("users").document(uid)
        .collection("valuations").document()
    )
    doc_ref.set(doc_data)
    logger.info(f"Saved valuation {doc_ref.id} for user {uid}")
    return doc_ref.id


def list_valuations(uid: str) -> list:
    """List all valuations for a user (metadata only).

    Returns list of dicts with doc_id + meta fields, sorted newest first.
    """
    db = get_firestore_client()
    col_ref = (
        db.collection("users").document(uid)
        .collection("valuations")
    )

    results = []
    for doc in col_ref.stream():
        raw = doc.to_dict()
        meta = {k: v for k, v in raw.items() if k != "payload"}
        meta["doc_id"] = doc.id
        results.append(meta)

    results.sort(key=lambda m: m.get("save_date", ""), reverse=True)
    return results


def load_valuation(uid: str, doc_id: str) -> dict:
    """Load a full valuation document from Firestore.

    Parses the JSON payload back into the original dict structure.
    """
    db = get_firestore_client()
    doc = (
        db.collection("users").document(uid)
        .collection("valuations").document(doc_id).get()
    )
    if not doc.exists:
        raise FileNotFoundError(f"Valuation {doc_id} not found")

    raw = doc.to_dict()
    payload = raw.get("payload")
    if payload:
        return json.loads(payload)
    return raw


def delete_valuation(uid: str, doc_id: str) -> bool:
    """Delete a valuation document. Returns True on success."""
    db = get_firestore_client()
    doc_ref = (
        db.collection("users").document(uid)
        .collection("valuations").document(doc_id)
    )
    doc = doc_ref.get()
    if not doc.exists:
        return False
    doc_ref.delete()
    logger.info(f"Deleted valuation {doc_id} for user {uid}")
    return True
