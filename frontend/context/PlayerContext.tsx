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
  resetPlayer: () => void; // resetPlayer 추가됨
}

const PlayerContext = createContext<PlayerContextType | undefined>(undefined);

export function PlayerProvider({ children }: { children: ReactNode }) {
  const [currentTrack, setCurrentTrack] = useState<Track | null>(null);
  const [playlist, setPlaylist] = useState<Track[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolumeState] = useState(0.7);
  const [isMuted, setIsMuted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState<number>(-1);

  // 초기화 함수
  const resetPlayer = useCallback(() => {
    setCurrentTrack(null);
    setPlaylist([]);
    setIsPlaying(false);
    setCurrentIndex(-1);
    // 볼륨과 음소거 상태는 UX 선택에 따라 유지하거나 초기화 가능
    // 현재는 사용자 설정 유지
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
      // 플레이리스트 끝
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
      // 현재 트랙 재시작 로직이 들어갈 수 있으나, 지금은 정지하거나 0초로 이동
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
      resetPlayer // resetPlayer 포함됨
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
