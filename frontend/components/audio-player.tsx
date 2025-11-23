"use client"

import { useState, useRef, useEffect } from "react"
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, ListMusic } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { usePlayer } from "@/context/PlayerContext"
import { recordListen } from "@/lib/api"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"

export function AudioPlayer() {
  const { token } = useAuth();
  const { 
    currentTrack, 
    isPlaying, 
    volume, 
    isMuted, 
    setIsPlaying, 
    nextTrack, 
    previousTrack, 
    setVolume, 
    toggleMute,
    playlist,
    playPlaylist
  } = usePlayer();

  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const getAlbumArtUrl = (url: string | null | undefined): string => {
    if (url && (url.includes('.jpg') || url.includes('.png') || url.includes('.gif'))) {
      return url;
    }
    return '/dark-purple-music-waves.jpg';
  }

  // Effect to control audio playback
  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise.catch(error => {
            // Ignore AbortError which happens if playback is interrupted
            if (error.name !== 'AbortError') {
              console.error("Audio play failed:", error);
            }
          });
        }
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying]);

  // Effect to handle track changes
  useEffect(() => {
    if (audioRef.current && currentTrack?.audio_url) {
      // Pause current playback
      audioRef.current.pause();
      
      // Update source
      audioRef.current.src = `${API_URL}${currentTrack.audio_url}`;
      audioRef.current.load();

      // If it was supposed to be playing (handled by context setting isPlaying=true on track change), play.
      if (isPlaying) {
         const playPromise = audioRef.current.play();
         if (playPromise !== undefined) {
            playPromise.catch(error => {
                if (error.name !== 'AbortError') {
                    console.error("Audio play failed on track change:", error);
                }
            });
         }
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentTrack, API_URL]); // Removed isPlaying from deps to avoid re-triggering

  // Effect to handle volume changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);
  
  // Record listening history
  useEffect(() => {
    if (isPlaying && currentTime > 1 && currentTime < 2 && token && currentTrack?.track_id && currentTrack?.genre_toplevel) {
      // console.log(`Recording listen for track: ${currentTrack.track_id}`);
      recordListen(
        { track_id: currentTrack.track_id.toString(), genre: currentTrack.genre_toplevel },
        token
      );
    }
  }, [currentTime, isPlaying, token, currentTrack]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressRef.current || !audioRef.current) return
    const rect = progressRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percentage = x / rect.width
    audioRef.current.currentTime = percentage * duration
  }

  const onTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  }

  const onLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  }

  if (!currentTrack) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur border-t border-border p-3 z-50 shadow-lg transition-transform duration-300 ease-in-out translate-y-0">
      <audio 
        ref={audioRef} 
        onEnded={nextTrack} 
        onTimeUpdate={onTimeUpdate}
        onLoadedMetadata={onLoadedMetadata}
      />
      
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        
        {/* Left: Track Info */}
        <div className="flex items-center gap-3 w-1/3 min-w-0">
            <img 
                src={getAlbumArtUrl(currentTrack.album_art_url)} 
                alt={currentTrack.title} 
                className="h-12 w-12 rounded-md object-cover shadow-sm flex-shrink-0"
                onError={(e) => { e.currentTarget.src = '/dark-purple-music-waves.jpg'; }}
            />
            <div className="flex flex-col min-w-0 justify-center">
              <h3 className="font-semibold truncate text-sm md:text-base leading-tight">{currentTrack.title}</h3>
              <p className="text-xs text-muted-foreground truncate">{currentTrack.artist_name}</p>
            </div>
        </div>

        {/* Center: Controls & Progress */}
        <div className="flex flex-col items-center flex-1 max-w-xl w-full gap-1">
          {/* Controls */}
          <div className="flex items-center gap-4">
            <button
              onClick={previousTrack}
              className="p-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <SkipBack className="h-5 w-5" />
            </button>

            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 bg-primary text-primary-foreground rounded-full hover:scale-105 transition-transform"
            >
              {isPlaying ? <Pause className="h-5 w-5 fill-current" /> : <Play className="h-5 w-5 fill-current" />}
            </button>

            <button
              onClick={nextTrack}
              className="p-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <SkipForward className="h-5 w-5" />
            </button>
          </div>

          {/* Progress Bar */}
          <div className="w-full flex items-center gap-2 text-xs text-muted-foreground">
            <span className="w-10 text-right">{formatTime(currentTime)}</span>
            <div
              ref={progressRef}
              onClick={handleProgressClick}
              className="relative h-1.5 flex-1 bg-secondary rounded-full cursor-pointer group overflow-hidden"
            >
              <div
                className="absolute inset-y-0 left-0 bg-primary transition-all"
                style={{ width: duration > 0 ? `${(currentTime / duration) * 100}%` : '0%' }}
              />
            </div>
            <span className="w-10">{formatTime(duration)}</span>
          </div>
        </div>

        {/* Right: Queue & Volume */}
        <div className="flex items-center justify-end gap-4 w-1/3">
          
          {/* Queue Sheet */}
          <Sheet>
            <SheetTrigger asChild>
              <button className="text-muted-foreground hover:text-foreground transition-colors p-2" title="Queue">
                <ListMusic className="h-5 w-5" />
              </button>
            </SheetTrigger>
            <SheetContent className="w-[400px] sm:w-[540px]">
              <SheetHeader className="mb-4">
                <SheetTitle>Queue</SheetTitle>
              </SheetHeader>
              <ScrollArea className="h-[calc(100vh-100px)] pr-4">
                <div className="space-y-2">
                  {playlist.map((track, index) => (
                    <div
                      key={`${track.track_id}-${index}`}
                      onClick={() => playPlaylist(playlist, index)}
                      className={cn(
                        "flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors hover:bg-accent",
                        currentTrack.track_id === track.track_id && "bg-accent/50 border-l-4 border-primary"
                      )}
                    >
                       <img 
                            src={getAlbumArtUrl(track.album_art_url)} 
                            alt={track.title} 
                            className="h-10 w-10 rounded object-cover"
                            onError={(e) => { e.currentTarget.src = '/dark-purple-music-waves.jpg'; }}
                        />
                      <div className="flex-1 min-w-0">
                        <p className={cn("text-sm font-medium truncate", currentTrack.track_id === track.track_id && "text-primary")}>
                          {track.title}
                        </p>
                        <p className="text-xs text-muted-foreground truncate">
                          {track.artist_name}
                        </p>
                      </div>
                      {currentTrack.track_id === track.track_id && (
                          <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </SheetContent>
          </Sheet>

          <div className="flex items-center gap-2">
            <button onClick={toggleMute} className="text-muted-foreground hover:text-foreground">
              {isMuted || volume === 0 ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={isMuted ? 0 : volume}
              onChange={(e) => setVolume(Number.parseFloat(e.target.value))}
              className="w-20 h-1.5 bg-secondary rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
            />
          </div>
        </div>

      </div>
    </div>
  )
}