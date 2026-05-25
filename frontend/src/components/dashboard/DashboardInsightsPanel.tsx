"use client";

import Link from "next/link";
import { Button, Card, Typography } from "antd";
import { BulbOutlined } from "@ant-design/icons";
import InsightCard from "@/components/insights/InsightCard";
import type { CommerceInsightPreview } from "@/lib/types";
import type { Insight } from "@/lib/types";

const { Title } = Typography;

interface DashboardInsightsPanelProps {
  insights: CommerceInsightPreview[];
  loading?: boolean;
}

function toInsight(preview: CommerceInsightPreview, index: number): Insight {
  return {
    id: `preview-${index}`,
    insight_type: preview.insight_type,
    category: preview.category,
    title: preview.title,
    body_markdown: preview.body_markdown,
    severity: preview.severity,
    data_context: null,
    is_read: false,
    generated_at: new Date().toISOString(),
  };
}

export default function DashboardInsightsPanel({ insights, loading }: DashboardInsightsPanelProps) {
  if (!loading && insights.length === 0) return null;

  const top = insights.slice(0, 3);

  return (
    <Card
      loading={loading}
      title={
        <>
          <BulbOutlined /> AI Insights
        </>
      }
      extra={
        <Link href="/insights">
          <Button type="link" size="small">
            View all
          </Button>
        </Link>
      }
      style={{ marginBottom: 24 }}
    >
      {top.map((item, index) => (
        <InsightCard key={`${item.title}-${index}`} insight={toInsight(item, index)} />
      ))}
    </Card>
  );
}
