"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Alert, Button, Col, Row, Segmented, Space, Table, Tag, Typography } from "antd";
import { LinkOutlined, PlusOutlined, ReloadOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import MetricCard from "@/components/dashboard/MetricCard";
import SetupChecklist from "@/components/dashboard/SetupChecklist";
import DashboardEmptyState from "@/components/dashboard/DashboardEmptyState";
import { useCommerceDashboardStore } from "@/stores/commerce-dashboard-store";
import { useAuthStore } from "@/stores/auth-store";
import type { RecentOrderSummary, TopCampaignSummary } from "@/lib/types";
import CommerceRevenueChart from "@/components/charts/CommerceRevenueChart";
import OrdersStatusChart from "@/components/charts/OrdersStatusChart";

const { Title, Text } = Typography;

const statusColors: Record<string, string> = {
  paid: "green",
  pending: "orange",
  failed: "red",
  refunded: "default",
};

const campaignStatusColors: Record<string, string> = {
  live: "green",
  draft: "default",
  ended: "red",
};

export default function DashboardPage() {
  const { user, fetchUser } = useAuthStore();
  const { overview, isLoading, error, periodDays, setPeriodDays, fetchCommerceOverview } =
    useCommerceDashboardStore();

  useEffect(() => {
    fetchUser();
    fetchCommerceOverview();
  }, [fetchUser, fetchCommerceOverview]);

  const kpis = overview?.kpis;
  const hasSales = (kpis?.orders_count ?? 0) > 0 || (kpis?.revenue ?? 0) > 0;

  const topCampaignColumns: ColumnsType<TopCampaignSummary> = [
    {
      title: "Campaign",
      dataIndex: "title",
      key: "title",
      render: (title: string, record) => (
        <div>
          <Text strong>{title}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.units_sold} sold
          </Text>
        </div>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => <Tag color={campaignStatusColors[status]}>{status.toUpperCase()}</Tag>,
    },
    {
      title: "Revenue",
      dataIndex: "revenue",
      key: "revenue",
      render: (v: number) => `$${Number(v).toFixed(2)}`,
    },
    {
      title: "",
      key: "action",
      render: (_: unknown, record) =>
        record.status === "live" ? (
          <Link href={`/campaign/${record.slug}`} target="_blank">
            <Button size="small">View</Button>
          </Link>
        ) : null,
    },
  ];

  const recentOrderColumns: ColumnsType<RecentOrderSummary> = [
    {
      title: "Customer",
      dataIndex: "customer_email",
      key: "customer_email",
      render: (email: string, record) => (
        <div>
          <Text>{email}</Text>
          {record.campaign_title && (
            <>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {record.campaign_title}
              </Text>
            </>
          )}
        </div>
      ),
    },
    {
      title: "Total",
      dataIndex: "total",
      key: "total",
      render: (v: number) => `$${Number(v).toFixed(2)}`,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>,
    },
    {
      title: "Date",
      dataIndex: "created_at",
      key: "created_at",
      render: (v: string) => new Date(v).toLocaleDateString(),
    },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <Title level={3} style={{ marginBottom: 4 }}>
            {user?.name ? `Welcome back, ${user.name}` : "Dashboard"}
          </Title>
          <Text type="secondary">
            {overview?.store?.name ? `${overview.store.name} — seller overview` : "Your store at a glance"}
          </Text>
        </div>
        <Space wrap>
          <Segmented
            options={[
              { label: "7 days", value: 7 },
              { label: "30 days", value: 30 },
              { label: "90 days", value: 90 },
            ]}
            value={periodDays}
            onChange={(v) => setPeriodDays(v as number)}
          />
          {overview?.store && (
            <a href={overview.store.storefront_url} target="_blank" rel="noreferrer">
              <Button icon={<LinkOutlined />}>View Storefront</Button>
            </a>
          )}
          <Link href="/campaigns/new">
            <Button type="primary" icon={<PlusOutlined />}>
              New Campaign
            </Button>
          </Link>
        </Space>
      </div>

      {error && (
        <Alert
          type="error"
          message={error}
          action={
            <Button size="small" icon={<ReloadOutlined />} onClick={fetchCommerceOverview}>
              Retry
            </Button>
          }
          style={{ marginBottom: 24 }}
        />
      )}

      {overview && <SetupChecklist setup={overview.setup} store={overview.store} />}

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Revenue"
            value={Number(kpis?.revenue ?? 0)}
            prefix="$"
            precision={2}
            changePct={kpis?.revenue_change_pct ?? null}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Orders" value={kpis?.orders_count ?? 0} loading={isLoading} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Units Sold" value={kpis?.units_sold ?? 0} loading={isLoading} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Live Campaigns" value={kpis?.live_campaigns ?? 0} loading={isLoading} />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Pending Orders"
            value={kpis?.orders_pending ?? 0}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Avg Order Value"
            value={Number(kpis?.avg_order_value ?? 0)}
            prefix="$"
            precision={2}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard title="Draft Campaigns" value={kpis?.draft_campaigns ?? 0} loading={isLoading} />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <CommerceRevenueChart data={overview?.revenue_by_day ?? []} loading={isLoading} />
        </Col>
        <Col xs={24} lg={12}>
          <OrdersStatusChart data={overview?.orders_by_status ?? []} loading={isLoading} />
        </Col>
      </Row>

      {!isLoading && overview && !hasSales && overview.top_campaigns.length === 0 ? (
        <DashboardEmptyState />
      ) : (
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Title level={5} style={{ marginBottom: 12 }}>
              Top Campaigns
            </Title>
            <Table
              rowKey="id"
              columns={topCampaignColumns}
              dataSource={overview?.top_campaigns ?? []}
              loading={isLoading}
              pagination={false}
              size="small"
            />
          </Col>
          <Col xs={24} lg={12}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <Title level={5} style={{ margin: 0 }}>
                Recent Orders
              </Title>
              <Link href="/orders">
                <Button type="link" size="small">
                  View all
                </Button>
              </Link>
            </div>
            <Table
              rowKey="id"
              columns={recentOrderColumns}
              dataSource={overview?.recent_orders ?? []}
              loading={isLoading}
              pagination={false}
              size="small"
            />
          </Col>
        </Row>
      )}
    </div>
  );
}
