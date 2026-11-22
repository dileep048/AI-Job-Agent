import type { Metadata } from "next";
import { Inter } from "next/font/google";

import "./globals.css";
import { AppProviders } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "AI Job Agent — Your AI-Powered Job Search Assistant",
    template: "%s · AI Job Agent",
  },
  description:
    "Let your AI job agent find relevant jobs, match opportunities to your profile, and automate repetitive job application work.",
  openGraph: {
    title: "AI Job Agent — Your AI-Powered Job Search Assistant",
    description:
      "Let your AI job agent find relevant jobs, match opportunities to your profile, and automate repetitive job application work.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen antialiased`}>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
