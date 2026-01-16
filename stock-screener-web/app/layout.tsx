import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

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
          <div className="min-h-screen bg-background">
            <header className="border-b">
              <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold">Stock Screener GARP</h1>
                    <p className="text-sm text-muted-foreground">
                      Growth at Reasonable Price
                    </p>
                  </div>
                  <nav className="flex gap-4">
                    <a
                      href="/"
                      className="text-sm font-medium hover:text-primary"
                    >
                      Dashboard
                    </a>
                    <a
                      href="/history"
                      className="text-sm font-medium hover:text-primary"
                    >
                      History
                    </a>
                  </nav>
                </div>
              </div>
            </header>
            <main className="container mx-auto px-4 py-6">{children}</main>
            <footer className="border-t mt-auto">
              <div className="container mx-auto px-4 py-4 text-center text-sm text-muted-foreground">
                Data updated daily at 6:00 AM EST
              </div>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}
