import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session


def default_uuid() -> str:
    return str(uuid.uuid4())


def to_serializable(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, (int, float, str, bool)):
        return val
    try:
        return str(val)
    except Exception:
        return None


def extract_actor(obj) -> str:
    """Extract authenticated officer email/ID or default to forest officer."""
    for field in (
        "officer_id",
        "changed_by",
        "assigned_to",
        "recorded_by",
        "generated_by",
        "pilot_in_command",
        "email",
    ):
        val = getattr(obj, field, None)
        if val and isinstance(val, str) and val.strip():
            return val.strip()
    return "officer.assam@forest.gov.in"


def audit_before_flush(session, flush_context, instances):
    """
    SQLAlchemy before_flush listener that automatically intercepts every
    INSERT, UPDATE, and DELETE across all tables and writes an immutable
    audit trail entry into the audit_logs table.
    """
    if session.info.get("skip_audit"):
        return

    from models import AuditLog

    logs_to_add = []

    # 1. New records (CREATE)
    for obj in list(session.new):
        if isinstance(obj, AuditLog):
            continue
        entity_type = obj.__class__.__name__
        insp = inspect(obj)

        # Ensure ID is pre-assigned before flush so entity_id is exact
        if not getattr(obj, "id", None):
            obj.id = default_uuid()
        entity_id = str(obj.id)

        new_vals = {}
        for col in insp.mapper.column_attrs:
            key = col.key
            new_vals[key] = to_serializable(getattr(obj, key, None))

        desc = f"Created new {entity_type} #{entity_id[:8]}"
        if hasattr(obj, "name") and obj.name:
            desc = f"Created {entity_type}: {obj.name}"
        elif hasattr(obj, "survey_name") and obj.survey_name:
            desc = f"Logged UAV Mission: {getattr(obj, 'mission_code', '')} - {obj.survey_name}"
        elif hasattr(obj, "alert_type") and obj.alert_type:
            desc = f"Registered Incident Alert: {obj.alert_type} ({getattr(obj, 'severity', 'Medium')} severity)"
        elif hasattr(obj, "report_type") and obj.report_type:
            desc = f"Generated Carbon MRV Dossier: {obj.report_type} ({getattr(obj, 'total_agb_tonnes', 0)} t AGB)"
        elif hasattr(obj, "scene_id") and obj.scene_id:
            desc = f"Ingested Satellite Scene: {obj.scene_id} ({getattr(obj, 'satellite_name', 'Optical')})"
        elif hasattr(obj, "compartment_number") and obj.compartment_number:
            desc = f"Demarcated Compartment: #{obj.compartment_number} ({getattr(obj, 'forest_type', 'Deciduous')})"
        elif hasattr(obj, "tree_number") and obj.tree_number:
            desc = f"Recorded Tree #{obj.tree_number} caliper measurement"

        log_entry = AuditLog(
            id=default_uuid(),
            entity_type=entity_type,
            entity_id=entity_id,
            action="CREATE",
            changed_by=extract_actor(obj),
            old_values=None,
            new_values=json.dumps(new_vals),
            description=desc,
            ip_address="127.0.0.1",
            timestamp=datetime.now(timezone.utc),
        )
        logs_to_add.append(log_entry)

    # 2. Modified records (UPDATE / STATUS_CHANGE)
    for obj in list(session.dirty):
        if isinstance(obj, AuditLog):
            continue
        entity_type = obj.__class__.__name__
        insp = inspect(obj)

        old_vals = {}
        new_vals = {}
        has_changes = False
        is_status_change = False
        old_status = None
        new_status = None

        for col in insp.mapper.column_attrs:
            h = insp.attrs[col.key].history
            if h.has_changes():
                has_changes = True
                old_val = h.deleted[0] if h.deleted else None
                new_val = h.added[0] if h.added else getattr(obj, col.key, None)
                if col.key == "status":
                    is_status_change = True
                    old_status = old_val
                    new_status = new_val
                old_vals[col.key] = to_serializable(old_val)
                new_vals[col.key] = to_serializable(new_val)

        if not has_changes:
            continue

        entity_id = str(getattr(obj, "id", "unknown"))
        action = "STATUS_CHANGE" if is_status_change else "UPDATE"

        if is_status_change:
            desc = f"Status transition on {entity_type} from '{old_status or 'None'}' to '{new_status or 'None'}'"
        else:
            changed_keys = ", ".join(new_vals.keys())
            desc = f"Modified {entity_type} [{changed_keys}]"
            if hasattr(obj, "name") and obj.name:
                desc += f" on '{obj.name}'"

        log_entry = AuditLog(
            id=default_uuid(),
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changed_by=extract_actor(obj),
            old_values=json.dumps(old_vals),
            new_values=json.dumps(new_vals),
            description=desc,
            ip_address="127.0.0.1",
            timestamp=datetime.now(timezone.utc),
        )
        logs_to_add.append(log_entry)

    # 3. Deleted records (DELETE)
    for obj in list(session.deleted):
        if isinstance(obj, AuditLog):
            continue
        entity_type = obj.__class__.__name__
        insp = inspect(obj)

        old_vals = {}
        for col in insp.mapper.column_attrs:
            key = col.key
            old_vals[key] = to_serializable(getattr(obj, key, None))

        entity_id = str(old_vals.get("id") or getattr(obj, "id", "deleted"))
        desc = f"Permanently deleted {entity_type} #{entity_id[:8]}"
        if hasattr(obj, "name") and obj.name:
            desc = f"Deleted {entity_type}: '{obj.name}'"

        log_entry = AuditLog(
            id=default_uuid(),
            entity_type=entity_type,
            entity_id=entity_id,
            action="DELETE",
            changed_by=extract_actor(obj),
            old_values=json.dumps(old_vals),
            new_values=None,
            description=desc,
            ip_address="127.0.0.1",
            timestamp=datetime.now(timezone.utc),
        )
        logs_to_add.append(log_entry)

    for l in logs_to_add:
        session.add(l)


def register_audit_listener(session_factory):
    """Register the before_flush audit hook on the session maker."""
    event.listen(session_factory, "before_flush", audit_before_flush)
