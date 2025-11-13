import { useState, useCallback } from "react"
import { Search, Music2, Plus } from "lucide-react"
import { cn } from "@/lib/utils"
import { useDebouncedCallback } from 'use-debounce';

interface Track {
  track_id: number;
  title: string;
  artist_name: string;
  genre_toplevel: string | null;
  audio_url?: string;
  album_art_url?: string | null;
}

interface TrackSearchProps {
  onSelectTrack: (track: Track) => void
  // The parent component might still use a different track type, let's be flexible
  selectedTracks: any[] 
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const getAlbumArtUrl = (url: string | null | undefined): string => {
  if (url && (url.includes('.jpg') || url.includes('.png') || url.includes('.gif'))) {
    return url;
  }
  return '/dark-purple-music-waves.jpg';
}

export function TrackSearch({ onSelectTrack, selectedTracks }: TrackSearchProps) {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<Track[]>([])
  const [isSearching, setIsSearching] = useState(false)

  const fetchTracks = async (searchQuery: string) => {
    if (searchQuery.trim().length < 2) {
      setResults([]);
      setIsSearching(false);
      return;
    }
    
    setIsSearching(true);
    try {
      const response = await fetch(`${API_URL}/api/tracks/search?q=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data: Track[] = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Failed to fetch tracks:", error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const debouncedSearch = useDebouncedCallback(fetchTracks, 300);

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    setIsSearching(true); // Show loading indicator immediately
    debouncedSearch(newQuery);
  }

  const isTrackSelected = (trackId: number) => {
    // The parent component uses `id` but our new type uses `track_id`
    return selectedTracks.some((t) => t.id === trackId.toString());
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
          onChange={handleQueryChange}
          className="w-full pl-12 pr-4 py-4 bg-surface-elevated border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
        />
        {isSearching && <div className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 border-2 border-muted-foreground/30 border-t-primary rounded-full animate-spin" />}
      </div>

      {/* Search Results */}
      {results.length > 0 && (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {results.map((track) => (
            <button
              key={track.track_id}
              onClick={() => !isTrackSelected(track.track_id) && onSelectTrack(track)}
              disabled={isTrackSelected(track.track_id)}
              className={cn(
                "w-full flex items-center gap-4 p-4 rounded-xl border transition-all text-left",
                isTrackSelected(track.track_id)
                  ? "bg-surface border-border opacity-50 cursor-not-allowed"
                  : "bg-surface-elevated border-border hover:border-primary/50 hover:bg-surface",
              )}
            >
              <div className="flex-shrink-0 w-12 h-12 bg-surface rounded-lg flex items-center justify-center overflow-hidden">
                <img 
                  src={getAlbumArtUrl(track.album_art_url)} 
                  alt={track.title}
                  className="w-full h-full object-cover"
                  onError={(e) => { e.currentTarget.src = '/dark-purple-music-waves.jpg'; }}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold truncate">{track.title}</div>
                <div className="text-sm text-muted-foreground truncate">{track.artist_name}</div>
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                {track.genre_toplevel && <span className="hidden sm:inline">{track.genre_toplevel}</span>}
                {!isTrackSelected(track.track_id) && <Plus className="h-5 w-5 text-primary" />}
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
