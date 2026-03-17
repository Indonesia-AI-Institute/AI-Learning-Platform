/**
 * middleware.ts
 * ============
 * Route protection via httpOnly cookie check.
 * Runs on Edge Runtime before page render.
 */

import { NextRequest, NextResponse } from "next/server";

// Routes yang butuh login
const PROTECTED_ROUTES = [
  "/dashboard",
  "/courses",
  "/classes",
  "/tasks",
  "/chat",
  "/analytics",
  "/enrollments",
];

// Routes yang tidak boleh diakses kalau sudah login
const AUTH_ROUTES = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token")?.value;

  const isProtected = PROTECTED_ROUTES.some((route) =>
    pathname.startsWith(route)
  );
  const isAuthRoute = AUTH_ROUTES.some((route) =>
    pathname.startsWith(route)
  );

  // Belum login, coba akses protected route → redirect ke /login
  if (isProtected && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname); // simpan tujuan asal
    return NextResponse.redirect(loginUrl);
  }

  // Sudah login, coba akses /login atau /register → redirect ke /dashboard
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match semua path kecuali:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     * - api routes
     */
    "/((?!_next/static|_next/image|favicon.ico|api).*)",
  ],
};