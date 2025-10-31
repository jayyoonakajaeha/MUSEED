import { HeroSection } from "@/components/hero-section"
import { PlaylistCard } from "@/components/playlist-card"
import { TrendingUp, Activity } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Mock data for demonstration
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
]

const feedActivities = [
  {
    id: "1",
    user: "Sarah Kim",
    action: "created a new playlist",
    playlist: "Summer Nights",
    time: "2 hours ago",
    coverImage: "/neon-electronic-music.jpg",
    playlistId: "2",
  },
  {
    id: "2",
    user: "Mike Johnson",
    action: "liked",
    playlist: "Midnight Vibes",
    time: "5 hours ago",
    coverImage: "/dark-purple-music-waves.jpg",
    playlistId: "1",
  },
  {
    id: "3",
    user: "Emma Davis",
    action: "created a new playlist",
    playlist: "Chill Coding",
    time: "1 day ago",
    coverImage: "/lofi-aesthetic-purple.jpg",
    playlistId: "4",
  },
]

export default function DashboardPage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <HeroSection />

      {/* Feed and Trending Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <Tabs defaultValue="feed" className="space-y-8">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
            <TabsTrigger value="feed" className="gap-2">
              <Activity className="h-4 w-4" />
              Feed
            </TabsTrigger>
            <TabsTrigger value="trending" className="gap-2">
              <TrendingUp className="h-4 w-4" />
              Trending
            </TabsTrigger>
          </TabsList>

          {/* Feed Tab */}
          <TabsContent value="feed" className="space-y-8">
            <div className="space-y-2">
              <h2 className="text-3xl md:text-4xl font-bold">Your Feed</h2>
              <p className="text-muted-foreground">See what your friends are listening to</p>
            </div>
            <div className="space-y-4">
              {feedActivities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center gap-4 p-4 rounded-lg bg-card border border-border hover:border-primary/50 transition-colors"
                >
                  <img
                    src={activity.coverImage || "/placeholder.svg"}
                    alt={activity.playlist}
                    className="w-16 h-16 rounded-md object-cover"
                  />
                  <div className="flex-1">
                    <p className="text-sm">
                      <span className="font-semibold text-primary">{activity.user}</span> {activity.action}{" "}
                      <span className="font-semibold">{activity.playlist}</span>
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Trending Tab */}
          <TabsContent value="trending" className="space-y-8">
            <div className="space-y-2">
              <h2 className="text-3xl md:text-4xl font-bold">Trending Playlists</h2>
              <p className="text-muted-foreground">Discover what the community is listening to</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {trendingPlaylists.map((playlist) => (
                <PlaylistCard key={playlist.id} {...playlist} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </section>
    </main>
  )
}
