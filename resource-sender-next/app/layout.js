import "./globals.css";

export const metadata = { title: "Resource Sender", robots: { index: false, follow: false } };

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
