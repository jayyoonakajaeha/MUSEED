"use client"

import { useState, useEffect } from "react"
import { HeroSection } from "@/components/hero-section"
import { PlaylistCard } from "@/components/playlist-card"
import { TrendingUp, Activity, Loader2 } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAuth } from "@/context/AuthContext"
import { cn } from "@/lib/utils"
import { getTrendingPlaylists } from "@/lib/api"

// Mock feed data (unchanged for now)
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

function TrendingSection() {
    const [playlists, setPlaylists] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { token } = useAuth();

    useEffect(() => {
        // For guest users, token might be null, but the API might require it.
        // Actually the backend endpoint likely requires auth for now based on typical router setup.
        // But crud.get_trending_playlists doesn't strictly need user info except for 'liked_by_user' check.
        // Let's assume we pass token if available, or empty string if not (backend might reject empty token).
        // If backend requires auth for /trending, guests won't see it.
        // Checking backend: router uses `current_user: models.User = Depends(get_current_user)`.
        // So guests CANNOT see trending playlists currently.
        // However, guests should probably see trending.
        // We will try to fetch if token exists.
        
        if (!token) {
            setLoading(false);
            return;
        }

        const fetchTrending = async () => {
            setLoading(true);
            const result = await getTrendingPlaylists(token);
            if (result.success) {
                setPlaylists(result.data);
            }
            setLoading(false);
        }
        fetchTrending();
    }, [token]);

    if (loading) {
        return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
    }

    if (playlists.length === 0) {
        return <p className="text-muted-foreground">No trending playlists found.</p>;
    }

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {playlists.map((playlist) => (
            <PlaylistCard key={playlist.id} playlist={playlist} />
          ))}
        </div>
    );
}

function LoggedInDashboard() {
  return (
    <Tabs defaultValue="feed" className="space-y-8">
      <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
        <TabsTrigger
          value="feed"
          className={cn(
            "gap-2 data-[state=inactive]:text-muted-foreground data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
            "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
          )}
        >
          <Activity className="h-4 w-4" />
          Feed
        </TabsTrigger>
        <TabsTrigger
          value="trending"
          className={cn(
            "gap-2 data-[state=inactive]:text-muted-foreground data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
            "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
          )}
        >
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
        <TrendingSection />
      </TabsContent>
    </Tabs>
  )
}

function GuestDashboard() {
  return (
    <div className="space-y-8">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl md:text-4xl font-bold">Join the Community</h2>
        <p className="text-muted-foreground">Sign up to create playlists and follow artists.</p>
      </div>
      {/* Guests can't see trending yet because API requires token. 
          In a real app, we'd make a public endpoint. For now, show a prompt. */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 opacity-50 pointer-events-none blur-sm select-none">
             {/* Fake placeholders to tease content */}
             {[1,2,3].map(i => (
                 <div key={i} className="aspect-square bg-muted rounded-xl"></div>
             ))}
        </div>
    </div>
  )
}


export default function DashboardPage() {
  const { user } = useAuth()

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <HeroSection />

      {/* Feed and Trending Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        {user ? <LoggedInDashboard /> : <GuestDashboard />}
      </section>
    </main>
  )
}