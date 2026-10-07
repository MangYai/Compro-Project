import os
import time
import unicodedata
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


def visual_len(text):
    """ความกว้างที่แสดงผลจริงของข้อความ (ไม่นับสระ/วรรณยุกต์ลอยของภาษาไทย
    เช่น ่ ้ ั ิ ี ึ ื ซึ่ง len() ปกตินับเป็นตัวอักษรแยก แต่ไม่ได้กินพื้นที่
    แสดงผลเพิ่ม — ใช้ค่านี้แทน len() เวลาจัดคอลัมน์ตารางที่มีข้อความไทย)"""
    return sum(1 for ch in str(text) if unicodedata.category(ch) != "Mn")


def pad_col(value, width, align="left"):
    """จัดข้อความให้ครบ width คอลัมน์ โดยอิงความกว้างแสดงผลจริง (visual_len)
    แทน f"{x:<N}"/f"{x:>N}" ปกติ ซึ่งจะเติมช่องว่างผิดถ้าข้อความมีภาษาไทย"""
    text = str(value)
    pad = " " * max(0, width - visual_len(text))
    return (pad + text) if align == "right" else (text + pad)


def render_table(headers, rows, aligns=None):
    """สร้างตารางแบบมีกรอบ (box table คั่นด้วย +/-/|) จาก headers (list ชื่อ
    คอลัมน์) และ rows (list ของ list ค่าในแต่ละแถว) คืนค่าเป็น list ของ
    บรรทัดข้อความพร้อมเส้นขอบ ความกว้างแต่ละคอลัมน์คำนวณจากความกว้างแสดงผล
    จริง (visual_len) ของเนื้อหาทั้งหมดในคอลัมน์นั้น (รองรับภาษาไทย) จึงตรง
    กับเนื้อหาเสมอ ไม่มีทางเบี้ยวแม้ข้อความแต่ละแถวยาวไม่เท่ากัน
    aligns: list ของ 'left'/'right' ต่อคอลัมน์ (ค่าเริ่มต้น = 'left' ทุกคอลัมน์)
    """
    n = len(headers)
    if aligns is None:
        aligns = ["left"] * n
    str_rows = [[str(cell) for cell in row] for row in rows]

    widths = []
    for i in range(n):
        w = visual_len(str(headers[i]))
        for row in str_rows:
            w = max(w, visual_len(row[i]))
        widths.append(w)

    def border():
        return "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt_row(cells):
        parts = [f" {pad_col(cells[i], widths[i], aligns[i])} " for i in range(n)]
        return "|" + "|".join(parts) + "|"

    lines = [border(), fmt_row(list(headers)), border()]
    for row in str_rows:
        lines.append(fmt_row(row))
    lines.append(border())
    return lines
