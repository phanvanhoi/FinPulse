"use client";

import { Col, Row, Typography, Card, Table } from "antd";
import MetricCard from "@/components/dashboard/MetricCard";
import RevenueChart from "@/components/charts/RevenueChart";

const { Title } = Typography;

const expenseColumns = [
  { title: "Category", dataIndex: "category", key: "category" },
  { title: "Amount", dataIndex: "amount", key: "amount", render: (v: number) => `$${v.toLocaleString()}` },
  { title: "% of Total", dataIndex: "pct", key: "pct", render: (v: number) => `${v}%` },
  { title: "Change", dataIndex: "change", key: "change", render: (v: number) => (
    <span style={{ color: v >= 0 ? "#ff4d4f" : "#52c41a" }}>{v >= 0 ? "+" : ""}{v}%</span>
  )},
];

const demoExpenses = [
  { key: "1", category: "Payroll", amount: 18000, pct: 47, change: 3 },
  { key: "2", category: "Marketing", amount: 12800, pct: 34, change: -5 },
  { key: "3", category: "Software & Tools", amount: 3200, pct: 8, change: 12 },
  { key: "4", category: "Office & Utilities", amount: 2500, pct: 7, change: 0 },
  { key: "5", category: "Other", amount: 1500, pct: 4, change: -8 },
];

export default function FinancePage() {
  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>Financial Overview</Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Revenue" value={67000} prefix="$" changePct={12.3} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Net Income" value={29000} prefix="$" changePct={8.1} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Cash on Hand" value={106250} prefix="$" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Cash Runway" value={8.5} suffix=" months" precision={1} />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={14}>
          <RevenueChart data={[]} />
        </Col>
        <Col xs={24} lg={10}>
          <Card title="Accounts Receivable & Payable">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <MetricCard title="Receivable" value={23400} prefix="$" />
              </Col>
              <Col span={12}>
                <MetricCard title="Payable" value={15200} prefix="$" />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Card title="Expense Breakdown">
        <Table columns={expenseColumns} dataSource={demoExpenses} pagination={false} />
      </Card>
    </div>
  );
}
