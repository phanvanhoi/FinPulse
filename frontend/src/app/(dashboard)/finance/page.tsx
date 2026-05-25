"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Alert, Col, Row, Segmented, Typography } from "antd";
import MetricCard from "@/components/dashboard/MetricCard";
import CommerceRevenueChart from "@/components/charts/CommerceRevenueChart";
import api from "@/lib/api";
import type { CommerceDashboardOverview } from "@/lib/types";

const { Title, Text } = Typography;

export default function FinancePage() {
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

  const finance = overview?.finance_snapshot;
  const kpis = overview?.kpis;
  const isAccounting = finance?.source === "accounting";

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <Title level={3} style={{ margin: 0 }}>Financial Overview</Title>
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

      {!isAccounting && (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
          message="Showing store sales data"
          description={
            <>
              Revenue below comes from paid orders in your FinPulse store.
              Connect QuickBooks in <Link href="/settings/connections">Connections</Link> for full P&amp;L when available.
            </>
          }
        />
      )}

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Revenue"
            value={Number(finance?.revenue ?? kpis?.revenue ?? 0)}
            prefix="$"
            precision={2}
            changePct={kpis?.revenue_change_pct ?? null}
            loading={loading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Net Income"
            value={finance?.net_income != null ? Number(finance.net_income) : 0}
            prefix="$"
            precision={2}
            loading={loading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Cash on Hand"
            value={finance?.cash_on_hand != null ? Number(finance.cash_on_hand) : 0}
            prefix="$"
            precision={2}
            loading={loading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Paid Orders" value={kpis?.orders_count ?? 0} loading={loading} />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <CommerceRevenueChart data={overview?.revenue_by_day ?? []} loading={loading} />
        </Col>
        <Col xs={24} lg={10}>
          <MetricCard title="Avg Order Value" value={Number(kpis?.avg_order_value ?? 0)} prefix="$" precision={2} loading={loading} />
          {finance?.detail && (
            <Text type="secondary" style={{ display: "block", marginTop: 16 }}>
              {finance.detail}
            </Text>
          )}
        </Col>
      </Row>
    </div>
  );
}
