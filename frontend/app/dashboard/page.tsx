"use client"

import { useState, useEffect } from "react"
import { HeroSection } from "@/components/hero-section"
import { PlaylistCard } from "@/components/playlist-card"
import { TrendingUp, Activity, Loader2, User, Music } from "lucide-react" // Added Music icon
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAuth } from "@/context/AuthContext"
import { cn } from "@/lib/utils"
import { getTrendingPlaylists, getUserFeed } from "@/lib/api"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import Link from "next/link"
import { useLanguage } from "@/context/LanguageContext"

// Interface for Activity Feed
interface ActivityItem {
    id: number;
    user: {
        id: number;
        username: string;
        nickname: string;
        profile_image_key: string;
    };
    action_type: string;
    target_playlist?: {
        id: number;
        name: string;
        tracks: any[]; // To access album art
    };
    target_user?: {
        id: number;
        username: string;
        nickname: string;
        profile_image_key: string;
    };
    created_at: string;
}

const getAlbumArtUrl = (url: string | null | undefined): string => {
    if (url && (url.includes('.jpg') || url.includes('.png') || url.includes('.gif'))) {
      return url;
    }
    return '/dark-purple-music-waves.jpg';
  }

function TrendingSection() {
    const [playlists, setPlaylists] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { token } = useAuth();

    useEffect(() => {
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
        return <p className="text-muted-foreground">No trending playlists found yet.</p>;
    }

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {playlists.map((playlist) => (
            <PlaylistCard key={playlist.id} playlist={playlist} />
          ))}
        </div>
    );
}

function FeedSection() {
    const [activities, setActivities] = useState<ActivityItem[]>([]);
    const [loading, setLoading] = useState(true);
    const { token } = useAuth();
    const { t } = useLanguage();

    useEffect(() => {
        if (!token) {
            setLoading(false);
            return;
        }

        const fetchFeed = async () => {
            setLoading(true);
            const result = await getUserFeed(token);
            if (result.success) {
                setActivities(result.data);
            }
            setLoading(false);
        }
        fetchFeed();
    }, [token]);

    if (loading) {
        return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
    }

    if (activities.length === 0) {
        return (
            <div className="text-center py-12 bg-card border border-border rounded-xl">
                <Activity className="h-12 w-12 text-muted-foreground/50 mx-auto mb-3" />
                <p className="text-muted-foreground">{t.dashboard.emptyFeed}</p>
                <p className="text-sm text-muted-foreground mt-1">{t.dashboard.emptyFeedSub}</p>
                <Link href="/discover" className="text-primary hover:underline mt-2 inline-block text-sm">
                    {t.dashboard.discoverPeople}
                </Link>
            </div>
        );
    }

    // Helper to format date roughly
    const formatTime = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="space-y-4">
          {activities.map((activity) => (
            <div
              key={activity.id}
              className="flex items-center gap-4 p-4 rounded-lg bg-card border border-border hover:border-primary/50 transition-colors"
            >
              <Link href={`/user/${activity.user.username}`}>
                <Avatar>
                    <AvatarImage src={`/profiles/${activity.user.profile_image_key || 'Default'}.png`} />
                    <AvatarFallback>{activity.user.username.substring(0, 2).toUpperCase()}</AvatarFallback>
                </Avatar>
              </Link>
              
              <div className="flex-1">
                <p className="text-sm">
                  <Link href={`/user/${activity.user.username}`} className="font-semibold text-primary hover:underline">
                    {activity.user.nickname}
                  </Link>{" "}
                  {activity.action_type === "created a new playlist" && "created a new playlist"}
                  {activity.action_type === "liked" && "liked playlist"}
                  {activity.action_type === "started following" && "started following"}
                  {" "}
                  {activity.target_playlist && (
                      <Link href={`/playlist/${activity.target_playlist.id}`} className="font-semibold hover:underline">
                          {activity.target_playlist.name}
                      </Link>
                  )}
                  {activity.target_user && (
                      <Link href={`/user/${activity.target_user.username}`} className="font-semibold hover:underline">
                          {activity.target_user.nickname}
                      </Link>
                  )}
                </p>
                <p className="text-xs text-muted-foreground mt-1">{formatTime(activity.created_at)}</p>
              </div>
              
              {activity.target_playlist && (
                  <div className="h-12 w-12 bg-muted rounded overflow-hidden flex-shrink-0">
                      {activity.target_playlist.tracks && activity.target_playlist.tracks.length > 0 ? (
                          <img 
                            src={getAlbumArtUrl(
                                activity.target_playlist.tracks[0].track 
                                    ? activity.target_playlist.tracks[0].track.album_art_url 
                                    : activity.target_playlist.tracks[0].album_art_url
                            )} 
                            alt="Playlist Cover" 
                            className="w-full h-full object-cover"
                            onError={(e) => { e.currentTarget.src = '/dark-purple-music-waves.jpg'; }}
                          />
                      ) : (
                          <Music className="h-full w-full p-3 text-muted-foreground" />
                      )}
                  </div>
              )}
            </div>
          ))}
        </div>
    );
}

function LoggedInDashboard() {
  const { t } = useLanguage();
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
          {t.dashboard.feed}
        </TabsTrigger>
        <TabsTrigger
          value="trending"
          className={cn(
            "gap-2 data-[state=inactive]:text-muted-foreground data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
            "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
          )}
        >
          <TrendingUp className="h-4 w-4" />
          {t.dashboard.trending}
        </TabsTrigger>
      </TabsList>

      {/* Feed Tab */}
      <TabsContent value="feed" className="space-y-8">
        <div className="space-y-2">
          <h2 className="text-3xl md:text-4xl font-bold">{t.dashboard.feedTitle}</h2>
          <p className="text-muted-foreground">{t.dashboard.feedSubtitle}</p>
        </div>
        <FeedSection />
      </TabsContent>

      {/* Trending Tab */}
      <TabsContent value="trending" className="space-y-8">
        <div className="space-y-2">
          <h2 className="text-3xl md:text-4xl font-bold">{t.dashboard.trendingTitle}</h2>
          <p className="text-muted-foreground">{t.dashboard.trendingSubtitle}</p>
        </div>
        <TrendingSection />
      </TabsContent>
    </Tabs>
  )
}

function GuestDashboard() {
  const { t } = useLanguage();
  return (
    <div className="space-y-8">
      <div className="space-y-2 text-center">
        <h2 className="text-3xl md:text-4xl font-bold">{t.dashboard.joinCommunity}</h2>
        <p className="text-muted-foreground">{t.dashboard.joinSubtitle}</p>
      </div>
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
