"use client"

import { useState } from "react"
import { AudioPlayer } from "@/components/audio-player"
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
import { useRouter } from "next/navigation"
import Link from "next/link"

interface Track {
  track_id: string
  title: string
  artist: string
  duration: number
  genre: string
}

// Mock generated playlist
const mockPlaylist: Track[] = [
  { track_id: "1", title: "Midnight City", artist: "M83", duration: 244, genre: "Electronic" },
  { track_id: "2", title: "Strobe", artist: "deadmau5", duration: 637, genre: "Electronic" },
  { track_id: "3", title: "Intro", artist: "The xx", duration: 131, genre: "Indie" },
  { track_id: "4", title: "Teardrop", artist: "Massive Attack", duration: 329, genre: "Trip-Hop" },
  { track_id: "5", title: "Electric Feel", artist: "MGMT", duration: 229, genre: "Indie" },
  { track_id: "6", title: "Breathe", artist: "Pink Floyd", duration: 163, genre: "Rock" },
  { track_id: "7", title: "Holocene", artist: "Bon Iver", duration: 339, genre: "Indie" },
  { track_id: "8", title: "Nude", artist: "Radiohead", duration: 254, genre: "Alternative" },
]

export default function PlaylistPage() {
  const router = useRouter()
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0)
  const [isLiked, setIsLiked] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [playlistTitle, setPlaylistTitle] = useState("AI Generated Playlist")
  const [isPublic, setIsPublic] = useState(true)
  const [isOwner, setIsOwner] = useState(true) // Mock owner status - set to false to see other user's playlist view

  const currentTrack = mockPlaylist[currentTrackIndex]

  const handleNext = () => {
    setCurrentTrackIndex((prev) => (prev + 1) % mockPlaylist.length)
  }

  const handlePrevious = () => {
    setCurrentTrackIndex((prev) => (prev - 1 + mockPlaylist.length) % mockPlaylist.length)
  }

  const handleTrackClick = (index: number) => {
    setCurrentTrackIndex(index)
  }

  const handleSaveTitle = () => {
    setIsEditingTitle(false)
  }

  const handleDelete = () => {
    if (confirm("Are you sure you want to delete this playlist?")) {
      router.push("/profile")
    }
  }

  const handleTogglePrivacy = () => {
    setIsPublic(!isPublic)
  }

  const handleCreateFromTrack = (trackId: string) => {
    router.push(`/create?seedTrack=${trackId}`)
  }

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
                  value={playlistTitle}
                  onChange={(e) => setPlaylistTitle(e.target.value)}
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
                <h1 className="flex-1 text-4xl md:text-5xl font-bold text-balance">{playlistTitle}</h1>
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
            <Link href="/user/1" className="hover:text-primary transition-colors">
              by Alex Chen
            </Link>
            <span>•</span>
            <div className="flex items-center gap-1">
              {isPublic ? <Globe className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
              <span>{isPublic ? "Public" : "Private"}</span>
            </div>
            <span>•</span>
            <span>{mockPlaylist.length} tracks</span>
            <span>•</span>
            <span>{Math.floor(mockPlaylist.reduce((acc, track) => acc + track.duration, 0) / 60)} minutes</span>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => {
                setIsLiked(!isLiked)
              }}
              className={cn(
                "flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all",
                isLiked
                  ? "bg-primary text-primary-foreground"
                  : "bg-surface-elevated hover:bg-border border border-border",
              )}
            >
              <Heart className={cn("h-5 w-5", isLiked && "fill-current")} />
              {isLiked ? "Liked" : "Like"}
            </button>

            {!isOwner && (
              <button
                onClick={() => {
                  setIsSaved(!isSaved)
                }}
                className={cn(
                  "flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all",
                  isSaved
                    ? "bg-primary text-primary-foreground"
                    : "bg-surface-elevated hover:bg-border border border-border",
                )}
              >
                <Save className={cn("h-5 w-5", isSaved && "fill-current")} />
                {isSaved ? "Saved" : "Save"}
              </button>
            )}

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
                    {isPublic ? <Lock className="h-4 w-4 mr-2" /> : <Globe className="h-4 w-4 mr-2" />}
                    Make {isPublic ? "Private" : "Public"}
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

        {/* Audio Player */}
        <AudioPlayer
          currentTrack={currentTrack}
          onNext={handleNext}
          onPrevious={handlePrevious}
        />

        {/* Track List */}
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <div className="p-6 border-b border-border">
            <h2 className="text-xl font-semibold">Tracks</h2>
          </div>
          <div className="divide-y divide-border">
            {mockPlaylist.map((track, index) => (
              <div
                key={track.track_id}
                className={cn(
                  "flex items-center gap-4 p-4 hover:bg-surface-elevated transition-colors group",
                  currentTrackIndex === index && "bg-surface-elevated",
                )}
              >
                <button onClick={() => handleTrackClick(index)} className="flex items-center gap-4 flex-1 text-left">
                  <div className="flex-shrink-0 w-8 text-center">
                    {currentTrackIndex === index ? (
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

                  <div className="flex-shrink-0 w-12 h-12 bg-surface-elevated rounded-lg flex items-center justify-center">
                    <Music2 className="h-6 w-6 text-primary" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className={cn("font-semibold truncate", currentTrackIndex === index && "text-primary")}>
                      {track.title}
                    </div>
                    <div className="text-sm text-muted-foreground truncate">{track.artist}</div>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="hidden sm:inline">{track.genre}</span>
                    <span>
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
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}
