"use client"

import type React from "react"

import { Geist, Geist_Mono } from "next/font/google"

import "./globals.css"

import { Navigation } from "@/components/navigation"

import { AuthProvider } from "@/context/AuthContext"

import { PlayerProvider } from "@/context/PlayerContext"

import { AudioPlayer } from "@/components/audio-player"

import { PlayerAuthSync } from "@/components/player-auth-sync"
import { Toaster } from "@/components/ui/toaster"
import { LanguageProvider } from "@/context/LanguageContext"


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
          <LanguageProvider>
            <PlayerProvider>

              <PlayerAuthSync />

              <Navigation />

              <main className="pb-24">

                {children}

              </main>

              <AudioPlayer />
              <Toaster />
            </PlayerProvider>
          </LanguageProvider>
        </AuthProvider>
        <footer className="w-full bg-background/95 backdrop-blur border-t border-border py-6 pb-32 text-center text-sm text-muted-foreground">
          <div className="container mx-auto px-4">
            <p>&copy; {new Date().getFullYear()} MUSEED. All rights reserved.</p>
            <p>Created by Jaeha Yoon (613jay@sju.ac.kr)</p>
            <p>This project was single-handedly developed by Jaeha Yoon.</p>
          </div>
        </footer>
      </body>
    </html>

  )

}
