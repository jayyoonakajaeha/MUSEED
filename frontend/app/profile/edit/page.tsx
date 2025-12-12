"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { getUserProfile, updateUserProfile } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, ArrowLeft } from "lucide-react"
import { toast } from "@/components/ui/use-toast"
import { useLanguage } from "@/context/LanguageContext"

interface UserProfile {
  username: string;
  nickname: string;
  email: string | null;
}

export default function EditProfilePage() {
  const router = useRouter()
  const { user, token, login } = useAuth() // 토큰 변경 시 login 필요 (여기선 드물지만 좋은 관습)
  const { t } = useLanguage()

  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [profile, setProfile] = useState<UserProfile | null>(null)

  const [nickname, setNickname] = useState("")
  // const [email, setEmail] = useState("") // 사용자 요청에 따라 제거됨
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  useEffect(() => {
    if (!token || !user) {
      router.push("/login")
      return
    }

    const loadProfile = async () => {
      const result = await getUserProfile(user.username, token)
      if (result.success) {
        setProfile(result.data)
        setNickname(result.data.nickname)
        // setEmail(result.data.email || "") // 사용자 요청에 따라 제거됨
      } else {
        toast({
          title: t.toast.error,
          description: "프로필 데이터를 불러오지 못했습니다.", // 일반적인 폴백 경고
          variant: "destructive",
        })
      }
      setIsLoading(false)
    }

    loadProfile()
  }, [token, user, router, t])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token || !user) return

    if (password && password !== confirmPassword) {
      toast({
        title: t.toast.error,
        description: t.toast.passwordsMismatch,
        variant: "destructive",
      })
      return
    }

    setIsSaving(true)

    const updateData: any = {
      nickname,
      // email: email || null, // 사용자 요청에 따라 제거됨
    }

    if (password) {
      updateData.password = password
    }

    const result = await updateUserProfile(user.username, token, updateData)

    if (result.success) {
      toast({
        title: t.toast.success,
        description: t.toast.profileUpdatedDesc,
      })
      router.push(`/user/${user.username}`)
    } else {
      toast({
        title: t.toast.error,
        description: result.error || "Failed to update profile.",
        variant: "destructive",
      })
    }
    setIsSaving(false)
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="container max-w-2xl mx-auto py-24 px-4">
      <Button
        variant="ghost"
        className="mb-6 pl-0 hover:bg-transparent hover:text-primary"
        onClick={() => router.back()}
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        {t.profile.profile}
      </Button>

      <Card className="border border-primary">
        <CardHeader>
          <CardTitle>{t.profile.editProfile}</CardTitle>
          <CardDescription>{t.profile.updateInfoDesc}</CardDescription>
        </CardHeader>
        <form onSubmit={handleSave}>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="username">{t.auth.username}</Label>
              <Input
                id="username"
                value={profile?.username || ""}
                disabled
                className="bg-muted"
              />
              <p className="text-xs text-muted-foreground">{t.profile.usernameHint}</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="nickname">{t.auth.nickname}</Label>
              <Input
                id="nickname"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                required
              />
            </div>
            {/* Email field removed as per user request */}

            <div className="space-y-2">
              <Label htmlFor="password">{t.auth.password}</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t.profile.passwordPlaceholder}
              />
            </div>

            {password && (
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">{t.common.confirm} {t.auth.password}</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
            )}
          </CardContent>
          <CardFooter className="flex justify-end gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={isSaving}
            >
              {t.common.cancel}
            </Button>
            <Button type="submit" disabled={isSaving}>
              {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {t.common.save}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
