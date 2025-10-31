"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { PlaylistCard } from "@/components/playlist-card"
import { ProfileStats } from "@/components/profile-stats"
import { GenreChart } from "@/components/genre-chart"
import { Settings, Award } from "lucide-react"
import { cn } from "@/lib/utils"

// Mock user data
const userData = {
  name: "Jaeha Yoon",
  username: "@jaehayoon",
  bio: "Music enthusiast and AI playlist curator. Always discovering new sounds.",
  avatar: "/placeholder.svg?height=120&width=120",
  stats: {
    playlistsCreated: 24,
    playlistsLiked: 156,
    followers: 1234,
    following: 567,
  },
  badges: [
    { id: "1", name: "Early Adopter", icon: "🎵" },
    { id: "2", name: "Playlist Master", icon: "🎧" },
    { id: "3", name: "Trendsetter", icon: "⭐" },
  ],
  genrePreferences: [
    { name: "Electronic", value: 35, color: "#8b5cf6" },
    { name: "Indie", value: 25, color: "#a78bfa" },
    { name: "Rock", value: 20, color: "#c4b5fd" },
    { name: "Jazz", value: 12, color: "#ddd6fe" },
    { name: "Other", value: 8, color: "#ede9fe" },
  ],
}

const createdPlaylists = [
  {
    id: "1",
    title: "Midnight Vibes",
    creator: "Jaeha Yoon",
    trackCount: 24,
    likes: 342,
    coverImage: "/dark-purple-music-waves.jpg",
  },
  {
    id: "2",
    title: "Electronic Dreams",
    creator: "Jaeha Yoon",
    trackCount: 18,
    likes: 289,
    coverImage: "/neon-electronic-music.jpg",
  },
  {
    id: "3",
    title: "Acoustic Sessions",
    creator: "Jaeha Yoon",
    trackCount: 15,
    likes: 456,
    coverImage: "/acoustic-guitar-warm.jpg",
  },
]

const likedPlaylists = [
  {
    id: "4",
    title: "Lo-Fi Study Beats",
    creator: "Emma Davis",
    trackCount: 32,
    likes: 678,
    coverImage: "/lofi-aesthetic-purple.jpg",
    isLiked: true,
  },
  {
    id: "5",
    title: "Jazz Fusion",
    creator: "David Lee",
    trackCount: 21,
    likes: 234,
    coverImage: "/jazz-saxophone-dark.jpg",
    isLiked: true,
  },
]

type TabType = "created" | "liked" | "stats"

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<TabType>("created")

  return (
    <>
      <Navigation />
      <main className="container mx-auto px-4 pt-24 pb-32 md:pb-16">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Profile Header */}
          <div className="bg-surface border border-border rounded-xl p-8">
            <div className="flex flex-col md:flex-row gap-8">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center text-5xl font-bold text-primary-foreground">
                  JY
                </div>
              </div>

              {/* Info */}
              <div className="flex-1 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                  <div>
                    <h1 className="text-3xl font-bold">{userData.name}</h1>
                    <p className="text-muted-foreground">{userData.username}</p>
                  </div>
                  <button className="flex items-center gap-2 px-6 py-3 bg-surface-elevated hover:bg-border border border-border rounded-lg font-medium transition-all">
                    <Settings className="h-5 w-5" />
                    Edit Profile
                  </button>
                </div>

                <p className="text-muted-foreground leading-relaxed">{userData.bio}</p>

                {/* Badges */}
                <div className="flex flex-wrap gap-2">
                  {userData.badges.map((badge) => (
                    <div
                      key={badge.id}
                      className="flex items-center gap-2 px-4 py-2 bg-surface-elevated border border-border rounded-full text-sm"
                    >
                      <span>{badge.icon}</span>
                      <span className="font-medium">{badge.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Stats */}
          <ProfileStats {...userData.stats} />

          {/* Tabs */}
          <div className="border-b border-border">
            <div className="flex gap-8">
              <button
                onClick={() => setActiveTab("created")}
                className={cn(
                  "pb-4 font-semibold transition-colors relative",
                  activeTab === "created" ? "text-primary" : "text-muted-foreground hover:text-foreground",
                )}
              >
                Created Playlists
                {activeTab === "created" && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
                )}
              </button>
              <button
                onClick={() => setActiveTab("liked")}
                className={cn(
                  "pb-4 font-semibold transition-colors relative",
                  activeTab === "liked" ? "text-primary" : "text-muted-foreground hover:text-foreground",
                )}
              >
                Liked Playlists
                {activeTab === "liked" && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
                )}
              </button>
              <button
                onClick={() => setActiveTab("stats")}
                className={cn(
                  "pb-4 font-semibold transition-colors relative",
                  activeTab === "stats" ? "text-primary" : "text-muted-foreground hover:text-foreground",
                )}
              >
                Genre Stats
                {activeTab === "stats" && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
                )}
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div>
            {activeTab === "created" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {createdPlaylists.map((playlist) => (
                  <PlaylistCard key={playlist.id} {...playlist} />
                ))}
              </div>
            )}

            {activeTab === "liked" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {likedPlaylists.map((playlist) => (
                  <PlaylistCard key={playlist.id} {...playlist} />
                ))}
              </div>
            )}

            {activeTab === "stats" && (
              <div className="bg-surface border border-border rounded-xl p-8">
                <div className="space-y-6">
                  <div className="text-center space-y-2">
                    <div className="flex items-center justify-center gap-2">
                      <Award className="h-6 w-6 text-primary" />
                      <h2 className="text-2xl font-bold">Your Genre Preferences</h2>
                    </div>
                    <p className="text-muted-foreground">Based on your created playlists</p>
                  </div>
                  <GenreChart data={userData.genrePreferences} />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  )
}
