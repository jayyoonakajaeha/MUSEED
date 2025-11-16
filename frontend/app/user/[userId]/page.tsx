"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { getUserProfile, getUserCreatedPlaylists, getUserLikedPlaylists, followUser, unfollowUser, deletePlaylist, updatePlaylist, getUserFollowers, getUserFollowing, getUserStats, getUserGenreStats } from "@/lib/api"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PlaylistCard } from "@/components/playlist-card"
import { UserListDialog } from "@/components/user-list-dialog"
import { GenreChart } from "@/components/genre-chart"
import { Loader2, UserPlus, UserCheck, Edit, Music, Users, Heart, PieChart } from "lucide-react"
import Link from "next/link"
import { toast } from "@/components/ui/use-toast"
import { cn } from "@/lib/utils"

// Define interfaces for the data structures
interface UserProfile {
  id: number;
  username: string;
  email: string;
  playlists: any[];
  liked_playlists: any[];
  followers_count: number;
  following_count: number;
  is_followed_by_current_user: boolean;
}

interface Playlist {
  id: number;
  name: string;
  owner: {
    id: number;
    username: string;
  };
  tracks: any[];
  is_public: boolean;
  likes_count: number;
  liked_by_user: boolean;
}

interface SimpleUser {
  id: number;
  username: string;
  profile_image_key: string;
}

interface GenreStat {
  genre: string;
  count: number;
}

const genreColors: { [key: string]: string } = {
  "Electronic": "#8884d8",
  "Rock": "#82ca9d",
  "Pop": "#ffc658",
  "Hip-Hop": "#ff8042",
  "Experimental": "#00C49F",
  "Folk": "#0088FE",
  "Jazz": "#FFBB28",
  "Instrumental": "#FF8042",
  "Classical": "#00C49F",
  "International": "#FFBB28",
  "Country": "#0088FE",
  "Old-Time / Historic": "#82ca9d",
  "Spoken": "#8884d8",
  "Blues": "#ffc658",
  "Easy Listening": "#00C49F",
  "Soul-RnB": "#FF8042",
};

export default function UserProfilePage() {
  const { userId } = useParams()
  const { user: currentUser, token } = useAuth()
  const router = useRouter()

  const [profileUser, setProfileUser] = useState<UserProfile | null>(null)
  const [createdPlaylists, setCreatedPlaylists] = useState<Playlist[]>([])
  const [likedPlaylists, setLikedPlaylists] = useState<Playlist[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [topGenre, setTopGenre] = useState<string | null>(null)
  const [genreStats, setGenreStats] = useState<GenreStat[]>([])
  
  // State for the user list dialog
  const [isListOpen, setIsListOpen] = useState(false)
  const [listTitle, setListTitle] = useState("")
  const [userList, setUserList] = useState<SimpleUser[]>([])
  const [listLoading, setListLoading] = useState(false)

  const username = Array.isArray(userId) ? userId[0] : userId

  useEffect(() => {
    if (!username) return

    const fetchAllData = async () => {
      setLoading(true)
      setError(null)

      // Fetch all data in parallel
      const [profileResult, statsResult, genreStatsResult, createdResult, likedResult] = await Promise.all([
        getUserProfile(username, token),
        getUserStats(username),
        token ? getUserGenreStats(username, token) : Promise.resolve({ success: false }),
        token ? getUserCreatedPlaylists(username, token) : Promise.resolve({ success: false }),
        token ? getUserLikedPlaylists(username, token) : Promise.resolve({ success: false }),
      ]);

      if (profileResult.success) {
        setProfileUser(profileResult.data)
      } else {
        setError(profileResult.error || "Failed to load user profile.")
        toast({
          title: "Error",
          description: `Could not load profile for ${username}.`,
          variant: "destructive",
        })
        setLoading(false)
        return;
      }

      if (statsResult.success) {
        setTopGenre(statsResult.data.top_genre)
      }
      
      if (genreStatsResult.success) {
        setGenreStats(genreStatsResult.data)
      }

      if (createdResult.success) {
        setCreatedPlaylists(createdResult.data)
      }

      if (likedResult.success) {
        setLikedPlaylists(likedResult.data)
      }

      setLoading(false)
    }

    fetchAllData()
  }, [username, token])

  const handleFollow = async () => {
    if (!token || !profileUser) return;

    const originalUser = profileUser;
    setProfileUser({
      ...profileUser,
      is_followed_by_current_user: true,
      followers_count: profileUser.followers_count + 1,
    });

    const result = await followUser(username, token);
    if (!result.success) {
      setProfileUser(originalUser);
      toast({
        title: "Error",
        description: `Could not follow ${username}.`,
        variant: "destructive",
      });
    } else {
        toast({
            title: "Success",
            description: `You are now following ${username}.`,
        });
    }
  };

  const handleUnfollow = async () => {
    if (!token || !profileUser) return;

    const originalUser = profileUser;
    setProfileUser({
      ...profileUser,
      is_followed_by_current_user: false,
      followers_count: profileUser.followers_count - 1,
    });

    const result = await unfollowUser(username, token);
    if (!result.success) {
      setProfileUser(originalUser);
      toast({
        title: "Error",
        description: `Could not unfollow ${username}.`,
        variant: "destructive",
      });
    } else {
        toast({
            title: "Success",
            description: `You have unfollowed ${username}.`,
        });
    }
  };

  const handleDeletePlaylist = async (playlistId: number) => {
    if (!token) return;
    if (window.confirm("Are you sure you want to delete this playlist?")) {
      const result = await deletePlaylist(playlistId, token);
      if (result.success) {
        setCreatedPlaylists(prev => prev.filter(p => p.id !== playlistId));
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
      setCreatedPlaylists(prev => prev.map(p => p.id === playlistId ? { ...p, is_public: isPublic } : p));
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

  const handleShowList = async (listType: 'followers' | 'following') => {
    if (!token) {
      toast({ title: "Error", description: "You must be logged in to view this.", variant: "destructive" });
      return;
    }
    setListLoading(true);
    setIsListOpen(true);
    setListTitle(listType === 'followers' ? "Followers" : "Following");

    const result = listType === 'followers' 
      ? await getUserFollowers(username, token)
      : await getUserFollowing(username, token);

    if (result.success) {
      setUserList(result.data);
    } else {
      toast({ title: "Error", description: `Could not load ${listType}.`, variant: "destructive" });
      setIsListOpen(false);
    }
    setListLoading(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !profileUser) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen text-center">
        <h2 className="text-2xl font-bold mb-2">User Not Found</h2>
        <p className="text-muted-foreground mb-4">{error || `The profile for "${username}" could not be loaded.`}</p>
        <Button onClick={() => router.push("/discover")}>Go to Discover</Button>
      </div>
    )
  }

  const isOwnProfile = currentUser?.username === profileUser.username
  
  const getProfileImage = () => {
    if (topGenre && genreColors[topGenre]) {
      return `/profiles/${topGenre}.png`;
    }
    if (createdPlaylists.length > 0) {
      return `/profiles/Default_Headphone.png`;
    }
    return `/profiles/Default.png`;
  }
  const profileImage = getProfileImage();

  const chartData = genreStats.map(stat => ({
    name: stat.genre,
    value: stat.count,
    color: genreColors[stat.genre] || '#cccccc' // Fallback color
  }));

  return (
    <>
      <main className="min-h-screen py-24">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="space-y-8">
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
              <Avatar className="h-32 w-32 border-4 border-primary/20">
                <AvatarImage src={profileImage} alt={profileUser.username} className="object-contain" />
                <AvatarFallback className="text-4xl bg-primary/10 text-primary">
                  {profileUser.username.substring(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 space-y-4">
                <div>
                  <h1 className="text-4xl font-bold">{profileUser.username}</h1>
                  <p className="text-muted-foreground">@{profileUser.username}</p>
                </div>

                <div className="flex flex-wrap gap-6">
                  <div className="flex items-center gap-2">
                    <Music className="h-5 w-5 text-primary" />
                    <span className="font-semibold">{createdPlaylists.length}</span>
                    <span className="text-muted-foreground">Playlists</span>
                  </div>
                  <button onClick={() => handleShowList('followers')} className="flex items-center gap-2 hover:bg-muted p-2 rounded-md transition-colors">
                    <Users className="h-5 w-5 text-primary" />
                    <span className="font-semibold">{profileUser.followers_count}</span>
                    <span className="text-muted-foreground">Followers</span>
                  </button>
                  <button onClick={() => handleShowList('following')} className="flex items-center gap-2 hover:bg-muted p-2 rounded-md transition-colors">
                    <Heart className="h-5 w-5 text-primary" />
                    <span className="font-semibold">{profileUser.following_count}</span>
                    <span className="text-muted-foreground">Following</span>
                  </button>
                </div>

                {isOwnProfile ? (
                  <Button asChild variant="outline" className="gap-2">
                    <Link href="/profile/edit">
                      <Edit className="h-4 w-4" />
                      Edit Profile
                    </Link>
                  </Button>
                ) : (
                  <Button onClick={profileUser.is_followed_by_current_user ? handleUnfollow : handleFollow} variant={profileUser.is_followed_by_current_user ? "secondary" : "default"} className="gap-2">
                    {profileUser.is_followed_by_current_user ? (
                      <>
                        <UserCheck className="h-4 w-4" />
                        Following
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

            <Tabs defaultValue="my-playlists" className="w-full pt-8">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger 
                  value="my-playlists" 
                  className={cn(
                    "data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
                    "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
                  )}
                >
                  My Playlists ({createdPlaylists.length})
                </TabsTrigger>
                <TabsTrigger 
                  value="liked-playlists" 
                  className={cn(
                    "data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
                    "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
                  )}
                >
                  Liked Playlists ({likedPlaylists.length})
                </TabsTrigger>
              </TabsList>
              <TabsContent value="my-playlists" className="mt-6">
                  {createdPlaylists.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                      {createdPlaylists.map((playlist) => (
                        <PlaylistCard 
                          key={playlist.id} 
                          playlist={playlist} 
                          isOwner={isOwnProfile}
                          onDelete={() => handleDeletePlaylist(playlist.id)}
                          onTogglePublic={() => handleTogglePublic(playlist.id, !playlist.is_public)}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <p>This user hasn't created any playlists yet.</p>
                    </div>
                  )}
              </TabsContent>
              <TabsContent value="liked-playlists" className="mt-6">
                  {likedPlaylists.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                      {likedPlaylists.map((playlist) => (
                        <PlaylistCard key={playlist.id} playlist={playlist} />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <p>This user hasn't liked any playlists yet.</p>
                    </div>
                  )}
              </TabsContent>
            </Tabs>

            {chartData.length > 0 && (
              <div className="space-y-4 pt-8">
                <div className="flex items-center gap-2">
                  <PieChart className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-bold">Top Genres</h2>
                </div>
                <div className="p-4 bg-card border border-primary rounded-lg">
                  <GenreChart data={chartData} />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
      <UserListDialog 
        isOpen={isListOpen}
        onClose={() => setIsListOpen(false)}
        title={listTitle}
        users={userList}
      />
    </>
  )
}