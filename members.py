"""
pack/unpack และ CRUD สำหรับ members.dat
"""
import re
import struct

import storage
from config import (
    MEMBERS_FILE,
    MEMBER_FORMAT,
    MEMBER_SIZE,
    STATUS_ACTIVE,
    STATUS_DELETED,
)


def pack_member(member_id, name, phone, join_date, status):
    name_size, phone_size = _string_field_sizes()
    return struct.pack(
        MEMBER_FORMAT,
        member_id,
        storage.encode_str(name, name_size),
        storage.encode_str(phone, phone_size),
        join_date,
        status,
    )


def unpack_member(raw):
    member_id, name_raw, phone_raw, join_date, status = struct.unpack(MEMBER_FORMAT, raw)
    return {
        "member_id": member_id,
        "name": storage.decode_str(name_raw),
        "phone": storage.decode_str(phone_raw),
        "join_date": join_date,
        "status": status,
    }


def _string_field_sizes():
    sizes = [int(n) for n in re.findall(r"(\d+)s", MEMBER_FORMAT)]
    return sizes[0], sizes[1]


def add(name, phone):
    if not name or not phone:
        raise ValueError("name และ phone ห้ามว่าง")
    storage.ensure_file(MEMBERS_FILE)
    new_id = storage.next_id(MEMBERS_FILE, MEMBER_SIZE, unpack_member, "member_id")
    raw = pack_member(new_id, name, phone, storage.now_ts(), STATUS_ACTIVE)
    storage.append_record(MEMBERS_FILE, raw)
    return new_id


def get(member_id):
    storage.ensure_file(MEMBERS_FILE)
    index, record = storage.find_index_by_id(MEMBERS_FILE, MEMBER_SIZE, unpack_member, "member_id", member_id)
    if index == -1 or record["status"] == STATUS_DELETED:
        return None
    return record


def update(member_id, name=None, phone=None):
    storage.ensure_file(MEMBERS_FILE)
    index, record = storage.find_index_by_id(MEMBERS_FILE, MEMBER_SIZE, unpack_member, "member_id", member_id)
    if record is None or record["status"] == STATUS_DELETED:
        return False
    if name is not None:
        record["name"] = name
    if phone is not None:
        record["phone"] = phone
    raw = pack_member(record["member_id"], record["name"], record["phone"], record["join_date"], record["status"])
    storage.overwrite_record_at_index(MEMBERS_FILE, MEMBER_SIZE, index, raw)
    return True


def delete(member_id):
    storage.ensure_file(MEMBERS_FILE)
    index, record = storage.find_index_by_id(MEMBERS_FILE, MEMBER_SIZE, unpack_member, "member_id", member_id)
    if record is None or record["status"] == STATUS_DELETED:
        return False
    raw = pack_member(record["member_id"], record["name"], record["phone"], record["join_date"], STATUS_DELETED)
    storage.overwrite_record_at_index(MEMBERS_FILE, MEMBER_SIZE, index, raw)
    return True


def list_all(active_only=True):
    storage.ensure_file(MEMBERS_FILE)
    records = storage.read_all(MEMBERS_FILE, MEMBER_SIZE, unpack_member)
    if active_only:
        return [r for r in records if r["status"] != STATUS_DELETED]
    return records
