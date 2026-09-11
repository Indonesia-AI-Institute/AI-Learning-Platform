import { describe, it, expect, beforeEach, mock } from "bun:test";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { withQueryClient } from "./testUtils";

const push = mock<(href: string) => void>();
const refresh = mock<() => void>();

mock.module("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
}));

const { RegisterForm } = await import("@/components/auth/RegisterForm");

const REGISTER_URL = "http://localhost:8000/api/v1/auth/register";

function renderRegisterForm() {
  const Wrapper = withQueryClient();
  return render(
    <Wrapper>
      <RegisterForm />
    </Wrapper>
  );
}

describe("RegisterForm", () => {
  beforeEach(() => {
    push.mockClear();
    refresh.mockClear();
  });

  it("renders all fields including the role selector, defaulting to student", () => {
    renderRegisterForm();
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("combobox")).toHaveTextContent("Student");
  });

  it("submits valid data and redirects to /dashboard on success", async () => {
    const user = userEvent.setup();
    renderRegisterForm();

    await user.type(screen.getByLabelText(/full name/i), "New Student");
    await user.type(screen.getByLabelText(/email/i), "new.student@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard"));
    expect(refresh).toHaveBeenCalled();
  });

  it("lets a visitor register as a teacher via the role dropdown", async () => {
    let capturedBody: { role?: string } | null = null;
    server.use(
      http.post(REGISTER_URL, async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(
          { access_token: "x", token_type: "bearer" },
          { status: 201 }
        );
      })
    );

    const user = userEvent.setup();
    renderRegisterForm();

    await user.type(screen.getByLabelText(/full name/i), "New Teacher");
    await user.type(screen.getByLabelText(/email/i), "new.teacher@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");

    await user.click(screen.getByRole("combobox"));
    // Radix renders the item text twice (a hidden measurement copy plus
    // the real, clickable option) — role="option" disambiguates to the
    // real one.
    await user.click(await screen.findByRole("option", { name: "Teacher" }));

    await user.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard"));
    // Documents existing, deliberately-unrestricted behavior: any visitor
    // can self-register as a teacher — see CLAUDE.md's known gaps.
    expect(capturedBody?.role).toBe("teacher");
  });

  it("blocks submission when the full name is too short", async () => {
    const user = userEvent.setup();
    renderRegisterForm();

    await user.type(screen.getByLabelText(/full name/i), "A");
    await user.type(screen.getByLabelText(/email/i), "valid@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    await new Promise((r) => setTimeout(r, 300));
    expect(push).not.toHaveBeenCalled();
  });

  it("blocks submission when the password is too short", async () => {
    const user = userEvent.setup();
    renderRegisterForm();

    await user.type(screen.getByLabelText(/full name/i), "Valid Name");
    await user.type(screen.getByLabelText(/email/i), "valid@example.com");
    await user.type(screen.getByLabelText(/password/i), "short");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    await new Promise((r) => setTimeout(r, 300));
    expect(push).not.toHaveBeenCalled();
  });

  it("blocks submission for an invalid email", async () => {
    const user = userEvent.setup();
    renderRegisterForm();

    await user.type(screen.getByLabelText(/full name/i), "Valid Name");
    await user.type(screen.getByLabelText(/email/i), "not-an-email");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    await new Promise((r) => setTimeout(r, 300));
    expect(push).not.toHaveBeenCalled();
  });

  it("shows the backend's error detail when registration fails (e.g. duplicate email)", async () => {
    server.use(
      http.post(REGISTER_URL, () =>
        HttpResponse.json({ detail: "Email already registered" }, { status: 400 })
      )
    );

    const user = userEvent.setup();
    renderRegisterForm();

    await user.type(screen.getByLabelText(/full name/i), "Existing User");
    await user.type(screen.getByLabelText(/email/i), "existing@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByText("Email already registered")).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });

  it("disables the submit button while the request is in flight", async () => {
    server.use(
      http.post(REGISTER_URL, async () => {
        await new Promise((r) => setTimeout(r, 100));
        return HttpResponse.json({ access_token: "x", token_type: "bearer" }, { status: 201 });
      })
    );

    const user = userEvent.setup();
    renderRegisterForm();

    await user.type(screen.getByLabelText(/full name/i), "Valid Name");
    await user.type(screen.getByLabelText(/email/i), "valid@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(screen.getByRole("button", { name: /creating account/i })).toBeDisabled();

    await waitFor(() => expect(push).toHaveBeenCalled());
  });
});
