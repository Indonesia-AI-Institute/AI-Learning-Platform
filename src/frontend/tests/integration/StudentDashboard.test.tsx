import { describe, it, expect } from "bun:test";
import { render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { StudentDashboard } from "@/components/dashboard/StudentDashboard";
import { withQueryClient } from "./testUtils";

const ANALYTICS_URL = "http://localhost:8000/api/v1/analytics/me";

function renderDashboard() {
  const Wrapper = withQueryClient();
  return render(
    <Wrapper>
      <StudentDashboard fullName="Ada Lovelace" />
    </Wrapper>
  );
}

describe("StudentDashboard", () => {
  it("greets the student by name", () => {
    renderDashboard();
    expect(screen.getByText(/welcome back, ada lovelace/i)).toBeInTheDocument();
  });

  it("shows a placeholder ('—') for every stat while analytics are loading", () => {
    server.use(http.get(ANALYTICS_URL, async () => {
      await new Promise((r) => setTimeout(r, 100));
      return HttpResponse.json({});
    }));

    renderDashboard();
    expect(screen.getAllByText("—")).toHaveLength(4);
  });

  it("renders every stat once analytics load", async () => {
    server.use(
      http.get(ANALYTICS_URL, () =>
        HttpResponse.json({
          total_sessions: 12,
          total_prompts: 48,
          total_tokens: 15234,
          total_duration_seconds: 3725,
          avg_prompt_length: 87.4,
        })
      )
    );

    renderDashboard();

    expect(await screen.findByText("12")).toBeInTheDocument();
    expect(screen.getByText("48")).toBeInTheDocument();
    expect(screen.getByText("15,234")).toBeInTheDocument();
    expect(screen.getByText("1h 2m")).toBeInTheDocument();
  });

  it("formats durations under a minute and under an hour correctly", async () => {
    server.use(
      http.get(ANALYTICS_URL, () =>
        HttpResponse.json({
          total_sessions: 1,
          total_prompts: 1,
          total_tokens: 10,
          total_duration_seconds: 45,
          avg_prompt_length: 10,
        })
      )
    );

    renderDashboard();
    expect(await screen.findByText("45s")).toBeInTheDocument();
  });

  it("shows the average-prompt-length card only once there are prompts", async () => {
    server.use(
      http.get(ANALYTICS_URL, () =>
        HttpResponse.json({
          total_sessions: 0,
          total_prompts: 0,
          total_tokens: 0,
          total_duration_seconds: 0,
          avg_prompt_length: 0,
        })
      )
    );

    renderDashboard();

    await waitFor(() => expect(screen.getAllByText("0")).not.toHaveLength(0));
    expect(screen.queryByText(/average prompt length/i)).not.toBeInTheDocument();
  });

  it("shows the average-prompt-length card when there are prompts", async () => {
    server.use(
      http.get(ANALYTICS_URL, () =>
        HttpResponse.json({
          total_sessions: 3,
          total_prompts: 9,
          total_tokens: 500,
          total_duration_seconds: 120,
          avg_prompt_length: 63.2,
        })
      )
    );

    renderDashboard();

    expect(await screen.findByText(/average prompt length/i)).toBeInTheDocument();
    expect(screen.getByText("63 characters")).toBeInTheDocument();
  });
});
