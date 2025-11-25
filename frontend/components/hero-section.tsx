"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Sparkles, TrendingUp, Users } from "lucide-react"
import { useLanguage } from "@/context/LanguageContext"
import { getGlobalStats } from "@/lib/api"

export function HeroSection() {
  const { t } = useLanguage()
  const [stats, setStats] = useState({ tracks: 0, users: 0, playlists: 0 })

  useEffect(() => {
    const fetchStats = async () => {
        const result = await getGlobalStats();
        if (result.success) {
            setStats(result.data);
        }
    }
    fetchStats();
  }, []);

  const formatNumber = (num: number) => {
      if (num >= 1000) {
          return `${(num / 1000).toFixed(1)}K+`;
      }
      if (num >= 100) {
          return `${Math.floor(num / 100) * 100}+`;
      }
      return num.toString();
  }

  return (
    <section className="relative py-20 md:py-32 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl opacity-20" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary/30 rounded-full blur-3xl opacity-20" />
      </div>

      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-elevated border border-border text-sm">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-muted-foreground">{t.hero.badge}</span>
          </div>

          {/* Heading */}
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight text-balance">
            {t.hero.title1}
            <br />
            {t.hero.title2} <span className="text-primary">AI</span>
          </h1>

          {/* Description */}
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto text-balance leading-relaxed">
            {t.hero.description}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              href="/create"
              className="w-full sm:w-auto px-8 py-4 bg-primary hover:bg-primary-hover text-primary-foreground rounded-xl font-semibold text-lg transition-all hover:shadow-lg hover:shadow-primary/20 hover:scale-105"
            >
              {t.hero.ctaCreate}
            </Link>
            <Link
              href="/discover"
              className="w-full sm:w-auto px-8 py-4 bg-surface-elevated hover:bg-border text-foreground rounded-xl font-semibold text-lg transition-all border border-border"
            >
              {t.hero.ctaExplore}
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 pt-12 max-w-2xl mx-auto">
            <div className="space-y-2">
              <div className="flex items-center justify-center gap-2 text-primary">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div className="text-3xl font-bold">{formatNumber(stats.tracks)}</div>
              <div className="text-sm text-muted-foreground">{t.hero.statTracks}</div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-center gap-2 text-primary">
                <Users className="h-5 w-5" />
              </div>
              <div className="text-3xl font-bold">{formatNumber(stats.users)}</div>
              <div className="text-sm text-muted-foreground">{t.hero.statUsers}</div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-center gap-2 text-primary">
                <Sparkles className="h-5 w-5" />
              </div>
              <div className="text-3xl font-bold">{formatNumber(stats.playlists)}</div>
              <div className="text-sm text-muted-foreground">{t.hero.statPlaylists}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
