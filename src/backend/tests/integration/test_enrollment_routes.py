"""
Integration coverage for api/v1/enrollment_routes.py — previously untested.
"""

import uuid

import pytest

from factories import (
    auth_headers,
    create_class,
    create_course,
    create_enrollment,
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
async def other_student(db_session):
    return await create_student(db_session, "b")


@pytest.fixture
async def klass(db_session, teacher):
    course = await create_course(db_session, teacher)
    return await create_class(db_session, course)


# ---------------------------------------------------------------------------
# enroll_in_class
# ---------------------------------------------------------------------------


async def test_enroll_as_student(client, student, klass):
    resp = await client.post(
        "/api/v1/enrollments/",
        json={"class_id": str(klass.id)},
        headers=auth_headers(student),
    )
    assert resp.status_code == 201
    assert resp.json()["student_id"] == str(student.id)
    assert resp.json()["class_id"] == str(klass.id)


async def test_enroll_requires_auth(client, klass):
    resp = await client.post("/api/v1/enrollments/", json={"class_id": str(klass.id)})
    assert resp.status_code == 401


async def test_enroll_rejects_teacher(client, teacher, klass):
    resp = await client.post(
        "/api/v1/enrollments/",
        json={"class_id": str(klass.id)},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 403


async def test_enroll_nonexistent_class_404(client, student):
    resp = await client.post(
        "/api/v1/enrollments/",
        json={"class_id": str(uuid.uuid4())},
        headers=auth_headers(student),
    )
    assert resp.status_code == 404


async def test_enroll_duplicate_is_409(client, student, klass, db_session):
    await create_enrollment(db_session, student, klass)
    resp = await client.post(
        "/api/v1/enrollments/",
        json={"class_id": str(klass.id)},
        headers=auth_headers(student),
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# unenroll_from_class — ownership (IDOR: can't unenroll someone else)
# ---------------------------------------------------------------------------


async def test_unenroll_own_enrollment(client, student, klass, db_session):
    enrollment = await create_enrollment(db_session, student, klass)
    resp = await client.delete(
        f"/api/v1/enrollments/{enrollment.id}", headers=auth_headers(student)
    )
    assert resp.status_code == 204


async def test_unenroll_someone_elses_enrollment_denied(
    client, student, other_student, klass, db_session
):
    enrollment = await create_enrollment(db_session, other_student, klass)
    resp = await client.delete(
        f"/api/v1/enrollments/{enrollment.id}", headers=auth_headers(student)
    )
    assert resp.status_code == 403


async def test_unenroll_nonexistent_404(client, student):
    resp = await client.delete(
        f"/api/v1/enrollments/{uuid.uuid4()}", headers=auth_headers(student)
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# get_my_enrollments
# ---------------------------------------------------------------------------


async def test_get_my_enrollments_only_own(
    client, student, other_student, klass, db_session
):
    await create_enrollment(db_session, student, klass)
    await create_enrollment(db_session, other_student, klass)

    resp = await client.get("/api/v1/enrollments/me", headers=auth_headers(student))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["student_id"] == str(student.id)


async def test_get_my_enrollments_rejects_teacher(client, teacher):
    resp = await client.get("/api/v1/enrollments/me", headers=auth_headers(teacher))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# get_class_enrollments — ownership (IDOR)
# ---------------------------------------------------------------------------


async def test_get_class_enrollments_as_owning_teacher(
    client, teacher, student, klass, db_session
):
    await create_enrollment(db_session, student, klass)
    resp = await client.get(
        f"/api/v1/enrollments/class/{klass.id}", headers=auth_headers(teacher)
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_get_class_enrollments_non_owning_teacher_denied(
    client, other_teacher, klass
):
    resp = await client.get(
        f"/api/v1/enrollments/class/{klass.id}", headers=auth_headers(other_teacher)
    )
    assert resp.status_code == 403


async def test_get_class_enrollments_rejects_student(client, student, klass):
    resp = await client.get(
        f"/api/v1/enrollments/class/{klass.id}", headers=auth_headers(student)
    )
    assert resp.status_code == 403
