"use client"

import { useState, useEffect } from "react"
import { Search, TrendingUp, Loader2, Music, ListMusic } from "lucide-react"
import { PlaylistCard } from "@/components/playlist-card"
import { useAuth } from "@/context/AuthContext"
import { usePlayer } from "@/context/PlayerContext" // Import usePlayer
import { getDiscoverPlaylists, searchTracks, searchUsers, searchPlaylists } from "@/lib/api"
import { toast } from "@/components/ui/use-toast"
import { useDebounce } from "@/hooks/use-debounce"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

// --- TYPE DEFINITIONS ---
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

// Use a flexible interface that matches both API response and PlayerContext needs roughly
interface Track {
  track_id: number;
  title: string;
  artist_name: string;
  genre_toplevel: string | null; // Added to match PlayerContext
  audio_url?: string; // Added to match PlayerContext
  duration: number; // Added to match PlayerContext
  album_art_url?: string | null;
}

interface User {
  id: number;
  username: string;
  email: string;
}

interface SearchResults {
  tracks: Track[];
  playlists: Playlist[];
  users: User[];
}

// --- DUMMY RESULT CARDS ---
const UserCard = ({ user }: { user: User }) => (
  <Link href={`/user/${user.username}`} className="flex items-center gap-4 p-3 rounded-lg bg-surface hover:bg-surface-elevated border border-border transition-colors">
    <Avatar>
      <AvatarImage src={`/profiles/Default.png`} />
      <AvatarFallback>{user.username.substring(0, 2).toUpperCase()}</AvatarFallback>
    </Avatar>
    <div>
      <p className="font-semibold">{user.username}</p>
      <p className="text-sm text-muted-foreground">{user.email}</p>
    </div>
  </Link>
);

// Updated TrackCard to be clickable
const TrackCard = ({ track, onClick }: { track: Track, onClick: () => void }) => (
    <div 
      onClick={onClick}
      className="flex items-center gap-4 p-3 rounded-lg bg-surface hover:bg-surface-elevated border border-border transition-colors cursor-pointer group"
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
        <div>
            <p className="font-semibold line-clamp-1">{track.title}</p>
            <p className="text-sm text-muted-foreground">{track.artist_name}</p>
        </div>
    </div>
);


export default function DiscoverPage() {
  const { token } = useAuth();
  const { playPlaylist } = usePlayer(); // Use the player context
  
  // State for discover playlists
  const [discoverPlaylists, setDiscoverPlaylists] = useState<Playlist[]>([]);
  const [discoverLoading, setDiscoverLoading] = useState(true);
  const [discoverError, setDiscoverError] = useState<string | null>(null);

  // State for search
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const [searchResults, setSearchResults] = useState<SearchResults>({ tracks: [], playlists: [], users: [] });
  const [searchLoading, setSearchLoading] = useState(false);

  // Fetch initial discover playlists
  useEffect(() => {
    if (token) {
      const fetchDiscoverPlaylists = async () => {
        setDiscoverLoading(true);
        setDiscoverError(null);
        const result = await getDiscoverPlaylists(token);
        if (result.success) {
          setDiscoverPlaylists(result.data);
        } else {
          setDiscoverError(result.error || "Failed to load playlists.");
          toast({
            title: "Error",
            description: result.error || "Failed to load playlists for discovery.",
            variant: "destructive",
          });
        }
        setDiscoverLoading(false);
      };
      fetchDiscoverPlaylists();
    } else {
      setDiscoverLoading(false);
      setDiscoverError("You must be logged in to discover playlists.");
    }
  }, [token]);

  // Effect for handling search
  useEffect(() => {
    if (!token || !debouncedSearchQuery) {
      setSearchResults({ tracks: [], playlists: [], users: [] });
      return;
    }

    const performSearch = async () => {
      setSearchLoading(true);
      const [tracksResult, playlistsResult, usersResult] = await Promise.all([
        searchTracks(debouncedSearchQuery, token),
        searchPlaylists(debouncedSearchQuery, token),
        searchUsers(debouncedSearchQuery, token),
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

  const totalResults = searchResults.tracks.length + searchResults.playlists.length + searchResults.users.length;

  return (
    <div className="min-h-screen bg-background pt-24 pb-32 md:pb-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-3 text-balance">Discover</h1>
          <p className="text-lg text-muted-foreground text-pretty">
            Find new tracks, playlists, and people
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-12">
          <div className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search for tracks, playlists, or users..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-surface border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
          </div>
        </div>

        {/* Conditional Content: Search Results or Discover Feed */}
        {debouncedSearchQuery ? (
          // Search Results View
          <div className="space-y-8">
            <h2 className="text-3xl font-bold">Search Results ({searchLoading ? <Loader2 className="inline h-6 w-6 animate-spin" /> : totalResults})</h2>
            <Tabs defaultValue="all">
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="tracks">Tracks ({searchResults.tracks.length})</TabsTrigger>
                <TabsTrigger value="playlists">Playlists ({searchResults.playlists.length})</TabsTrigger>
                <TabsTrigger value="users">Users ({searchResults.users.length})</TabsTrigger>
              </TabsList>
              
              <TabsContent value="all" className="mt-6">
                {searchLoading && <div className="flex justify-center py-12"><Loader2 className="h-12 w-12 animate-spin text-primary" /></div>}
                {!searchLoading && totalResults === 0 && <p>No results found for "{debouncedSearchQuery}".</p>}
                
                {searchResults.tracks.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold">Tracks</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {searchResults.tracks.map((track, index) => (
                        <TrackCard 
                            key={track.track_id} 
                            track={track} 
                            onClick={() => handlePlayTrack(index)}
                        />
                      ))}
                    </div>
                  </div>
                )}
                {searchResults.playlists.length > 0 && (
                  <div className="space-y-4 mt-8">
                    <h3 className="text-xl font-semibold">Playlists</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                      {searchResults.playlists.map(playlist => <PlaylistCard key={playlist.id} playlist={playlist} />)}
                    </div>
                  </div>
                )}
                {searchResults.users.length > 0 && (
                  <div className="space-y-4 mt-8">
                    <h3 className="text-xl font-semibold">Users</h3>
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
          // Discover Feed View
          <div>
            {discoverLoading ? (
              <div className="flex justify-center items-center py-24">
                <Loader2 className="h-16 w-16 animate-spin text-primary" />
              </div>
            ) : discoverError ? (
              <div className="text-center py-24">
                <p className="text-destructive">{discoverError}</p>
              </div>
            ) : (
              <div>
                <div className="flex items-center gap-2 mb-6">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  <h2 className="text-2xl font-bold">Recently Added</h2>
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
                    <p className="text-muted-foreground">No public playlists found.</p>
                    <p className="text-sm text-muted-foreground mt-1">Be the first to create one!</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}