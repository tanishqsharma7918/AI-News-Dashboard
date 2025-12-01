import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Pulse | Intelligent News",
  description: "Real-time AI News Aggregator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/* Uses system fonts to prevent network timeouts */}
      <body className="font-sans antialiased text-slate-800 bg-slate-50">
        {children}
      </body>
    </html>
  );
}