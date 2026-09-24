"""
Regression tests for finding #4 (HIGH): analytics endpoints checked role
(teacher) but not ownership, so any teacher could read any other teacher's
student analytics by guessing/enumerating a class/course/task/student/session
UUID. Builds two fully independent teacher/course/class/task/student/session
graphs and asserts teacher A gets nothing back for teacher B's data.
"""

import pytest
from backend.auth.security import create_access_token, hash_password
from backend.models.chat_history import ChatHistory, MessageRole
from backend.models.chat_session import ChatSession
from backend.models.class_model import Class
from backend.models.course import Course
from backend.models.enrollment import Enrollment
from backend.models.prompt_classification import PromptClassification
from backend.models.session_analytics import SessionAnalytics
from backend.models.task import Task
from backend.models.user import User, UserRole


def _token(user) -> str:
    return create_access_token(user_id=str(user.id), role=user.role.value)


async def _build_world(db, suffix: str):
    """One teacher with one course/class/task, one enrolled student, one
    ended chat session with a real message + analytics + classification."""
    teacher = User(
        full_name=f"Teacher {suffix}",
        email=f"teacher-{suffix}@example.com",
        hashed_password=hash_password("x"),
        role=UserRole.TEACHER,
    )
    student = User(
        full_name=f"Student {suffix}",
        email=f"student-{suffix}@example.com",
        hashed_password=hash_password("x"),
        role=UserRole.STUDENT,
    )
    db.add_all([teacher, student])
    await db.commit()
    await db.refresh(teacher)
    await db.refresh(student)

    course = Course(teacher_id=teacher.id, title=f"Course {suffix}")
    db.add(course)
    await db.commit()
    await db.refresh(course)

    klass = Class(course_id=course.id, name=f"Class {suffix}")
    db.add(klass)
    await db.commit()
    await db.refresh(klass)

    task = Task(course_id=course.id, class_id=klass.id, title=f"Task {suffix}")
    db.add(task)
    await db.commit()
    await db.refresh(task)

    db.add(Enrollment(student_id=student.id, class_id=klass.id))
    await db.commit()

    session = ChatSession(student_id=student.id, task_id=task.id, is_active=False)
    db.add(session)
    await db.commit()
    await db.refresh(session)

    message = ChatHistory(
        session_id=session.id,
        user_id=student.id,
        role=MessageRole.USER,
        content="hello",
        message_index=0,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    db.add(
        SessionAnalytics(
            chat_session_id=session.id,
            user_id=student.id,
            task_id=task.id,
            total_prompts=1,
            avg_prompt_length=5.0,
            session_duration_seconds=10,
            prompt_tokens=5,
            completion_tokens=5,
            total_tokens=10,
        )
    )
    db.add(
        PromptClassification(
            chat_history_id=message.id,
            session_id=session.id,
            student_id=student.id,
            task_id=task.id,
            is_direct_answer=True,
        )
    )
    await db.commit()

    return {
        "teacher": teacher,
        "student": student,
        "course": course,
        "class": klass,
        "task": task,
        "session": session,
    }


@pytest.fixture
async def worlds(db_session):
    a = await _build_world(db_session, "a")
    b = await _build_world(db_session, "b")
    return a, b


async def test_teacher_sees_own_class_analytics(client, worlds):
    a, _b = worlds
    resp = await client.get(
        f"/api/v1/analytics/class/{a['class'].id}",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()["students"]) == 1
    assert resp.json()["students"][0]["student_id"] == str(a["student"].id)


async def test_teacher_cannot_see_other_teachers_class_analytics(client, worlds):
    a, b = worlds
    resp = await client.get(
        f"/api/v1/analytics/class/{b['class'].id}",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    assert resp.json()["students"] == []


async def test_teacher_sees_own_class_classifications_with_student_name(client, worlds):
    a, _b = worlds
    resp = await client.get(
        f"/api/v1/analytics/class/{a['class'].id}/classifications",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    students = resp.json()["students"]
    assert len(students) == 1
    assert students[0]["student_id"] == str(a["student"].id)
    assert students[0]["student_name"] == "Student a"


async def test_teacher_cannot_see_other_teachers_class_classifications(client, worlds):
    a, b = worlds
    resp = await client.get(
        f"/api/v1/analytics/class/{b['class'].id}/classifications",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    assert resp.json()["students"] == []


async def test_teacher_cannot_see_other_teachers_course_classifications(client, worlds):
    a, b = worlds
    resp = await client.get(
        f"/api/v1/analytics/course/{b['course'].id}/classifications",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    assert resp.json()["students"] == []


async def test_teacher_cannot_see_other_teachers_task_analytics(client, worlds):
    a, b = worlds
    resp = await client.get(
        f"/api/v1/analytics/task/{b['task'].id}",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    assert resp.json()["students"] == []


async def test_teacher_cannot_see_other_teachers_task_classifications(client, worlds):
    a, b = worlds
    resp = await client.get(
        f"/api/v1/analytics/task/{b['task'].id}/classifications",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    assert resp.json()["students"] == []


async def test_teacher_cannot_see_other_teachers_student_classifications(client, worlds):
    a, b = worlds
    resp = await client.get(
        f"/api/v1/analytics/student/{b['student'].id}/classifications",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []


async def test_teacher_cannot_see_other_teachers_session_analytics(client, worlds):
    """This is the one that went through session_service.get_session_detail,
    whose teacher branch was a literal `pass` before the fix."""
    a, b = worlds
    resp = await client.get(
        f"/api/v1/analytics/sessions/{b['session'].id}",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 403


async def test_teacher_sees_own_session_analytics(client, worlds):
    a, _b = worlds
    resp = await client.get(
        f"/api/v1/analytics/sessions/{a['session'].id}",
        headers={"Authorization": f"Bearer {_token(a['teacher'])}"},
    )
    assert resp.status_code == 200
    assert resp.json()["student_id"] == str(a["student"].id)


async def test_student_cannot_access_teacher_analytics_routes(client, worlds):
    a, _b = worlds
    resp = await client.get(
        f"/api/v1/analytics/class/{a['class'].id}",
        headers={"Authorization": f"Bearer {_token(a['student'])}"},
    )
    assert resp.status_code == 403
