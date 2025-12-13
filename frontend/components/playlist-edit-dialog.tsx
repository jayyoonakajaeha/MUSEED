"use client"

import React, { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { useAuth } from "@/context/AuthContext"
import { updatePlaylist } from "@/lib/api"
import { toast } from "@/components/ui/use-toast"
import { Loader2 } from "lucide-react"

interface PlaylistEditDialogProps {
  isOpen: boolean
  onClose: () => void
  playlist: {
    id: number
    name: string
    is_public: boolean
  }
  onUpdate: (updatedPlaylist: { name: string; is_public: boolean }) => void
}

export function PlaylistEditDialog({ isOpen, onClose, playlist, onUpdate }: PlaylistEditDialogProps) {
  const { token } = useAuth()
  const [name, setName] = useState(playlist.name)
  const [isPublic, setIsPublic] = useState(playlist.is_public)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // playlist prop 변경 시 상태 업데이트 (예: 다른 플레이리스트로 다이얼로그 열림)
  useEffect(() => {
    setName(playlist.name)
    setIsPublic(playlist.is_public)
  }, [playlist])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    if (!token) {
      setError("Authentication required.")
      setIsLoading(false)
      return
    }

    const result = await updatePlaylist(playlist.id, { name, is_public: isPublic }, token)

    setIsLoading(false)
    if (result.success) {
      toast({
        title: "Success",
        description: "Playlist updated successfully.",
      })
      onUpdate({ name, is_public: isPublic }) // parent component 업데이트 알림
      onClose()
    } else {
      setError(result.error || "Failed to update playlist.")
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Playlist</DialogTitle>
          <DialogDescription>
            Make changes to your playlist here. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="public" className="text-right">
                Public
              </Label>
              <Switch
                id="public"
                checked={isPublic}
                onCheckedChange={setIsPublic}
                className="col-span-3"
              />
            </div>
            {error && <p className="text-sm text-destructive col-span-4 text-center">{error}</p>}
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Save Changes
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
