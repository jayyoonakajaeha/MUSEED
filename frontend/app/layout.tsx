"use client"

import type React from "react"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"
import { Navigation } from "@/components/navigation"
import { AuthProvider } from "@/context/AuthContext"
import { PlayerProvider } from "@/context/PlayerContext"
import { AudioPlayer } from "@/components/audio-player"

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
})

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`dark ${geistSans.variable} ${geistMono.variable}`}>
      <body className="min-h-screen bg-background text-foreground">
        <AuthProvider>
          <PlayerProvider>
            <Navigation />
            <main className="pb-24">
              {children}
            </main>
            <AudioPlayer />
          </PlayerProvider>
        </AuthProvider>
      </body>
    </html>
  )
}