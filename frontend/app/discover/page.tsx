"use client"

import { useState } from "react"
import { Search, TrendingUp } from "lucide-react"
import { PlaylistCard } from "@/components/playlist-card"
import Link from "next/link"

// Mock data for trending playlists
const trendingPlaylists = [
  {
    id: "1",
    title: "Midnight Vibes",
    creator: "DJ Luna",
    trackCount: 24,
    likes: 1247,
    coverImage: "/dark-purple-music-waves.jpg",
    isLiked: false,
  },
  {
    id: "2",
    title: "Electronic Dreams",
    creator: "SynthWave",
    trackCount: 18,
    likes: 892,
    coverImage: "/neon-electronic-music.jpg",
    isLiked: true,
  },
  {
    id: "3",
    title: "Acoustic Sessions",
    creator: "Sarah Mitchell",
    trackCount: 15,
    likes: 654,
    coverImage: "/acoustic-guitar-warm.jpg",
    isLiked: false,
  },
  {
    id: "4",
    title: "Lo-fi Study Beats",
    creator: "Chill Collective",
    trackCount: 32,
    likes: 2103,
    coverImage: "/lofi-aesthetic-purple.jpg",
    isLiked: false,
  },
  {
    id: "5",
    title: "Jazz After Dark",
    creator: "Miles Ahead",
    trackCount: 21,
    likes: 743,
    coverImage: "/jazz-saxophone-dark.jpg",
    isLiked: true,
  },
  {
    id: "6",
    title: "Indie Rock Essentials",
    creator: "The Strummers",
    trackCount: 27,
    likes: 1456,
    coverImage: "/indie-rock-concert.png",
    isLiked: false,
  },
]

// Mock search function
const searchPlaylists = (query: string) => {
  if (!query.trim()) return []
  return trendingPlaylists.filter(
    (playlist) =>
      playlist.title.toLowerCase().includes(query.toLowerCase()) ||
      playlist.creator.toLowerCase().includes(query.toLowerCase()),
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
                  <Link key={playlist.id} href={`/playlist/${playlist.id}`}>
                    <PlaylistCard {...playlist} />
                  </Link>
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
              <Link key={playlist.id} href={`/playlist/${playlist.id}`}>
                <PlaylistCard {...playlist} />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
