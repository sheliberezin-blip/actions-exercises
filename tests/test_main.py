import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app

client = TestClient(app)


def seed_students():
    return {
        1: main.Student(id=1, name="Alice", age=20, major="Computer Science"),
        2: main.Student(id=2, name="Bob", age=22, major="Mathematics"),
        3: main.Student(id=3, name="Charlie", age=21, major="Physics"),
    }


@pytest.fixture(autouse=True)
def reset_state():
    main.students = seed_students()
    main.next_id = 4
    yield
    main.students = seed_students()
    main.next_id = 4


def create_sample_student():
    return client.post(
        "/students", json={"name": "Dave", "age": 23, "major": "Chemistry"}
    )


def test_create_student():
    response = create_sample_student()
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["name"] == "Dave"
    assert data["age"] == 23
    assert data["major"] == "Chemistry"


def test_create_student_invalid_age():
    response = client.post(
        "/students", json={"name": "Eve", "age": -1, "major": "Biology"}
    )
    assert response.status_code == 422


def test_list_students_default_seed():
    response = client.get("/students")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert {student["name"] for student in data} == {"Alice", "Bob", "Charlie"}


def test_list_students_after_create():
    create_sample_student()

    response = client.get("/students")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_get_student():
    response = client.get("/students/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"


def test_get_student_not_found():
    response = client.get("/students/999")
    assert response.status_code == 404


def test_update_student():
    response = client.put(
        "/students/1",
        json={"name": "Alice Updated", "age": 21, "major": "Data Science"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice Updated"
    assert data["age"] == 21
    assert data["major"] == "Data Science"


def test_update_student_not_found():
    response = client.put(
        "/students/999", json={"name": "Ghost", "age": 20, "major": "Undead Studies"}
    )
    assert response.status_code == 404


def test_delete_student():
    response = client.delete("/students/1")
    assert response.status_code == 204

    response = client.get("/students/1")
    assert response.status_code == 404


def test_delete_student_not_found():
    response = client.delete("/students/999")
    assert response.status_code == 404
