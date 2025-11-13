"use client"

import { useState, useRef, useEffect } from "react"
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { recordListen } from "@/lib/api"

interface Track {
  track_id: number;
  title: string;
  artist_name: string;
  genre_toplevel: string | null;
  audio_url?: string;
  duration: number;
}

interface AudioPlayerProps {
  currentTrack: Track;
  onNext: () => void
  onPrevious: () => void
}

export function AudioPlayer({ currentTrack, onNext, onPrevious }: AudioPlayerProps) {
  const { token } = useAuth();
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(0.7)
  const [isMuted, setIsMuted] = useState(false)
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  // Effect to control audio playback (play/pause)
  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch(error => console.error("Audio play failed:", error));
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying]);

  // Effect to handle track changes
  useEffect(() => {
    if (audioRef.current && currentTrack?.audio_url) {
      const wasPlaying = isPlaying;
      setIsPlaying(false); // Stop playback while loading new track
      audioRef.current.src = `${API_URL}${currentTrack.audio_url}`;
      audioRef.current.load(); // Preload metadata
      if (wasPlaying) {
        audioRef.current.play().catch(error => console.error("Audio play failed:", error));
        setIsPlaying(true);
      }
    }
    // We only want this to run when the track itself changes, not when isPlaying changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentTrack, API_URL]);

  // Effect to handle volume changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);
  
  // Effect for recording listening history
  useEffect(() => {
    if (isPlaying && currentTime > 1 && currentTime < 2 && token && currentTrack.track_id && currentTrack.genre_toplevel) {
      console.log(`Recording listen for track: ${currentTrack.track_id}, genre: ${currentTrack.genre_toplevel}`);
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

  const toggleMute = () => {
    setIsMuted(!isMuted)
  }

  return (
    <div className="bg-surface-elevated border border-border rounded-xl p-6 space-y-6">
      <audio 
        ref={audioRef} 
        onEnded={onNext} 
        onTimeUpdate={onTimeUpdate}
        onLoadedMetadata={onLoadedMetadata}
      />
      {/* Track Info */}
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold text-balance">{currentTrack.title}</h3>
        <p className="text-muted-foreground">{currentTrack.artist_name}</p>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div
          ref={progressRef}
          onClick={handleProgressClick}
          className="relative h-2 bg-surface rounded-full cursor-pointer group"
        >
          <div
            className="absolute inset-y-0 left-0 bg-primary rounded-full transition-all"
            style={{ width: duration > 0 ? `${(currentTime / duration) * 100}%` : '0%' }}
          />
          <div
            className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-primary rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ left: duration > 0 ? `calc(${(currentTime / duration) * 100}% - 8px)` : '0%' }}
          />
        </div>
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={onPrevious}
          className="p-3 hover:bg-surface rounded-full transition-colors text-muted-foreground hover:text-foreground"
        >
          <SkipBack className="h-5 w-5" />
        </button>

        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-5 bg-primary hover:bg-primary-hover text-primary-foreground rounded-full transition-all hover:scale-105"
        >
          {isPlaying ? <Pause className="h-6 w-6 fill-current" /> : <Play className="h-6 w-6 fill-current" />}
        </button>

        <button
          onClick={onNext}
          className="p-3 hover:bg-surface rounded-full transition-colors text-muted-foreground hover:text-foreground"
        >
          <SkipForward className="h-5 w-5" />
        </button>
      </div>

      {/* Volume Control */}
      <div className="flex items-center gap-3">
        <button onClick={toggleMute} className="text-muted-foreground hover:text-foreground transition-colors">
          {isMuted || volume === 0 ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
        </button>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={isMuted ? 0 : volume}
          onChange={(e) => {
            setVolume(Number.parseFloat(e.target.value))
            setIsMuted(false)
          }}
          className="flex-1 h-2 bg-surface rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:cursor-pointer"
        />
      </div>
    </div>
  )
}
