"""
เมนู CLI สำหรับผู้ใช้งาน (Add/Update/Delete/View/Report/Exit)
"""

import config
import books
import members
import rentals
import report


def input_int(prompt):
    while True:
        val = input(prompt).strip()
        if val.isdigit():
            return int(val)
        print("กรุณากรอกตัวเลขเท่านั้น")


def input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("ห้ามเว้นว่าง")


# ---------------- ADD ----------------

def add_book():
    print("\n-- เพิ่มหนังสือ/การ์ตูน --")
    title = input_nonempty("ชื่อเรื่อง: ")
    author = input_nonempty("ผู้แต่ง: ")
    print(f"หมวดหมู่ที่เลือกได้: {', '.join(config.GENRE_PRICE.keys())}")
    genre = input_nonempty("หมวดหมู่: ")
    stock = input_int("จำนวนเล่มทั้งหมด: ")
    try:
        book_id = books.add(title, author, genre, stock)
        print(f"เพิ่มสำเร็จ! book_id = {book_id}")
    except ValueError as e:
        print(f"เกิดข้อผิดพลาด: {e}")


def add_member():
    print("\n-- เพิ่มสมาชิก --")
    name = input_nonempty("ชื่อ-นามสกุล: ")
    phone = input_nonempty("เบอร์โทร: ")
    member_id = members.add(name, phone)
    print(f"เพิ่มสำเร็จ! member_id = {member_id}")


def add_rental():
    print("\n-- เพิ่มรายการเช่า --")
    book_id = input_int("book_id: ")
    member_id = input_int("member_id: ")
    try:
        rent_id = rentals.add(book_id, member_id)
        print(f"เช่าสำเร็จ! rent_id = {rent_id}")
    except ValueError as e:
        print(f"เกิดข้อผิดพลาด: {e}")


def menu_add():
    print("\n1) เพิ่มหนังสือ  2) เพิ่มสมาชิก  3) เพิ่มรายการเช่า")
    choice = input("เลือก: ").strip()
    if choice == "1":
        add_book()
    elif choice == "2":
        add_member()
    elif choice == "3":
        add_rental()
    else:
        print("ตัวเลือกไม่ถูกต้อง")


# ---------------- UPDATE ----------------

def menu_update():
    print("\n1) แก้ไขหนังสือ  2) แก้ไขสมาชิก  3) คืนหนังสือ (return)")
    choice = input("เลือก: ").strip()
    if choice == "1":
        book_id = input_int("book_id ที่จะแก้ไข: ")
        if books.get(book_id) is None:
            print("ไม่พบ book_id นี้")
            return
        print("(เว้นว่างถ้าไม่ต้องการแก้ไขฟิลด์นั้น)")
        title = input("ชื่อเรื่องใหม่: ").strip() or None
        author = input("ผู้แต่งใหม่: ").strip() or None
        stock_str = input("จำนวนเล่มทั้งหมดใหม่: ").strip()
        stock = int(stock_str) if stock_str.isdigit() else None
        ok = books.update(book_id, title=title, author=author, stock_total=stock)
        print("แก้ไขสำเร็จ" if ok else "แก้ไขไม่สำเร็จ (อาจถูกลบไปแล้ว)")
    elif choice == "2":
        member_id = input_int("member_id ที่จะแก้ไข: ")
        if members.get(member_id) is None:
            print("ไม่พบ member_id นี้")
            return
        name = input("ชื่อใหม่ (เว้นว่างถ้าไม่แก้): ").strip() or None
        phone = input("เบอร์ใหม่ (เว้นว่างถ้าไม่แก้): ").strip() or None
        ok = members.update(member_id, name=name, phone=phone)
        print("แก้ไขสำเร็จ" if ok else "แก้ไขไม่สำเร็จ (อาจถูกลบไปแล้ว)")
    elif choice == "3":
        rent_id = input_int("rent_id ที่จะคืน: ")
        try:
            fine = rentals.return_book(rent_id)
            if fine > 0:
                print(f"คืนสำเร็จ! คืนช้า มีค่าปรับ {fine:.2f} บาท")
            else:
                print("คืนสำเร็จ! ไม่มีค่าปรับ")
        except ValueError as e:
            print(f"เกิดข้อผิดพลาด: {e}")
    else:
        print("ตัวเลือกไม่ถูกต้อง")


# ---------------- DELETE ----------------

def menu_delete():
    print("\n1) ลบหนังสือ  2) ลบสมาชิก  3) ลบรายการเช่า")
    choice = input("เลือก: ").strip()
    if choice == "1":
        book_id = input_int("book_id ที่จะลบ: ")
        ok = books.delete(book_id)
        print("ลบสำเร็จ (soft-delete)" if ok else "ไม่พบข้อมูล")
    elif choice == "2":
        member_id = input_int("member_id ที่จะลบ: ")
        ok = members.delete(member_id)
        print("ลบสำเร็จ (soft-delete)" if ok else "ไม่พบข้อมูล")
    elif choice == "3":
        rent_id = input_int("rent_id ที่จะลบ: ")
        ok = rentals.delete(rent_id)
        print("ลบสำเร็จ (soft-delete)" if ok else "ไม่พบข้อมูล")
    else:
        print("ตัวเลือกไม่ถูกต้อง")


# ---------------- VIEW ----------------

def print_book_row(b):
    status_str = "Active" if b["status"] == config.STATUS_ACTIVE else "Deleted"
    print(f"[{b['book_id']}] {b['title']} - {b['author']} ({b['genre']}) "
          f"ราคา {b['price_per_day']:.2f}/วัน คงเหลือ {b['stock_available']}/{b['stock_total']} [{status_str}]")


def menu_view():
    print("\n1) ดูรายการเดียว  2) ดูทั้งหมด  3) ดูแบบกรอง  4) สถิติโดยสรุป")
    choice = input("เลือก: ").strip()
    if choice == "1":
        book_id = input_int("book_id: ")
        b = books.get(book_id)
        print_book_row(b) if b else print("ไม่พบข้อมูล")
    elif choice == "2":
        book_list = books.list_all(active_only=False)
        if not book_list:
            print("ยังไม่มีข้อมูลหนังสือ")
        for b in book_list:
            print_book_row(b)
    elif choice == "3":
        genre = input("กรองตามหมวดหมู่ (เว้นว่าง = ไม่กรอง): ").strip() or None
        avail = input("เฉพาะที่ว่างให้เช่าเท่านั้น? (y/n): ").strip().lower() == "y"
        result = books.filter_books(genre=genre, available_only=avail)
        if not result:
            print("ไม่พบข้อมูลตามเงื่อนไข")
        for b in result:
            print_book_row(b)
    elif choice == "4":
        s = books.stats()
        r = rentals.stats()
        print(f"หนังสือทั้งหมด: {s['total_titles']} (Active {s['active_titles']}, Deleted {s['deleted_titles']})")
        print(f"จำนวนเล่มทั้งหมด: {s['total_copies']} | กำลังถูกยืม: {s['currently_borrowed']} | ว่าง: {s['available_now']}")
        print(f"ราคา/วัน Min={s['price_min']:.2f} Max={s['price_max']:.2f} Avg={s['price_avg']:.2f}")
        print(f"รายการเช่าที่ยังไม่คืน: {r['total_active_rentals']} | ค้างเกินกำหนด: {r['overdue_rentals']}")
        print(f"ค่าปรับที่เก็บได้สะสม: {r['total_fine_collected']:.2f} บาท")
    else:
        print("ตัวเลือกไม่ถูกต้อง")


# ---------------- MAIN LOOP ----------------

def main_menu():
    while True:
        print("\n" + "=" * 40)
        print(f"       {config.APP_NAME}")
        print("=" * 40)
        print("1) Add (เพิ่ม)")
        print("2) Update (แก้ไข)")
        print("3) Delete (ลบ)")
        print("4) View (ดู)")
        print("5) Generate Report (.txt)")
        print("0) Exit (ออก)")
        choice = input("เลือกเมนู: ").strip()

        if choice == "1":
            menu_add()
        elif choice == "2":
            menu_update()
        elif choice == "3":
            menu_delete()
        elif choice == "4":
            menu_view()
        elif choice == "5":
            path = report.generate()
            print(f"สร้างรายงานเรียบร้อย: {path}")
        elif choice == "0":
            report.generate()
            print("บันทึกรายงานอัตโนมัติก่อนออกโปรแกรม... ลาก่อน!")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาเลือกใหม่")