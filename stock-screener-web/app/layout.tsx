import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { Providers } from "./providers";
import { ThemeToggle } from "@/components/theme-toggle";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Stock Screener GARP",
  description: "Growth at Reasonable Price stock screener with daily updates",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-background flex flex-col">
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
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
                    <nav className="flex gap-4">
                      <Link
                        href="/"
                        className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                      >
                        Dashboard
                      </Link>
                      <Link
                        href="/history"
                        className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                      >
                        History
                      </Link>
                    </nav>
                    <ThemeToggle />
                  </div>
                </div>
              </div>
            </header>
            <main className="container mx-auto px-4 py-6 flex-1">{children}</main>
            <footer className="border-t">
              <div className="container mx-auto px-4 py-4 text-center text-sm text-muted-foreground">
                Data updated daily at 6:00 AM EST
              </div>
            </footer>
          </div>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
