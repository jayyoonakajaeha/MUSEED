"use client"

import { useState, useEffect, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Navigation } from "@/components/navigation"
import { TrackSearch } from "@/components/track-search"
import { FileUpload } from "@/components/file-upload"
import { Sparkles, X, Music2 } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { createPlaylistFromId, createPlaylistFromUpload, searchTracks, getTaskStatus } from "@/lib/api"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useLanguage } from "@/context/LanguageContext"

interface Track {
  track_id: number;
  title: string;
  artist_name: string;
  genre_toplevel: string | null;
  audio_url?: string;
}

interface UploadedFile {
  id: string
  name: string
  size: string
  file: File
}

function CreatePlaylistForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { token, refreshProfile } = useAuth()
  const { t } = useLanguage()

  const [seedTrack, setSeedTrack] = useState<Track | null>(null)
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null)
  const [playlistName, setPlaylistName] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [statusMessage, setStatusMessage] = useState<string>("") // 상태 메시지 표시 (분석 중... 등)

  useEffect(() => {
    const seedTrackId = searchParams.get('seedTrack');
    if (seedTrackId) {
      const fetchSeedTrack = async () => {
        const result = await searchTracks(seedTrackId, token || null);
        if (result.success && result.data.length > 0) {
          setSeedTrack(result.data[0]);
        }
      };
      fetchSeedTrack();
    }
  }, [searchParams, token]);

  const handleSelectTrack = (track: Track) => {
    setSeedTrack(track)
    setUploadedFile(null) // 한 번에 하나의 시드 유형만 활성화
  }

  const handleRemoveTrack = () => {
    setSeedTrack(null)
  }

  const handleFileUpload = (file: UploadedFile) => {
    setUploadedFile(file)
    setSeedTrack(null) // 한 번에 하나의 시드 유형만 활성화
  }

  const handleRemoveFile = () => {
    setUploadedFile(null)
  }

  const pollTaskStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const statusResult = await getTaskStatus(taskId, token || null);
        if (statusResult.success) {
          const { status, result } = statusResult.data;

          if (status === 'SUCCESS') {
            clearInterval(pollInterval);
            setIsGenerating(false);
            const playlistId = result.playlist_id;
            if (!token) {
              alert("플레이리스트가 생성되었지만, 로그인하지 않아 계정에 저장되지 않습니다. 지금 로그인하여 저장하세요!");
            }
            refreshProfile(); // "Seed Planter" / "Curator" 업적 확인
            router.push(`/playlist/${playlistId}`);
          } else if (status === 'FAILURE') {
            clearInterval(pollInterval);
            setIsGenerating(false);
            setError("Task Failed: " + (result?.error || "Unknown Error"));
          } else {
            // 여전히 처리 중 (PENDING, STARTED, 또는 사용자 정의)
            // 선택적으로 상태 메시지 업데이트
            setStatusMessage("AI is analyzing your music...");
          }
        } else {
          // 폴링 중 네트워크 오류 발생 시 재시도 또는 실패 처리?
          // 일단 404가 아니면 계속 재시도
        }
      } catch (e) {
        console.error("Polling error", e);
      }
    }, 1000);
  };

  const handleGeneratePlaylist = async () => {
    if (!playlistName) {
      setError("Please provide a playlist name.");
      return;
    }
    if (!seedTrack && !uploadedFile) {
      setError("Please select a seed track or upload a file.");
      return;
    }

    setIsGenerating(true)
    setError(null)
    setStatusMessage("Starting generation...")

    let result;
    if (seedTrack) {
      result = await createPlaylistFromId(playlistName, seedTrack.track_id.toString(), token || null)
    } else if (uploadedFile) {
      result = await createPlaylistFromUpload(playlistName, uploadedFile.file, token || null)
    } else {
      setError("No seed selected.");
      setIsGenerating(false);
      return;
    }

    if (result.success) {
      const taskId = result.data.task_id;
      if (taskId) {
        // 폴링 시작
        pollTaskStatus(taskId);
      } else {
        // 즉시 응답에 대한 폴백 (필요한 경우 레거시 지원)
        setIsGenerating(false);
        router.push(`/playlist/${result.data.id}`);
      }
    } else {
      setIsGenerating(false);
      setError(result.error || "Failed to initiate playlist generation.")
    }
  }

  const hasSeed = seedTrack || uploadedFile;

  return (
    <>
      <main className="container mx-auto px-4 pt-24 pb-32 md:pb-16">
        <div className="max-w-3xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-elevated border border-border text-sm">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-muted-foreground">{t.create.badge}</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-balance">{t.create.title}</h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-balance">
              {t.create.description}
            </p>
          </div>

          {/* Selected Seed Display */}
          {hasSeed && (
            <div className="bg-surface-elevated border border-border rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-lg">
                {t.create.selectedSeed}
              </h3>
              {seedTrack && (
                <div className="flex items-center gap-4 p-3 bg-surface rounded-lg border border-border">
                  <div className="flex-shrink-0 w-10 h-10 bg-surface-elevated rounded-lg flex items-center justify-center"><Music2 className="h-5 w-5 text-primary" /></div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{seedTrack.title}</div>
                    <div className="text-sm text-muted-foreground truncate">{seedTrack.artist_name}</div>
                  </div>
                  <button onClick={handleRemoveTrack} className="flex-shrink-0 p-2 hover:bg-surface-elevated rounded-lg transition-colors"><X className="h-4 w-4" /></button>
                </div>
              )}
              {uploadedFile && (
                <div className="flex items-center gap-4 p-3 bg-surface rounded-lg border border-border">
                  <div className="flex-shrink-0 w-10 h-10 bg-surface-elevated rounded-lg flex items-center justify-center"><Music2 className="h-5 w-5 text-primary" /></div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{uploadedFile.name}</div>
                    <div className="text-sm text-muted-foreground">{uploadedFile.size}</div>
                  </div>
                  <button onClick={handleRemoveFile} className="flex-shrink-0 p-2 hover:bg-surface-elevated rounded-lg transition-colors"><X className="h-4 w-4" /></button>
                </div>
              )}

              {/* Playlist Name Input */}
              <div className="space-y-2 pt-4">
                <Label htmlFor="playlist-name" className="font-semibold text-lg">{t.create.playlistName}</Label>
                <Input
                  id="playlist-name"
                  placeholder={t.create.playlistNamePlaceholder}
                  value={playlistName}
                  onChange={(e) => setPlaylistName(e.target.value)}
                  className="text-base"
                />
              </div>
            </div>
          )}

          {/* 트랙 검색 (시드 미선택 시) */}
          {!hasSeed && (
            <div className="bg-surface border border-border rounded-xl p-6 space-y-4">
              <div>
                <h2 className="text-xl font-semibold mb-2">{t.create.searchLibrary}</h2>
                <p className="text-sm text-muted-foreground">{t.create.searchLibraryDesc}</p>
              </div>
              <TrackSearch onSelectTrack={handleSelectTrack} selectedTracks={seedTrack ? [seedTrack] : []} />
            </div>
          )}

          {/* Upload Files (only if no seed is selected) */}
          {!hasSeed && (
            <div className="bg-surface border border-border rounded-xl p-6 space-y-4">
              <div>
                <h2 className="text-xl font-semibold mb-2">{t.create.uploadMusic}</h2>
                <p className="text-sm text-muted-foreground">{t.create.uploadMusicDesc}</p>
              </div>
              <FileUpload onFileUpload={handleFileUpload} uploadedFiles={uploadedFile ? [uploadedFile] : []} onRemoveFile={handleRemoveFile} />
            </div>
          )}

          {/* Generate Button */}
          <div className="flex justify-center pt-4">
            <button
              onClick={handleGeneratePlaylist}
              disabled={!hasSeed || !playlistName || isGenerating}
              className="px-8 py-4 bg-primary hover:bg-primary-hover text-primary-foreground rounded-xl font-semibold text-lg transition-all hover:shadow-lg hover:shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none flex items-center gap-3"
            >
              {isGenerating ? (
                <>
                  <div className="h-5 w-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                  {t.create.generating}
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  {t.create.generateButton}
                </>
              )}
            </button>
          </div>
          {error && <p className="mt-4 text-center text-sm text-destructive">{error}</p>}
        </div>
      </main>
    </>
  )
}

export default function CreatePlaylistPage() {
  return (
    <>
      <Navigation />
      <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
        <CreatePlaylistForm />
      </Suspense>
    </>
  )
}