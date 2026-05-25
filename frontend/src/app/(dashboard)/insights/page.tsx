"use client";

import { useState } from "react";
import { Typography, Segmented, Empty } from "antd";
import InsightCard from "@/components/insights/InsightCard";
import type { Insight } from "@/lib/types";

const { Title } = Typography;

const demoInsights: Insight[] = [
  {
    id: "1",
    insight_type: "alert",
    category: "blended",
    title: "Marketing spend is 19% of revenue - approaching your 20% cap",
    body_markdown:
      "This month's ad spend ($12,800) represents 19.1% of your revenue ($67,000). Your configured threshold is 20%. If the current spend rate continues, you'll exceed the cap by next Tuesday. Consider reviewing campaign performance and pausing low-ROAS campaigns.",
    severity: "warning",
    data_context: null,
    is_read: false,
    generated_at: new Date().toISOString(),
  },
  {
    id: "2",
    insight_type: "recommendation",
    category: "marketing",
    title: "Shift $800 from Display to Brand Search for better ROAS",
    body_markdown:
      "Brand Search consistently delivers 5.2x ROAS while Display only manages 1.4x. Moving $800/month from Display to Brand Search could generate an estimated additional $3,040 in attributed revenue based on historical conversion rates.",
    severity: "info",
    data_context: null,
    is_read: false,
    generated_at: new Date().toISOString(),
  },
  {
    id: "3",
    insight_type: "summary",
    category: "financial",
    title: "Weekly Financial Summary: Revenue up 12%, margins stable",
    body_markdown:
      "Revenue grew 12.3% month-over-month to $67,000. Gross margin remains stable at 43.3%. Net income of $29,000 represents a healthy 43% net margin. Cash position is strong at $106,250 (8.5 months runway). No significant expense anomalies detected.",
    severity: "info",
    data_context: null,
    is_read: true,
    generated_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: "4",
    insight_type: "anomaly",
    category: "financial",
    title: "Software costs jumped 12% - new subscription detected",
    body_markdown:
      "Your Software & Tools category increased by $340 this month (12% increase). This appears to be from a new subscription. Verify this is an expected expense.",
    severity: "warning",
    data_context: null,
    is_read: false,
    generated_at: new Date(Date.now() - 172800000).toISOString(),
  },
];

export default function InsightsPage() {
  const [filter, setFilter] = useState<string>("all");

  const filtered =
    filter === "all"
      ? demoInsights
      : demoInsights.filter((i) => i.category === filter);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>AI Insights</Title>
        <Segmented
          options={[
            { label: "All", value: "all" },
            { label: "Financial", value: "financial" },
            { label: "Marketing", value: "marketing" },
            { label: "Blended", value: "blended" },
          ]}
          value={filter}
          onChange={(v) => setFilter(v as string)}
        />
      </div>

      {filtered.length === 0 ? (
        <Empty description="No insights in this category" />
      ) : (
        filtered.map((insight) => (
          <InsightCard key={insight.id} insight={insight} onDismiss={() => {}} />
        ))
      )}
    </div>
  );
}
