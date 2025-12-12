"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Music, Home, PlusCircle, User, Search, LogOut, LogIn, Languages } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/context/AuthContext"
import { useLanguage } from "@/context/LanguageContext"
import { Button } from "@/components/ui/button"

export function Navigation() {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const { language, setLanguage, t } = useLanguage()

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'ko' : 'en');
  }

  interface NavItem {
    label: string
    icon: any
    href?: string
    action?: () => void
  }

  const navItems = [
    { href: "/dashboard", label: t.nav.home, icon: Home },
    { href: "/discover", label: t.nav.discover, icon: Search },
    { href: "/create", label: t.nav.create, icon: PlusCircle },
  ]

  // 모바일 네비게이션을 위한 프로필 링크 및 언어 토글 추가
  const mobileNavItems: NavItem[] = user
    ? [
      ...navItems,
      { href: `/user/${user.username}`, label: t.nav.profile, icon: User },
      { label: language === 'en' ? 'KO' : 'EN', icon: Languages, action: toggleLanguage }
    ]
    : [ // 비로그인 상태일 때도 언어 선택 버튼 포함
      ...navItems,
      { href: "/login", label: t.nav.signIn, icon: User },
      { label: language === 'en' ? 'KO' : 'EN', icon: Languages, action: toggleLanguage }
    ]

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* 로고 */}
          <Link href="/dashboard" className="flex items-center gap-2 group flex-shrink-0">
            <div className="relative">
              <Music className="h-7 w-7 text-primary transition-transform group-hover:scale-110" />
              <div className="absolute inset-0 bg-primary/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <span className="text-xl font-bold tracking-tight">MUSEED</span>
          </Link>

          {/* 데스크탑 네비게이션 */}
          <div className="hidden lg:flex items-center gap-1 flex-1 justify-center">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-surface-elevated",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              )
            })}
          </div>

          {/* 유저 액션 (데스크탑) */}
          <div className="hidden lg:flex items-center gap-3 flex-shrink-0">
            <Button variant="ghost" size="sm" onClick={toggleLanguage} className="text-muted-foreground hover:text-foreground">
              <Languages className="h-4 w-4 mr-1" />
              {language === 'en' ? 'KO' : 'EN'}
            </Button>
            {user ? (
              <>
                <Link
                  href={`/user/${user.username}`}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all text-muted-foreground hover:text-foreground hover:bg-surface-elevated"
                >
                  <User className="h-4 w-4" />
                  {t.nav.profile}
                </Link>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
                >
                  <LogOut className="h-4 w-4" />
                  {t.nav.signOut}
                </Button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-surface-elevated hover:bg-border text-sm font-medium transition-all"
                >
                  {t.nav.signIn}
                </Link>
                <Link
                  href="/signup"
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-medium transition-all"
                >
                  {t.nav.getStarted}
                </Link>
              </>
            )}
          </div>

          {/* 모바일 헤더 액션 (로그인/로그아웃) */}
          <div className="flex lg:hidden items-center gap-1 flex-shrink-0">
            {!user ? (
              <Link href="/login" className="text-muted-foreground hover:text-foreground p-2 active:scale-95 transition-transform">
                <LogIn className="h-6 w-6" />
              </Link>
            ) : (
              <button onClick={logout} className="text-muted-foreground hover:text-foreground p-2 active:scale-95 transition-transform">
                <LogOut className="h-6 w-6" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 모바일 네비게이션 (하단) */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 border-t border-border bg-background/95 backdrop-blur-xl pb-safe">
        <div className="flex items-center justify-around px-2 py-2">
          {mobileNavItems.map((item, index) => {
            const Icon = item.icon
            const isActive = item.href ? pathname === item.href : false

            if (item.action) {
              return (
                <button
                  key={index}
                  onClick={item.action}
                  className="flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-all active:scale-90 text-muted-foreground hover:text-foreground"
                >
                  <Icon className="h-5 w-5" />
                  <span className="text-[10px] font-medium">{item.label}</span>
                </button>
              )
            }

            return (
              <Link
                key={index}
                href={item.href!}
                className={cn(
                  "flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-all active:scale-90",
                  isActive ? "text-primary" : "text-muted-foreground",
                )}
              >
                <Icon className="h-5 w-5" />
                <span className="text-[10px] font-medium">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
