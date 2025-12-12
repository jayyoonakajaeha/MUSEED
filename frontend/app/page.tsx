import { HeroSection } from "@/components/hero-section"
import { PlaylistCard } from "@/components/playlist-card"
import { TrendingUp } from "lucide-react"
import { redirect } from "next/navigation"

// 시연용 더미 데이터
const trendingPlaylists = [
  {
    id: "1",
    title: "Midnight Vibes",
    creator: "Alex Chen",
    trackCount: 24,
    likes: 342,
    coverImage: "/dark-purple-music-waves.jpg",
  },
  {
    id: "2",
    title: "Electronic Dreams",
    creator: "Sarah Kim",
    trackCount: 18,
    likes: 289,
    coverImage: "/neon-electronic-music.jpg",
  },
  {
    id: "3",
    title: "Acoustic Sessions",
    creator: "Mike Johnson",
    trackCount: 15,
    likes: 456,
    coverImage: "/acoustic-guitar-warm.jpg",
  },
  {
    id: "4",
    title: "Lo-Fi Study Beats",
    creator: "Emma Davis",
    trackCount: 32,
    likes: 678,
    coverImage: "/lofi-aesthetic-purple.jpg",
  },
  {
    id: "5",
    title: "Jazz Fusion",
    creator: "David Lee",
    trackCount: 21,
    likes: 234,
    coverImage: "/jazz-saxophone-dark.jpg",
  },
  {
    id: "6",
    title: "Indie Rock Essentials",
    creator: "Lisa Park",
    trackCount: 27,
    likes: 512,
    coverImage: "/indie-rock-concert.png",
  },
]

export default function HomePage() {
  redirect("/dashboard")

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <HeroSection />

      {/* Trending Playlists Feed */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="space-y-8">
          {/* Section Header */}
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-primary" />
                <h2 className="text-3xl md:text-4xl font-bold">Trending Playlists</h2>
              </div>
              <p className="text-muted-foreground">Discover what the community is listening to</p>
            </div>
          </div>

          {/* Playlist Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {trendingPlaylists.map((playlist) => (
              <PlaylistCard key={playlist.id} {...playlist} />
            ))}
          </div>
        </div>
      </section>
    </main>
  )
}
