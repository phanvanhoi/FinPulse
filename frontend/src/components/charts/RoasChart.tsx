"use client";

import { Card } from "antd";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

interface CampaignRoas {
  name: string;
  roas: number;
  spend: number;
}

interface RoasChartProps {
  data: CampaignRoas[];
  loading?: boolean;
}

const demoData: CampaignRoas[] = [
  { name: "Brand Search", roas: 5.2, spend: 3200 },
  { name: "Retargeting", roas: 3.8, spend: 2100 },
  { name: "Display", roas: 1.4, spend: 4500 },
  { name: "Social", roas: 2.1, spend: 1800 },
  { name: "Video", roas: 0.8, spend: 1200 },
];

export default function RoasChart({ data, loading = false }: RoasChartProps) {
  const chartData = data.length > 0 ? data : demoData;

  return (
    <Card title="ROAS by Campaign" loading={loading}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="name" type="category" width={120} />
          <Tooltip formatter={(v) => `${Number(v).toFixed(2)}x`} />
          <ReferenceLine x={1} stroke="#ff4d4f" strokeDasharray="3 3" label="Break-even" />
          <Bar
            dataKey="roas"
            fill="#1677ff"
            radius={[0, 4, 4, 0]}
            label={{ position: "right", formatter: (v: unknown) => `${Number(v).toFixed(1)}x` }}
          />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
