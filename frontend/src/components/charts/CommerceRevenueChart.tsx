"use client";

import { Card, Empty } from "antd";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RevenueByDay } from "@/lib/types";

interface CommerceRevenueChartProps {
  data: RevenueByDay[];
  loading?: boolean;
}

function formatDateLabel(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function CommerceRevenueChart({ data, loading = false }: CommerceRevenueChartProps) {
  const chartData = data.map((row) => ({
    date: formatDateLabel(row.date),
    revenue: Number(row.revenue),
    orders: row.orders,
  }));

  const hasRevenue = chartData.some((row) => row.revenue > 0);

  return (
    <Card title="Revenue Trend" loading={loading} style={{ height: "100%" }}>
      {!hasRevenue && !loading ? (
        <Empty description="No paid orders in this period" style={{ padding: "48px 0" }} />
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis tickFormatter={(v) => `$${v}`} width={56} />
            <Tooltip
              formatter={(value, name) =>
                name === "revenue" ? [`$${Number(value).toFixed(2)}`, "Revenue"] : [value, "Orders"]
              }
            />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#1677ff"
              fill="#1677ff20"
              name="revenue"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
