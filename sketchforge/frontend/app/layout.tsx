import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SketchForge — photo to sketch & paint-by-numbers",
  description:
    "Turn a photo into a realistic pencil sketch, a traceable outline or an SVG paint-by-numbers. Same photo and settings always give the same result.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
