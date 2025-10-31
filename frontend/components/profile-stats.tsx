import { Music, Heart, Users, Award } from "lucide-react"

interface ProfileStatsProps {
  playlistsCreated: number
  playlistsLiked: number
  followers: number
  following: number
}

export function ProfileStats({ playlistsCreated, playlistsLiked, followers, following }: ProfileStatsProps) {
  const stats = [
    { label: "Playlists Created", value: playlistsCreated, icon: Music, color: "text-primary" },
    { label: "Playlists Liked", value: playlistsLiked, icon: Heart, color: "text-primary" },
    { label: "Followers", value: followers, icon: Users, color: "text-primary" },
    { label: "Following", value: following, icon: Award, color: "text-primary" },
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <div key={stat.label} className="bg-surface-elevated border border-border rounded-xl p-6 space-y-3">
            <div className="flex items-center justify-between">
              <Icon className={`h-5 w-5 ${stat.color}`} />
            </div>
            <div>
              <div className="text-3xl font-bold">{stat.value}</div>
              <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
