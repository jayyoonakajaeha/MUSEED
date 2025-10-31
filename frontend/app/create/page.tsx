"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { TrackSearch } from "@/components/track-search"
import { FileUpload } from "@/components/file-upload"
import { Sparkles, X, Music2 } from "lucide-react"
import { useRouter } from "next/navigation"

interface Track {
  id: string
  title: string
  artist: string
  duration: string
  genre: string
}

interface UploadedFile {
  id: string
  name: string
  size: string
  file: File
}

export default function CreatePlaylistPage() {
  const router = useRouter()
  const [selectedTracks, setSelectedTracks] = useState<Track[]>([])
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleSelectTrack = (track: Track) => {
    setSelectedTracks([...selectedTracks, track])
  }

  const handleRemoveTrack = (trackId: string) => {
    setSelectedTracks(selectedTracks.filter((t) => t.id !== trackId))
  }

  const handleFileUpload = (file: UploadedFile) => {
    setUploadedFiles([...uploadedFiles, file])
  }

  const handleRemoveFile = (fileId: string) => {
    setUploadedFiles(uploadedFiles.filter((f) => f.id !== fileId))
  }

  const handleGeneratePlaylist = async () => {
    if (selectedTracks.length === 0 && uploadedFiles.length === 0) return

    setIsGenerating(true)

    // Simulate AI generation
    await new Promise((resolve) => setTimeout(resolve, 2000))

    setIsGenerating(false)
    router.push("/playlist/demo")
  }

  const totalSeeds = selectedTracks.length + uploadedFiles.length

  return (
    <>
      <Navigation />
      <main className="container mx-auto px-4 pt-24 pb-32 md:pb-16">
        <div className="max-w-5xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-elevated border border-border text-sm">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-muted-foreground">AI Playlist Generator</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-balance">Create Your Playlist</h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-balance">
              Select seed tracks from our library or upload your own audio files. Our AI will generate a personalized
              playlist based on your selections.
            </p>
          </div>

          {/* Selected Seeds Display */}
          {totalSeeds > 0 && (
            <div className="bg-surface-elevated border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-lg">
                  Selected Seeds <span className="text-primary">({totalSeeds})</span>
                </h3>
              </div>

              <div className="space-y-2">
                {selectedTracks.map((track) => (
                  <div
                    key={track.id}
                    className="flex items-center gap-4 p-3 bg-surface rounded-lg border border-border"
                  >
                    <div className="flex-shrink-0 w-10 h-10 bg-surface-elevated rounded-lg flex items-center justify-center">
                      <Music2 className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{track.title}</div>
                      <div className="text-sm text-muted-foreground truncate">{track.artist}</div>
                    </div>
                    <button
                      onClick={() => handleRemoveTrack(track.id)}
                      className="flex-shrink-0 p-2 hover:bg-surface-elevated rounded-lg transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}

                {uploadedFiles.map((file) => (
                  <div key={file.id} className="flex items-center gap-4 p-3 bg-surface rounded-lg border border-border">
                    <div className="flex-shrink-0 w-10 h-10 bg-surface-elevated rounded-lg flex items-center justify-center">
                      <Music2 className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{file.name}</div>
                      <div className="text-sm text-muted-foreground">{file.size}</div>
                    </div>
                    <button
                      onClick={() => handleRemoveFile(file.id)}
                      className="flex-shrink-0 p-2 hover:bg-surface-elevated rounded-lg transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Search Tracks */}
          <div className="bg-surface border border-border rounded-xl p-6 space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-2">Search Library</h2>
              <p className="text-sm text-muted-foreground">Find tracks from our FMA music library</p>
            </div>
            <TrackSearch onSelectTrack={handleSelectTrack} selectedTracks={selectedTracks} />
          </div>

          {/* Upload Files */}
          <div className="bg-surface border border-border rounded-xl p-6 space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-2">Upload Your Music</h2>
              <p className="text-sm text-muted-foreground">Upload your own audio files to use as seed tracks</p>
            </div>
            <FileUpload onFileUpload={handleFileUpload} uploadedFiles={uploadedFiles} onRemoveFile={handleRemoveFile} />
          </div>

          {/* Generate Button */}
          <div className="flex justify-center pt-4">
            <button
              onClick={handleGeneratePlaylist}
              disabled={totalSeeds === 0 || isGenerating}
              className="px-8 py-4 bg-primary hover:bg-primary-hover text-primary-foreground rounded-xl font-semibold text-lg transition-all hover:shadow-lg hover:shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none flex items-center gap-3"
            >
              {isGenerating ? (
                <>
                  <div className="h-5 w-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  Generate Playlist
                </>
              )}
            </button>
          </div>
        </div>
      </main>
    </>
  )
}
