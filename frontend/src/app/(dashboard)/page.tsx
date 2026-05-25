"use client";

import { useEffect } from "react";
import { Col, Row, Typography } from "antd";
import MetricCard from "@/components/dashboard/MetricCard";
import RevenueChart from "@/components/charts/RevenueChart";
import RoasChart from "@/components/charts/RoasChart";
import InsightCard from "@/components/insights/InsightCard";
import { useDashboardStore } from "@/stores/dashboard-store";

const { Title } = Typography;

// Demo insights for initial display before API is connected
const demoInsights = [
  {
    id: "1",
    insight_type: "recommendation",
    category: "blended",
    title: "Your Google Ads ROAS dropped 18% while COGS rose 5%",
    body_markdown:
      "Your advertising return on spend decreased from 3.2x to 2.6x this week. At the same time, your cost of goods sold increased by 5%. Consider pausing underperforming campaigns and investigating the supply cost increase.",
    severity: "warning",
    data_context: null,
    is_read: false,
    generated_at: new Date().toISOString(),
  },
  {
    id: "2",
    insight_type: "summary",
    category: "financial",
    title: "Cash runway is healthy at 8.5 months",
    body_markdown:
      "Based on your current burn rate of $12,500/month and cash on hand of $106,250, you have approximately 8.5 months of runway. Revenue growth of 12% month-over-month is extending this further.",
    severity: "info",
    data_context: null,
    is_read: false,
    generated_at: new Date().toISOString(),
  },
  {
    id: "3",
    insight_type: "alert",
    category: "marketing",
    title: "Brand Search campaign is your top performer at 5.2x ROAS",
    body_markdown:
      "Consider increasing budget allocation to Brand Search. It consistently outperforms other campaigns and has room to scale based on impression share data.",
    severity: "info",
    data_context: null,
    is_read: true,
    generated_at: new Date().toISOString(),
  },
];

export default function DashboardPage() {
  const { overview, isLoading, fetchOverview, fetchCampaigns, fetchInsights } = useDashboardStore();

  useEffect(() => {
    fetchOverview();
    fetchCampaigns();
    fetchInsights();
  }, [fetchOverview, fetchCampaigns, fetchInsights]);

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        Dashboard Overview
      </Title>

      {/* Financial Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Revenue"
            value={overview?.financial.revenue ?? 67000}
            prefix="$"
            precision={0}
            changePct={overview?.financial.revenue_change_pct ?? 12.3}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Net Income"
            value={overview?.financial.net_income ?? 29000}
            prefix="$"
            precision={0}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Cash on Hand"
            value={overview?.financial.cash_on_hand ?? 106250}
            prefix="$"
            precision={0}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Gross Margin"
            value={overview?.financial.gross_margin_pct ?? 43.3}
            suffix="%"
            precision={1}
            loading={isLoading}
          />
        </Col>
      </Row>

      {/* Marketing Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Ad Spend"
            value={overview?.marketing.total_spend ?? 12800}
            prefix="$"
            precision={0}
            changePct={overview?.marketing.spend_change_pct ?? -5.2}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Conversions"
            value={overview?.marketing.total_conversions ?? 342}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Overall ROAS"
            value={overview?.marketing.overall_roas ?? 2.8}
            suffix="x"
            precision={1}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Est. CAC"
            value={overview?.estimated_cac ?? 37.4}
            prefix="$"
            precision={2}
            loading={isLoading}
          />
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <RevenueChart data={[]} loading={isLoading} />
        </Col>
        <Col xs={24} lg={12}>
          <RoasChart data={[]} loading={isLoading} />
        </Col>
      </Row>

      {/* AI Insights */}
      <Title level={4} style={{ marginBottom: 16 }}>
        AI Insights
      </Title>
      {demoInsights.map((insight) => (
        <InsightCard key={insight.id} insight={insight} />
      ))}
    </div>
  );
}
