"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/context/AuthContext"
import { usePlayer } from "@/context/PlayerContext" // Import usePlayer
import { getPlaylist, deletePlaylist, updatePlaylist, likePlaylist, unlikePlaylist } from "@/lib/api"
import { useParams, useRouter } from "next/navigation"
// Remove AudioPlayer import
import { Heart, Share2, Save, Music2, Edit2, Check, Trash2, Lock, Globe, Plus } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { MoreVertical } from "lucide-react"
import Link from "next/link"
import { toast } from "@/components/ui/use-toast"

// Updated interfaces to match backend schema
interface Track {
  track_id: number;
  title: string;
  artist_name: string;
  genre_toplevel: string | null;
  audio_url?: string;
  album_art_url?: string | null;
  duration: number;
}

interface PlaylistOwner {
  id: number;
  username: string;
}

interface Playlist {
  id: number;
  name: string;
  owner_id: number;
  is_public: boolean;
  created_at: string;
  owner: PlaylistOwner;
  tracks: Track[];
  likes_count: number;
  liked_by_user: boolean;
}

const getAlbumArtUrl = (url: string | null | undefined): string => {
  if (url && (url.includes('.jpg') || url.includes('.png') || url.includes('.gif'))) {
    return url;
  }
  return '/dark-purple-music-waves.jpg';
}

export default function PlaylistPage() {
  const router = useRouter()
  const params = useParams()
  const { user, token } = useAuth()
  const { playPlaylist, currentTrack } = usePlayer() // Use global player context

  const [playlist, setPlaylist] = useState<Playlist | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [likedState, setLikedState] = useState(false)
  const [currentLikeCount, setCurrentLikeCount] = useState(0)
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  
  const playlistId = params.id as string;

  useEffect(() => {
    if (!playlistId || !token) return;

    const fetchPlaylist = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const result = await getPlaylist(playlistId, token)
        if (result.success) {
          setPlaylist(result.data)
          setLikedState(result.data.liked_by_user)
          setCurrentLikeCount(result.data.likes_count)
        } else {
          setError(result.error || "Failed to load playlist.")
        }
      } catch (err) {
        setError("An unexpected error occurred.")
      } finally {
        setIsLoading(false)
      }
    }

    fetchPlaylist()
  }, [playlistId, token])

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading playlist...</div>
  }

  if (error) {
    return <div className="min-h-screen flex items-center justify-center text-destructive">Error: {error}</div>
  }

  if (!playlist) {
    return <div className="min-h-screen flex items-center justify-center">Playlist not found.</div>
  }

  const isOwner = user?.id === playlist.owner_id
  
  // Handle track click to play from global player
  const handleTrackClick = (index: number) => {
      if (playlist && playlist.tracks.length > 0) {
          playPlaylist(playlist.tracks, index);
      }
  }

  const handleSaveTitle = async () => {
    if (!token || !playlist) return;
    const result = await updatePlaylist(playlist.id, { name: playlist.name }, token);
    if (result.success) {
      setPlaylist(result.data);
      toast({
        title: "Success",
        description: "Playlist title updated successfully.",
      });
    } else {
      toast({
        title: "Error",
        description: result.error || "Failed to update playlist title.",
        variant: "destructive",
      });
    }
    setIsEditingTitle(false)
  }

  const handleDelete = async () => {
    if (!token || !playlist) return;
    if (window.confirm("Are you sure you want to delete this playlist? This action cannot be undone.")) {
      const result = await deletePlaylist(playlist.id, token);
      if (result.success) {
        toast({
          title: "Success",
          description: "Playlist deleted successfully.",
        });
        router.push(`/user/${user?.username}`);
      } else {
        toast({
          title: "Error",
          description: result.error || "Failed to delete playlist.",
          variant: "destructive",
        });
      }
    }
  }

  const handleTogglePrivacy = async () => {
    if (!token || !playlist) return;
    const newPrivacyStatus = !playlist.is_public;
    const result = await updatePlaylist(playlist.id, { is_public: newPrivacyStatus }, token);
    if (result.success) {
      setPlaylist(result.data);
      toast({
        title: "Success",
        description: `Playlist set to ${newPrivacyStatus ? 'public' : 'private'}.`,
      });
    } else {
      toast({
        title: "Error",
        description: result.error || "Failed to update playlist privacy.",
        variant: "destructive",
      });
    }
  }

  const handleLike = async () => {
    if (!token || !playlist) {
      toast({
        title: "Login Required",
        description: "You must be logged in to like playlists.",
        variant: "destructive",
      });
      return;
    }

    if (likedState) {
      const result = await unlikePlaylist(playlist.id, token);
      if (result.success) {
        setLikedState(false);
        setCurrentLikeCount(prev => prev - 1);
      } else {
        toast({
          title: "Error",
          description: result.error || "Failed to unlike playlist.",
          variant: "destructive",
        });
      }
    } else {
      const result = await likePlaylist(playlist.id, token);
      if (result.success) {
        setLikedState(true);
        setCurrentLikeCount(prev => prev + 1);
      } else {
        toast({
          title: "Error",
          description: result.error || "Failed to like playlist.",
          variant: "destructive",
        });
      }
    }
  }

  const handleCreateFromTrack = (trackId: number) => {
    router.push(`/create?seedTrack=${trackId}`)
  }
  
  const totalDurationMinutes = Math.floor(playlist.tracks.reduce((acc, track) => acc + track.duration, 0) / 60)

  return (
    <main className="container mx-auto px-4 pt-24 pb-32 md:pb-16">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-6">
          {/* Title */}
          <div className="flex items-center gap-3">
            {isEditingTitle && isOwner ? (
              <>
                <input
                  type="text"
                  value={playlist.name} 
                  onChange={(e) => setPlaylist(prev => prev ? { ...prev, name: e.target.value } : null)}
                  className="flex-1 text-4xl md:text-5xl font-bold bg-transparent border-b-2 border-primary focus:outline-none"
                  autoFocus
                />
                <button
                  onClick={handleSaveTitle}
                  className="p-3 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg transition-colors"
                >
                  <Check className="h-6 w-6" />
                </button>
              </>
            ) : (
              <>
                <h1 className="flex-1 text-4xl md:text-5xl font-bold text-balance">{playlist.name}</h1>
                {isOwner && (
                  <button
                    onClick={() => setIsEditingTitle(true)}
                    className="p-3 hover:bg-surface-elevated rounded-lg transition-colors text-muted-foreground hover:text-foreground"
                  >
                    <Edit2 className="h-5 w-5" />
                  </button>
                )}
              </>
            )}
          </div>

          {/* Metadata */}
          <div className="flex items-center gap-4 text-muted-foreground">
            <Link href={`/user/${playlist.owner.username}`} className="hover:text-primary transition-colors">
              by {playlist.owner.username}
            </Link>
            <span>•</span>
            <div className="flex items-center gap-1">
              {playlist.is_public ? <Globe className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
              <span>{playlist.is_public ? "Public" : "Private"}</span>
            </div>
            <span>•</span>
            <span>{playlist.tracks.length} tracks</span>
            {totalDurationMinutes > 0 && (
              <>
                <span>•</span>
                <span>{totalDurationMinutes} minutes</span>
              </>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleLike}
              className={cn(
                "flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all",
                likedState
                  ? "bg-primary text-primary-foreground"
                  : "bg-surface-elevated hover:bg-border border border-border",
              )}
            >
              <Heart className={cn("h-5 w-5", likedState && "fill-current")} />
              {likedState ? "Liked" : "Like"} ({currentLikeCount})
            </button>

            <button className="flex items-center gap-2 px-6 py-3 bg-surface-elevated hover:bg-border border border-border rounded-lg font-medium transition-all">
              <Share2 className="h-5 w-5" />
              Share
            </button>

            {isOwner && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon" className="h-12 w-12 bg-transparent">
                    <MoreVertical className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={handleTogglePrivacy}>
                    {playlist.is_public ? <Lock className="h-4 w-4 mr-2" /> : <Globe className="h-4 w-4 mr-2" />}
                    Make {playlist.is_public ? "Private" : "Public"}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleDelete} className="text-destructive focus:text-destructive">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Playlist
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>

        {/* Track List */}
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <div className="p-6 border-b border-border">
            <h2 className="text-xl font-semibold">Tracks</h2>
          </div>
          <div className="divide-y divide-border">
            {playlist.tracks.map((track, index) => {
              const isCurrentTrack = currentTrack?.track_id === track.track_id;
              
              return (
                <div
                  key={track.track_id}
                  className={cn(
                    "flex items-center gap-4 p-4 hover:bg-surface-elevated transition-colors group",
                    isCurrentTrack && "bg-surface-elevated",
                  )}
                >
                  <button onClick={() => handleTrackClick(index)} className="flex items-center gap-4 flex-1 text-left">
                    <div className="flex-shrink-0 w-8 text-center">
                      {isCurrentTrack ? (
                        <div className="flex items-center justify-center">
                          <div className="flex gap-1">
                            <div className="w-1 h-4 bg-primary animate-pulse" />
                            <div className="w-1 h-4 bg-primary animate-pulse [animation-delay:0.2s]" />
                            <div className="w-1 h-4 bg-primary animate-pulse [animation-delay:0.4s]" />
                          </div>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">{index + 1}</span>
                      )}
                    </div>

                    <div className="flex-shrink-0 w-12 h-12 bg-surface rounded-lg flex items-center justify-center overflow-hidden">
                      <img 
                        src={getAlbumArtUrl(track.album_art_url)}
                        alt={track.title}
                        className="w-full h-full object-cover"
                        onError={(e) => { e.currentTarget.src = '/dark-purple-music-waves.jpg'; }}
                      />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className={cn("font-semibold truncate", isCurrentTrack && "text-primary")}>
                        {track.title}
                      </div>
                      <div className="text-sm text-muted-foreground truncate">{track.artist_name}</div>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      {track.genre_toplevel && <span className="hidden sm:inline">{track.genre_toplevel}</span>}
                      <span className="hidden md:inline">
                        {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, "0")}
                      </span>
                    </div>
                  </button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCreateFromTrack(track.track_id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Create
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </main>
  )
}