"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Upload, X, FileAudio } from "lucide-react"
import { cn } from "@/lib/utils"
import { useLanguage } from "@/context/LanguageContext"

interface UploadedFile {
  id: string
  name: string
  size: string
  file: File
}

interface FileUploadProps {
  onFileUpload: (file: UploadedFile) => void
  uploadedFiles: UploadedFile[]
  onRemoveFile: (id: string) => void
}

export function FileUpload({ onFileUpload, uploadedFiles, onRemoveFile }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const { t } = useLanguage()

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
    return (bytes / (1024 * 1024)).toFixed(1) + " MB"
  }

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      // 드롭된 파일 처리
      const files = Array.from(e.dataTransfer.files)
      files.forEach((file) => {
        if (file.type.startsWith("audio/")) {
          const uploadedFile: UploadedFile = {
            id: Math.random().toString(36).substr(2, 9),
            name: file.name,
            size: formatFileSize(file.size),
            file,
          }
          onFileUpload(uploadedFile)
        }
      })
    },
    [onFileUpload],
  )

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    files.forEach((file) => {
      const uploadedFile: UploadedFile = {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: formatFileSize(file.size),
        file,
      }
      onFileUpload(uploadedFile)
    })
  }

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-12 transition-all",
          isDragging ? "border-primary bg-primary/5" : "border-border bg-surface-elevated hover:border-primary/50",
        )}
      >
        <input
          type="file"
          accept="audio/*"
          multiple
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-surface rounded-full flex items-center justify-center">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          <div>
            <p className="text-lg font-semibold">{t?.fileUpload?.dropFiles || "Drop your audio files here"}</p>
            <p className="text-sm text-muted-foreground mt-1">{t?.fileUpload?.clickToBrowse || "or click to browse"}</p>
          </div>
          <p className="text-xs text-muted-foreground">{t?.fileUpload?.supports || "Supports MP3, WAV, FLAC, and more"}</p>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">Uploaded Files</h4>
          {uploadedFiles.map((file) => (
            <div
              key={file.id}
              className="flex items-center gap-4 p-4 bg-surface-elevated border border-border rounded-xl"
            >
              <div className="flex-shrink-0 w-10 h-10 bg-surface rounded-lg flex items-center justify-center">
                <FileAudio className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{file.name}</div>
                <div className="text-sm text-muted-foreground">{file.size}</div>
              </div>
              <button
                onClick={() => onRemoveFile(file.id)}
                className="flex-shrink-0 p-2 hover:bg-surface rounded-lg transition-colors text-muted-foreground hover:text-foreground"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
