"""
สร้างไฟล์รายงานสรุป 3 ไฟล์แยกกัน (.txt)
- report_books.txt   : books.dat   + rentals.dat
- report_members.txt : members.dat + rentals.dat
- report_rentals.txt : books.dat   + members.dat + rentals.dat

แต่ละรายงานมี 3 ส่วนตามลำดับ: (1) หัวตาราง/รายละเอียด (2) ตาราง (3) สรุปท้าย
ตารางจัดคอลัมน์ด้วย storage.pad_col() ซึ่งรองรับภาษาไทย (นับความกว้างแสดงผล
จริง ไม่ใช่ len() เฉย ๆ) หัวคอลัมน์กับข้อมูลจึงเรียงตรงกันเสมอแม้มีชื่อไทยปน
และคำนวณจากไฟล์ข้อมูลสดทุกครั้งที่เรียก generate_* จึงอัปเดตตามข้อมูลล่าสุด
"""
import books
import members
import rentals
import storage
from config import (
    APP_NAME,
    APP_VERSION,
    REPORT_BOOKS_FILE,
    REPORT_MEMBERS_FILE,
    REPORT_RENTALS_FILE,
    STATUS_DELETED,
    STATUS_BORROWING,
    STATUS_RETURNED,
)

LINE = "=" * 78
SUB = "-" * 78


def _header(title):
    return [
        LINE,
        f"{APP_NAME} v{APP_VERSION}",
        title,
        f"สร้างเมื่อ: {storage.ts_to_str(storage.now_ts())}",
        LINE,
        "",
    ]


def _footer():
    return [LINE, "จบรายงาน", LINE]


# ---------------------------------------------------------------------------
# รายงาน 1: หนังสือ (books.dat + rentals.dat)
# ---------------------------------------------------------------------------
def generate_books_report():
    """สร้าง report_books.txt (ข้อมูลจาก books.dat + rentals.dat) คืน path ของไฟล์"""
    book_rows = books.list_all(active_only=True)
    all_rentals = [r for r in rentals.list_all() if r["status"] != STATUS_DELETED]

    rent_count = {}
    for r in all_rentals:
        rent_count[r["book_id"]] = rent_count.get(r["book_id"], 0) + 1

    lines = _header("รายงานหนังสือและสถิติการเช่า")
    lines += [
        "รายละเอียด: ตารางด้านล่างแสดงหนังสือที่ยังใช้งานทุกเล่ม",
        "ผนวกจำนวนครั้งที่เคยถูกเช่าของแต่ละเล่ม",
        "",
    ]

    if book_rows:
        headers = ["ID", "ชื่อเรื่อง", "ผู้แต่ง", "ประเภท", "ราคา/วัน", "ว่าง/ทั้งหมด", "เช่าไปแล้ว"]
        aligns = ["left", "left", "left", "left", "right", "left", "right"]
        rows = []
        for b in book_rows:
            times = rent_count.get(b["book_id"], 0)
            stock = f"{b['stock_available']}/{b['stock_total']}"
            rows.append([b["book_id"], b["title"], b["author"], b["genre"],
                         f"{b['price_per_day']:.2f}", stock, times])
        lines += storage.render_table(headers, rows, aligns)
    else:
        lines.append("  (ไม่มีข้อมูล)")

    lines.append("")
    lines.append("สรุปท้ายรายงาน")
    lines.append(SUB)
    if book_rows:
        most_id, most_n = max(rent_count.items(), key=lambda kv: kv[1]) if rent_count else (None, 0)
        title_of = {b["book_id"]: b["title"] for b in book_rows}
        genre_total = {}
        for b in book_rows:
            genre_total[b["genre"]] = genre_total.get(b["genre"], 0) + rent_count.get(b["book_id"], 0)
        top_genre = max(genre_total.items(), key=lambda kv: kv[1]) if genre_total else (None, 0)
        lines.append(f"  จำนวนชื่อเรื่องทั้งหมด (ใช้งาน) : {len(book_rows)}")
        lines.append(f"  จำนวนครั้งที่ถูกเช่ารวม          : {sum(rent_count.values())}")
        if most_id is not None and most_n > 0:
            lines.append(f"  หนังสือที่ถูกเช่ามากที่สุด        : {title_of.get(most_id, '?')} ({most_n} ครั้ง)")
        else:
            lines.append("  หนังสือที่ถูกเช่ามากที่สุด        : (ยังไม่มีการเช่า)")
        if top_genre[0] is not None and top_genre[1] > 0:
            lines.append(f"  ประเภทที่ถูกเช่ามากที่สุด        : {top_genre[0]} ({top_genre[1]} ครั้ง)")
    else:
        lines.append("  (ไม่มีข้อมูลสำหรับสรุป)")

    lines += [""] + _footer()

    with open(REPORT_BOOKS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return REPORT_BOOKS_FILE


# ---------------------------------------------------------------------------
# รายงาน 2: สมาชิก (members.dat + rentals.dat)
# ---------------------------------------------------------------------------
def generate_members_report():
    """สร้าง report_members.txt (ข้อมูลจาก members.dat + rentals.dat) คืน path ของไฟล์"""
    member_rows = members.list_all(active_only=True)
    all_rentals = [r for r in rentals.list_all() if r["status"] != STATUS_DELETED]

    total_rentals = {}
    borrowing_now = {}
    fine_paid = {}
    for r in all_rentals:
        total_rentals[r["member_id"]] = total_rentals.get(r["member_id"], 0) + 1
        if r["status"] == STATUS_BORROWING:
            borrowing_now[r["member_id"]] = borrowing_now.get(r["member_id"], 0) + 1
        if r["status"] == STATUS_RETURNED:
            fine_paid[r["member_id"]] = fine_paid.get(r["member_id"], 0.0) + r["fine_amount"]

    lines = _header("รายงานสมาชิกและสถิติการเช่า")
    lines += [
        "รายละเอียด: ตารางด้านล่างแสดงสมาชิกที่ยังใช้งานทุกคน",
        "ผนวกจำนวนครั้งที่เช่า / รายการที่ยังไม่คืน / ค่าปรับสะสม",
        "",
    ]

    if member_rows:
        headers = ["ID", "ชื่อ", "เบอร์โทร", "วันที่สมัคร", "เช่าไปแล้ว", "ยังไม่คืน", "ค่าปรับสะสม"]
        aligns = ["left", "left", "left", "left", "right", "right", "right"]
        rows = []
        for m in member_rows:
            rows.append([
                m["member_id"], m["name"], m["phone"], storage.ts_to_str(m["join_date"]),
                total_rentals.get(m["member_id"], 0),
                borrowing_now.get(m["member_id"], 0),
                f"{fine_paid.get(m['member_id'], 0.0):.2f}",
            ])
        lines += storage.render_table(headers, rows, aligns)
    else:
        lines.append("  (ไม่มีข้อมูล)")

    lines.append("")
    lines.append("สรุปท้ายรายงาน")
    lines.append(SUB)
    if member_rows:
        name_of = {m["member_id"]: m["name"] for m in member_rows}
        most_id, most_n = max(total_rentals.items(), key=lambda kv: kv[1]) if total_rentals else (None, 0)
        lines.append(f"  จำนวนสมาชิกทั้งหมด (ใช้งาน)     : {len(member_rows)}")
        lines.append(f"  ยอดค่าปรับสะสมรวมทุกคน          : {sum(fine_paid.values()):.2f} บาท")
        lines.append(f"  จำนวนรายการที่ยังไม่คืนทั้งหมด    : {sum(borrowing_now.values())}")
        if most_id is not None and most_n > 0:
            lines.append(f"  สมาชิกที่เช่าบ่อยที่สุด           : {name_of.get(most_id, '?')} ({most_n} ครั้ง)")
        else:
            lines.append("  สมาชิกที่เช่าบ่อยที่สุด           : (ยังไม่มีการเช่า)")
    else:
        lines.append("  (ไม่มีข้อมูลสำหรับสรุป)")

    lines += [""] + _footer()

    with open(REPORT_MEMBERS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return REPORT_MEMBERS_FILE


# ---------------------------------------------------------------------------
# รายงาน 3: การเช่าโดยรวม (books.dat + members.dat + rentals.dat)
# ---------------------------------------------------------------------------
def generate_rentals_report():
    """สร้าง report_rentals.txt (ข้อมูลจาก books.dat + members.dat + rentals.dat) คืน path ของไฟล์"""
    items = [r for r in rentals.list_all() if r["status"] != STATUS_DELETED]
    now = storage.now_ts()

    borrowing = [r for r in items if r["status"] == STATUS_BORROWING]
    returned = [r for r in items if r["status"] == STATUS_RETURNED]
    overdue = [r for r in borrowing if r["due_date"] < now]
    total_fine = sum(r["fine_amount"] for r in returned)

    book_title = {b["book_id"]: b["title"] for b in books.list_all(active_only=False)}
    member_name = {m["member_id"]: m["name"] for m in members.list_all(active_only=False)}

    lines = _header("รายงานการเช่า-คืนโดยรวม")
    lines += [
        "รายละเอียด: ตารางด้านล่างแสดงรายการเช่าทั้งหมด",
        "พร้อมชื่อหนังสือ และชื่อสมาชิก ของแต่ละรายการ",
        "",
    ]

    if items:
        headers = ["ID", "หนังสือ", "สมาชิก", "วันเช่า", "กำหนดคืน", "วันคืน", "ค่าปรับ", "สถานะ"]
        aligns = ["left", "left", "left", "left", "left", "left", "right", "left"]
        rows = []
        for r in items:
            if r["status"] == STATUS_RETURNED:
                state = "คืนแล้ว"
            elif r["due_date"] < now:
                state = "เกินกำหนด"
            else:
                state = "กำลังยืม"
            rows.append([
                r["rent_id"], book_title.get(r["book_id"], "?"),
                member_name.get(r["member_id"], "?"),
                storage.ts_to_str(r["rent_date"]), storage.ts_to_str(r["due_date"]),
                storage.ts_to_str(r["return_date"]), f"{r['fine_amount']:.2f}", state,
            ])
        lines += storage.render_table(headers, rows, aligns)
    else:
        lines.append("  (ไม่มีข้อมูล)")

    lines.append("")
    lines.append("สรุปท้ายรายงาน")
    lines.append(SUB)
    lines.append(f"  จำนวนรายการเช่าทั้งหมด : {len(items)}")
    lines.append(f"  ยังไม่คืน              : {len(borrowing)}")
    lines.append(f"    - เกินกำหนดแล้ว      : {len(overdue)}")
    lines.append(f"  คืนแล้ว                : {len(returned)}")
    lines.append(f"  ค่าปรับรวม (ที่คืนแล้ว) : {total_fine:.2f} บาท")

    lines += [""] + _footer()

    with open(REPORT_RENTALS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return REPORT_RENTALS_FILE


def generate():
    """สร้างรายงานทั้ง 3 ไฟล์ คืน list ของ path ที่สร้าง"""
    return [
        generate_books_report(),
        generate_members_report(),
        generate_rentals_report(),
    ]
