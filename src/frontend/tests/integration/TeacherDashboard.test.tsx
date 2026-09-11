import { describe, it, expect, beforeEach, mock } from "bun:test";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { withQueryClient } from "./testUtils";

const push = mock<(href: string) => void>();

mock.module("next/navigation", () => ({
  useRouter: () => ({ push, refresh: mock() }),
}));

const { TeacherDashboard } = await import("@/components/dashboard/TeacherDashboard");

const CLASSES_URL = "http://localhost:8000/api/v1/classes/";

function renderDashboard() {
  const Wrapper = withQueryClient();
  return render(
    <Wrapper>
      <TeacherDashboard fullName="Grace Hopper" />
    </Wrapper>
  );
}

function makeClass(overrides: Partial<{ id: string; name: string; is_active: boolean; description: string | null }>) {
  return {
    id: "class-1",
    name: "Algebra I",
    description: null,
    is_active: true,
    course_id: "course-1",
    teacher_id: "teacher-1",
    created_at: new Date().toISOString(),
    ...overrides,
  };
}

describe("TeacherDashboard", () => {
  beforeEach(() => {
    push.mockClear();
  });

  it("greets the teacher by name", () => {
    renderDashboard();
    expect(screen.getByText(/welcome back, grace hopper/i)).toBeInTheDocument();
  });

  it("counts active vs inactive classes correctly", async () => {
    server.use(
      http.get(CLASSES_URL, () =>
        HttpResponse.json([
          makeClass({ id: "1", is_active: true }),
          makeClass({ id: "2", is_active: true }),
          makeClass({ id: "3", is_active: false }),
        ])
      )
    );

    renderDashboard();

    expect(await screen.findByText("3")).toBeInTheDocument(); // total
    expect(screen.getByText("2")).toBeInTheDocument(); // active
    expect(screen.getByText("1")).toBeInTheDocument(); // inactive
  });

  it("shows zero counts and no class list when there are no classes", async () => {
    server.use(http.get(CLASSES_URL, () => HttpResponse.json([])));

    renderDashboard();

    await screen.findAllByText("0");
    // Exact text, not a substring regex — the welcome subtitle also
    // contains the words "your classes" ("Manage your classes and
    // monitor..."), which a loose /your classes/i match picks up too.
    expect(screen.queryByText("Your classes")).toBeNull();
  });

  it("lists up to 5 classes with an active/inactive badge", async () => {
    server.use(
      http.get(CLASSES_URL, () =>
        HttpResponse.json([
          makeClass({ id: "1", name: "Algebra I", is_active: true }),
          makeClass({ id: "2", name: "Algebra II", is_active: false }),
        ])
      )
    );

    renderDashboard();

    expect(await screen.findByText("Algebra I")).toBeInTheDocument();
    expect(screen.getByText("Algebra II")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByText("Inactive")).toBeInTheDocument();
  });

  it("shows a 'view all' button only when there are more than 5 classes", async () => {
    server.use(
      http.get(CLASSES_URL, () =>
        HttpResponse.json(
          Array.from({ length: 7 }, (_, i) => makeClass({ id: String(i), name: `Class ${i}` }))
        )
      )
    );

    renderDashboard();

    expect(await screen.findByText(/view all 7 classes/i)).toBeInTheDocument();
    // Only the first 5 are rendered in the preview list.
    expect(screen.queryByText("Class 5")).not.toBeInTheDocument();
  });

  it("navigates to the class detail page when a class row is clicked", async () => {
    server.use(
      http.get(CLASSES_URL, () => HttpResponse.json([makeClass({ id: "class-42", name: "Geometry" })]))
    );

    const user = userEvent.setup();
    renderDashboard();

    await user.click(await screen.findByText("Geometry"));

    expect(push).toHaveBeenCalledWith("/classes/class-42");
  });

  it("navigates via each quick-action button", async () => {
    server.use(http.get(CLASSES_URL, () => HttpResponse.json([])));

    const user = userEvent.setup();
    renderDashboard();

    await user.click(screen.getByRole("button", { name: /create course/i }));
    expect(push).toHaveBeenCalledWith("/courses/create");

    await user.click(screen.getByRole("button", { name: /create class/i }));
    expect(push).toHaveBeenCalledWith("/classes/create");

    await user.click(screen.getByRole("button", { name: /create task/i }));
    expect(push).toHaveBeenCalledWith("/tasks/create");

    await user.click(screen.getByRole("button", { name: /view analytics/i }));
    expect(push).toHaveBeenCalledWith("/analytics");
  });
});
