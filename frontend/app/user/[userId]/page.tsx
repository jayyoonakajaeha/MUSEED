"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { PlaylistCard } from "@/components/playlist-card"
import { UserPlus, UserMinus, Music, Heart, Users, Loader2, Edit } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { getUserProfile } from "@/lib/api"

// Define a type for the user profile data for better type safety
type UserProfile = {
  id: number;
  username: string;
  email: string;
  // Add other fields as they become available from the API
  // For now, we'll mock the stats and playlists for display purposes
  stats: {
    playlists: number;
    followers: number;
    following: number;
  };
  playlists: any[];
};

export default function UserProfilePage() {
  const params = useParams()
  const userId = params.userId as string;
  const { user: currentUser, token } = useAuth()

  const [profileData, setProfileData] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isFollowing, setIsFollowing] = useState(false)

  useEffect(() => {
    // Ensure we don't fetch until the token is loaded
    if (token === undefined) {
        return;
    }

    if (!token) {
        // Handle case where user is not logged in
        setLoading(false)
        setError("You must be logged in to view profiles.")
        return;
    }
    
    if (userId) {
      const fetchProfile = async () => {
        setLoading(true)
        setError(null)
        const result = await getUserProfile(userId, token)
        if (result.success) {
          // Mocking stats and playlists for now as the API doesn't provide them yet
          setProfileData({
            ...result.data,
            stats: { playlists: 0, followers: 0, following: 0 },
            playlists: [],
          })
        } else {
          setError(result.error || "Failed to load profile.")
        }
        setLoading(false)
      }
      fetchProfile()
    }
  }, [userId, token])

  const handleFollowToggle = () => {
    setIsFollowing(!isFollowing)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-destructive">{error}</p>
      </div>
    )
  }

  if (!profileData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>User not found.</p>
      </div>
    )
  }

  const isOwnProfile = currentUser?.sub === profileData.username;

  return (
    <main className="min-h-screen py-24">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Profile Header */}
        <div className="space-y-8">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <Avatar className="h-32 w-32 border-4 border-primary/20">
              <AvatarFallback className="text-4xl bg-primary/10 text-primary">
                {profileData.username.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1 space-y-4">
              <div>
                <h1 className="text-4xl font-bold">{profileData.username}</h1>
                <p className="text-muted-foreground">@{profileData.username}</p>
              </div>

              <div className="flex flex-wrap gap-6">
                <div className="flex items-center gap-2">
                  <Music className="h-5 w-5 text-primary" />
                  <span className="font-semibold">{profileData.stats.playlists}</span>
                  <span className="text-muted-foreground">Playlists</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  <span className="font-semibold">{profileData.stats.followers}</span>
                  <span className="text-muted-foreground">Followers</span>
                </div>
                <div className="flex items-center gap-2">
                  <Heart className="h-5 w-5 text-primary" />
                  <span className="font-semibold">{profileData.stats.following}</span>
                  <span className="text-muted-foreground">Following</span>
                </div>
              </div>

              {isOwnProfile ? (
                <Button asChild variant="outline" className="gap-2">
                  <Link href="/profile/edit">
                    <Edit className="h-4 w-4" />
                    Edit Profile
                  </Link>
                </Button>
              ) : (
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
              )}
            </div>
          </div>

          {/* Public Playlists */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Public Playlists</h2>
              <Badge variant="secondary">{profileData.playlists.length} playlists</Badge>
            </div>

            {profileData.playlists.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {profileData.playlists.map((playlist) => (
                  <PlaylistCard key={playlist.id} {...playlist} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p>This user hasn't created any public playlists yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
