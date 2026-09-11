"""
Integration coverage for api/v1/class_routes.py — previously untested.
Ownership here flows through Class -> Course.teacher_id, not a direct
column on Class itself.
"""

import uuid

import pytest
from factories import (
    auth_headers,
    create_class,
    create_course,
    create_student,
    create_teacher,
)


@pytest.fixture
async def teacher(db_session):
    return await create_teacher(db_session, "a")


@pytest.fixture
async def other_teacher(db_session):
    return await create_teacher(db_session, "b")


@pytest.fixture
async def student(db_session):
    return await create_student(db_session, "a")


@pytest.fixture
async def course(db_session, teacher):
    return await create_course(db_session, teacher)


@pytest.fixture
async def other_course(db_session, other_teacher):
    return await create_course(db_session, other_teacher, "other")


# ---------------------------------------------------------------------------
# create_class
# ---------------------------------------------------------------------------


async def test_create_class_as_course_owner(client, teacher, course):
    resp = await client.post(
        "/api/v1/classes/",
        json={"name": "Section A", "course_id": str(course.id)},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Section A"


async def test_create_class_requires_auth(client, course):
    resp = await client.post(
        "/api/v1/classes/", json={"name": "x", "course_id": str(course.id)}
    )
    assert resp.status_code == 401


async def test_create_class_rejects_student(client, student, course):
    resp = await client.post(
        "/api/v1/classes/",
        json={"name": "x", "course_id": str(course.id)},
        headers=auth_headers(student),
    )
    assert resp.status_code == 403


async def test_create_class_in_someone_elses_course_denied(client, teacher, other_course):
    resp = await client.post(
        "/api/v1/classes/",
        json={"name": "x", "course_id": str(other_course.id)},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 403


async def test_create_class_nonexistent_course_404(client, teacher):
    resp = await client.post(
        "/api/v1/classes/",
        json={"name": "x", "course_id": str(uuid.uuid4())},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 404


async def test_create_class_rejects_name_over_255(client, teacher, course):
    resp = await client.post(
        "/api/v1/classes/",
        json={"name": "x" * 256, "course_id": str(course.id)},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# get_classes_by_course / get_my_classes
# ---------------------------------------------------------------------------


async def test_get_classes_by_course_visible_to_students(
    client, student, course, db_session
):
    await create_class(db_session, course, "a")
    resp = await client.get(
        f"/api/v1/classes/course/{course.id}", headers=auth_headers(student)
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_get_my_classes_only_returns_own(
    client, teacher, other_teacher, course, other_course, db_session
):
    await create_class(db_session, course, "mine")
    await create_class(db_session, other_course, "theirs")

    resp = await client.get("/api/v1/classes/", headers=auth_headers(teacher))
    assert resp.status_code == 200
    names = {c["name"] for c in resp.json()}
    assert names == {"Class mine"}


async def test_get_my_classes_rejects_student(client, student):
    resp = await client.get("/api/v1/classes/", headers=auth_headers(student))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# get_class_detail
# ---------------------------------------------------------------------------


async def test_get_class_detail_not_found(client, teacher):
    resp = await client.get(f"/api/v1/classes/{uuid.uuid4()}", headers=auth_headers(teacher))
    assert resp.status_code == 404


async def test_get_class_detail_other_teacher_denied(
    client, teacher, other_course, db_session
):
    other_class = await create_class(db_session, other_course)
    resp = await client.get(
        f"/api/v1/classes/{other_class.id}", headers=auth_headers(teacher)
    )
    assert resp.status_code == 403


async def test_get_class_detail_student_can_read(client, student, course, db_session):
    klass = await create_class(db_session, course)
    resp = await client.get(f"/api/v1/classes/{klass.id}", headers=auth_headers(student))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# update_class / delete_class — ownership (IDOR)
# ---------------------------------------------------------------------------


async def test_update_class_non_owner_denied(client, teacher, other_course, db_session):
    other_class = await create_class(db_session, other_course)
    resp = await client.put(
        f"/api/v1/classes/{other_class.id}",
        json={"name": "Hijacked"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 403


async def test_update_class_owner_succeeds(client, teacher, course, db_session):
    klass = await create_class(db_session, course)
    resp = await client.put(
        f"/api/v1/classes/{klass.id}",
        json={"name": "Renamed"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"


async def test_delete_class_non_owner_denied(client, teacher, other_course, db_session):
    other_class = await create_class(db_session, other_course)
    resp = await client.delete(
        f"/api/v1/classes/{other_class.id}", headers=auth_headers(teacher)
    )
    assert resp.status_code == 403


async def test_delete_class_owner_succeeds(client, teacher, course, db_session):
    klass = await create_class(db_session, course)
    resp = await client.delete(f"/api/v1/classes/{klass.id}", headers=auth_headers(teacher))
    assert resp.status_code == 200
