import { describe, it, expect, mock, beforeEach } from "bun:test";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatInput } from "@/components/chat/ChatInput";

describe("ChatInput", () => {
  let onSend: ReturnType<typeof mock>;
  let onStop: ReturnType<typeof mock>;

  beforeEach(() => {
    onSend = mock();
    onStop = mock();
  });

  function textarea() {
    return screen.getByPlaceholderText(/type your message/i);
  }

  it("sends the trimmed message and clears the input on button click", async () => {
    const user = userEvent.setup();
    render(<ChatInput onSend={onSend} isStreaming={false} />);

    await user.type(textarea(), "  Hello there  ");
    await user.click(screen.getByRole("button"));

    expect(onSend).toHaveBeenCalledWith("Hello there");
    expect(textarea()).toHaveValue("");
  });

  it("sends on Enter", async () => {
    const user = userEvent.setup();
    render(<ChatInput onSend={onSend} isStreaming={false} />);

    await user.type(textarea(), "Quick message{Enter}");

    expect(onSend).toHaveBeenCalledWith("Quick message");
  });

  it("inserts a newline on Shift+Enter instead of sending", async () => {
    const user = userEvent.setup();
    render(<ChatInput onSend={onSend} isStreaming={false} />);

    await user.type(textarea(), "line one{Shift>}{Enter}{/Shift}line two");

    expect(onSend).not.toHaveBeenCalled();
    expect(textarea()).toHaveValue("line one\nline two");
  });

  it("does not send an empty or whitespace-only message", async () => {
    const user = userEvent.setup();
    render(<ChatInput onSend={onSend} isStreaming={false} />);

    await user.type(textarea(), "   {Enter}");

    expect(onSend).not.toHaveBeenCalled();
  });

  it("disables the send button while there is no text", () => {
    render(<ChatInput onSend={onSend} isStreaming={false} />);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("disables the textarea when disabled prop is set", () => {
    render(<ChatInput onSend={onSend} isStreaming={false} disabled />);
    expect(textarea()).toBeDisabled();
  });

  it("shows a stop button instead of send while streaming, and disables the textarea", () => {
    render(<ChatInput onSend={onSend} onStop={onStop} isStreaming />);

    expect(textarea()).toBeDisabled();
    const button = screen.getByRole("button");
    expect(button).not.toBeDisabled();
  });

  it("calls onStop when the stop button is clicked while streaming", async () => {
    const user = userEvent.setup();
    render(<ChatInput onSend={onSend} onStop={onStop} isStreaming />);

    await user.click(screen.getByRole("button"));

    expect(onStop).toHaveBeenCalledTimes(1);
    expect(onSend).not.toHaveBeenCalled();
  });

  it("ignores Enter while already streaming", async () => {
    const user = userEvent.setup();
    const { rerender } = render(<ChatInput onSend={onSend} isStreaming={false} />);

    await user.type(textarea(), "typed before streaming started");
    rerender(<ChatInput onSend={onSend} isStreaming />);

    await user.type(textarea(), "{Enter}");

    expect(onSend).not.toHaveBeenCalled();
  });
});
