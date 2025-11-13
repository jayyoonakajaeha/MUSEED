"use client"

import type React from "react"
import { Play, Heart, Share2, Music2 } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"
import { useRouter } from "next/navigation"

// Interface for the playlist object coming from the backend
interface Playlist {
  id: number;
  name: string;
  owner: {
    id: number;
    username: string;
  };
  tracks: any[]; // We just need the count
  // These are not yet available from the backend, so they are optional
  coverImage?: string; 
  likes?: number;
  isLiked?: boolean;
}

interface PlaylistCardProps {
  playlist: Playlist;
}

export function PlaylistCard({ playlist }: PlaylistCardProps) {
  const { 
    id, 
    name: title, 
    owner, 
    tracks, 
    coverImage, 
    likes = 0, 
    isLiked = false 
  } = playlist;
  
  const creator = owner.username;
  const creatorId = owner.id.toString();
  const trackCount = tracks.length;

  const [liked, setLiked] = useState(isLiked)
  const [likeCount, setLikeCount] = useState(likes)
  const router = useRouter()

  const handleCardClick = () => {
    router.push(`/playlist/${id}`)
  }

  const handleCreatorClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (creatorId) {
      router.push(`/user/${creatorId}`)
    }
  }

  const handleLike = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setLiked(!liked)
    setLikeCount(liked ? likeCount - 1 : likeCount + 1)
  }

  const handleShare = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    // Share functionality
  }

  // Use the first track's album art as the cover, if available
  const dynamicCoverImage = coverImage || (tracks[0] && tracks[0].album_art_url);

  const getAlbumArtUrl = (url: string | null | undefined): string => {
    if (url && (url.includes('.jpg') || url.includes('.png') || url.includes('.gif'))) {
      return url;
    }
    return '/dark-purple-music-waves.jpg';
  }

  return (
    <div
      onClick={handleCardClick}
      className="group relative bg-surface rounded-xl overflow-hidden border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 cursor-pointer"
    >
      {/* Cover Image */}
      <div className="relative aspect-square bg-surface-elevated overflow-hidden">
        <img 
            src={getAlbumArtUrl(dynamicCoverImage)} 
            alt={title} 
            className="w-full h-full object-cover"
            onError={(e) => { e.currentTarget.src = '/dark-purple-music-waves.jpg'; }}
        />

        {/* Play Button Overlay */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <button className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-full p-4 transform scale-90 group-hover:scale-100 transition-transform">
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
              <span className="text-xs font-medium">{likeCount}</span>
            </button>

            <button onClick={handleShare} className="p-1 text-muted-foreground hover:text-foreground transition-colors">
              <Share2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}