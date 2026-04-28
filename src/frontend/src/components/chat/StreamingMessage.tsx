"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function StreamingMessage({ content }: { content: string }) {
  return (
    <div className="flex w-full justify-start">
      <div className="max-w-[75%] rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm bg-muted text-foreground">
        <div className="prose prose-sm dark:prose-invert max-w-none leading-relaxed
          prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1
          prose-li:my-0.5 prose-code:text-xs prose-pre:my-2">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
        </div>
        <span className="inline-block w-0.5 h-4 bg-foreground ml-0.5 animate-pulse" />
      </div>
    </div>
  );
}