"use client";

import { Card } from "antd";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface DataPoint {
  date: string;
  revenue: number;
  expenses: number;
}

interface RevenueChartProps {
  data: DataPoint[];
  loading?: boolean;
}

// Demo data for initial display
const demoData: DataPoint[] = [
  { date: "Jan", revenue: 45000, expenses: 32000 },
  { date: "Feb", revenue: 52000, expenses: 34000 },
  { date: "Mar", revenue: 48000, expenses: 30000 },
  { date: "Apr", revenue: 61000, expenses: 36000 },
  { date: "May", revenue: 55000, expenses: 33000 },
  { date: "Jun", revenue: 67000, expenses: 38000 },
];

export default function RevenueChart({ data, loading = false }: RevenueChartProps) {
  const chartData = data.length > 0 ? data : demoData;

  return (
    <Card title="Revenue vs Expenses" loading={loading}>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} />
          <Tooltip formatter={(v) => `$${Number(v).toLocaleString()}`} />
          <Area type="monotone" dataKey="revenue" stroke="#1677ff" fill="#1677ff20" name="Revenue" />
          <Area type="monotone" dataKey="expenses" stroke="#ff4d4f" fill="#ff4d4f20" name="Expenses" />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}
