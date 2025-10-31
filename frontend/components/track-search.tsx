"use client"

import { useState } from "react"
import { Search, Music2, Plus } from "lucide-react"
import { cn } from "@/lib/utils"

interface Track {
  id: string
  title: string
  artist: string
  duration: string
  genre: string
}

interface TrackSearchProps {
  onSelectTrack: (track: Track) => void
  selectedTracks: Track[]
}

// Mock track database
const mockTracks: Track[] = [
  { id: "1", title: "Midnight City", artist: "M83", duration: "4:04", genre: "Electronic" },
  { id: "2", title: "Electric Feel", artist: "MGMT", duration: "3:49", genre: "Indie" },
  { id: "3", title: "Breathe", artist: "Pink Floyd", duration: "2:43", genre: "Rock" },
  { id: "4", title: "Strobe", artist: "deadmau5", duration: "10:37", genre: "Electronic" },
  { id: "5", title: "Teardrop", artist: "Massive Attack", duration: "5:29", genre: "Trip-Hop" },
  { id: "6", title: "Intro", artist: "The xx", duration: "2:11", genre: "Indie" },
]

export function TrackSearch({ onSelectTrack, selectedTracks }: TrackSearchProps) {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<Track[]>([])
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery)
    setIsSearching(true)

    if (searchQuery.trim()) {
      const filtered = mockTracks.filter(
        (track) =>
          track.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          track.artist.toLowerCase().includes(searchQuery.toLowerCase()),
      )
      setResults(filtered)
    } else {
      setResults([])
    }

    setIsSearching(false)
  }

  const isTrackSelected = (trackId: string) => {
    return selectedTracks.some((t) => t.id === trackId)
  }

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search for tracks or artists..."
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          className="w-full pl-12 pr-4 py-4 bg-surface-elevated border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
        />
      </div>

      {/* Search Results */}
      {results.length > 0 && (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {results.map((track) => (
            <button
              key={track.id}
              onClick={() => !isTrackSelected(track.id) && onSelectTrack(track)}
              disabled={isTrackSelected(track.id)}
              className={cn(
                "w-full flex items-center gap-4 p-4 rounded-xl border transition-all text-left",
                isTrackSelected(track.id)
                  ? "bg-surface border-border opacity-50 cursor-not-allowed"
                  : "bg-surface-elevated border-border hover:border-primary/50 hover:bg-surface",
              )}
            >
              <div className="flex-shrink-0 w-12 h-12 bg-surface rounded-lg flex items-center justify-center">
                <Music2 className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold truncate">{track.title}</div>
                <div className="text-sm text-muted-foreground truncate">{track.artist}</div>
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="hidden sm:inline">{track.genre}</span>
                <span>{track.duration}</span>
                {!isTrackSelected(track.id) && <Plus className="h-5 w-5 text-primary" />}
              </div>
            </button>
          ))}
        </div>
      )}

      {query && results.length === 0 && !isSearching && (
        <div className="text-center py-12 text-muted-foreground">
          <Music2 className="h-12 w-12 mx-auto mb-4 opacity-30" />
          <p>No tracks found. Try a different search term.</p>
        </div>
      )}
    </div>
  )
}
