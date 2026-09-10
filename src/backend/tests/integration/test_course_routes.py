"""
Integration coverage for api/v1/course_routes.py — previously untested.
Full response-code matrix per route plus the ownership/IDOR check for
every endpoint that scopes data to "the current teacher's own courses".
"""

import uuid

import pytest

from factories import (
    auth_headers,
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


# ---------------------------------------------------------------------------
# create_course
# ---------------------------------------------------------------------------


async def test_create_course_as_teacher(client, teacher):
    resp = await client.post(
        "/api/v1/courses/create/",
        json={"title": "Intro to AI"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Intro to AI"
    assert body["teacher_id"] == str(teacher.id)


async def test_create_course_requires_auth(client):
    resp = await client.post("/api/v1/courses/create/", json={"title": "x"})
    assert resp.status_code == 401


async def test_create_course_rejects_student(client, student):
    resp = await client.post(
        "/api/v1/courses/create/",
        json={"title": "x"},
        headers=auth_headers(student),
    )
    assert resp.status_code == 403


async def test_create_course_rejects_missing_title(client, teacher):
    resp = await client.post(
        "/api/v1/courses/create/", json={}, headers=auth_headers(teacher)
    )
    assert resp.status_code == 422


async def test_create_course_rejects_title_over_255(client, teacher):
    resp = await client.post(
        "/api/v1/courses/create/",
        json={"title": "x" * 256},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# get_all_courses / get_my_courses
# ---------------------------------------------------------------------------


async def test_get_all_courses_requires_auth(client):
    resp = await client.get("/api/v1/courses/all")
    assert resp.status_code == 401


async def test_get_all_courses_lists_every_active_course_regardless_of_owner(
    client, teacher, other_teacher, student, db_session
):
    await create_course(db_session, teacher, "mine")
    await create_course(db_session, other_teacher, "theirs")

    resp = await client.get("/api/v1/courses/all", headers=auth_headers(student))
    assert resp.status_code == 200
    titles = {c["title"] for c in resp.json()}
    assert {"Course mine", "Course theirs"}.issubset(titles)


async def test_get_my_courses_only_returns_own_courses(
    client, teacher, other_teacher, db_session
):
    await create_course(db_session, teacher, "mine")
    await create_course(db_session, other_teacher, "theirs")

    resp = await client.get("/api/v1/courses/", headers=auth_headers(teacher))
    assert resp.status_code == 200
    titles = {c["title"] for c in resp.json()}
    assert titles == {"Course mine"}


# ---------------------------------------------------------------------------
# get_course_detail
# ---------------------------------------------------------------------------


async def test_get_course_detail_owner(client, teacher, db_session):
    course = await create_course(db_session, teacher)
    resp = await client.get(f"/api/v1/courses/{course.id}", headers=auth_headers(teacher))
    assert resp.status_code == 200
    assert resp.json()["id"] == str(course.id)


async def test_get_course_detail_not_found(client, teacher):
    resp = await client.get(f"/api/v1/courses/{uuid.uuid4()}", headers=auth_headers(teacher))
    assert resp.status_code == 404


async def test_get_course_detail_other_teacher_denied(
    client, teacher, other_teacher, db_session
):
    course = await create_course(db_session, other_teacher)
    resp = await client.get(f"/api/v1/courses/{course.id}", headers=auth_headers(teacher))
    assert resp.status_code == 403


async def test_get_course_detail_student_can_browse_any_course(
    client, student, other_teacher, db_session
):
    """Deliberate: students can view any course to browse before enrolling."""
    course = await create_course(db_session, other_teacher)
    resp = await client.get(f"/api/v1/courses/{course.id}", headers=auth_headers(student))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# update_course / delete_course — ownership (IDOR)
# ---------------------------------------------------------------------------


async def test_update_course_owner_succeeds(client, teacher, db_session):
    course = await create_course(db_session, teacher)
    resp = await client.put(
        f"/api/v1/courses/{course.id}",
        json={"title": "Updated"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


async def test_update_course_non_owner_denied(client, teacher, other_teacher, db_session):
    course = await create_course(db_session, other_teacher)
    resp = await client.put(
        f"/api/v1/courses/{course.id}",
        json={"title": "Hijacked"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 403


async def test_update_course_requires_teacher_role(client, student, teacher, db_session):
    course = await create_course(db_session, teacher)
    resp = await client.put(
        f"/api/v1/courses/{course.id}",
        json={"title": "x"},
        headers=auth_headers(student),
    )
    assert resp.status_code == 403


async def test_update_course_nonexistent_returns_404(client, teacher):
    resp = await client.put(
        f"/api/v1/courses/{uuid.uuid4()}",
        json={"title": "x"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 404


async def test_delete_course_non_owner_denied(client, teacher, other_teacher, db_session):
    course = await create_course(db_session, other_teacher)
    resp = await client.delete(f"/api/v1/courses/{course.id}", headers=auth_headers(teacher))
    assert resp.status_code == 403


async def test_delete_course_owner_succeeds(client, teacher, db_session):
    course = await create_course(db_session, teacher)
    resp = await client.delete(f"/api/v1/courses/{course.id}", headers=auth_headers(teacher))
    assert resp.status_code == 200

    # Confirm it's actually gone, not just a 200 with no effect.
    follow_up = await client.get(f"/api/v1/courses/{course.id}", headers=auth_headers(teacher))
    assert follow_up.status_code == 404
