import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login", "/register"];

// Presence-only check: redirects requests with no session cookie at all
// before the page ever renders, closing the gap where an unauthenticated
// visitor would briefly see a protected page's shell while client-side
// data fetches were still resolving. This is NOT a substitute for real
// auth — proxy has no access to SECRET_KEY, so it can't verify the cookie
// is valid or unexpired, only that one was sent. Every request still goes
// through the backend's own auth checks (see api/deps.py), which remain
// the actual authorization boundary.
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_PATHS.some((path) => pathname === path)) {
    return NextResponse.next();
  }

  if (!request.cookies.has("access_token")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|env-config.js).*)"],
};
