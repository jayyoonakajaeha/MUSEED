"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { getUserProfile, getUserCreatedPlaylists, getUserLikedPlaylists, followUser, unfollowUser, deletePlaylist, updatePlaylist, getUserFollowers, getUserFollowing, getUserStats, getUserGenreStats } from "@/lib/api"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PlaylistCard } from "@/components/playlist-card"
import { UserListDialog } from "@/components/user-list-dialog"
import { GenreChart } from "@/components/genre-chart"
import { Loader2, UserPlus, UserCheck, Edit, Music, Users, Heart, PieChart, Award, User, LogOut } from "lucide-react" // Added User icon
import Link from "next/link"
import { toast } from "@/components/ui/use-toast"
import { cn } from "@/lib/utils"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useLanguage } from "@/context/LanguageContext"

// 인터페이스 정의
interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
}

interface UserProfile {
  id: number;
  username: string;
  nickname: string;
  email: string;
  playlists: any[];
  liked_playlists: any[];
  followers_count: number;
  following_count: number;
  is_followed_by_current_user: boolean;
  achievements: Achievement[];
  profile_image_key?: string; // Added
}

interface Playlist {
  id: number;
  name: string;
  owner: {
    id: number;
    username: string;
    nickname?: string;
  };
  tracks: any[];
  is_public: boolean;
  likes_count: number;
  liked_by_user: boolean;
}

interface SimpleUser {
  id: number;
  username: string;
  nickname: string;
  profile_image_key: string;
}

interface GenreStat {
  genre: string;
  count: number;
}

const genreColors: { [key: string]: string } = {
  "Electronic": "#6F98FC",
  "Rock": "#F46F6F",
  "Pop": "#43C59E",
  "Hip-Hop": "#FFD159",
  "Experimental": "#B665F8",
  "Folk": "#F8931F",
  "Jazz": "#5FDBE9",
  "Instrumental": "#DD7DFF",
  "Classical": "#C7F960",
  "International": "#FC896F",
  "Country": "#6155A6",
  "Old-Time / Historic": "#F9CC6C",
  "Spoken": "#7C66FE",
  "Blues": "#D65F8C",
  "Easy Listening": "#76B041",
  "Soul-RnB": "#FD9644",
};

// 문자열 기반 일관된 색상 생성
const stringToColor = (str: string) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  let color = '#';
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xFF;
    color += ('00' + value.toString(16)).substr(-2);
  }
  return color;
}

export default function UserProfilePage() {
  const { userId } = useParams()
  const { user: currentUser, token, isLoading: authLoading, logout, refreshProfile } = useAuth()
  const router = useRouter()
  const { t } = useLanguage()

  const [profileUser, setProfileUser] = useState<UserProfile | null>(null)
  const [createdPlaylists, setCreatedPlaylists] = useState<Playlist[]>([])
  const [likedPlaylists, setLikedPlaylists] = useState<Playlist[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [topGenre, setTopGenre] = useState<string | null>(null)
  const [genreStats, setGenreStats] = useState<GenreStat[]>([])

  const [isListOpen, setIsListOpen] = useState(false)
  const [listTitle, setListTitle] = useState("")
  const [userList, setUserList] = useState<SimpleUser[]>([])
  const [listLoading, setListLoading] = useState(false)

  const username = Array.isArray(userId) ? userId[0] : userId

  useEffect(() => {
    if (!username || authLoading) return

    const fetchAllData = async () => {
      setLoading(true)
      setError(null)

      const [profileResult, statsResult, genreStatsResult, createdResult, likedResult] = await Promise.all([
        getUserProfile(username, token),
        getUserStats(username),
        getUserGenreStats(username, token || null),
        getUserCreatedPlaylists(username, token || null),
        getUserLikedPlaylists(username, token || null),
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
  }, [username, token, authLoading])

  const handleFollow = async () => {
    if (!token) {
      toast({
        title: "Login Required",
        description: "You must be logged in to follow users.",
        variant: "destructive",
      });
      return;
    }
    if (!profileUser) return; // Ensure profileUser exists

    const originalUser = profileUser;
    setProfileUser({
      ...profileUser,
      is_followed_by_current_user: true,
      followers_count: profileUser.followers_count + 1,
    });

    const result = await followUser(username || "", token);
    if (!result.success) {
      setProfileUser(originalUser);
      toast({
        title: t.toast.error,
        description: `Could not follow ${profileUser.nickname}.`,
        variant: "destructive",
      });
    } else {
      refreshProfile(); // Check for "Social Butterfly" achievement
      toast({
        title: t.toast.success,
        description: t.toast.followedUser.replace("{nickname}", profileUser.nickname),
      });
    }
  };

  const handleUnfollow = async () => {
    if (!token) {
      toast({
        title: "Login Required",
        description: "You must be logged in to unfollow users.",
        variant: "destructive",
      });
      return;
    }
    if (!profileUser) return; // Ensure profileUser exists

    const originalUser = profileUser;
    setProfileUser({
      ...profileUser,
      is_followed_by_current_user: false,
      followers_count: profileUser.followers_count - 1,
    });

    const result = await unfollowUser(username || "", token);
    if (!result.success) {
      setProfileUser(originalUser);
      toast({
        title: t.toast.error,
        description: `Could not unfollow ${profileUser.nickname}.`,
        variant: "destructive",
      });
    } else {
      refreshProfile();
      toast({
        title: t.toast.success,
        description: t.toast.unfollowedUser.replace("{nickname}", profileUser.nickname),
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
      ? await getUserFollowers(username || "", token)
      : await getUserFollowing(username || "", token);

    if (result.success) {
      setUserList(result.data);
    } else {
      toast({ title: "Error", description: `Could not load ${listType}.`, variant: "destructive" });
      setIsListOpen(false);
    }
    setListLoading(false);
  };

  if (loading || authLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !profileUser) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen text-center gap-4">
        <h2 className="text-2xl font-bold">User Not Found or Error Loading Profile</h2>
        <p className="text-muted-foreground">{error || `The profile for "${username}" could not be loaded.`}</p>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => { logout(); router.push("/login"); }}>
            Go to Login
          </Button>
          <Button onClick={() => router.push("/discover")}>
            Go to Discover
          </Button>
        </div>
      </div>
    )
  }

  const isOwnProfile = currentUser?.username === profileUser.username

  const getProfileImage = () => {
    if (profileUser?.profile_image_key) {
      return `/profiles/${profileUser.profile_image_key}.png`;
    }
    if (topGenre && genreColors[topGenre]) {
      return `/profiles/${topGenre}.png`;
    }
    if (profileUser?.playlists && profileUser.playlists.length > 0) {
      return `/profiles/Default_Headphone.png`;
    }
    return `/profiles/Default.png`;
  }
  const profileImage = getProfileImage();

  const chartData = genreStats.map(stat => ({
    name: stat.genre,
    value: stat.count,
    color: genreColors[stat.genre] || stringToColor(stat.genre)
  }));

  return (
    <>
      <main className="min-h-screen py-24">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="space-y-6">

            {/* 상단 섹션: 프로필 카드 (2/3) + 장르 차트 (1/3) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

              {/* 프로필 헤더 카드 */}
              <Card className="border border-primary lg:col-span-2 h-full">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <User className="h-5 w-5 text-primary" /> {/* 프로필용 User 아이콘 사용 */}
                    {t?.profile?.profile || "Profile"}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 h-full flex flex-col justify-center">
                  <div className="flex flex-col sm:flex-row items-start gap-8">
                    {/* 왼쪽 컬럼: 아바타 + 유저 정보 + 버튼 */}
                    <div className="flex flex-col items-center text-center sm:text-left sm:items-start gap-4 min-w-[160px]">
                      <Avatar className="h-32 w-32 border-4 border-primary/20">
                        <AvatarImage src={profileImage} alt={profileUser.nickname || profileUser.username} className="object-contain" />
                        <AvatarFallback className="text-4xl bg-primary/10 text-primary">
                          {profileUser.username.substring(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>

                      <div className="space-y-1 w-full">
                        <h1 className="text-2xl font-bold break-words">{profileUser.nickname}</h1>
                        <p className="text-muted-foreground text-sm break-all">@{profileUser.username}</p>
                      </div>

                      {isOwnProfile ? (
                        <div className="flex gap-2 w-full">
                          <Button asChild variant="outline" className="flex-1 gap-2">
                            <Link href="/profile/edit">
                              <Edit className="h-4 w-4" />
                              {t.profile.edit}
                            </Link>
                          </Button>
                          <Button onClick={logout} variant="outline" className="gap-2 text-destructive hover:text-destructive hover:bg-destructive/10">
                            <LogOut className="h-4 w-4" />
                            {t.nav.signOut}
                          </Button>
                        </div>
                      ) : (
                        <Button onClick={profileUser.is_followed_by_current_user ? handleUnfollow : handleFollow} variant={profileUser.is_followed_by_current_user ? "secondary" : "default"} className="w-full gap-2">
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

                    {/* 오른쪽 컬럼: 통계 + 업적 */}
                    <div className="flex-1 w-full flex flex-col gap-6 pt-2">
                      {/* 통계 - 균등 배치 */}
                      <div className="grid grid-cols-3 gap-4 text-center bg-surface-elevated rounded-lg p-4 border border-border">
                        <div className="flex flex-col items-center justify-center">
                          <Music className="h-5 w-5 text-primary mb-1" />
                          <span className="font-bold text-lg">{profileUser.playlists.length}</span>
                          <span className="text-xs text-muted-foreground">{t.profile.playlists}</span>
                        </div>
                        <button onClick={() => handleShowList('followers')} className="flex flex-col items-center justify-center hover:bg-muted rounded transition-colors p-1">
                          <Users className="h-5 w-5 text-primary mb-1" />
                          <span className="font-bold text-lg">{profileUser.followers_count}</span>
                          <span className="text-xs text-muted-foreground">{t.profile.followers}</span>
                        </button>
                        <button onClick={() => handleShowList('following')} className="flex flex-col items-center justify-center hover:bg-muted rounded transition-colors p-1">
                          <Heart className="h-5 w-5 text-primary mb-1" />
                          <span className="font-bold text-lg">{profileUser.following_count}</span>
                          <span className="text-xs text-muted-foreground">{t.profile.following}</span>
                        </button>
                      </div>

                      {/* Achievements */}
                      {profileUser.achievements && profileUser.achievements.length > 0 && (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
                            <Award className="h-4 w-4 text-primary" />
                            {t.profile.achievements}
                          </div>
                          <div className="flex flex-wrap gap-3">
                            <TooltipProvider>
                              {profileUser.achievements.map((achievement) => (
                                <Tooltip key={achievement.id}>
                                  <TooltipTrigger asChild>
                                    <div className="flex items-center justify-center w-12 h-12 bg-surface-elevated border border-border rounded-full text-2xl cursor-help hover:border-primary transition-colors shadow-sm">
                                      {achievement.icon}
                                    </div>
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p className="font-semibold">{(t.achievements as any)[achievement.id]?.name || achievement.name}</p>
                                    <p className="text-xs text-muted-foreground">{(t.achievements as any)[achievement.id]?.desc || achievement.description}</p>
                                  </TooltipContent>
                                </Tooltip>
                              ))}
                            </TooltipProvider>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 장르 차트 카드 (오른쪽) */}
              <Card className="border border-primary lg:col-span-1 h-full">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <PieChart className="h-5 w-5 text-primary" />
                    {t.profile.topGenres}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0 min-h-[250px] h-auto flex items-center justify-center">
                  {chartData.length > 0 ? (
                    <div className="w-full h-[350px]"> {/* 범례 표시 위해 높이 350px로 증가 */}
                      <GenreChart data={chartData} />
                    </div>
                  ) : (
                    <p className="text-muted-foreground text-sm">{t.profile.noData}</p>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Playlists Section */}
            <Tabs defaultValue="my-playlists" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger
                  value="my-playlists"
                  className={cn(
                    "data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
                    "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
                  )}
                >
                  {t.profile.myPlaylists} ({createdPlaylists.length})
                </TabsTrigger>
                <TabsTrigger
                  value="liked-playlists"
                  className={cn(
                    "data-[state=inactive]:hover:text-foreground data-[state=inactive]:hover:bg-foreground/5",
                    "data-[state=active]:!bg-primary data-[state=active]:!text-primary-foreground"
                  )}
                >
                  {t.profile.likedPlaylists} ({likedPlaylists.length})
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
                    <p>{t.profile.noCreated}</p>
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
                    <p>{t.profile.noLiked}</p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
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
