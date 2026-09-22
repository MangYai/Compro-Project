"""
ฟังก์ชันช่วยเหลือทั่วไปสำหรับอ่าน/เขียนไฟล์ไบนารีแบบ fixed-length
ใช้ร่วมกันได้ทั้ง books / members / rentals
"""

import os
import time
from datetime import datetime
 
 
def encode_str(value, size):
    raw = value.encode("utf-8")[:size]
    return raw.ljust(size, b"\x00")
 
 
def decode_str(raw_bytes):
    return raw_bytes.split(b"\x00", 1)[0].decode("utf-8", errors="ignore")
 
 
def now_ts():
    return int(time.time())
 
 
def ts_to_str(ts):
    if ts == 0:
        return "-"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
 
 
def ensure_file(path):
    if not os.path.exists(path):
        open(path, "wb").close()
 
 
def count_records(path, record_size):
    ensure_file(path)
    return os.path.getsize(path) // record_size
 
 
def read_all(path, record_size, unpack_fn):
    ensure_file(path)
    records = []
    with open(path, "rb") as f:
        while True:
            raw = f.read(record_size)
            if len(raw) < record_size:
                break
            records.append(unpack_fn(raw))
    return records
 
 
def append_record(path, raw_bytes):
    ensure_file(path)
    with open(path, "ab") as f:
        f.write(raw_bytes)
 
 
def overwrite_record_at_index(path, record_size, index, raw_bytes):
    with open(path, "r+b") as f:
        f.seek(index * record_size)
        f.write(raw_bytes)
 
 
def find_index_by_id(path, record_size, unpack_fn, id_field, target_id):
    ensure_file(path)
    with open(path, "rb") as f:
        index = 0
        while True:
            raw = f.read(record_size)
            if len(raw) < record_size:
                break
            rec = unpack_fn(raw)
            if rec[id_field] == target_id:
                return index, rec
            index += 1
    return -1, None
 
 
def next_id(path, record_size, unpack_fn, id_field):
    records = read_all(path, record_size, unpack_fn)
    if not records:
        return 1
    return max(r[id_field] for r in records) + 1
 