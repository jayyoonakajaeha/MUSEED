"use client"

import { useState, useEffect } from "react"
import { Search, TrendingUp, Loader2, Music, ListMusic, Sparkles, Plus } from "lucide-react"
import { PlaylistCard } from "@/components/playlist-card"
import { useAuth } from "@/context/AuthContext"
import { usePlayer } from "@/context/PlayerContext"
import { getDiscoverPlaylists, searchTracks, searchUsers, searchPlaylists, getRecommendedUsers, getTrendingPlaylists } from "@/lib/api"
import { toast } from "@/components/ui/use-toast"
import { useDebounce } from "@/hooks/use-debounce"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { useLanguage } from "@/context/LanguageContext"

// --- 타입 정의 ---
interface Playlist {
  id: number;
  name: string;
  owner: { id: number; username: string; };
  tracks: any[];
  is_public: boolean;
  likes_count: number;
  liked_by_user: boolean;
  coverImage?: string;
}

interface Track {
  track_id: number;
  title: string;
  artist_name: string;
  genre_toplevel: string | null;
  audio_url?: string;
  duration: number;
  album_art_url?: string | null;
}

interface User {
  id: number;
  username: string;
  email: string;
  nickname?: string;
  profile_image_key?: string;
}

interface RecommendedUser extends User {
  similarity: number;
}

interface SearchResults {
  tracks: Track[];
  playlists: Playlist[];
  users: User[];
}

// --- 더미 결과 카드 ---
const UserCard = ({ user }: { user: User }) => (
  <Link href={`/user/${user.username}`} className="flex items-center gap-4 p-3 rounded-lg bg-surface hover:bg-surface-elevated border border-border transition-colors">
    <Avatar>
      <AvatarImage src={`/profiles/${user.profile_image_key || 'Default'}.png`} />
      <AvatarFallback>{user.username.substring(0, 2).toUpperCase()}</AvatarFallback>
    </Avatar>
    <div>
      <p className="font-semibold">{user.username}</p>
      <p className="text-sm text-muted-foreground">{user.email}</p>
    </div>
  </Link>
);

const RecommendedUserCard = ({ user, t }: { user: RecommendedUser, t: any }) => (
  <Link href={`/user/${user.username}`} className="flex items-center gap-4 p-3 rounded-lg bg-surface hover:bg-surface-elevated border border-border transition-colors group active:scale-[0.98]">
    <Avatar>
      <AvatarImage src={`/profiles/${user.profile_image_key || 'Default'}.png`} />
      <AvatarFallback>{user.username.substring(0, 2).toUpperCase()}</AvatarFallback>
    </Avatar>
    <div className="flex-1 min-w-0">
      <div className="flex items-center justify-between">
        <p className="font-semibold truncate">{user.nickname}</p>
        <Badge variant="secondary" className="text-xs bg-primary/10 text-primary ml-2 whitespace-nowrap">
          {Math.round(user.similarity * 100)}% {t.discover.match}
        </Badge>
      </div>
      <p className="text-xs text-muted-foreground truncate">@{user.username}</p>
    </div>
  </Link>
);

const TrackCard = ({ track, onClick, onCreate, t }: { track: Track, onClick: () => void, onCreate: () => void, t: any }) => (
  <div
    onClick={onClick}
    className="flex items-center gap-4 p-3 rounded-lg bg-surface hover:bg-surface-elevated border border-border transition-colors cursor-pointer group relative"
  >
    <div className="relative">
      <Avatar>
        <AvatarImage src={track.album_art_url || '/dark-purple-music-waves.jpg'} />
        <AvatarFallback><Music className="h-5 w-5" /></AvatarFallback>
      </Avatar>
      <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded-full">
        <Music className="h-4 w-4 text-white" />
      </div>
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-semibold line-clamp-1">{track.title}</p>
      <div className="flex items-center gap-2">
        <p className="text-sm text-muted-foreground truncate">{track.artist_name}</p>
        {track.genre_toplevel && (
          <Badge variant="secondary" className="text-[10px] px-1.5 py-0 h-5 font-normal">
            {track.genre_toplevel}
          </Badge>
        )}
      </div>
    </div>

    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
      <Button
        variant="ghost"
        size="sm"
        onClick={(e) => {
          e.stopPropagation();
          onCreate();
        }}
      >
        <Plus className="h-4 w-4 mr-1" />
        {t.common.create}
      </Button>
    </div>
  </div>
);


export default function DiscoverPage() {
  const router = useRouter();
  const { token } = useAuth();
  const { playPlaylist } = usePlayer();
  const { t } = useLanguage();

  // 디스커버 상태
  const [discoverPlaylists, setDiscoverPlaylists] = useState<Playlist[]>([]);
  const [trendingPlaylists, setTrendingPlaylists] = useState<Playlist[]>([]);
  const [recommendedUsers, setRecommendedUsers] = useState<RecommendedUser[]>([]);
  const [discoverLoading, setDiscoverLoading] = useState(true);
  const [discoverError, setDiscoverError] = useState<string | null>(null);

  // 검색 상태
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const [searchResults, setSearchResults] = useState<SearchResults>({ tracks: [], playlists: [], users: [] });
  const [searchLoading, setSearchLoading] = useState(false);

  // 초기 디스커버 데이터 조회
  useEffect(() => {
    const fetchData = async () => {
      setDiscoverLoading(true);
      setDiscoverError(null);

      // 인증 상태 기반 조회 대상 결정
      const promises = [
        getDiscoverPlaylists(token || ""),
        getTrendingPlaylists(token || "")
      ];

      if (token) {
        promises.push(getRecommendedUsers(token));
      }

      const results = await Promise.all(promises);
      const playlistResult = results[0];
      const trendingResult = results[1];
      const usersResult = token ? results[2] : { success: true, data: [] }; // 게스트의 경우 기본값 빈 배열

      if (playlistResult.success) {
        setDiscoverPlaylists(playlistResult.data);
      } else {
        setDiscoverError(playlistResult.error || "Failed to load playlists.");
      }

      if (trendingResult.success) {
        setTrendingPlaylists(trendingResult.data);
      }

      if (usersResult.success) {
        setRecommendedUsers(usersResult.data);
      }

      setDiscoverLoading(false);
    };
    fetchData();
  }, [token]);

  // 검색 처리 이펙트
  useEffect(() => {
    if (!debouncedSearchQuery || debouncedSearchQuery.length < 2) {
      setSearchResults({ tracks: [], playlists: [], users: [] });
      return;
    }

    const performSearch = async () => {
      setSearchLoading(true);
      const safeToken = token || "";
      const [tracksResult, playlistsResult, usersResult] = await Promise.all([
        searchTracks(debouncedSearchQuery, safeToken),
        searchPlaylists(debouncedSearchQuery, safeToken),
        searchUsers(debouncedSearchQuery, safeToken),
      ]);

      setSearchResults({
        tracks: tracksResult.success ? tracksResult.data : [],
        playlists: playlistsResult.success ? playlistsResult.data : [],
        users: usersResult.success ? usersResult.data : [],
      });
      setSearchLoading(false);
    };

    performSearch();
  }, [debouncedSearchQuery, token]);

  const handlePlayTrack = (startIndex: number) => {
    if (searchResults.tracks.length > 0) {
      playPlaylist(searchResults.tracks, startIndex);
    }
  };

  const handleCreateFromTrack = (trackId: number) => {
    router.push(`/create?seedTrack=${trackId}`);
  };

  const totalResults = searchResults.tracks.length + searchResults.playlists.length + searchResults.users.length;

  return (
    <div className="min-h-screen bg-background pt-24 pb-32 md:pb-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-3 text-balance">{t.discover.title}</h1>
          <p className="text-lg text-muted-foreground text-pretty">
            {t.discover.subtitle}
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-12">
          <div className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <input
              type="text"
              placeholder={t.discover.searchPlaceholder}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-surface border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
          </div>
        </div>

        {/* Conditional Content: Search Results or Discover Feed */}
        {debouncedSearchQuery ? (
          // 검색 결과 뷰
          <div className="space-y-8">
            <h2 className="text-3xl font-bold">{t.discover.searchResults} ({searchLoading ? <Loader2 className="inline h-6 w-6 animate-spin" /> : totalResults})</h2>
            <Tabs defaultValue="all">
              <TabsList>
                <TabsTrigger value="all">{t.discover.all}</TabsTrigger>
                <TabsTrigger value="tracks">{t.discover.tracks} ({searchResults.tracks.length})</TabsTrigger>
                <TabsTrigger value="playlists">{t.discover.playlists} ({searchResults.playlists.length})</TabsTrigger>
                <TabsTrigger value="users">{t.discover.users} ({searchResults.users.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="mt-6">
                {searchLoading && <div className="flex justify-center py-12"><Loader2 className="h-12 w-12 animate-spin text-primary" /></div>}
                {!searchLoading && totalResults === 0 && <p>No results found for "{debouncedSearchQuery}".</p>}

                {searchResults.tracks.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold">{t.discover.tracks}</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {searchResults.tracks.map((track, index) => (
                        <TrackCard
                          key={track.track_id}
                          track={track}
                          onClick={() => handlePlayTrack(index)}
                          onCreate={() => handleCreateFromTrack(track.track_id)}
                          t={t}
                        />
                      ))}
                    </div>
                  </div>
                )}
                {searchResults.playlists.length > 0 && (
                  <div className="space-y-4 mt-8">
                    <h3 className="text-xl font-semibold">{t.discover.playlists}</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                      {searchResults.playlists.map(playlist => <PlaylistCard key={playlist.id} playlist={playlist} />)}
                    </div>
                  </div>
                )}
                {searchResults.users.length > 0 && (
                  <div className="space-y-4 mt-8">
                    <h3 className="text-xl font-semibold">{t.discover.users}</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {searchResults.users.map(user => <UserCard key={user.id} user={user} />)}
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="tracks" className="mt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {searchResults.tracks.map((track, index) => (
                    <TrackCard
                      key={track.track_id}
                      track={track}
                      onClick={() => handlePlayTrack(index)}
                      onCreate={() => handleCreateFromTrack(track.track_id)}
                      t={t}
                    />
                  ))}
                </div>
              </TabsContent>
              <TabsContent value="playlists" className="mt-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {searchResults.playlists.map(playlist => <PlaylistCard key={playlist.id} playlist={playlist} />)}
                </div>
              </TabsContent>
              <TabsContent value="users" className="mt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {searchResults.users.map(user => <UserCard key={user.id} user={user} />)}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        ) : (
          // 디스커버 피드 뷰
          <div className="space-y-12">
            {discoverLoading ? (
              <div className="flex justify-center items-center py-24">
                <Loader2 className="h-16 w-16 animate-spin text-primary" />
              </div>
            ) : discoverError ? (
              <div className="text-center py-24">
                <p className="text-destructive">{discoverError}</p>
              </div>
            ) : (
              <>
                {/* Recommended Users Section */}
                {/* 추천 유저 섹션 */}
                {recommendedUsers.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-6">
                      <Sparkles className="h-5 w-5 text-primary" />
                      <h2 className="text-2xl font-bold">{t.discover.recommended}</h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {recommendedUsers.map((user) => (
                        <RecommendedUserCard key={user.id} user={user} t={t} />
                      ))}
                    </div>
                  </div>
                )}

                {/* 트렌딩 플레이리스트 섹션 */}
                {trendingPlaylists.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-6">
                      <TrendingUp className="h-5 w-5 text-primary" />
                      <h2 className="text-2xl font-bold">{t.discover.trending}</h2>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                      {trendingPlaylists.map((playlist) => (
                        <PlaylistCard key={playlist.id} playlist={playlist} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Recently Added Playlists Section */}
                <div>
                  <div className="flex items-center gap-2 mb-6">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    <h2 className="text-2xl font-bold">{t.discover.recentlyAdded}</h2>
                  </div>
                  {discoverPlaylists.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                      {discoverPlaylists.map((playlist) => (
                        <PlaylistCard key={playlist.id} playlist={playlist} />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 bg-surface rounded-xl border border-border">
                      <ListMusic className="h-12 w-12 text-muted-foreground/50 mx-auto mb-3" />
                      <p className="text-muted-foreground">{t.discover.noPlaylists}</p>
                      <p className="text-sm text-muted-foreground mt-1">{t.discover.beFirst}</p>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}