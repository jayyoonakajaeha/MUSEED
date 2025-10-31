"use client"

import { useState } from "react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { PlaylistCard } from "@/components/playlist-card"
import { UserPlus, UserMinus, Music, Heart, Users } from "lucide-react"
import { use } from "react"

// Mock data
const userData = {
  id: "2",
  name: "Sarah Kim",
  username: "sarahkim",
  bio: "Music lover and playlist curator",
  stats: {
    playlists: 24,
    followers: 1234,
    following: 567,
  },
  playlists: [
    {
      id: "2",
      title: "Electronic Dreams",
      creator: "Sarah Kim",
      trackCount: 18,
      likes: 289,
      coverImage: "/neon-electronic-music.jpg",
    },
    {
      id: "7",
      title: "Summer Nights",
      creator: "Sarah Kim",
      trackCount: 22,
      likes: 156,
      coverImage: "/dark-purple-music-waves.jpg",
    },
  ],
}

export default function UserProfilePage({ params }: { params: Promise<{ userId: string }> }) {
  const { userId } = use(params)
  const [isFollowing, setIsFollowing] = useState(false)

  const handleFollowToggle = () => {
    setIsFollowing(!isFollowing)
  }

  return (
    <main className="min-h-screen py-24">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Profile Header */}
        <div className="space-y-8">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <Avatar className="h-32 w-32 border-4 border-primary/20">
              <AvatarFallback className="text-4xl bg-primary/10 text-primary">
                {userData.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1 space-y-4">
              <div>
                <h1 className="text-4xl font-bold">{userData.name}</h1>
                <p className="text-muted-foreground">@{userData.username}</p>
              </div>

              {userData.bio && <p className="text-foreground/80">{userData.bio}</p>}

              <div className="flex flex-wrap gap-6">
                <div className="flex items-center gap-2">
                  <Music className="h-5 w-5 text-primary" />
                  <span className="font-semibold">{userData.stats.playlists}</span>
                  <span className="text-muted-foreground">Playlists</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  <span className="font-semibold">{userData.stats.followers}</span>
                  <span className="text-muted-foreground">Followers</span>
                </div>
                <div className="flex items-center gap-2">
                  <Heart className="h-5 w-5 text-primary" />
                  <span className="font-semibold">{userData.stats.following}</span>
                  <span className="text-muted-foreground">Following</span>
                </div>
              </div>

              <Button onClick={handleFollowToggle} variant={isFollowing ? "outline" : "default"} className="gap-2">
                {isFollowing ? (
                  <>
                    <UserMinus className="h-4 w-4" />
                    Unfollow
                  </>
                ) : (
                  <>
                    <UserPlus className="h-4 w-4" />
                    Follow
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Public Playlists */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Public Playlists</h2>
              <Badge variant="secondary">{userData.playlists.length} playlists</Badge>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {userData.playlists.map((playlist) => (
                <PlaylistCard key={playlist.id} {...playlist} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
