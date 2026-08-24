/**
 * app/layout.tsx
 * ==============
 * Root Server Layout.
 */

import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { Providers } from "@/components/providers";
import "./globals.css";
import Script from "next/script";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Learning Platform",
  description: "AI-powered learning management system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
          <Script src="/env-config.js" strategy="beforeInteractive" />
      </head>

      <body className={geist.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}