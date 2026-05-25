"use client";

import { useEffect, useState } from "react";
import { Button, Space, Table, Tag, Typography, message } from "antd";
import { DownloadOutlined, ReloadOutlined } from "@ant-design/icons";
import api from "@/lib/api";
import { downloadCsv } from "@/lib/export-csv";
import type { Order } from "@/lib/types/order";

const { Title, Text } = Typography;

const statusColors: Record<string, string> = {
  pending: "orange",
  paid: "green",
  failed: "red",
  refunded: "default",
};

const fulfillmentColors: Record<string, string> = {
  pending: "default",
  submitted: "blue",
  unpaid: "gold",
  in_production: "processing",
  shipped: "cyan",
  delivered: "green",
  failed: "red",
  cancelled: "default",
};

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [retryingId, setRetryingId] = useState<string | null>(null);

  const loadOrders = () => {
    setLoading(true);
    api
      .get<{ orders: Order[]; total: number }>("/orders")
      .then(({ data }) => setOrders(data.orders))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const handleExportPage = () => {
    if (orders.length === 0) {
      message.info("No orders to export");
      return;
    }
    downloadCsv(
      `orders-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Order ID", "Campaign", "Customer", "Total", "Status", "Fulfillment", "Tracking", "Date"],
      orders.map((o) => [
        o.id,
        o.campaign_title ?? "",
        o.customer_email,
        Number(o.total).toFixed(2),
        o.status,
        o.fulfillment_status ?? "",
        o.tracking_number ?? "",
        new Date(o.created_at).toISOString(),
      ])
    );
    message.success("Orders exported");
  };

  const handleExportAll = async () => {
    setExporting(true);
    try {
      const { data } = await api.get<Blob>("/orders/export/csv", { responseType: "blob" });
      const url = URL.createObjectURL(data);
      const link = document.createElement("a");
      link.href = url;
      link.download = `orders-export-${new Date().toISOString().slice(0, 10)}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      message.success("Full export downloaded");
    } catch {
      message.error("Export failed");
    } finally {
      setExporting(false);
    }
  };

  const handleRetryFulfillment = async (orderId: string) => {
    setRetryingId(orderId);
    try {
      await api.post(`/orders/${orderId}/retry-fulfillment`);
      message.success("Fulfillment retry queued");
      loadOrders();
    } catch {
      message.error("Retry failed");
    } finally {
      setRetryingId(null);
    }
  };

  const columns = [
    {
      title: "Order",
      dataIndex: "id",
      key: "id",
      render: (id: string) => `#${id.slice(0, 8)}`,
    },
    {
      title: "Campaign",
      dataIndex: "campaign_title",
      key: "campaign_title",
      render: (v: string | null) => v || "—",
    },
    {
      title: "Customer",
      dataIndex: "customer_email",
      key: "customer_email",
    },
    {
      title: "Total",
      dataIndex: "total",
      key: "total",
      render: (v: number) => `$${Number(v).toFixed(2)}`,
    },
    {
      title: "Payment",
      dataIndex: "status",
      key: "status",
      render: (status: string) => <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>,
    },
    {
      title: "Fulfillment",
      dataIndex: "fulfillment_status",
      key: "fulfillment_status",
      render: (status: string | null | undefined) =>
        status ? (
          <Tag color={fulfillmentColors[status] || "default"}>{status.replace(/_/g, " ")}</Tag>
        ) : (
          "—"
        ),
    },
    {
      title: "Tracking",
      dataIndex: "tracking_number",
      key: "tracking_number",
      render: (v: string | null | undefined) => v || "—",
    },
    {
      title: "Date",
      dataIndex: "created_at",
      key: "created_at",
      render: (v: string) => new Date(v).toLocaleDateString(),
    },
    {
      title: "",
      key: "actions",
      render: (_: unknown, record: Order) =>
        record.fulfillment_status === "failed" ? (
          <Button
            size="small"
            icon={<ReloadOutlined />}
            loading={retryingId === record.id}
            onClick={() => handleRetryFulfillment(record.id)}
          >
            Retry
          </Button>
        ) : null,
    },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <div>
          <Title level={3} style={{ marginBottom: 4 }}>Orders</Title>
          <Text type="secondary">Manage customer orders and BurgerPrints fulfillment status</Text>
        </div>
        <Space wrap>
          <Button icon={<DownloadOutlined />} onClick={handleExportPage} disabled={orders.length === 0}>
            Export page
          </Button>
          <Button type="primary" icon={<DownloadOutlined />} loading={exporting} onClick={handleExportAll}>
            Export all (CSV)
          </Button>
        </Space>
      </div>
      <Table rowKey="id" columns={columns} dataSource={orders} loading={loading} pagination={{ pageSize: 20 }} scroll={{ x: 960 }} />
    </div>
  );
}
