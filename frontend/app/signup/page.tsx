"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Music } from "lucide-react"
import { registerUser } from "@/lib/api"
import { useLanguage } from "@/context/LanguageContext"

export default function SignupPage() {
  const router = useRouter()
  const { t } = useLanguage()
  const [username, setUsername] = useState("")
  const [nickname, setNickname] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (password !== confirmPassword) {
      setError(t.toast.passwordsMismatch)
      return
    }

    setLoading(true)
    // 변경됨: 이메일 제거, 닉네임 추가
    const result = await registerUser({ username, nickname, password })
    setLoading(false)

    if (result.success) {
      // 가입 성공 시 로그인 페이지로 이동
      router.push("/login")
    } else {
      // 에러 발생 시 표시
      setError(result.error || "Failed to create an account.")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-background to-primary/5">
      <Card className="w-full max-w-md border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader className="space-y-4 text-center">
          <div className="flex justify-center">
            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Music className="h-6 w-6 text-primary" />
            </div>
          </div>
          <div>
            <CardTitle className="text-2xl">{t.auth.createAccount}</CardTitle>
            <CardDescription>{t.auth.signupSubtitle}</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSignup} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">{t.auth.username}</Label>
              <Input
                id="username"
                type="text"
                placeholder={t.auth.username}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="nickname">{t.auth.nickname}</Label>
              <Input
                id="nickname"
                type="text"
                placeholder={t.auth.nickname}
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">{t.auth.password}</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-password">{t.common.confirm} {t.auth.password}</Label>
              <Input
                id="confirm-password"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? t.auth.signingUp : t.auth.signUp}
            </Button>
          </form>
          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">{t.auth.hasAccount} </span>
            <Link href="/login" className="text-primary hover:underline">
              {t.auth.signIn}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}