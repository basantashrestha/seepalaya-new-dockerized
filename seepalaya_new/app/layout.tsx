import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/app/globals.css";
import { LanguageProvider } from "@/app/utils/LanguageContext";
import StoreProvider from "@/lib/redux/StoreProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Seepalaya",
  description: "A Learning Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <LanguageProvider>
      <html lang="en">
        <body className={`${inter.className}`}>
          <StoreProvider>{children}</StoreProvider>
        </body>
      </html>
    </LanguageProvider>
  );
}
