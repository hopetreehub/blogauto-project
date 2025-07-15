import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";
import { SidebarProvider, MainContent } from "@/components/SidebarLayout";
import { WorkflowProvider } from "@/contexts/WorkflowContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import "@/styles/design-tokens.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "블로그 자동화 시스템",
  description: "AI 기반 블로그 콘텐츠 자동화 솔루션",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-50 dark:bg-gray-900`}
      >
        <ThemeProvider defaultTheme="system" storageKey="blogauto-theme">
          <WorkflowProvider>
            <SidebarProvider>
              <Navigation />
              <div className="pt-16">
                <MainContent>
                  <main>
                    {children}
                  </main>
                </MainContent>
              </div>
            </SidebarProvider>
          </WorkflowProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
