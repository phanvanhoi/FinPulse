"use client";

import { Col, Row, Typography, Card, Table, Tag } from "antd";
import MetricCard from "@/components/dashboard/MetricCard";
import RoasChart from "@/components/charts/RoasChart";

const { Title } = Typography;

const campaignColumns = [
  { title: "Campaign", dataIndex: "name", key: "name" },
  { title: "Status", dataIndex: "status", key: "status", render: (v: string) => (
    <Tag color={v === "active" ? "green" : v === "paused" ? "orange" : "default"}>{v.toUpperCase()}</Tag>
  )},
  { title: "Spend", dataIndex: "spend", key: "spend", render: (v: number) => `$${v.toLocaleString()}` },
  { title: "Clicks", dataIndex: "clicks", key: "clicks", render: (v: number) => v.toLocaleString() },
  { title: "Conversions", dataIndex: "conversions", key: "conversions" },
  { title: "CPC", dataIndex: "cpc", key: "cpc", render: (v: number) => `$${v.toFixed(2)}` },
  { title: "ROAS", dataIndex: "roas", key: "roas", render: (v: number) => (
    <span style={{ color: v >= 1 ? "#52c41a" : "#ff4d4f", fontWeight: 600 }}>{v.toFixed(1)}x</span>
  )},
];

const demoCampaigns = [
  { key: "1", name: "Brand Search", status: "active", spend: 3200, clicks: 4800, conversions: 120, cpc: 0.67, roas: 5.2 },
  { key: "2", name: "Retargeting", status: "active", spend: 2100, clicks: 1200, conversions: 85, cpc: 1.75, roas: 3.8 },
  { key: "3", name: "Display Awareness", status: "active", spend: 4500, clicks: 8200, conversions: 45, cpc: 0.55, roas: 1.4 },
  { key: "4", name: "Social - Instagram", status: "active", spend: 1800, clicks: 2100, conversions: 62, cpc: 0.86, roas: 2.1 },
  { key: "5", name: "Video - YouTube", status: "paused", spend: 1200, clicks: 900, conversions: 30, cpc: 1.33, roas: 0.8 },
];

export default function MarketingPage() {
  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>Marketing Performance</Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Total Ad Spend" value={12800} prefix="$" changePct={-5.2} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Total Conversions" value={342} changePct={15.8} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Overall ROAS" value={2.8} suffix="x" precision={1} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Avg. CPC" value={0.94} prefix="$" precision={2} changePct={-3.1} />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <RoasChart data={[]} />
        </Col>
      </Row>

      <Card title="Campaign Performance">
        <Table columns={campaignColumns} dataSource={demoCampaigns} pagination={false} />
      </Card>
    </div>
  );
}
