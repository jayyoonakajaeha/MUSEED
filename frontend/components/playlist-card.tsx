"use client"

import type React from "react"

import { Play, Heart, Share2, Music2 } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"
import { useRouter } from "next/navigation"

interface PlaylistCardProps {
  id: string
  title: string
  creator: string
  creatorId?: string
  trackCount: number
  likes: number
  coverImage?: string
  isLiked?: boolean
}

export function PlaylistCard({
  id,
  title,
  creator,
  creatorId,
  trackCount,
  likes,
  coverImage,
  isLiked = false,
}: PlaylistCardProps) {
  const [liked, setLiked] = useState(isLiked)
  const [likeCount, setLikeCount] = useState(likes)
  const router = useRouter()

  const handleCardClick = () => {
    router.push(`/playlist/${id}`)
  }

  const handleCreatorClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    router.push(`/user/${creatorId || "1"}`)
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

  return (
    <div
      onClick={handleCardClick}
      className="group relative bg-surface rounded-xl overflow-hidden border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 cursor-pointer"
    >
      {/* Cover Image */}
      <div className="relative aspect-square bg-surface-elevated overflow-hidden">
        {coverImage ? (
          <img src={coverImage || "/placeholder.svg"} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Music2 className="h-16 w-16 text-muted-foreground/30" />
          </div>
        )}

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
