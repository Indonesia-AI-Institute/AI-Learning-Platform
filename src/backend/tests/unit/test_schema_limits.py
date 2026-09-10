import pytest
from pydantic import ValidationError

from backend.schemas.auth.register_request import RegisterRequest
from backend.schemas.chat.chat_request import ChatMessage, ChatRequest
from backend.schemas.chat.chat_session_create_request import ChatSessionCreateRequest
from backend.schemas.classes.class_create import ClassCreate
from backend.schemas.classes.class_update import ClassUpdate
from backend.schemas.course.course_create import CourseCreate
from backend.schemas.course.course_update import CourseUpdate
from backend.schemas.task.task_create import TaskCreate
from backend.schemas.task.task_update import TaskUpdate


def test_chat_message_content_within_limit_ok():
    ChatMessage(role="user", content="x" * 8000)


def test_chat_message_content_over_limit_rejected():
    with pytest.raises(ValidationError):
        ChatMessage(role="user", content="x" * 8001)


def test_chat_message_empty_content_rejected():
    with pytest.raises(ValidationError):
        ChatMessage(role="user", content="")


def test_chat_request_system_prompt_over_limit_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[ChatMessage(role="user", content="hi")],
            system_prompt="x" * 4001,
        )


def test_chat_request_too_many_messages_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[ChatMessage(role="user", content="hi") for _ in range(201)]
        )


@pytest.mark.parametrize(
    "schema_cls,field,kwargs",
    [
        (CourseCreate, "title", {"title": "x" * 256}),
        (CourseUpdate, "title", {"title": "x" * 256}),
        (ClassCreate, "name", {"name": "x" * 256, "course_id": "c1"}),
        (ClassUpdate, "name", {"name": "x" * 256}),
        (TaskCreate, "title", {"title": "x" * 256}),
        (TaskUpdate, "title", {"title": "x" * 256}),
    ],
)
def test_title_or_name_over_255_rejected(schema_cls, field, kwargs):
    with pytest.raises(ValidationError):
        schema_cls(**kwargs)


@pytest.mark.parametrize(
    "schema_cls,base_kwargs",
    [
        (CourseCreate, {"title": "Intro to AI"}),
        (CourseUpdate, {}),
        (ClassCreate, {"name": "Class A", "course_id": "c1"}),
        (ClassUpdate, {}),
        (TaskCreate, {"title": "Homework 1"}),
        (TaskUpdate, {}),
    ],
)
def test_description_over_5000_rejected(schema_cls, base_kwargs):
    with pytest.raises(ValidationError):
        schema_cls(**base_kwargs, description="x" * 5001)


def test_within_limits_still_accepted():
    CourseCreate(title="Intro to AI", description="x" * 5000)
    TaskCreate(title="Homework 1", description="x" * 5000)


# ---------------------------------------------------------------------------
# Exact-boundary checks (off-by-one is the most common way a max_length
# constraint is silently wrong)
# ---------------------------------------------------------------------------


def test_chat_message_content_exactly_8000_accepted_8001_rejected():
    ChatMessage(role="user", content="x" * 8000)
    with pytest.raises(ValidationError):
        ChatMessage(role="user", content="x" * 8001)


def test_title_exactly_255_accepted():
    CourseCreate(title="x" * 255)
    TaskCreate(title="x" * 255)
    ClassCreate(name="x" * 255, course_id="c1")


def test_description_exactly_5000_accepted_5001_rejected():
    CourseCreate(title="t", description="x" * 5000)
    with pytest.raises(ValidationError):
        CourseCreate(title="t", description="x" * 5001)


def test_chat_request_exactly_200_messages_accepted_201_rejected():
    ChatRequest(messages=[ChatMessage(role="user", content="hi") for _ in range(200)])
    with pytest.raises(ValidationError):
        ChatRequest(messages=[ChatMessage(role="user", content="hi") for _ in range(201)])


def test_chat_request_system_prompt_exactly_4000_accepted():
    ChatRequest(
        messages=[ChatMessage(role="user", content="hi")],
        system_prompt="x" * 4000,
    )


# ---------------------------------------------------------------------------
# Auth schemas (pre-existing constraints, not part of the security fixes,
# but every bit as load-bearing)
# ---------------------------------------------------------------------------


def test_register_request_valid():
    req = RegisterRequest(
        full_name="Jane Doe",
        email="jane@example.com",
        password="longenough123",
        role="student",
    )
    assert req.role.value == "student"


def test_register_request_rejects_short_password():
    with pytest.raises(ValidationError):
        RegisterRequest(
            full_name="Jane Doe",
            email="jane@example.com",
            password="short",
            role="student",
        )


def test_register_request_rejects_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(
            full_name="Jane Doe",
            email="not-an-email",
            password="longenough123",
            role="student",
        )


def test_register_request_rejects_empty_full_name():
    with pytest.raises(ValidationError):
        RegisterRequest(
            full_name="",
            email="jane@example.com",
            password="longenough123",
            role="student",
        )


def test_register_request_rejects_invalid_role():
    with pytest.raises(ValidationError):
        RegisterRequest(
            full_name="Jane Doe",
            email="jane@example.com",
            password="longenough123",
            role="admin",
        )


def test_chat_session_create_request_title_over_limit_rejected():
    with pytest.raises(ValidationError):
        ChatSessionCreateRequest(title="x" * 256)


def test_chat_session_create_request_title_optional():
    req = ChatSessionCreateRequest()
    assert req.title is None
