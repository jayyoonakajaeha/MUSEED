"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { getUserProfile, updateUserProfile } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"

export default function EditProfilePage() {
  const { user, token, logout } = useAuth()
  const router = useRouter()
  
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    if (user && token) {
      const fetchProfile = async () => {
        setLoading(true)
        const result = await getUserProfile(user.username, token)
        if (result.success) {
          setUsername(result.data.username)
          setEmail(result.data.email)
        } else {
          setError("Failed to load user data.")
        }
        setLoading(false)
      }
      fetchProfile()
    } else if (token === null) { // Only run if token is explicitly null (not undefined)
        router.push("/login")
    }
  }, [user, token, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setSuccess(null)

    if (password && password !== confirmPassword) {
      setError("Passwords do not match.")
      setSaving(false)
      return
    }

    if (user && token) {
      const updateData: { username?: string; email?: string; password?: string } = {}
      let usernameChanged = false;
      
      if (username && username !== user.username) {
        updateData.username = username;
        usernameChanged = true;
      }
      if (email) updateData.email = email
      if (password) updateData.password = password

      const result = await updateUserProfile(user.username, token, updateData)
      if (result.success) {
        if (usernameChanged) {
            alert("Username changed successfully! Please log in again with your new username.");
            logout();
            router.push("/login");
        } else {
            setSuccess("Profile updated successfully!")
            setTimeout(() => router.push(`/user/${user.username}`), 1500)
        }
      } else {
        setError(result.error || "Failed to update profile.")
      }
    }
    setSaving(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-16 w-16 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <main className="min-h-screen py-24">
      <div className="container mx-auto px-4 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Edit Profile</CardTitle>
            <CardDescription>Update your account details. Leave password fields blank to keep it unchanged.</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">New Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col items-start">
              <Button type="submit" disabled={saving}>
                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                {saving ? "Saving..." : "Save Changes"}
              </Button>
              {error && <p className="mt-4 text-sm text-destructive">{error}</p>}
              {success && <p className="mt-4 text-sm text-green-600">{success}</p>}
            </CardFooter>
          </form>
        </Card>
      </div>
    </main>
  )
}