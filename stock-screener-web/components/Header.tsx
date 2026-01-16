"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/theme-toggle";
import { UserMenu } from "@/components/auth";
import { cn } from "@/lib/utils";

export function Header() {
  const pathname = usePathname();
  const isLanding = pathname === "/";

  return (
    <header className={cn(
      "sticky top-0 z-50 w-full border-b backdrop-blur supports-[backdrop-filter]:bg-background/60",
      isLanding ? "bg-transparent border-transparent" : "bg-background/95"
    )}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div>
            <Link href="/" className="hover:opacity-80 transition-opacity">
              <h1 className="text-2xl font-bold">Stock Screener GARP</h1>
              <p className="text-sm text-muted-foreground">
                Growth at Reasonable Price
              </p>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <nav className="hidden md:flex gap-4">
              <Link
                href="/dashboard"
                className={cn(
                  "text-sm font-medium transition-colors",
                  pathname === "/dashboard" ? "text-foreground" : "text-muted-foreground hover:text-foreground"
                )}
              >
                Dashboard
              </Link>
              <Link
                href="/history"
                className={cn(
                  "text-sm font-medium transition-colors",
                  pathname === "/history" ? "text-foreground" : "text-muted-foreground hover:text-foreground"
                )}
              >
                History
              </Link>
              <Link
                href="/pricing"
                className={cn(
                  "text-sm font-medium transition-colors",
                  pathname === "/pricing" ? "text-foreground" : "text-muted-foreground hover:text-foreground"
                )}
              >
                Pricing
              </Link>
            </nav>
            <ThemeToggle />
            <UserMenu />
          </div>
        </div>
      </div>
    </header>
  );
}
