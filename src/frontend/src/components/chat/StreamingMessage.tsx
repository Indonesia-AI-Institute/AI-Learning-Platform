"use client";

/**
 * StreamingMessage.tsx
 * ====================
 * Displays streaming AI response with blinking cursor.
 */

export function StreamingMessage({ content }: { content: string }) {
  return (
    <div className="flex w-full justify-start">
      <div className="max-w-[75%] rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm bg-muted text-foreground">
        <p className="whitespace-pre-wrap leading-relaxed">
          {content}
          <span className="inline-block w-0.5 h-4 bg-foreground ml-0.5 animate-pulse" />
        </p>
      </div>
    </div>
  );
}