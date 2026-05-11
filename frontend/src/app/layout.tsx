import type { Metadata } from "next";
import { Noto_Sans } from "next/font/google";

import "./globals.css";

const notoSans = Noto_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "AI Nepal Platform",
  description: "Monorepo foundation for AI tools built for Nepal.",
  icons: {
    icon: "/icon.svg",
    shortcut: "/icon.svg",
    apple: "/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${notoSans.variable} min-h-screen font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
