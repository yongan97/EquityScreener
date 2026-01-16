import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Stock Screener GARP - AI-Powered Stock Screening",
  description: "Find the best growth stocks at reasonable prices with AI-powered daily screening. GARP strategy with complete trade ideas and analysis.",
  keywords: ["stock screener", "GARP", "growth investing", "AI stock analysis", "trade ideas"],
  openGraph: {
    title: "Stock Screener GARP - AI-Powered Stock Screening",
    description: "Find the best growth stocks at reasonable prices with AI-powered daily screening.",
    type: "website",
  },
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
            <Header />
            <main className="flex-1">{children}</main>
          </div>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
