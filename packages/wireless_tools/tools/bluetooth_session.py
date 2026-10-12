"""Persist and operate Bluetooth configuration and node objects for agents.

This CLI is a pure-Python replacement for the mutable MATLAB handle-object
workflow.  Every request names a SQLite ``session_file``; no Python process
or callback function is kept alive between calls.  Node callbacks are exposed
as filtered, ordered event logs through ``subscribe`` and ``events``.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import sqlite3
import time
import uuid
from typing import Any

from _bluetooth_common import InputError, run_cli
from _bluetooth_session_runtime import (
    PUBLIC_OBJECT_KINDS,
    create_object,
    invoke_object,
    public_value,
    run_nodes,
    set_properties,
)


SESSION_VERSION = 1
MAX_EVENT_PAGE = 1000


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def _decode(value: str) -> Any:
    return json.loads(value)


def _path(request: dict[str, Any]) -> Path:
    value = request.get("session_file")
    if not isinstance(value, str) or not value.strip():
        raise InputError("session_file must be a nonempty path")
    path = Path(value).expanduser().resolve()
    if path.exists() and path.is_dir():
        raise InputError("session_file must name a file, not a directory")
    return path


def _connect(path: Path, *, create: bool) -> sqlite3.Connection:
    if not path.exists() and not create:
        raise InputError("session_file does not exist; create it with create_session")
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def _initialize(connection: sqlite3.Connection) -> bool:
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY NOT NULL,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS objects (
            object_id TEXT PRIMARY KEY NOT NULL,
            object_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            revision INTEGER NOT NULL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_time REAL NOT NULL,
            object_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id TEXT PRIMARY KEY NOT NULL,
            object_id TEXT,
            event_types TEXT NOT NULL,
            created_at REAL NOT NULL
        );
    """)
    row = connection.execute("SELECT value FROM metadata WHERE key = 'session_version'").fetchone()
    if row is None:
        now = time.time()
        connection.executemany("INSERT INTO metadata(key,value) VALUES(?,?)", [
            ("session_version", str(SESSION_VERSION)),
            ("session_id", str(uuid.uuid4())),
            ("simulation_time", "0.0"),
            ("created_at", repr(now)),
        ])
        connection.commit()
        return True
    if row["value"] != str(SESSION_VERSION):
        raise InputError(f"session_file has unsupported session version {row['value']}")
    return False


def _meta(connection: sqlite3.Connection, key: str) -> str:
    row = connection.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
    if row is None:
        raise InputError(f"session metadata is missing {key}")
    return str(row["value"])


def _time(connection: sqlite3.Connection) -> float:
    return float(_meta(connection, "simulation_time"))


def _set_time(connection: sqlite3.Connection, simulation_time: float) -> None:
    connection.execute("UPDATE metadata SET value = ? WHERE key = 'simulation_time'", (repr(simulation_time),))


def _object_id(request: dict[str, Any]) -> str:
    value = request.get("object_id")
    if not isinstance(value, str) or not value:
        raise InputError("object_id must be a nonempty string")
    return value


def _load_object(connection: sqlite3.Connection, object_id: str) -> tuple[str, dict[str, Any], int]:
    row = connection.execute("SELECT object_type,payload,revision FROM objects WHERE object_id = ?", (object_id,)).fetchone()
    if row is None:
        raise InputError("object_id does not exist in this session")
    return str(row["object_type"]), _decode(str(row["payload"])), int(row["revision"])


def _save_object(connection: sqlite3.Connection, object_id: str, payload: dict[str, Any], revision: int) -> int:
    next_revision = revision + 1
    connection.execute("UPDATE objects SET payload = ?, revision = ?, updated_at = ? WHERE object_id = ?",
                       (_json(payload), next_revision, time.time(), object_id))
    return next_revision


def _emit(connection: sqlite3.Connection, object_id: str, event_type: str,
          payload: dict[str, Any], simulation_time: float) -> None:
    connection.execute("INSERT INTO events(simulation_time,object_id,event_type,payload) VALUES(?,?,?,?)",
                       (simulation_time, object_id, event_type, _json(payload)))


def _session_info(connection: sqlite3.Connection, path: Path) -> dict[str, Any]:
    count = connection.execute("SELECT COUNT(*) AS count FROM objects").fetchone()["count"]
    return {
        "session_file": str(path), "session_id": _meta(connection, "session_id"),
        "session_version": SESSION_VERSION, "simulation_time": _time(connection),
        "object_count": int(count),
    }


def _create_session(request: dict[str, Any]) -> dict[str, Any]:
    path = _path(request)
    if "overwrite" in request and not isinstance(request["overwrite"], bool):
        raise InputError("overwrite must be boolean")
    if path.exists() and request.get("overwrite", False):
        # An existing SQLite session is a user-specified explicit target.  This
        # operation avoids shell deletion and removes only protocol tables.
        connection = _connect(path, create=False)
        try:
            connection.executescript("DROP TABLE IF EXISTS subscriptions; DROP TABLE IF EXISTS events;"
                                   "DROP TABLE IF EXISTS objects; DROP TABLE IF EXISTS metadata;")
            connection.commit()
        finally:
            connection.close()
    connection = _connect(path, create=True)
    try:
        created = _initialize(connection)
        return {"result": {**_session_info(connection, path), "created": created}}
    finally:
        connection.close()


def _create_object(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    object_type = request.get("object_type")
    if not isinstance(object_type, str):
        raise InputError("object_type must be a string")
    payload = create_object(object_type, request.get("properties", {}))
    object_id = request.get("new_object_id") or str(uuid.uuid4())
    if not isinstance(object_id, str) or not object_id:
        raise InputError("new_object_id must be a nonempty string when supplied")
    if connection.execute("SELECT 1 FROM objects WHERE object_id = ?", (object_id,)).fetchone() is not None:
        raise InputError("new_object_id already exists in this session")
    now = time.time()
    connection.execute("INSERT INTO objects(object_id,object_type,payload,revision,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                       (object_id, object_type, _json(payload), 1, now, now))
    _emit(connection, object_id, "ObjectCreated", {"object_type": object_type}, _time(connection))
    return {"object_id": object_id, "object_type": object_type, "revision": 1,
            "value": public_value(object_type, payload)}


def _list_objects(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    type_filter = request.get("object_type")
    if type_filter is not None and type_filter not in PUBLIC_OBJECT_KINDS:
        raise InputError("object_type is unsupported")
    rows = connection.execute(
        "SELECT object_id,object_type,payload,revision FROM objects" +
        (" WHERE object_type = ?" if type_filter else "") + " ORDER BY created_at,object_id",
        (type_filter,) if type_filter else (),
    ).fetchall()
    return {"objects": [{"object_id": row["object_id"], "object_type": row["object_type"],
                          "revision": row["revision"],
                          "value": public_value(row["object_type"], _decode(row["payload"]))}
                         for row in rows]}


def _get(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    object_id = _object_id(request)
    object_type, payload, revision = _load_object(connection, object_id)
    return {"object_id": object_id, "object_type": object_type, "revision": revision,
            "value": public_value(object_type, payload)}


def _set(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    object_id = _object_id(request)
    object_type, payload, revision = _load_object(connection, object_id)
    payload = set_properties(object_type, payload, request.get("properties"))
    revision = _save_object(connection, object_id, payload, revision)
    _emit(connection, object_id, "PropertiesChanged", {"properties": request["properties"]}, _time(connection))
    return {"object_id": object_id, "revision": revision, "value": public_value(object_type, payload)}


def _node_for_association(connection: sqlite3.Connection, object_id: Any, expected_type: str,
                          expected_role: str) -> tuple[str, dict[str, Any], int]:
    if not isinstance(object_id, str) or not object_id:
        raise InputError("node object identifiers must be nonempty strings")
    object_type, payload, revision = _load_object(connection, object_id)
    if object_type != expected_type:
        raise InputError(f"{object_id} must be a {expected_type} object")
    if payload["descriptor"]["role"] != expected_role:
        raise InputError(f"{object_id} must have role {expected_role}")
    return object_type, payload, revision


def _record_connection(payload: dict[str, Any], configuration_object_id: str,
                       peer_node_ids: list[int]) -> None:
    entries = payload["runtime"]["connections"]
    entries[:] = [item for item in entries if item["configuration_object_id"] != configuration_object_id]
    entries.append({"configuration_object_id": configuration_object_id, "peer_node_ids": peer_node_ids})


def _configure_nodes(connection: sqlite3.Connection, object_id: str, object_type: str,
                     payload: dict[str, Any], revision: int, method: str,
                     arguments: Any) -> dict[str, Any] | None:
    """Implement pure-Python counterparts of public configuration bind methods."""
    supported = {
        ("bluetoothConnectionConfig", "configureConnection"),
        ("bluetoothLEConnectionConfig", "configureConnection"),
        ("bluetoothLEBIGConfig", "configureBIG"),
        ("bluetoothLEPeriodicAdvConfig", "configurePeriodicAdv"),
        ("bluetoothMeshFriendshipConfig", "configureFriendship"),
    }
    if (object_type, method) not in supported:
        return None
    if not isinstance(arguments, dict):
        raise InputError(f"{method} arguments must be a JSON object")
    if object_type == "bluetoothConnectionConfig":
        required = {"central_object_id", "peripheral_object_ids"}
        if set(arguments) != required:
            raise InputError("Classic configureConnection requires central_object_id and peripheral_object_ids")
        _central_type, central, central_revision = _node_for_association(
            connection, arguments["central_object_id"], "bluetoothNode", "central")
        peripheral_ids = arguments["peripheral_object_ids"]
        if not isinstance(peripheral_ids, list) or not peripheral_ids:
            raise InputError("peripheral_object_ids must be a nonempty list")
        peripherals = [_node_for_association(connection, item, "bluetoothNode", "peripheral") for item in peripheral_ids]
    elif object_type == "bluetoothLEConnectionConfig":
        allowed = {"central_object_id", "peripheral_object_id", "cis_object_ids"}
        if not {"central_object_id", "peripheral_object_id"} <= set(arguments) or set(arguments) - allowed:
            raise InputError("LE configureConnection requires central_object_id, peripheral_object_id, optional cis_object_ids")
        _central_type, central, central_revision = _node_for_association(
            connection, arguments["central_object_id"], "bluetoothLENode", "central")
        peripherals = [_node_for_association(connection, arguments["peripheral_object_id"], "bluetoothLENode", "peripheral")]
        cis_ids = arguments.get("cis_object_ids", [])
        if not isinstance(cis_ids, list) or len(cis_ids) > 31:
            raise InputError("cis_object_ids must contain at most 31 object identifiers")
        for cis_id in cis_ids:
            cis_type, _cis_payload, _cis_revision = _load_object(connection, cis_id)
            if cis_type != "bluetoothLECISConfig":
                raise InputError("cis_object_ids must refer to bluetoothLECISConfig objects")
    elif object_type == "bluetoothLEBIGConfig":
        if set(arguments) != {"broadcaster_object_id", "receiver_object_id"}:
            raise InputError("configureBIG requires broadcaster_object_id and receiver_object_id")
        _central_type, central, central_revision = _node_for_association(
            connection, arguments["broadcaster_object_id"], "bluetoothLENode", "isochronous-broadcaster")
        peripherals = [_node_for_association(connection, arguments["receiver_object_id"], "bluetoothLENode", "synchronized-receiver")]
        cis_ids = []
    elif object_type == "bluetoothLEPeriodicAdvConfig":
        if set(arguments) != {"broadcaster_object_id", "observer_object_id"}:
            raise InputError("configurePeriodicAdv requires broadcaster_object_id and observer_object_id")
        _central_type, central, central_revision = _node_for_association(
            connection, arguments["broadcaster_object_id"], "bluetoothLENode", "broadcaster")
        peripherals = [_node_for_association(connection, arguments["observer_object_id"], "bluetoothLENode", "observer")]
        cis_ids = []
    else:
        if set(arguments) != {"friend_object_id", "low_power_object_id"}:
            raise InputError("configureFriendship requires friend_object_id and low_power_object_id")
        _central_type, central, central_revision = _node_for_association(
            connection, arguments["friend_object_id"], "bluetoothLENode", "broadcaster-observer")
        peripherals = [_node_for_association(connection, arguments["low_power_object_id"], "bluetoothLENode", "broadcaster-observer")]
        cis_ids = []
    central_id = arguments.get("central_object_id", arguments.get("broadcaster_object_id", arguments.get("friend_object_id")))
    peripheral_object_ids = (arguments.get("peripheral_object_ids") or
                             [arguments.get("peripheral_object_id", arguments.get("receiver_object_id", arguments.get("observer_object_id", arguments.get("low_power_object_id"))))])
    peer_node_ids = [item[1]["descriptor"]["id"] for item in peripherals]
    configuration = deepcopy(payload["configuration"])
    payload.setdefault("associations", {})[method] = {
        "primary_object_id": central_id, "peer_object_ids": peripheral_object_ids,
        "cis_object_ids": cis_ids,
    }
    _record_connection(central, object_id, peer_node_ids)
    central["descriptor"]["connection_config"] = configuration
    _save_object(connection, central_id, central, central_revision)
    for peer_object_id, (_peer_type, peer, peer_revision) in zip(peripheral_object_ids, peripherals):
        _record_connection(peer, object_id, [central["descriptor"]["id"]])
        peer["descriptor"]["connection_config"] = configuration
        _save_object(connection, peer_object_id, peer, peer_revision)
    now = _time(connection)
    _emit(connection, central_id, "ConnectionEstablished", {"configuration_object_id": object_id,
          "peer_node_ids": peer_node_ids}, now)
    for peer_object_id in peripheral_object_ids:
        _emit(connection, peer_object_id, "ConnectionEstablished", {"configuration_object_id": object_id,
              "peer_node_ids": [central["descriptor"]["id"]]}, now)
    revision = _save_object(connection, object_id, payload, revision)
    return {"object_id": object_id, "revision": revision, "result": {
        "configuration": public_value(object_type, payload), "primary_node_id": central["descriptor"]["id"],
        "peer_node_ids": peer_node_ids,
    }}


def _invoke(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    object_id = _object_id(request)
    object_type, payload, revision = _load_object(connection, object_id)
    now = _time(connection)
    method = request.get("method")
    if method == "set":
        arguments = request.get("arguments")
        properties = arguments.get("properties") if isinstance(arguments, dict) and set(arguments) == {"properties"} else arguments
        payload = set_properties(object_type, payload, properties)
        revision = _save_object(connection, object_id, payload, revision)
        _emit(connection, object_id, "PropertiesChanged", {"properties": properties}, now)
        return {"object_id": object_id, "revision": revision, "result": {"value": public_value(object_type, payload)}}
    if method == "isvalid":
        return {"object_id": object_id, "revision": revision, "result": {"isvalid": True}}
    configured = _configure_nodes(connection, object_id, object_type, payload, revision, method, request.get("arguments", {}))
    if configured is not None:
        return configured

    def emit(event_object_id: str, event_type: str, event_payload: dict[str, Any], event_time: float) -> None:
        _emit(connection, event_object_id, event_type, event_payload, event_time)

    payload, result = invoke_object(object_type, payload, method, request.get("arguments", {}),
                                    now, emit, object_id)
    if method == "run":
        requested = request.get("arguments", {}).get("current_time")
        if requested is not None and requested > now:
            _set_time(connection, float(requested))
    revision = _save_object(connection, object_id, payload, revision)
    return {"object_id": object_id, "revision": revision, "result": result}


def _delete_object(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    object_id = _object_id(request)
    object_type, _payload, _revision = _load_object(connection, object_id)
    now = _time(connection)
    _emit(connection, object_id, "ObjectDeleted", {"object_type": object_type}, now)
    connection.execute("DELETE FROM subscriptions WHERE object_id = ?", (object_id,))
    connection.execute("DELETE FROM objects WHERE object_id = ?", (object_id,))
    return {"object_id": object_id, "deleted": True}


def _run(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    has_duration = "duration" in request
    has_until = "until" in request
    if has_duration == has_until:
        raise InputError("provide exactly one of duration or until")
    start = _time(connection)
    if has_duration:
        duration = request["duration"]
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 0 <= duration < float("inf"):
            raise InputError("duration must be a finite nonnegative number")
        until = start + float(duration)
    else:
        until = request["until"]
        if isinstance(until, bool) or not isinstance(until, (int, float)) or not start <= until < float("inf"):
            raise InputError("until must be a finite number no earlier than simulation_time")
        until = float(until)
    rows = connection.execute("SELECT object_id,object_type,payload,revision FROM objects").fetchall()
    objects = {str(row["object_id"]): (str(row["object_type"]), _decode(str(row["payload"]))) for row in rows}

    def emit(object_id: str, event_type: str, payload: dict[str, Any], event_time: float) -> None:
        _emit(connection, object_id, event_type, payload, event_time)

    summary = run_nodes(objects, start, until, emit)
    for row in rows:
        object_id = str(row["object_id"])
        object_type, payload = objects[object_id]
        if object_type in {"bluetoothNode", "bluetoothLENode"}:
            _save_object(connection, object_id, payload, int(row["revision"]))
    _set_time(connection, until)
    return {"simulation": summary}


def _subscribe(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    object_id = request.get("object_id")
    if object_id is not None:
        if not isinstance(object_id, str):
            raise InputError("object_id must be a string")
        _load_object(connection, object_id)
    types = request.get("event_types", ["*"])
    if not isinstance(types, list) or not types or any(not isinstance(item, str) or not item for item in types):
        raise InputError("event_types must be a nonempty list of event names")
    if "*" in types and len(types) != 1:
        raise InputError("event_types may contain * only by itself")
    subscription_id = request.get("subscription_id") or str(uuid.uuid4())
    if not isinstance(subscription_id, str) or not subscription_id:
        raise InputError("subscription_id must be a nonempty string when supplied")
    if connection.execute("SELECT 1 FROM subscriptions WHERE subscription_id = ?", (subscription_id,)).fetchone() is not None:
        raise InputError("subscription_id already exists in this session")
    connection.execute("INSERT INTO subscriptions(subscription_id,object_id,event_types,created_at) VALUES(?,?,?,?)",
                       (subscription_id, object_id, _json(types), time.time()))
    return {"subscription_id": subscription_id, "object_id": object_id, "event_types": types}


def _events(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    after = request.get("after_sequence", 0)
    if not isinstance(after, int) or isinstance(after, bool) or after < 0:
        raise InputError("after_sequence must be a nonnegative integer")
    limit = request.get("limit", 100)
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_EVENT_PAGE:
        raise InputError(f"limit must be an integer in 1..{MAX_EVENT_PAGE}")
    subscription_id = request.get("subscription_id")
    object_id = None
    event_types = ["*"]
    if subscription_id is not None:
        if not isinstance(subscription_id, str):
            raise InputError("subscription_id must be a string")
        subscription = connection.execute("SELECT object_id,event_types FROM subscriptions WHERE subscription_id = ?",
                                          (subscription_id,)).fetchone()
        if subscription is None:
            raise InputError("subscription_id does not exist in this session")
        object_id = subscription["object_id"]
        event_types = _decode(subscription["event_types"])
    rows = connection.execute("SELECT sequence,simulation_time,object_id,event_type,payload FROM events "
                              "WHERE sequence > ? ORDER BY sequence LIMIT ?", (after, MAX_EVENT_PAGE)).fetchall()
    selected = []
    for row in rows:
        if object_id is not None and row["object_id"] != object_id:
            continue
        if event_types != ["*"] and row["event_type"] not in event_types:
            continue
        selected.append({"sequence": row["sequence"], "simulation_time": row["simulation_time"],
                         "object_id": row["object_id"], "event_type": row["event_type"],
                         "payload": _decode(row["payload"])})
        if len(selected) == limit:
            break
    next_sequence = selected[-1]["sequence"] if selected else after
    return {"events": selected, "next_sequence": next_sequence, "has_more": len(rows) == MAX_EVENT_PAGE}


def _snapshot(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    include_events = request.get("include_events", False)
    if not isinstance(include_events, bool):
        raise InputError("include_events must be boolean")
    objects = [{"object_id": row["object_id"], "object_type": row["object_type"],
                "revision": row["revision"], "payload": _decode(row["payload"])}
               for row in connection.execute("SELECT object_id,object_type,payload,revision FROM objects ORDER BY created_at,object_id")]
    subscriptions = [{"subscription_id": row["subscription_id"], "object_id": row["object_id"],
                      "event_types": _decode(row["event_types"])}
                     for row in connection.execute("SELECT subscription_id,object_id,event_types FROM subscriptions ORDER BY created_at")]
    snapshot: dict[str, Any] = {"snapshot_version": SESSION_VERSION, "simulation_time": _time(connection),
                                "objects": objects, "subscriptions": subscriptions}
    if include_events:
        snapshot["events"] = _events(connection, {"after_sequence": 0, "limit": MAX_EVENT_PAGE})["events"]
        if connection.execute("SELECT COUNT(*) AS count FROM events").fetchone()["count"] > MAX_EVENT_PAGE:
            raise InputError("snapshot event log exceeds 1000 events; use events paging instead")
    return {"snapshot": snapshot}


def _restore(connection: sqlite3.Connection, request: dict[str, Any]) -> dict[str, Any]:
    snapshot = request.get("snapshot")
    if not isinstance(snapshot, dict) or snapshot.get("snapshot_version") != SESSION_VERSION:
        raise InputError("snapshot must be a version 1 session snapshot")
    objects = snapshot.get("objects")
    subscriptions = snapshot.get("subscriptions", [])
    if not isinstance(objects, list) or not isinstance(subscriptions, list):
        raise InputError("snapshot objects and subscriptions must be lists")
    existing = connection.execute("SELECT COUNT(*) AS count FROM objects").fetchone()["count"]
    replace = request.get("replace", False)
    if not isinstance(replace, bool):
        raise InputError("replace must be boolean")
    if existing and not replace:
        raise InputError("session is not empty; pass replace=true to restore")
    if replace:
        connection.executescript("DELETE FROM subscriptions; DELETE FROM events; DELETE FROM objects;")
    now = time.time()
    seen: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            raise InputError("snapshot.objects items must be objects")
        object_id = item.get("object_id")
        object_type = item.get("object_type")
        if not isinstance(object_id, str) or not object_id or object_id in seen or object_type not in PUBLIC_OBJECT_KINDS:
            raise InputError("snapshot object has an invalid or duplicate identifier/type")
        seen.add(object_id)
        payload = item.get("payload")
        if not isinstance(payload, dict):
            raise InputError("snapshot object payload must be an object")
        # Verify that the checkpoint contains the expected public shape before
        # retaining transient queues, traffic schedules and mobility state.
        try:
            public_value(object_type, payload)
        except (KeyError, TypeError, ValueError) as exc:
            raise InputError("snapshot object payload is invalid") from exc
        connection.execute("INSERT INTO objects(object_id,object_type,payload,revision,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                           (object_id, object_type, _json(payload), int(item.get("revision", 1)), now, now))
    for item in subscriptions:
        if not isinstance(item, dict) or not isinstance(item.get("subscription_id"), str):
            raise InputError("snapshot subscription is invalid")
        if item.get("object_id") is not None and item["object_id"] not in seen:
            raise InputError("snapshot subscription refers to an unknown object")
        types = item.get("event_types")
        if not isinstance(types, list) or not types:
            raise InputError("snapshot subscription event_types is invalid")
        connection.execute("INSERT INTO subscriptions(subscription_id,object_id,event_types,created_at) VALUES(?,?,?,?)",
                           (item["subscription_id"], item.get("object_id"), _json(types), now))
    events = snapshot.get("events", [])
    if events:
        if not isinstance(events, list):
            raise InputError("snapshot events must be a list")
        for event in events:
            if not isinstance(event, dict) or event.get("object_id") not in seen:
                raise InputError("snapshot event is invalid")
            _emit(connection, event["object_id"], event.get("event_type"), event.get("payload", {}),
                  float(event.get("simulation_time", 0)))
    simulation_time = snapshot.get("simulation_time")
    if isinstance(simulation_time, bool) or not isinstance(simulation_time, (int, float)) or simulation_time < 0:
        raise InputError("snapshot simulation_time is invalid")
    _set_time(connection, float(simulation_time))
    return {"restored_objects": len(objects), "simulation_time": float(simulation_time)}


def _close_session(path: Path, request: dict[str, Any]) -> dict[str, Any]:
    delete = request.get("delete", False)
    if not isinstance(delete, bool):
        raise InputError("delete must be boolean")
    if not path.exists():
        raise InputError("session_file does not exist")
    if delete:
        # The exact user-provided path has already been resolved and checked.
        path.unlink()
        wal = path.with_name(path.name + "-wal")
        shm = path.with_name(path.name + "-shm")
        if wal.exists():
            wal.unlink()
        if shm.exists():
            shm.unlink()
    return {"session_file": str(path), "deleted": delete}


def _handler(_args, request: dict[str, Any]) -> dict[str, Any]:
    operation = request.get("operation")
    operations = {"create_session", "create_object", "delete_object", "list_objects", "get", "set", "invoke", "run",
                  "subscribe", "events", "snapshot", "restore", "close_session"}
    if operation not in operations:
        raise InputError("operation must be one of " + ", ".join(sorted(operations)))
    if operation == "create_session":
        return _create_session(request)
    path = _path(request)
    if operation == "close_session":
        return {"result": _close_session(path, request)}
    connection = _connect(path, create=False)
    try:
        _initialize(connection)
        if operation == "create_object":
            result = _create_object(connection, request)
        elif operation == "delete_object":
            result = _delete_object(connection, request)
        elif operation == "list_objects":
            result = _list_objects(connection, request)
        elif operation == "get":
            result = _get(connection, request)
        elif operation == "set":
            result = _set(connection, request)
        elif operation == "invoke":
            result = _invoke(connection, request)
        elif operation == "run":
            result = _run(connection, request)
        elif operation == "subscribe":
            result = _subscribe(connection, request)
        elif operation == "events":
            result = _events(connection, request)
        elif operation == "snapshot":
            result = _snapshot(connection, request)
        else:
            result = _restore(connection, request)
        connection.commit()
        return {"result": result}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    run_cli("bluetooth_session", _handler, description=__doc__)
