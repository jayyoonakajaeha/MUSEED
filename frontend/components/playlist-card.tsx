"use client"

import type React from "react"
import { Play, Heart, Share2, Music2, Trash2, Eye, EyeOff, Check } from "lucide-react"
import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { useRouter } from "next/navigation"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/context/AuthContext"
import { usePlayer } from "@/context/PlayerContext"
import { likePlaylist, unlikePlaylist } from "@/lib/api"
import { toast } from "@/components/ui/use-toast"
import { Button } from "@/components/ui/button"
import { useLanguage } from "@/context/LanguageContext"


// Interface for the playlist object coming from the backend
interface Playlist {
  id: number;
  name: string;
  owner: {
    id: number;
    username: string;
    nickname?: string;
  };
  owner_username: string; // Added for convenience
  tracks: any[]; // We just need the count
  is_public: boolean; // Added
  likes_count: number; // Added
  liked_by_user: boolean; // Added
  // These are not yet available from the backend, so they are optional
  coverImage?: string; 
}

interface PlaylistCardProps {
  playlist: Playlist;
  isOwner?: boolean; // New prop to indicate if the current user owns this playlist
  onDelete?: (playlistId: number) => void; // New prop for delete action
  onTogglePublic?: (playlistId: number, isPublic: boolean) => void; // New prop for public/private toggle
}

export function PlaylistCard({ playlist, isOwner = false, onDelete, onTogglePublic }: PlaylistCardProps) {
  const { 
    id, 
    name: title, 
    owner, 
    tracks, 
    is_public,
    likes_count,
    liked_by_user,
    coverImage, 
  } = playlist;
  
  // Use nickname if available, otherwise fallback to username. Handle guest playlists (no owner).
  const creator = owner ? (owner.nickname || owner.username) : "Guest";
  const creatorUsername = owner ? owner.username : null;
  const trackCount = tracks.length;

  const { token } = useAuth();
  const { playPlaylist } = usePlayer();
  const { t } = useLanguage();

  const [liked, setLiked] = useState(liked_by_user)
  const [currentLikeCount, setCurrentLikeCount] = useState(likes_count)
  const [isPublicState, setIsPublicState] = useState(is_public);
  const [isCopied, setIsCopied] = useState(false);
  const [isLikeLoading, setIsLikeLoading] = useState(false);

  useEffect(() => {
    setLiked(liked_by_user);
    setCurrentLikeCount(likes_count);
    setIsPublicState(is_public);
  }, [liked_by_user, likes_count, is_public]);

  const router = useRouter()

  const handleCardClick = () => {
    router.push(`/playlist/${id}`)
  }

  const handleCreatorClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (creatorUsername) {
      router.push(`/user/${creatorUsername}`)
    }
  }

  const handlePlay = (e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    if (tracks && tracks.length > 0) {
      // Normalize tracks: check if they are nested in a 'track' property (PlaylistTrack) or direct (Track)
      const playerTracks = tracks.map((t: any) => t.track ? t.track : t);
      playPlaylist(playerTracks);
    } else {
      toast({
         title: "Empty Playlist",
         description: "This playlist has no tracks.",
      });
    }
  }

  const handleLike = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (!token) {
      toast({
        title: t.toast.loginRequired,
        description: t.toast.loginRequiredDesc,
        variant: "destructive",
      });
      return;
    }

    if (isLikeLoading) return;
    setIsLikeLoading(true);

    try {
        if (liked) {
        const result = await unlikePlaylist(id, token);
        if (result.success) {
            setLiked(false);
            setCurrentLikeCount(prev => prev - 1);
        } else {
            toast({
            title: t.toast.error,
            description: result.error || "Failed to unlike playlist.",
            variant: "destructive",
            });
        }
        } else {
        const result = await likePlaylist(id, token);
        if (result.success) {
            setLiked(true);
            setCurrentLikeCount(prev => prev + 1);
        } else {
            toast({
            title: t.toast.error,
            description: result.error || "Failed to like playlist.",
            variant: "destructive",
            });
        }
        }
    } finally {
        setIsLikeLoading(false);
    }
  }

  const handleShare = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    const shareUrl = `${window.location.origin}/playlist/${id}`;
    try {
        await navigator.clipboard.writeText(shareUrl);
        setIsCopied(true);
        toast({
            title: t.toast.linkCopied,
            description: t.toast.linkCopiedDesc,
        });
        setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
        toast({
            title: t.toast.shareFailed,
            description: t.toast.shareFailedDesc,
            variant: "destructive",
        });
    }
  }

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onDelete?.(id);
  };

  const handlePublicToggle = (checked: boolean) => {
    setIsPublicState(checked);
    onTogglePublic?.(id, checked);
  };

  // Use the first track's album art as the cover, if available.
  // Handle both old schema (direct track object) and new schema (nested in .track)
  const firstTrack = tracks[0];
  let coverArt = coverImage;
  
  if (!coverArt && firstTrack) {
      if (firstTrack.track && firstTrack.track.album_art_url) {
          coverArt = firstTrack.track.album_art_url;
      } else if (firstTrack.album_art_url) {
          coverArt = firstTrack.album_art_url;
      }
  }

  const getAlbumArtUrl = (url: string | null | undefined): string => {
    if (url && (url.includes('.jpg') || url.includes('.png') || url.includes('.gif'))) {
      return url;
    }
    return '/dark-purple-music-waves.jpg';
  }

  return (
    <div
      onClick={handleCardClick}
      className="group relative bg-surface rounded-xl overflow-hidden border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 cursor-pointer active:scale-[0.98] active:shadow-sm"
    >
      {/* Cover Image */}
      <div className="relative aspect-square bg-surface-elevated overflow-hidden">
        <img 
            src={getAlbumArtUrl(coverArt)} 
            alt={title} 
            className="w-full h-full object-cover"
            onError={(e) => { e.currentTarget.src = '/dark-purple-music-waves.jpg'; }}
        />

        {/* Play Button Overlay */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <button 
            onClick={handlePlay}
            className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-full p-4 transform scale-90 group-hover:scale-100 transition-transform"
          >
            <Play className="h-6 w-6 fill-current" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-semibold text-lg line-clamp-1 text-balance">{title}</h3>
          <p className="text-sm text-muted-foreground">
            by{" "}
            <button onClick={handleCreatorClick} className="hover:text-primary transition-colors hover:underline">
              {creator}
            </button>
          </p>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">{trackCount} tracks</span>

          <div className="flex items-center gap-2">
            <button
              onClick={handleLike}
              className={cn(
                "flex items-center gap-1 px-2 py-1 rounded-md transition-all",
                liked ? "text-primary" : "text-muted-foreground hover:text-foreground",
              )}
            >
              <Heart className={cn("h-4 w-4", liked && "fill-current")} />
              <span className="text-xs font-medium">{currentLikeCount}</span>
            </button>

            <button onClick={handleShare} className="p-1 text-muted-foreground hover:text-foreground transition-colors">
              {isCopied ? <Check className="h-4 w-4 text-green-500" /> : <Share2 className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {isOwner && (
          <div className="flex items-center justify-between pt-2 border-t border-border-200">
            <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
              <Switch
                id={`public-toggle-${id}`}
                checked={isPublicState}
                onCheckedChange={handlePublicToggle}
              />
              <Label htmlFor={`public-toggle-${id}`} className="text-sm flex items-center gap-1">
                {isPublicState ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                {isPublicState ? "Public" : "Private"}
              </Label>
            </div>
            <Button variant="ghost" size="icon" onClick={handleDeleteClick} className="text-destructive hover:bg-destructive/10">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}