"use client"

import { createContext, useContext, useState, ReactNode, useCallback } from 'react';

export interface Track {
  track_id: number;
  title: string;
  artist_name: string;
  genre_toplevel: string | null;
  audio_url?: string;
  duration: number;
}

interface PlayerContextType {
  currentTrack: Track | null;
  isPlaying: boolean;
  playlist: Track[];
  volume: number;
  isMuted: boolean;
  playTrack: (track: Track) => void;
  playPlaylist: (tracks: Track[], startIndex?: number) => void;
  togglePlay: () => void;
  nextTrack: () => void;
  previousTrack: () => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  setIsPlaying: (isPlaying: boolean) => void;
  resetPlayer: () => void; // Added resetPlayer
}

const PlayerContext = createContext<PlayerContextType | undefined>(undefined);

export function PlayerProvider({ children }: { children: ReactNode }) {
  const [currentTrack, setCurrentTrack] = useState<Track | null>(null);
  const [playlist, setPlaylist] = useState<Track[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolumeState] = useState(0.7);
  const [isMuted, setIsMuted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState<number>(-1);

  // Reset function
  const resetPlayer = useCallback(() => {
    setCurrentTrack(null);
    setPlaylist([]);
    setIsPlaying(false);
    setCurrentIndex(-1);
    // volume and isMuted can persist or be reset too, depending on UX choice
    // For now, let's keep them as user preferences
  }, []);

  const playTrack = useCallback((track: Track) => {
    setCurrentTrack(track);
    setPlaylist([track]);
    setCurrentIndex(0);
    setIsPlaying(true);
  }, []);

  const playPlaylist = useCallback((tracks: Track[], startIndex: number = 0) => {
    if (tracks.length === 0) return;
    setPlaylist(tracks);
    setCurrentIndex(startIndex);
    setCurrentTrack(tracks[startIndex]);
    setIsPlaying(true);
  }, []);

  const togglePlay = useCallback(() => {
    if (currentTrack) {
      setIsPlaying((prev) => !prev);
    }
  }, [currentTrack]);

  const nextTrack = useCallback(() => {
    if (playlist.length === 0 || currentIndex === -1) return;
    
    const nextIndex = currentIndex + 1;
    if (nextIndex < playlist.length) {
      setCurrentIndex(nextIndex);
      setCurrentTrack(playlist[nextIndex]);
      setIsPlaying(true);
    } else {
      // End of playlist
      setIsPlaying(false);
    }
  }, [playlist, currentIndex]);

  const previousTrack = useCallback(() => {
    if (playlist.length === 0 || currentIndex === -1) return;

    const prevIndex = currentIndex - 1;
    if (prevIndex >= 0) {
      setCurrentIndex(prevIndex);
      setCurrentTrack(playlist[prevIndex]);
      setIsPlaying(true);
    } else {
      // Restart current track logic could go here, but for now just stop or go to 0
      setCurrentIndex(0);
      setCurrentTrack(playlist[0]);
      setIsPlaying(true);
    }
  }, [playlist, currentIndex]);

  const setVolume = useCallback((vol: number) => {
    setVolumeState(vol);
    if (vol > 0) setIsMuted(false);
  }, []);

  const toggleMute = useCallback(() => {
    setIsMuted((prev) => !prev);
  }, []);

  return (
    <PlayerContext.Provider value={{
      currentTrack,
      isPlaying,
      playlist,
      volume,
      isMuted,
      playTrack,
      playPlaylist,
      togglePlay,
      nextTrack,
      previousTrack,
      setVolume,
      toggleMute,
      setIsPlaying,
      resetPlayer // Included resetPlayer
    }}>
      {children}
    </PlayerContext.Provider>
  );
}

export function usePlayer() {
  const context = useContext(PlayerContext);
  if (context === undefined) {
    throw new Error('usePlayer must be used within a PlayerProvider');
  }
  return context;
}
