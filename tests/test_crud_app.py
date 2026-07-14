"""crud_app.py에 대한 regression test (pytest)"""

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


# ---------- load_data / save_data ----------

def test_파일이_없으면_빈_리스트를_반환한다(db_file):
    assert crud_app.load_data() == []


def test_저장하고_불러오면_동일한_데이터를_반환한다(db_file):
    records = [{"id": 1, "name": "Alice"}]
    crud_app.save_data(records)
    assert crud_app.load_data() == records


def test_파일이_비어있으면_빈_리스트를_반환한다(db_file):
    db_file.write_bytes(b"")
    assert crud_app.load_data() == []


# ---------- next_id / find_by_id ----------

def test_데이터가_없으면_다음_id는_1이다():
    assert crud_app.next_id([]) == 1


def test_다음_id는_기존_최대_id에서_증가한다():
    data = [{"id": 1}, {"id": 5}, {"id": 3}]
    assert crud_app.next_id(data) == 6


def test_id로_레코드를_찾는다():
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    assert crud_app.find_by_id(data, 2) == {"id": 2, "name": "Bob"}


def test_존재하지_않는_id는_찾지_못한다():
    data = [{"id": 1, "name": "Alice"}]
    assert crud_app.find_by_id(data, 99) is None


# ---------- Create ----------

def test_레코드_생성시_추가되고_파일에_저장된다(db_file, monkeypatch):
    feed_inputs(monkeypatch, ["Alice", "alice@example.com", "30", "y", "dev,python"])

    crud_app.create_record()

    data = crud_app.load_data()
    assert len(data) == 1
    assert data[0] == {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
        "is_active": True,
        "tags": ["dev", "python"],
    }


def test_레코드_생성시_id가_순차적으로_증가한다(db_file, monkeypatch):
    crud_app.save_data([{"id": 1, "name": "Existing", "email": "", "age": None, "is_active": False, "tags": []}])

    feed_inputs(monkeypatch, ["Bob", "bob@example.com", "25", "n", ""])
    crud_app.create_record()

    data = crud_app.load_data()
    assert len(data) == 2
    assert data[1]["id"] == 2
    assert data[1]["is_active"] is False
    assert data[1]["tags"] == []


def test_나이를_비워두면_None으로_저장된다(db_file, monkeypatch):
    feed_inputs(monkeypatch, ["NoAge", "noage@example.com", "", "n", ""])
    crud_app.create_record()

    data = crud_app.load_data()
    assert data[0]["age"] is None


# ---------- Read ----------

def test_전체_목록_조회시_모든_레코드가_출력된다(db_file, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])

    crud_app.read_all()

    out = capsys.readouterr().out
    assert "Alice" in out
    assert "Bob" in out


def test_데이터가_없으면_안내_메시지가_출력된다(db_file, capsys):
    crud_app.read_all()
    out = capsys.readouterr().out
    assert "없습니다" in out


def test_id로_검색하면_해당_레코드만_출력된다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
    feed_inputs(monkeypatch, ["2"])

    crud_app.read_one()

    out = capsys.readouterr().out
    assert "Bob" in out
    assert "Alice" not in out


def test_이름_일부로_검색하면_일치하는_레코드가_출력된다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
    feed_inputs(monkeypatch, ["ali"])

    crud_app.read_one()

    out = capsys.readouterr().out
    assert "Alice" in out
    assert "Bob" not in out


def test_검색결과가_없으면_안내_메시지가_출력된다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, ["nobody"])

    crud_app.read_one()

    out = capsys.readouterr().out
    assert "없습니다" in out


# ---------- Update ----------

def test_필드_수정시_값이_변경된다(db_file, monkeypatch):
    crud_app.save_data([{"id": 1, "name": "Alice", "email": "a@x.com", "age": 30, "is_active": True, "tags": []}])
    feed_inputs(monkeypatch, ["1", "age", "31"])

    crud_app.update_record()

    data = crud_app.load_data()
    assert data[0]["age"] == 31


def test_tags_필드_수정시_리스트로_변환된다(db_file, monkeypatch):
    crud_app.save_data([{"id": 1, "name": "Alice", "email": "", "age": None, "is_active": False, "tags": []}])
    feed_inputs(monkeypatch, ["1", "tags", "a, b, c"])

    crud_app.update_record()

    data = crud_app.load_data()
    assert data[0]["tags"] == ["a", "b", "c"]


def test_존재하지_않는_id_수정시_변경되지_않는다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, ["99"])

    crud_app.update_record()

    out = capsys.readouterr().out
    assert "없습니다" in out
    assert crud_app.load_data() == [{"id": 1, "name": "Alice"}]


def test_지원하지_않는_필드명_입력시_안내_메시지가_출력된다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, ["1", "unknown_field"])

    crud_app.update_record()

    out = capsys.readouterr().out
    assert "지원하지 않는" in out


# ---------- Delete ----------

def test_삭제_확인시_레코드가_삭제된다(db_file, monkeypatch):
    crud_app.save_data([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
    feed_inputs(monkeypatch, ["1", "y"])

    crud_app.delete_record()

    data = crud_app.load_data()
    assert [r["id"] for r in data] == [2]


def test_삭제_취소시_레코드가_유지된다(db_file, monkeypatch):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, ["1", "n"])

    crud_app.delete_record()

    data = crud_app.load_data()
    assert len(data) == 1


def test_존재하지_않는_id_삭제시_변경되지_않는다(db_file, monkeypatch, capsys):
    crud_app.save_data([{"id": 1, "name": "Alice"}])
    feed_inputs(monkeypatch, ["99"])

    crud_app.delete_record()

    out = capsys.readouterr().out
    assert "없습니다" in out
    assert len(crud_app.load_data()) == 1
