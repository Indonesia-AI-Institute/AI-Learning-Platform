"""
Integration coverage for api/v1/task_routes.py — previously untested,
and previously buggy: every route in this file called its TaskService
method with no try/except at all, while TaskService raises ValueError
("not found") and PermissionError ("not allowed") expecting a route to
map them to 404/403 — the same pattern every sibling route file follows.
With nothing catching them, FastAPI's default unhandled-exception
handling turned every "not found" and "access denied" case into a raw
500. The 404/403 assertions below are the regression tests for that fix.
"""

import uuid

import pytest

from factories import (
    auth_headers,
    create_class,
    create_course,
    create_enrollment,
    create_student,
    create_task,
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
async def klass(db_session, course):
    return await create_class(db_session, course)


@pytest.fixture
async def other_course(db_session, other_teacher):
    return await create_course(db_session, other_teacher, "other")


# ---------------------------------------------------------------------------
# create_task — this alone used to 500 on every error path
# ---------------------------------------------------------------------------


async def test_create_task_as_course_owner(client, teacher, course):
    resp = await client.post(
        f"/api/v1/tasks/course/{course.id}",
        json={"title": "Homework 1"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Homework 1"


async def test_create_task_requires_auth(client, course):
    resp = await client.post(
        f"/api/v1/tasks/course/{course.id}", json={"title": "x"}
    )
    assert resp.status_code == 401


async def test_create_task_rejects_student(client, student, course):
    resp = await client.post(
        f"/api/v1/tasks/course/{course.id}",
        json={"title": "x"},
        headers=auth_headers(student),
    )
    assert resp.status_code == 403


async def test_create_task_nonexistent_course_is_404_not_500(client, teacher):
    resp = await client.post(
        f"/api/v1/tasks/course/{uuid.uuid4()}",
        json={"title": "x"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 404


async def test_create_task_in_someone_elses_course_is_403_not_500(
    client, teacher, other_course
):
    resp = await client.post(
        f"/api/v1/tasks/course/{other_course.id}",
        json={"title": "x"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 403


async def test_create_task_rejects_title_over_255(client, teacher, course):
    resp = await client.post(
        f"/api/v1/tasks/course/{course.id}",
        json={"title": "x" * 256},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# get_tasks_by_course / get_tasks_by_class
# ---------------------------------------------------------------------------


async def test_get_tasks_by_course_nonexistent_is_404_not_500(client, teacher):
    resp = await client.get(
        f"/api/v1/tasks/course/{uuid.uuid4()}", headers=auth_headers(teacher)
    )
    assert resp.status_code == 404


async def test_get_tasks_by_course_other_teacher_is_403_not_500(
    client, teacher, other_course
):
    resp = await client.get(
        f"/api/v1/tasks/course/{other_course.id}", headers=auth_headers(teacher)
    )
    assert resp.status_code == 403


async def test_get_tasks_by_course_unenrolled_student_is_403_not_500(
    client, student, course
):
    resp = await client.get(
        f"/api/v1/tasks/course/{course.id}", headers=auth_headers(student)
    )
    assert resp.status_code == 403


async def test_get_tasks_by_course_enrolled_student_succeeds(
    client, student, course, klass, db_session
):
    await create_enrollment(db_session, student, klass)
    await create_task(db_session, course, klass)

    resp = await client.get(
        f"/api/v1/tasks/course/{course.id}", headers=auth_headers(student)
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_get_tasks_by_class_nonexistent_is_404_not_500(client, teacher):
    resp = await client.get(
        f"/api/v1/tasks/class/{uuid.uuid4()}", headers=auth_headers(teacher)
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# get_task_detail
# ---------------------------------------------------------------------------


async def test_get_task_detail_nonexistent_is_404_not_500(client, teacher):
    resp = await client.get(f"/api/v1/tasks/{uuid.uuid4()}", headers=auth_headers(teacher))
    assert resp.status_code == 404


async def test_get_task_detail_other_teacher_is_403_not_500(
    client, teacher, other_course, db_session
):
    other_task = await create_task(db_session, other_course)
    resp = await client.get(f"/api/v1/tasks/{other_task.id}", headers=auth_headers(teacher))
    assert resp.status_code == 403


async def test_get_task_detail_unenrolled_student_is_403_not_500(
    client, student, course, db_session
):
    task = await create_task(db_session, course)
    resp = await client.get(f"/api/v1/tasks/{task.id}", headers=auth_headers(student))
    assert resp.status_code == 403


async def test_get_task_detail_owner_succeeds(client, teacher, course, db_session):
    task = await create_task(db_session, course)
    resp = await client.get(f"/api/v1/tasks/{task.id}", headers=auth_headers(teacher))
    assert resp.status_code == 200
    assert resp.json()["id"] == str(task.id)


# ---------------------------------------------------------------------------
# update_task / delete_task — ownership (IDOR), also previously 500s
# ---------------------------------------------------------------------------


async def test_update_task_non_owner_is_403_not_500(client, teacher, other_course, db_session):
    other_task = await create_task(db_session, other_course)
    resp = await client.put(
        f"/api/v1/tasks/{other_task.id}",
        json={"title": "Hijacked"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 403


async def test_update_task_nonexistent_is_404_not_500(client, teacher):
    resp = await client.put(
        f"/api/v1/tasks/{uuid.uuid4()}",
        json={"title": "x"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 404


async def test_update_task_owner_succeeds(client, teacher, course, db_session):
    task = await create_task(db_session, course)
    resp = await client.put(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Updated"},
        headers=auth_headers(teacher),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


async def test_delete_task_non_owner_is_403_not_500(client, teacher, other_course, db_session):
    other_task = await create_task(db_session, other_course)
    resp = await client.delete(f"/api/v1/tasks/{other_task.id}", headers=auth_headers(teacher))
    assert resp.status_code == 403


async def test_delete_task_nonexistent_is_404_not_500(client, teacher):
    resp = await client.delete(f"/api/v1/tasks/{uuid.uuid4()}", headers=auth_headers(teacher))
    assert resp.status_code == 404


async def test_delete_task_owner_succeeds(client, teacher, course, db_session):
    task = await create_task(db_session, course)
    resp = await client.delete(f"/api/v1/tasks/{task.id}", headers=auth_headers(teacher))
    assert resp.status_code == 204
