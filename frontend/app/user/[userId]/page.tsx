"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { PlaylistCard } from "@/components/playlist-card"
import { UserPlus, UserMinus, Music, Heart, Users, Loader2, Edit } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { getUserProfile, getUserStats, getUserCreatedPlaylists, getUserLikedPlaylists, deletePlaylist, updatePlaylist } from "@/lib/api"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "@/components/ui/use-toast"
import { cn } from "@/lib/utils"

// More accurate types to match backend
interface Playlist {
  id: number;
  name: string;
  owner_id: number;
  owner_username: string; // Added
  is_public: boolean;
  likes_count: number; // Added
  liked_by_user: boolean; // Added
  // Add other relevant playlist fields if needed
}

type UserProfile = {
  id: number;
  username: string;
  email: string;
  playlists: Playlist[]; // This will now represent created playlists
};

// Helper to format genre names into image file names
const getGenreImageName = (genre: string | null | undefined): string => {
    if (!genre) return "Default.png";
    // Replace spaces and slashes with underscores
    return `${genre.replace(/[\s/]/g, '_')}.png`;
}

export default function UserProfilePage() {
  const params = useParams()
  const userId = params.userId as string;
  const { user: currentUser, token } = useAuth()

  const [profileData, setProfileData] = useState<UserProfile | null>(null)
  const [topGenre, setTopGenre] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isFollowing, setIsFollowing] = useState(false) // Mocked for now
  const [activeTab, setActiveTab] = useState("my-playlists"); // New state for active tab
  const [userPlaylists, setUserPlaylists] = useState<Playlist[]>([]); // New state for user's created playlists
  const [likedPlaylists, setLikedPlaylists] = useState<Playlist[]>([]); // New state for user's liked playlists

  useEffect(() => {
    if (userId && token) {
      const fetchAllData = async () => {
        setLoading(true);
        setError(null);
  
        const [profileResult, statsResult, createdResult, likedResult] = await Promise.all([
          getUserProfile(userId, token),
          getUserStats(userId),
          getUserCreatedPlaylists(userId, token),
          getUserLikedPlaylists(userId, token),
        ]);
  
        if (profileResult.success) {
          setProfileData(profileResult.data);
        } else {
          setError(profileResult.error || "Failed to load profile.");
        }
  
        if (statsResult.success) {
          setTopGenre(statsResult.data.top_genre);
        }
  
        if (createdResult.success) {
          setUserPlaylists(createdResult.data);
        } else {
          toast({
            title: "Error",
            description: createdResult.error || "Failed to load user's playlists.",
            variant: "destructive",
          });
        }
  
        if (likedResult.success) {
          setLikedPlaylists(likedResult.data);
        } else {
          toast({
            title: "Error",
            description: likedResult.error || "Failed to load liked playlists.",
            variant: "destructive",
          });
        }
  
        setLoading(false);
      };
      fetchAllData();
    }
  }, [userId, token]);


  const handleFollowToggle = () => {
    setIsFollowing(!isFollowing)
    // Implement actual follow/unfollow logic here
    toast({
      title: "Feature Coming Soon",
      description: "Follow/Unfollow functionality is not yet implemented.",
    });
  }

  const handleDeletePlaylist = async (playlistId: number) => {
    if (!token) return;
    if (window.confirm("Are you sure you want to delete this playlist?")) {
      const result = await deletePlaylist(playlistId, token);
      if (result.success) {
        setUserPlaylists(prev => prev.filter(p => p.id !== playlistId));
        toast({
          title: "Success",
          description: "Playlist deleted successfully.",
        });
      } else {
        toast({
          title: "Error",
          description: result.error || "Failed to delete playlist.",
          variant: "destructive",
        });
      }
    }
  };

  const handleTogglePublic = async (playlistId: number, isPublic: boolean) => {
    if (!token) return;
    const result = await updatePlaylist(playlistId, { is_public: isPublic }, token);
    if (result.success) {
      setUserPlaylists(prev => prev.map(p => p.id === playlistId ? { ...p, is_public: isPublic } : p));
      toast({
        title: "Success",
        description: `Playlist set to ${isPublic ? 'public' : 'private'}.`,
      });
    } else {
      toast({
        title: "Error",
        description: result.error || "Failed to update playlist visibility.",
        variant: "destructive",
      });
    }
  };


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
  const profileImage = `/profiles/${getGenreImageName(topGenre)}`;
  
  // Mocked stats until backend provides them
  const stats = {
    playlists: userPlaylists.length, // Use actual count
    followers: 0,
    following: 0,
  };

  return (
    <main className="min-h-screen py-24">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Profile Header */}
        <div className="space-y-8">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <Avatar className="h-32 w-32 border-4 border-primary/20">
              <AvatarImage src={profileImage} alt={profileData.username} className="object-contain" />
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
                  <span className="font-semibold">{stats.playlists}</span>
                  <span className="text-muted-foreground">Playlists</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  <span className="font-semibold">{stats.followers}</span>
                  <span className="text-muted-foreground">Followers</span>
                </div>
                <div className="flex items-center gap-2">
                  <Heart className="h-5 w-5 text-primary" />
                  <span className="font-semibold">{stats.following}</span>
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

          {/* Playlist Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger 
                value="my-playlists"
                className={cn(
                  "gap-2 data-[state=inactive]:text-muted-foreground data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
                  "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
                )}
              >
                My Playlists ({userPlaylists.length})
              </TabsTrigger>
              <TabsTrigger 
                value="liked-playlists"
                className={cn(
                  "gap-2 data-[state=inactive]:text-muted-foreground data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
                  "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
                )}
              >
                Liked Playlists ({likedPlaylists.length})
              </TabsTrigger>
            </TabsList>
            <TabsContent value="my-playlists" className="mt-6">
              <div className="space-y-6">
                <h2 className="text-2xl font-bold">My Playlists</h2>
                {userPlaylists.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {userPlaylists.map((playlist) => (
                      playlist ? (
                        <PlaylistCard 
                          key={playlist.id} 
                          playlist={playlist} 
                          isOwner={isOwnProfile}
                          onDelete={handleDeletePlaylist}
                          onTogglePublic={handleTogglePublic}
                        />
                      ) : null
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <p>You haven't created any playlists yet.</p>
                  </div>
                )}
              </div>
            </TabsContent>
            <TabsContent value="liked-playlists" className="mt-6">
              <div className="space-y-6">
                <h2 className="text-2xl font-bold">Liked Playlists</h2>
                {likedPlaylists.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {likedPlaylists.map((playlist) => (
                      playlist ? <PlaylistCard key={playlist.id} playlist={playlist} /> : null
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <p>You haven't liked any playlists yet.</p>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </main>
  )
}