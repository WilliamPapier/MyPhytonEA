
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import Navbar from "@/components/Navbar";
import CartProvider from "@/components/CartProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Digital Luxe Market | Premium Digital Products for Africa & Beyond",
  description: "Discover premium digital downloads, templates, and tools for entrepreneurs, creators, and professionals. Instant delivery, secure payments, and expert support.",
  keywords: [
    "digital products",
    "templates",
    "downloads",
    "Africa",
    "entrepreneur",
    "premium",
    "workflow",
    "business tools",
    "instant delivery",
    "PayPal",
    "Ozow",
    "PayFast"
  ],
  openGraph: {
    title: "Digital Luxe Market | Premium Digital Products for Africa & Beyond",
    description: "Discover premium digital downloads, templates, and tools for entrepreneurs, creators, and professionals. Instant delivery, secure payments, and expert support.",
    url: "https://yourdomain.com/",
    siteName: "Digital Luxe Market",
    images: [
      {
        url: "https://yourdomain.com/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Digital Luxe Market - Premium Digital Products"
      }
    ],
    locale: "en_ZA",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Digital Luxe Market | Premium Digital Products for Africa & Beyond",
    description: "Discover premium digital downloads, templates, and tools for entrepreneurs, creators, and professionals. Instant delivery, secure payments, and expert support.",
    images: ["https://yourdomain.com/og-image.jpg"]
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
  <html lang="en" dir="ltr">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased pt-20 bg-background`}
        aria-label="Digital Luxe Market main content"
      >
        <CartProvider>
          <Navbar />
          <main id="main-content" tabIndex={-1}>
            {children}
          </main>
        </CartProvider>
      </body>
    </html>
  );
}
