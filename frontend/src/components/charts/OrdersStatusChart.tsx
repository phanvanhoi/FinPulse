"use client";

import { Card, Empty } from "antd";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { OrdersByStatus } from "@/lib/types";

interface OrdersStatusChartProps {
  data: OrdersByStatus[];
  loading?: boolean;
  compact?: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  paid: "#52c41a",
  pending: "#faad14",
  failed: "#ff4d4f",
  refunded: "#8c8c8c",
};

export default function OrdersStatusChart({ data, loading = false, compact = false }: OrdersStatusChartProps) {
  const chartData = data.map((row) => ({
    status: row.status.charAt(0).toUpperCase() + row.status.slice(1),
    count: row.count,
    key: row.status,
  }));

  const hasOrders = chartData.some((row) => row.count > 0);

  return (
    <Card title="Orders by Status" loading={loading} style={{ height: "100%" }}>
      {!hasOrders && !loading ? (
        <Empty description="No orders in this period" style={{ padding: "48px 0" }} />
      ) : (
        <ResponsiveContainer width="100%" height={compact ? 220 : 280}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="status" />
            <YAxis allowDecimals={false} width={32} />
            <Tooltip />
            <Bar dataKey="count" name="Orders" radius={[4, 4, 0, 0]}>
              {chartData.map((row) => (
                <Cell key={row.key} fill={STATUS_COLORS[row.key] ?? "#1677ff"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
