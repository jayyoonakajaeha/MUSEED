"use client"

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts"

interface GenreData {
  name: string
  value: number
  color: string
}

interface GenreChartProps {
  data: GenreData[]
}

export function GenreChart({ data }: GenreChartProps) {
  return (
    <div className="w-full h-full min-h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%" // 수직 중앙 정렬
            labelLine={false}
            label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
            outerRadius={80} // 공간 채우기 위해 반지름 증가 
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--surface-elevated))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
            }}
            itemStyle={{
              color: "#FFFFFF",
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            wrapperStyle={{
              fontSize: '12px',
              paddingTop: '10px',
              width: '100%',
              display: 'flex',
              justifyContent: 'center',
              flexWrap: 'wrap'
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
