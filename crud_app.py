"""JSON 파일 기반 CRUD 콘솔 애플리케이션

PoC(poc_json_compare.py)에서 사용한 orjson 기반 JSON 파싱/저장 구조를 그대로 사용한다.
레코드 스키마는 PoC 샘플 데이터(id, name, email, age, is_active, tags)를 따른다.
"""

import orjson
import os

DB_FILE = "db.json"


def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "rb") as f:
        content = f.read()
    if not content:
        return []
    return orjson.loads(content)


def save_data(data):
    with open(DB_FILE, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))


def next_id(data):
    if not data:
        return 1
    return max(record["id"] for record in data) + 1


def find_by_id(data, record_id):
    for record in data:
        if record["id"] == record_id:
            return record
    return None


# ---------- Create ----------

def create_record():
    data = load_data()

    name = input("name: ").strip()
    email = input("email: ").strip()
    age_input = input("age: ").strip()
    is_active_input = input("is_active (y/n): ").strip().lower()
    tags_input = input("tags (comma-separated, 생략 가능): ").strip()

    record = {
        "id": next_id(data),
        "name": name,
        "email": email,
        "age": int(age_input) if age_input else None,
        "is_active": is_active_input == "y",
        "tags": [t.strip() for t in tags_input.split(",") if t.strip()],
    }

    data.append(record)
    save_data(data)
    print(f"생성 완료: {record}")


# ---------- Read ----------

def read_all():
    data = load_data()
    if not data:
        print("데이터가 없습니다.")
        return
    for record in data:
        print(record)


def read_one():
    data = load_data()
    key = input("검색할 id 또는 name: ").strip()

    if key.isdigit():
        record = find_by_id(data, int(key))
        results = [record] if record else []
    else:
        results = [r for r in data if key.lower() in r["name"].lower()]

    if not results:
        print("일치하는 데이터가 없습니다.")
        return
    for record in results:
        print(record)


# ---------- Update ----------

def update_record():
    data = load_data()
    id_input = input("수정할 id: ").strip()

    if not id_input.isdigit():
        print("id는 숫자여야 합니다.")
        return

    record = find_by_id(data, int(id_input))
    if record is None:
        print("해당 id의 데이터가 없습니다.")
        return

    print(f"현재 데이터: {record}")
    field = input("수정할 필드명 (name/email/age/is_active/tags): ").strip()

    if field not in ("name", "email", "age", "is_active", "tags"):
        print("지원하지 않는 필드입니다.")
        return

    new_value = input(f"새로운 {field} 값: ").strip()

    if field == "age":
        record[field] = int(new_value) if new_value else None
    elif field == "is_active":
        record[field] = new_value.lower() == "y"
    elif field == "tags":
        record[field] = [t.strip() for t in new_value.split(",") if t.strip()]
    else:
        record[field] = new_value

    save_data(data)
    print(f"수정 완료: {record}")


# ---------- Delete ----------

def delete_record():
    data = load_data()
    id_input = input("삭제할 id: ").strip()

    if not id_input.isdigit():
        print("id는 숫자여야 합니다.")
        return

    record_id = int(id_input)
    record = find_by_id(data, record_id)
    if record is None:
        print("해당 id의 데이터가 없습니다.")
        return

    confirm = input(f"정말 삭제하시겠습니까? {record} (y/n): ").strip().lower()
    if confirm != "y":
        print("삭제를 취소했습니다.")
        return

    data = [r for r in data if r["id"] != record_id]
    save_data(data)
    print("삭제 완료")


# ---------- Menu ----------

MENU = """
==== JSON CRUD 콘솔 애플리케이션 ====
1. Create - 데이터 생성
2. Read (all) - 전체 목록 보기
3. Read (one) - id/name으로 검색
4. Update - 데이터 수정
5. Delete - 데이터 삭제
0. 종료
"""


def main():
    actions = {
        "1": create_record,
        "2": read_all,
        "3": read_one,
        "4": update_record,
        "5": delete_record,
    }

    while True:
        print(MENU)
        choice = input("선택: ").strip()

        if choice == "0":
            print("종료합니다.")
            break

        action = actions.get(choice)
        if action is None:
            print("잘못된 선택입니다.")
            continue

        action()


if __name__ == "__main__":
    main()
