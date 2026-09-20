<div align="center">

# 🎓 AI Learning Platform

**Teach students how to think with AI — not just whether they used it.**

[![Test](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/actions/workflows/test.yml/badge.svg)](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/Indonesia-AI-Institute/AI-Learning-Platform?label=release)](https://github.com/Indonesia-AI-Institute/AI-Learning-Platform/releases)
[![License](https://img.shields.io/badge/license-Internal%20Use-lightgrey)](#-license)

[Quick Start](#-quick-start) · [Features](#-features) · [How It Works](#-how-it-works) · [Teacher Dashboard](#-the-teacher-dashboard) · [Under the Hood](#-under-the-hood) · [Documentation](#-documentation)

</div>

---

Students already use AI to do their homework. The question that matters for
a classroom isn't *whether* they do it — it's whether they're using it to
**learn** or to **skip the learning**. A student who pastes in a whole
assignment and copies back the answer is in a very different place than one
who works through it with the AI's help: asking for a hint, requesting an
explanation, or checking their own attempt.

Right now, teachers can't tell the difference. A chat log looks the same
either way unless someone reads every message.

**AI Learning Platform closes that gap.** Teachers assign tasks; students
work through them in a focused AI chat scoped to that task; and every single
message a student sends is classified in the background — asking for the
answer outright, asking for an explanation, asking for a step-by-step
walkthrough, asking for feedback on their own work, and more — then rolled
up into dashboards a teacher can actually act on. No extra step for the
student, no added latency, and no reading through hundreds of raw
transcripts to find the pattern. A teacher can see, at a glance, who's
outsourcing an assignment wholesale, who's asking good clarifying questions,
and use that to coach the whole class on *how* to prompt an AI well — before
it turns into a grading problem.

## ✨ Features

- 📊 **Prompt-behavior analytics, not just usage logs.** Every student
  message is classified into concrete signals — `direct_answer`,
  `explanation`, `step_by_step`, `example`, `rewrite`, `feedback`,
  `summary`, `translation`, `brainstorm` — so a teacher isn't just told "AI
  was used," they're shown *how*. Dashboards break this down per class, per
  task, and per student, with a chart of the category mix and a table to
  drill into any individual — down to their actual chat transcript.
- 🎯 **Built for coaching, not policing.** The goal is to help teachers
  teach students *how* to use AI as a learning tool — asking an
  understanding question before asking for an answer, requesting an
  explanation instead of a solution — not to catch or punish AI use
  outright.
- 🧑‍🏫 **Course, class & task management** — teachers build courses,
  organize students into classes, and assign tasks with their own
  instructions and context, so every chat session (and every classification)
  is tied to a specific assignment.
- 💬 **Task-scoped AI chat for students** — students work through an
  assigned task in a session tied to it, streamed token-by-token over SSE
  for a live, responsive feel.
- 🧭 **Pluggable tutoring styles.** The agent layer already includes a
  direct-answer tutor and a Socratic tutor that leads with a guiding
  question or hint and only explains once it's confirmed the student
  understands the concept — the same platform can support different
  teaching philosophies as it grows.
- 🔌 **Bring your own LLM** — OpenAI, OpenRouter, Google Gemini, Anthropic,
  or any OpenAI-compatible endpoint (including self-hosted models via
  Ollama), switchable through a single environment variable.
- 🔐 **Secure by default** — JWT auth via HttpOnly cookies, role-scoped
  access for teachers vs. students, ownership-checked at every layer.
- 🐳 **Deploy in minutes** — one Docker Compose command, whether you're
  pulling prebuilt images or building from source.

## 🏗 How It Works

```
 👩‍🏫 TEACHER                              🧑‍🎓 STUDENT
 ───────────                              ───────────
 1. Build a course, a class,
    and a task
                          ──────▶   2. Open the task, chat with
                                       the AI tutor about it
                                       (hint? explanation? a check
                                        on my own attempt?)
                                                │
                                                ▼
                                   3. Every message is tagged with
                                      a behavior signal — invisibly,
                                      with zero delay to the student
                                                │
 4. Open the dashboard,     ◀──────────────────┘
    spot the pattern
        │
        ▼
 5. Coach with specifics —
    "ask why, not just what" ──────▶  loops back into the next task
```

### For students

1. **Open an assigned task.** Every task lives inside a class, so a
   student only ever sees the work that's actually theirs.
2. **Chat with the AI tutor about it.** The conversation is scoped to
   that one task — ask for a hint, an explanation, a check on an attempt,
   whatever the moment calls for. Responses stream back live, like any
   modern chat.
3. **That's it.** Nothing else changes for the student — no extra step,
   no "you're being watched" banner, no added delay while a message is
   sent off to be analyzed behind the scenes.

### For teachers

1. **Create a course, add classes, assign tasks.** Each task carries its
   own instructions and context, so every conversation a student has
   about it is grounded in what was actually assigned.
2. **Let students work.** No extra setup — the analytics are already
   being collected in the background from the moment a student sends a
   first message.
3. **Open the dashboard when you're ready to check in.** See
   [The Teacher Dashboard](#-the-teacher-dashboard) below for exactly
   what's on it.
4. **Coach with specifics, not guesses.** Instead of a vague "use AI
   responsibly" reminder, a teacher can point to an actual pattern — "you
   asked for the answer six times this week without asking why it
   works" — and redirect it: ask an understanding question first, request
   an explanation before a solution, use the AI to check your own
   reasoning instead of replacing it.

## 📊 The Teacher Dashboard

This is where the coaching insight actually lives — everything a teacher
sees once students have started chatting.

- **Drill down by course → class → task.** Pick any level and see just
  that group's activity, so a pattern in one class doesn't get buried in
  the noise of every other class you teach.
- **A behavior-mix chart for the group.** A chart shows what percentage
  of that group's messages fell into each of the nine signals —
  `direct_answer`, `explanation`, `step_by_step`, `example`, `rewrite`,
  `feedback`, `summary`, `translation`, `brainstorm` — so you can tell at
  a glance whether a class is leaning on AI to think *for* them or *with*
  them.
- **A per-student table**, ranked by how many prompts each student sent,
  with their own category breakdown next to their name — the student
  asking for `direct_answer` on nearly every message stands out
  immediately next to one who's mostly asking for `explanation` or
  `feedback`.
- **Drill into one student.** Click through from the table to that
  student's own summary, then into their actual chat sessions — either
  the full back-and-forth conversation, or a "prompts only" view that
  shows just their messages, for a fast scan without re-reading every AI
  response in between.

## ⚙️ Under the Hood

This is the same flow above, from the system's point of view — useful if
you're evaluating the architecture rather than using the product.

```
Student sends a message (inside a task-scoped chat session)
        │
        ▼
FastAPI  ──stream──▶  LLM Provider  ──SSE──▶  Student sees tokens live
   │
   └──background──▶  Prompt Classifier  ──▶  9 signals saved  ──▶  Teacher dashboards
                      (direct_answer, explanation, step_by_step,
                       example, rewrite, feedback, summary,
                       translation, brainstorm)
```

The chat response and the classification happen **in parallel**: the
student's message streams to the LLM and back immediately, while a
separate background call tags that same message against all nine signals
(a message can match more than one) and saves the result. The classifier
is never on the critical path — a slow classification, or even a failed
one, has zero effect on how fast the student sees their reply.

**Stack:** FastAPI + SQLAlchemy + PostgreSQL on the backend, Next.js 16 +
React 19 on the frontend, shipped as two Docker images. See
[Documentation](#-documentation) below for the full technical breakdown.

## 🚀 Quick Start

You need [Docker 24+ and Docker Compose v2](https://docs.docker.com/get-docker/).
Pick one of the two paths below.

### Option A — Run the prebuilt images (fastest)

No cloning required — just grab the compose file and env templates:

```bash
mkdir ai-learning-platform && cd ai-learning-platform
curl -O https://raw.githubusercontent.com/Indonesia-AI-Institute/AI-Learning-Platform/main/docker-compose.prod.yml
curl -o .env.be https://raw.githubusercontent.com/Indonesia-AI-Institute/AI-Learning-Platform/main/.env.be.example
curl -o .env.fe https://raw.githubusercontent.com/Indonesia-AI-Institute/AI-Learning-Platform/main/.env.fe.example
```

Fill in `.env.be` (Postgres credentials, `SECRET_KEY`, an LLM provider key)
and `.env.fe` (the API URL), then:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Option B — Build from source

Clone the repo and build the images yourself — useful if you want to
inspect or modify the code:

```bash
git clone https://github.com/Indonesia-AI-Institute/AI-Learning-Platform.git
cd AI-Learning-Platform
cp .env.be.example .env.be
cp .env.fe.example .env.fe
# fill in .env.be / .env.fe

docker compose up -d --build
```

Either way, once it's up:

- Frontend → `http://localhost:3000`
- API + docs → `http://localhost:8000/docs`

```bash
docker compose ps                     # check both services are healthy
docker compose logs api --tail=30     # tail the backend if something looks off
```

### Deploying frontend and API on different subdomains

If the two are served from sibling hosts (e.g. `app.example.com` and
`api.example.com`), set these so login works — without a shared cookie
domain the browser keeps the session cookie on the API host only, the
frontend never sees it, and every login bounces back to `/login`:

| File | Variable | Example |
|---|---|---|
| `.env.be` | `ENVIRONMENT` | `production` (marks the cookie `Secure`, so serve both over HTTPS) |
| `.env.be` | `CORS_ORIGINS` | `["https://app.example.com"]` |
| `.env.be` | `COOKIE_DOMAIN` | `.example.com` (the shared parent domain) |
| `.env.fe` | `NEXT_PUBLIC_API_URL` | `https://api.example.com/api/v1` |

Leave `COOKIE_DOMAIN` empty for local or same-host setups. After changing
it, users need to log in again.

> Need a different LLM provider, a non-Docker setup, or a full environment
> variable reference? See [Documentation](#-documentation) below.

## 📚 Documentation

This README is the front door. Everything past "getting it running" lives
in project-specific docs, each scoped to what it covers:

| Doc | Covers |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Repo-wide architecture, dev vs. prod Docker Compose, CI/CD pipeline, versioning |
| [`src/backend/README.md`](src/backend/README.md) | Backend setup without Docker, environment variables, migrations, API reference, testing |
| [`src/frontend/README.md`](src/frontend/README.md) | Frontend setup without Docker, environment variables, pages, testing |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history, generated automatically on every release |

## 🤝 Contributing

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
(`feat`, `fix`, `perf`, `refactor`, `docs`, …) — they drive automatic
versioning on every merge to `main`, so a clear type/description pays off
in a readable changelog. Branch names follow `feat|fix/<short-description>`
or `chore/<area>-<what>`. See [`CLAUDE.md`](CLAUDE.md) for the full
conventions and the release pipeline.

## 📄 License

Internal Use — AI Learning Platform.
