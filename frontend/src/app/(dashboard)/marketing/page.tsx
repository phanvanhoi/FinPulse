"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Alert, Col, Row, Segmented, Table, Typography } from "antd";
import MetricCard from "@/components/dashboard/MetricCard";
import api from "@/lib/api";
import type { CommerceDashboardOverview, TopCampaignSummary } from "@/lib/types";

const { Title, Text } = Typography;

export default function MarketingPage() {
  const [overview, setOverview] = useState<CommerceDashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [periodDays, setPeriodDays] = useState(30);

  useEffect(() => {
    setLoading(true);
    api
      .get<CommerceDashboardOverview>("/dashboard/commerce-overview", { params: { period_days: periodDays } })
      .then(({ data }) => setOverview(data))
      .finally(() => setLoading(false));
  }, [periodDays]);

  const marketing = overview?.marketing_snapshot;
  const kpis = overview?.kpis;
  const isAds = marketing?.source === "ads";

  const campaignColumns = [
    { title: "Campaign", dataIndex: "title", key: "title" },
    { title: "Status", dataIndex: "status", key: "status", render: (v: string) => v.toUpperCase() },
    { title: "Units Sold", dataIndex: "units_sold", key: "units_sold" },
    {
      title: "Revenue",
      dataIndex: "revenue",
      key: "revenue",
      render: (v: number) => `$${Number(v).toFixed(2)}`,
    },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <Title level={3} style={{ margin: 0 }}>Marketing Performance</Title>
        <Segmented
          options={[
            { label: "7d", value: 7 },
            { label: "30d", value: 30 },
            { label: "90d", value: 90 },
          ]}
          value={periodDays}
          onChange={(v) => setPeriodDays(v as number)}
        />
      </div>

      {!isAds && (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
          message="Showing sales campaign performance"
          description={
            <>
              Metrics below come from your live FinPulse campaigns and paid orders.
              Connect Google Ads in <Link href="/settings/connections">Connections</Link> for ad spend and ROAS when available.
            </>
          }
        />
      )}

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title={isAds ? "Ad Spend" : "Live Campaigns"}
            value={isAds ? Number(marketing?.ad_spend ?? 0) : (marketing?.live_campaigns ?? kpis?.live_campaigns ?? 0)}
            prefix={isAds ? "$" : undefined}
            precision={isAds ? 2 : 0}
            loading={loading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Units Sold" value={marketing?.units_sold ?? kpis?.units_sold ?? 0} loading={loading} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Overall ROAS"
            value={marketing?.overall_roas != null ? Number(marketing.overall_roas) : 0}
            suffix={marketing?.overall_roas != null ? "x" : undefined}
            precision={1}
            loading={loading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Store Revenue" value={Number(kpis?.revenue ?? 0)} prefix="$" precision={2} loading={loading} />
        </Col>
      </Row>

      {!isAds && (
        <>
          <Title level={5} style={{ marginBottom: 12 }}>Top Sales Campaigns</Title>
          <Table<TopCampaignSummary>
            rowKey="id"
            columns={campaignColumns}
            dataSource={overview?.top_campaigns ?? []}
            loading={loading}
            pagination={false}
          />
          {marketing?.detail && (
            <Text type="secondary" style={{ display: "block", marginTop: 16 }}>
              {marketing.detail}
            </Text>
          )}
        </>
      )}
    </div>
  );
}
