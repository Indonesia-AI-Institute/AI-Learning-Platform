"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { cn } from "@/lib/utils";
import { ChatMessage as ChatMessageType } from "@/types/chat.types";
import "katex/dist/katex.min.css";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-2.5 text-sm",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : "bg-muted text-foreground rounded-bl-sm"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none leading-relaxed
            prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1
            prose-li:my-0.5 prose-code:text-xs prose-pre:my-2
            prose-blockquote:my-1 prose-table:my-2">
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{
                code({ node: _node, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || "");
                  const isInline = !match && !className;
                  
                  if (isInline) {
                    return <code className="bg-muted-foreground/20 px-1 py-0.5 rounded text-xs font-mono" {...props}>{children}</code>;
                  }
                  
                  return (
                    <SyntaxHighlighter
                      style={oneDark}
                      language={match ? match[1] : "text"}
                      PreTag="div"
                      customStyle={{
                        margin: "0.5rem 0",
                        borderRadius: "0.5rem",
                        padding: "1rem",
                        fontSize: "0.8rem"
                      }}
                    >
                      {String(children).replace(/\n$/, "")}
                    </SyntaxHighlighter>
                  );
                },
                h1: ({ children }) => <h1 className="text-xl font-bold my-2">{children}</h1>,
                h2: ({ children }) => <h2 className="text-lg font-semibold my-2">{children}</h2>,
                h3: ({ children }) => <h3 className="text-md font-medium my-1">{children}</h3>,
                ul: ({ children }) => <ul className="list-disc list-inside my-1 space-y-0.5">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside my-1 space-y-0.5">{children}</ol>,
                li: ({ children }) => <li className="my-0.5">{children}</li>,
                blockquote: ({ children }) => <blockquote className="border-l-4 border-primary/50 pl-3 italic opacity-80 my-1">{children}</blockquote>,
                a: ({ href, children }) => <a href={href} className="text-primary underline hover:text-primary/80" target="_blank" rel="noopener noreferrer">{children}</a>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        <p className={cn(
          "text-xs mt-1 opacity-60",
          isUser ? "text-right" : "text-left"
        )}>
          {new Date(message.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </p>
      </div>
    </div>
  );
}
