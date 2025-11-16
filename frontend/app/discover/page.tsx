"use client"

import { useState } from "react"
import { Search, TrendingUp } from "lucide-react"
import { PlaylistCard } from "@/components/playlist-card"
import Link from "next/link"

// Mock data for trending playlists - UPDATED to match the PlaylistCard's expected prop structure
const trendingPlaylists = [
  {
    id: 101,
    name: "Midnight Vibes",
    owner: { id: 1, username: "DJ Luna" },
    tracks: Array(24).fill({}),
    likes_count: 1247,
    liked_by_user: false,
    is_public: true,
    coverImage: "/dark-purple-music-waves.jpg",
  },
  {
    id: 102,
    name: "Electronic Dreams",
    owner: { id: 2, username: "SynthWave" },
    tracks: Array(18).fill({}),
    likes_count: 892,
    liked_by_user: true,
    is_public: true,
    coverImage: "/neon-electronic-music.jpg",
  },
  {
    id: 103,
    name: "Acoustic Sessions",
    owner: { id: 3, username: "Sarah Mitchell" },
    tracks: Array(15).fill({}),
    likes_count: 654,
    liked_by_user: false,
    is_public: true,
    coverImage: "/acoustic-guitar-warm.jpg",
  },
  {
    id: 104,
    name: "Lo-fi Study Beats",
    owner: { id: 4, username: "Chill Collective" },
    tracks: Array(32).fill({}),
    likes_count: 2103,
    liked_by_user: false,
    is_public: true,
    coverImage: "/lofi-aesthetic-purple.jpg",
  },
  {
    id: 105,
    name: "Jazz After Dark",
    owner: { id: 5, username: "Miles Ahead" },
    tracks: Array(21).fill({}),
    likes_count: 743,
    liked_by_user: true,
    is_public: true,
    coverImage: "/jazz-saxophone-dark.jpg",
  },
  {
    id: 106,
    name: "Indie Rock Essentials",
    owner: { id: 6, username: "The Strummers" },
    tracks: Array(27).fill({}),
    likes_count: 1456,
    liked_by_user: false,
    is_public: true,
    coverImage: "/indie-rock-concert.png",
  },
]

// Mock search function
const searchPlaylists = (query: string) => {
  if (!query.trim()) return []
  return trendingPlaylists.filter(
    (playlist) =>
      playlist.name.toLowerCase().includes(query.toLowerCase()) ||
      playlist.owner.username.toLowerCase().includes(query.toLowerCase()),
  )
}

export default function DiscoverPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<typeof trendingPlaylists>([])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    const results = searchPlaylists(query)
    setSearchResults(results)
  }

  return (
    <div className="min-h-screen bg-background pt-24 pb-32 md:pb-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-3 text-balance">Discover Playlists</h1>
          <p className="text-lg text-muted-foreground text-pretty">
            Explore trending playlists and find your next favorite music
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-12">
          <div className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search playlists, artists, or genres..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-surface border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
          </div>
        </div>

        {/* Search Results */}
        {searchQuery && (
          <div className="mb-12">
            <div className="flex items-center gap-2 mb-6">
              <Search className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold">
                Search Results {searchResults.length > 0 && `(${searchResults.length})`}
              </h2>
            </div>

            {searchResults.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {searchResults.map((playlist) => (
                  <PlaylistCard key={playlist.id} playlist={playlist} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-surface rounded-xl border border-border">
                <Search className="h-12 w-12 text-muted-foreground/50 mx-auto mb-3" />
                <p className="text-muted-foreground">No playlists found for "{searchQuery}"</p>
                <p className="text-sm text-muted-foreground mt-1">Try searching with different keywords</p>
              </div>
            )}
          </div>
        )}

        {/* Trending Playlists */}
        <div>
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h2 className="text-2xl font-bold">Trending Playlists</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {trendingPlaylists.map((playlist) => (
              <PlaylistCard key={playlist.id} playlist={playlist} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
