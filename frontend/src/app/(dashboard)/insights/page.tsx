"use client";

import { useEffect, useState } from "react";
import { Alert, Button, Empty, Segmented, Spin, Typography } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import InsightCard from "@/components/insights/InsightCard";
import { useInsightsStore } from "@/stores/insights-store";

const { Title } = Typography;

export default function InsightsPage() {
  const [filter, setFilter] = useState<string>("all");
  const { items, isLoading, isRefreshing, error, fetchInsights, refreshInsights, dismissInsight } =
    useInsightsStore();

  useEffect(() => {
    fetchInsights(1, filter);
  }, [fetchInsights, filter]);

  const filtered =
    filter === "all" ? items : items.filter((i) => i.category === filter);

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24,
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <Title level={3} style={{ margin: 0 }}>
          AI Insights
        </Title>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
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
          <Button icon={<ReloadOutlined />} loading={isRefreshing} onClick={refreshInsights}>
            Refresh insights
          </Button>
        </div>
      </div>

      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}

      {isLoading ? (
        <div style={{ textAlign: "center", padding: 48 }}>
          <Spin />
        </div>
      ) : filtered.length === 0 ? (
        <Empty description="No insights yet. Click Refresh to generate recommendations from your store data.">
          <Button type="primary" loading={isRefreshing} onClick={refreshInsights}>
            Generate insights
          </Button>
        </Empty>
      ) : (
        filtered.map((insight) => (
          <InsightCard key={insight.id} insight={insight} onDismiss={dismissInsight} />
        ))
      )}
    </div>
  );
}
