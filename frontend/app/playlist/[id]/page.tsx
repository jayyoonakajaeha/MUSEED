"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/context/AuthContext"
import { usePlayer } from "@/context/PlayerContext"
import { getPlaylist, deletePlaylist, updatePlaylist, likePlaylist, unlikePlaylist, removeTrackFromPlaylist, reorderPlaylistTracks, addTrackToPlaylist, removePlaylistEntry } from "@/lib/api"
import { useParams, useRouter } from "next/navigation"
import { Heart, Share2, Music2, Edit2, Check, Trash2, Lock, Globe, Plus, GripVertical, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { MoreVertical } from "lucide-react"
import Link from "next/link"
import { toast } from "@/components/ui/use-toast"
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { TrackSearch } from "@/components/track-search" // Import TrackSearch

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

interface PlaylistTrack {
    id: number; // Unique association ID
    position: number;
    track: Track;
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
  tracks: PlaylistTrack[];
  likes_count: number;
  liked_by_user: boolean;
}

const getAlbumArtUrl = (url: string | null | undefined): string => {
  if (url && (url.includes('.jpg') || url.includes('.png') || url.includes('.gif'))) {
    return url;
  }
  return '/dark-purple-music-waves.jpg';
}

// Helper to reorder array
const reorder = (list: any[], startIndex: number, endIndex: number) => {
    const result = Array.from(list);
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);
    return result;
};

export default function PlaylistPage() {
  const router = useRouter()
  const params = useParams()
  const { user, token } = useAuth()
  const { playPlaylist, currentTrack } = usePlayer() 

  const [playlist, setPlaylist] = useState<Playlist | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [likedState, setLikedState] = useState(false)
  const [currentLikeCount, setCurrentLikeCount] = useState(0)
  
  const [isCopied, setIsCopied] = useState(false)

  // Edit Mode State
  const [isEditing, setIsEditing] = useState(false)
  const [editName, setEditName] = useState("")
  const [editIsPublic, setEditIsPublic] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

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
          // Initialize edit state
          setEditName(result.data.name)
          setEditIsPublic(result.data.is_public)
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

  // Update edit state when playlist changes
  useEffect(() => {
    if (playlist) {
      setEditName(playlist.name)
      setEditIsPublic(playlist.is_public)
    }
  }, [playlist])

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading playlist...</div>
  }

  if (error) {
    return <div className="min-h-screen flex items-center justify-center text-destructive">Error: {error}</div>
  }

  if (!playlist) {
    return <div className="min-h-screen flex items-center justify-center">Playlist not found.</div>
  }

  const isOwner = user?.username === playlist.owner.username
  
  const handleTrackClick = (index: number) => {
      if (isEditing) return; // Prevent play in edit mode
      if (playlist && playlist.tracks.length > 0) {
          // Create a list of tracks for the player
          const playerTracks = playlist.tracks.map(pt => pt.track);
          playPlaylist(playerTracks, index);
      }
  }

  const toggleEditMode = async () => {
      if (isEditing) {
          // Saving changes
          await handleSaveChanges();
      } else {
          // Entering edit mode
          setIsEditing(true);
      }
  }

  const handleSaveChanges = async () => {
    if (!token || !playlist) return;
    setIsSaving(true);
    
    // Only update if changes were made
    if (playlist.name !== editName || playlist.is_public !== editIsPublic) {
        const result = await updatePlaylist(playlist.id, { 
            name: editName, 
            is_public: editIsPublic 
        }, token);

        if (result.success) {
            setPlaylist(result.data);
            toast({
                title: "Success",
                description: "Playlist updated successfully.",
            });
            setIsEditing(false);
        } else {
            toast({
                title: "Error",
                description: result.error || "Failed to update playlist.",
                variant: "destructive",
            });
            // Don't exit edit mode on error
        }
    } else {
        setIsEditing(false);
    }
    setIsSaving(false);
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

  const handleDeleteTrack = async (entryId: number) => {
    if (!token || !playlist) return;
    if (window.confirm("Remove this track from playlist?")) {
        const result = await removePlaylistEntry(playlist.id, entryId, token);
        if (result.success) {
            setPlaylist(prev => prev ? {
                ...prev,
                tracks: prev.tracks.filter(item => item.id !== entryId)
            } : null);
            toast({
                title: "Success",
                description: "Track removed from playlist.",
            });
        } else {
            toast({
                title: "Error",
                description: result.error || "Failed to remove track.",
                variant: "destructive",
            });
        }
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

  const handleShare = async () => {
    if (!playlist) return;
    const shareUrl = `${window.location.origin}/playlist/${playlist.id}`;
    try {
        await navigator.clipboard.writeText(shareUrl);
        setIsCopied(true);
        toast({
            title: "Link Copied",
            description: "Playlist link copied to clipboard.",
        });
        setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
        console.error("Failed to copy: ", err);
        toast({
            title: "Share Failed",
            description: "Could not copy link to clipboard.",
            variant: "destructive",
        });
    }
  }

  const handleCreateFromTrack = (trackId: number) => {
    router.push(`/create?seedTrack=${trackId}`)
  }

  const onDragEnd = async (result: DropResult) => {
    if (!result.destination || !playlist || !token || !isOwner) {
      return;
    }

    const reorderedTracks = reorder(
      playlist.tracks,
      result.source.index,
      result.destination.index
    );

    setPlaylist(prev => prev ? { ...prev, tracks: reorderedTracks } : null);

    // Currently mapping back to track_ids for compatibility with existing backend API
    const newTrackIdsOrder = reorderedTracks.map(item => item.track.track_id);
    const apiResult = await reorderPlaylistTracks(playlist.id, newTrackIdsOrder, token);

    if (!apiResult.success) {
      toast({
        title: "Error",
        description: apiResult.error || "Failed to reorder tracks.",
        variant: "destructive",
      });
      setPlaylist(playlist); // Revert
    }
  };

  const handleAddTrack = async (track: { track_id: number }) => {
    if (!token || !playlist) return;
    
    const result = await addTrackToPlaylist(playlist.id, track.track_id, token);
    if (result.success) {
        toast({
            title: "Success",
            description: "Track added to playlist.",
        });
        // Refresh playlist to get the full track object and updated list
        const updatedPlaylist = await getPlaylist(playlist.id.toString(), token);
        if (updatedPlaylist.success) {
            setPlaylist(updatedPlaylist.data);
        }
    } else {
        toast({
            title: "Error",
            description: result.error || "Failed to add track.",
            variant: "destructive",
        });
    }
  }
  
  const totalDurationMinutes = Math.floor((playlist?.tracks || []).reduce((acc, item) => acc + item.track.duration, 0) / 60)

  // Determine playlist cover art from the first track
  const playlistCoverArtUrl = getAlbumArtUrl(playlist.tracks.length > 0 ? playlist.tracks[0].track.album_art_url : null);


  return (
    <main className="container mx-auto px-4 pt-24 pb-32 md:pb-16">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-6">
          {/* Cover Art and Title & Edit Controls */}
          <div className="flex items-center gap-6">
              <div className="flex-shrink-0 w-32 h-32 md:w-48 md:h-48 bg-surface rounded-xl overflow-hidden shadow-lg">
                  <img 
                      src={playlistCoverArtUrl} 
                      alt="Playlist Cover" 
                      className="w-full h-full object-cover"
                      onError={(e) => { e.currentTarget.src = '/dark-purple-music-waves.jpg'; }}
                  />
              </div>
              <div className="flex flex-col gap-4 flex-1">
                 {isEditing && isOwner ? (
                    <div className="space-y-4 p-4 bg-surface-elevated rounded-xl border border-border">
                        <div className="space-y-2">
                            <Label htmlFor="edit-name">Playlist Name</Label>
                            <Input 
                                id="edit-name"
                                value={editName} 
                                onChange={(e) => setEditName(e.target.value)} 
                                className="text-xl font-bold"
                            />
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <Switch
                                    id="edit-public"
                                    checked={editIsPublic}
                                    onCheckedChange={setEditIsPublic}
                                />
                                <Label htmlFor="edit-public">{editIsPublic ? "Public" : "Private"}</Label>
                            </div>
                            <span className="text-sm text-muted-foreground">
                                {editIsPublic ? "Anyone can see this playlist" : "Only you can see this playlist"}
                            </span>
                        </div>
                    </div>
                 ) : (
                    <div className="flex items-center gap-3">
                        <h1 className="flex-1 text-4xl md:text-5xl font-bold text-balance">{playlist.name}</h1>
                    </div>
                 )}
              </div>
          </div>

          {/* Metadata */}
          {!isEditing && (
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
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            {!isEditing && (
                <>
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

                    <button 
                        onClick={handleShare}
                        className="flex items-center gap-2 px-6 py-3 bg-surface-elevated hover:bg-border border border-border rounded-lg font-medium transition-all"
                    >
                    {isCopied ? <Check className="h-5 w-5 text-green-500" /> : <Share2 className="h-5 w-5" />}
                    {isCopied ? "Copied!" : "Share"}
                    </button>
                </>
            )}

            {isOwner && (
              <>
                <Button 
                    onClick={toggleEditMode}
                    className={cn(
                        "flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all h-auto",
                        isEditing ? "bg-primary text-primary-foreground hover:bg-primary/90" : "bg-surface-elevated hover:bg-border border border-border text-foreground"
                    )}
                    variant={isEditing ? "default" : "ghost"}
                >
                    {isEditing ? <Check className="h-5 w-5" /> : <Edit2 className="h-5 w-5" />}
                    {isEditing ? "Done" : "Edit Playlist"}
                </Button>

                {!isEditing && (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                        <Button variant="outline" size="icon" className="h-12 w-12 bg-transparent border-border">
                            <MoreVertical className="h-5 w-5" />
                        </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-48">
                        <DropdownMenuItem onClick={handleDelete} className="text-destructive focus:text-destructive">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete Playlist
                        </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )}
              </>
            )}
          </div>
        </div>

        {/* Track List */}
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <div className="p-6 border-b border-border flex justify-between items-center">
            <h2 className="text-xl font-semibold">Tracks</h2>
            {isEditing && <span className="text-sm text-muted-foreground">Drag to reorder</span>}
          </div>
          <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId="tracks">
              {(provided) => (
                <div 
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  className="divide-y divide-border"
                >
                  {playlist.tracks.map((item, index) => {
                    const track = item.track;
                    const isCurrentTrack = currentTrack?.track_id === track.track_id;
                    
                    return (
                        <Draggable 
                            key={item.id} 
                            draggableId={item.id.toString()} 
                            index={index}
                            isDragDisabled={!isEditing} 
                        >
                            {(provided, snapshot) => (
                                <div
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  className={cn(
                                    "flex items-center gap-4 p-4 transition-colors group",
                                    isCurrentTrack && !isEditing && "bg-surface-elevated",
                                    snapshot.isDragging ? "bg-accent shadow-md" : "hover:bg-surface-elevated",
                                    isEditing && "hover:bg-surface" 
                                  )}
                                >
                                    {isEditing && (
                                        <div {...provided.dragHandleProps} className="p-2 -ml-2 text-muted-foreground hover:text-foreground cursor-grab active:cursor-grabbing">
                                            <GripVertical className="h-5 w-5" />
                                        </div>
                                    )}
                                    
                                    <div 
                                        onClick={() => handleTrackClick(index)} 
                                        className={cn(
                                            "flex items-center gap-4 flex-1 text-left",
                                            isEditing ? "cursor-default" : "cursor-pointer"
                                        )}
                                    >
                                        <div className="flex-shrink-0 w-8 text-center">
                                            {isCurrentTrack && !isEditing ? (
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
                                            <div className={cn("font-semibold truncate", isCurrentTrack && !isEditing && "text-primary")}>
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
                                    </div>

                                    <div className="flex items-center gap-2">
                                        {isEditing ? (
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDeleteTrack(item.id); // Pass item.id (association ID)
                                                }}
                                            >
                                                <Trash2 className="h-5 w-5" />
                                            </Button>
                                        ) : (
                                            <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleCreateFromTrack(track.track_id);
                                                    }}
                                                >
                                                    <Plus className="h-4 w-4 mr-1" />
                                                    Create
                                                </Button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </Draggable>
                    );
                  })}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div>
        
        {/* Add Tracks Section ... */}
        {isEditing && (
            <div className="bg-surface border border-border rounded-xl overflow-hidden p-6 space-y-4">
                <h2 className="text-xl font-semibold">Add Tracks</h2>
                <p className="text-sm text-muted-foreground">Search for tracks to add to this playlist.</p>
                <TrackSearch onSelectTrack={handleAddTrack} />
            </div>
        )}

      </div>
    </main>
  )
}