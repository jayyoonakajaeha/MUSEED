"use client"

import Link from "next/link"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useLanguage } from "@/context/LanguageContext"

interface User {
  id: number;
  username: string;
  profile_image_key: string;
}

interface UserListDialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  users: User[];
}

export function UserListDialog({ isOpen, onClose, title, users }: UserListDialogProps) {
  const { t } = useLanguage()

  const getProfileImageUrl = (key: string) => {
    // A simple check to see if the key corresponds to a known genre image file.
    // This list could be expanded or managed more dynamically.
    const knownGenreImages = [
      "Blues", "Classical", "Country", "Electronic", "Experimental", 
      "Folk", "Hip-Hop", "Instrumental", "International", "Jazz", 
      "Old-Time / Historic", "Pop", "Rock", "Soul-RnB", "Spoken", 
      "Easy Listening", "Default_Headphone", "Default"
    ];
    if (knownGenreImages.includes(key)) {
      return `/profiles/${key}.png`;
    }
    return '/profiles/Default.png';
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>
            {users.length > 0 ? `${t?.common?.totalUsers || "Total users:"} ${users.length}` : (t?.common?.noUsers || "No users to display.")}
          </DialogDescription>
        </DialogHeader>
        <ScrollArea className="h-[300px] w-full">
          <div className="space-y-4 pr-6">
            {users.length > 0 ? (
              users.map((user) => (
                <Link
                  key={user.id}
                  href={`/user/${user.username}`}
                  onClick={onClose}
                  className="flex items-center gap-4 p-2 rounded-lg hover:bg-muted transition-colors"
                >
                  <Avatar>
                    <AvatarImage 
                      src={getProfileImageUrl(user.profile_image_key)} 
                      alt={user.username} 
                      onError={(e) => { e.currentTarget.src = '/profiles/Default.png'; }}
                    />
                    <AvatarFallback>{user.username.substring(0, 2).toUpperCase()}</AvatarFallback>
                  </Avatar>
                  <span className="font-semibold">{user.username}</span>
                </Link>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <p>{t?.common?.nothingHere || "Nothing to see here."}</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
