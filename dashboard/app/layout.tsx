import type { Metadata } from "next";
import { Providers } from "./providers";
import "../src/index.css";

export const metadata: Metadata = {
  title: "Running Dashboard",
  description: "Fitness running dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  const stored = localStorage.getItem('dashboard-store');
                  if (stored) {
                    const parsed = JSON.parse(stored);
                    const themeValue = parsed?.state?.theme || 'system';
                    const effectiveTheme = themeValue === 'system' 
                      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
                      : themeValue;
                    if (effectiveTheme === 'dark') {
                      document.documentElement.classList.add('dark');
                    } else {
                      document.documentElement.classList.remove('dark');
                    }
                  }
                } catch (e) {
                  // Ignore errors
                }
              })();
            `,
          }}
        />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
