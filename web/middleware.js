import { NextRequest, NextResponse } from "next/server";

export function middleware(request) {
  const pathname = request.nextUrl.pathname;
  const accessToken = request.cookies.get("access_token")?.value;

  // Redirect unauthenticated users trying to access dashboard
  if (pathname.startsWith("/dashboard")) {
    if (!accessToken) {
      return NextResponse.redirect(new URL("/auth/login", request.url));
    }
  }

  // Redirect authenticated users away from auth pages
  if (pathname.startsWith("/auth/")) {
    if (accessToken) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  // Redirect root to dashboard if authenticated, otherwise show landing page
  if (pathname === "/") {
    if (accessToken) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/dashboard/:path*", "/auth/:path*"],
};
