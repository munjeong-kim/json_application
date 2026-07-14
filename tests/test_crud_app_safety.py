"""crud_app.py에 대한 safety test (pytest)

이상한 값 입력, 손상된 데이터 파일, 극단적인 사용자 행동을 가정하고
앱이 예외를 던지며 죽지 않고 안전하게(graceful) 처리하는지 검증한다.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import crud_app


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "db.json"
    monkeypatch.setattr(crud_app, "DB_FILE", str(path))
    return path


def feed_inputs(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(iterator))


# ---------- Create: 이상한 age 입력 ----------

def test_age에_문자를_입력해도_죽지_않고_생성이_취소된다(db_file, monkeypatch, capsys):
    feed_inputs(monkeypatch, ["Alice", "alice@example.com", "abc", "y", ""])

    crud_app.create_record()  # 예외 없이 리턴되어야 한다

    out = capsys.readouterr().out
    assert "숫자여야" in out
    assert crud_app.load_data() == []  # 잘못된 입력으로는 저장되지 않는다


def test_age에_특수문자와_기호를_입력해도_죽지_않는다(db_file, monkeypatch):
    # int()가 실제로 파싱 가능한 유니코드 숫자(٣, ０)는 정상 생성되고,
    # 그 외 파싱 불가능한 값은 거부되어야 한다. 중요한 건 어떤 값도 예외로 죽지 않는 것.
    for bad_age in ["!!!", "1e10", "3.14", "-", "0x10"]:
        feed_inputs(monkeypatch, ["Name", "a@b.com", bad_age, "n", ""])
        crud_app.create_record()  # 예외가 나면 여기서 테스트 실패

    assert crud_app.load_data() == []


def test_age에_매우_긴_숫자_문자열은_거부된다(db_file, monkeypatch, capsys):
    huge_number = "9" * 1000
    feed_inputs(monkeypatch, ["Name", "a@b.com", huge_number, "y", ""])

    crud_app.create_record()  # 64비트 범위 초과로 죽지 않고 거부되어야 한다

    out = capsys.readouterr().out
    assert "너무 큽니다" in out
    assert crud_app.load_data() == []


# ---------- Create: 악의적/극단적 문자열 ----------

@pytest.mark.parametrize(
    "malicious_name",
    [
        pytest.param("'; DROP TABLE users; --", id="sql_injection"),
        pytest.param("<script>alert(1)</script>", id="xss"),
        pytest.param("../../../../etc/passwd", id="path_traversal"),
        pytest.param("\x00\x01\x02", id="null_bytes"),
        pytest.param("A" * 100_000, id="very_long_string"),
        pytest.param("😀🔥💀" * 100, id="emoji"),
        pytest.param("{{7*7}}", id="template_injection"),
        pytest.param("{'id': 999, 'is_active': True}", id="dict_like_string"),
    ],
)
def test_악의적인_name_입력도_그대로_저장되고_조회된다(db_file, monkeypatch, malicious_name):
    feed_inputs(monkeypatch, [malicious_name, "a@b.com", "", "n", ""])

    crud_app.create_record()  # 예외 없이 저장되어야 한다

    data = crud_app.load_data()
    assert data[0]["name"] == malicious_name


def test_공백만으로_이루어진_name은_strip되어_빈문자열로_저장된다(db_file, monkeypatch):
    feed_inputs(monkeypatch, ["\n\r\t", "a@b.com", "", "n", ""])

    crud_app.create_record()  # 예외 없이 저장되어야 한다

    data = crud_app.load_data()
    assert data[0]["name"] == ""


def test_tags에_구분자만_잔뜩_입력해도_죽지_않는다(db_file, monkeypatch):
    feed_inputs(monkeypatch, ["Name", "a@b.com", "", "n", ",,,,,, , , ,,,"])

    crud_app.create_record()

    data = crud_app.load_data()
    assert data[0]["tags"] == []


def test_모든_필드를_빈_문자열로_입력해도_죽지_않는다(db_file, monkeypatch):
    feed_inputs(monkeypatch, ["", "", "", "", ""])

    crud_app.create_record()

    data = crud_app.load_data()
    assert data[0]["name"] == ""
    assert data[0]["age"] is None
    assert data[0]["is_active"] is False
    assert data[0]["tags"] == []


# ---------- Read: 극단적인 검색 키 ----------

@pytest.mark.parametrize(
    "weird_key",
    ["", " ", "-1", "99999999999999999999", "🙂", "\x00", "%00", "' OR '1'='1"],
)
def test_이상한_검색어를_입력해도_죽지_않는다(db_file, monkeypatch, capsys, weird_key):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, [weird_key])

    crud_app.read_one()  # 예외 없이 리턴되어야 한다

    out = capsys.readouterr().out
    assert out  # 뭔가는 출력되어야 함 (에러 없이 종료)


def test_name_키가_없는_레코드가_섞여있어도_검색이_죽지_않는다(db_file, monkeypatch):
    crud_app.save_data([{"id": 1}, {"id": 2, "name": "Bob"}])
    feed_inputs(monkeypatch, ["bob"])

    crud_app.read_one()  # name 키가 없는 레코드 때문에 KeyError가 나면 안 된다


# ---------- Update / Delete: 극단적인 id ----------

@pytest.mark.parametrize(
    "weird_id",
    ["-1", "0", "abc", "1.5", "99999999999999999999", "' OR '1'='1", "1;drop table", ""],
)
def test_update시_이상한_id를_입력해도_죽지_않는다(db_file, monkeypatch, capsys, weird_id):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, [weird_id])

    crud_app.update_record()

    out = capsys.readouterr().out
    assert out
    assert crud_app.load_data() == [{"id": 1, "name": "Alice"}]  # 변경되지 않아야 함


@pytest.mark.parametrize(
    "weird_id",
    ["-1", "0", "abc", "1.5", "99999999999999999999", "' OR '1'='1", "1;drop table", ""],
)
def test_delete시_이상한_id를_입력해도_죽지_않는다(db_file, monkeypatch, capsys, weird_id):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, [weird_id])

    crud_app.delete_record()

    out = capsys.readouterr().out
    assert out
    assert crud_app.load_data() == [{"id": 1, "name": "Alice"}]  # 삭제되지 않아야 함


def test_동일한_id를_두번_삭제해도_두번째는_안전하게_처리된다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}])

    feed_inputs(monkeypatch, ["1", "y"])
    crud_app.delete_record()
    assert crud_app.load_data() == []

    feed_inputs(monkeypatch, ["1"])
    crud_app.delete_record()  # 이미 삭제된 id를 다시 삭제 시도

    out = capsys.readouterr().out
    assert "없습니다" in out


def test_update시_field_이름에_악의적인_값을_넣어도_거부된다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, ["1", "__class__"])

    crud_app.update_record()

    out = capsys.readouterr().out
    assert "지원하지 않는" in out
    assert crud_app.load_data() == [{"id": 1, "name": "Alice"}]


def test_update시_age를_문자로_넣어도_죽지_않고_취소된다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice", "age": 30}])
    feed_inputs(monkeypatch, ["1", "age", "not-a-number"])

    crud_app.update_record()

    out = capsys.readouterr().out
    assert "숫자여야" in out
    assert crud_app.load_data() == [{"id": 1, "name": "Alice", "age": 30}]  # 변경되지 않음


# ---------- 손상된 db.json 파일 ----------

def test_손상된_json_파일을_로드해도_죽지_않고_빈_목록을_반환한다(db_file, capsys):
    db_file.write_bytes(b"{not valid json!!! ///")

    data = crud_app.load_data()

    assert data == []
    out = capsys.readouterr().out
    assert "손상" in out


def test_최상위가_리스트가_아닌_json도_안전하게_처리된다(db_file, capsys):
    db_file.write_bytes(b'{"id": 1, "name": "not a list"}')

    data = crud_app.load_data()

    assert data == []
    out = capsys.readouterr().out
    assert "올바르지" in out


def test_레코드에_id가_없어도_next_id가_죽지_않는다():
    data = [{"name": "no id here"}]
    assert crud_app.next_id(data) == 1


def test_레코드에_id가_없어도_find_by_id가_죽지_않는다():
    data = [{"name": "no id here"}, {"id": 5, "name": "has id"}]
    assert crud_app.find_by_id(data, 5) == {"id": 5, "name": "has id"}
    assert crud_app.find_by_id(data, 1) is None


# ---------- main() 메뉴 루프: 잘못된 메뉴 입력 ----------

def test_메뉴에_잘못된_값을_반복_입력해도_죽지_않고_종료할_수_있다(db_file, monkeypatch, capsys):
    feed_inputs(monkeypatch, ["abc", "", "999", "-1", "😀", "0"])

    crud_app.main()  # 예외 없이 루프를 빠져나와야 한다

    out = capsys.readouterr().out
    assert out.count("잘못된 선택입니다.") >= 4
    assert "종료합니다." in out
