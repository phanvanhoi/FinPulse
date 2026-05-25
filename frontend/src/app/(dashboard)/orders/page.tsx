"use client";

import { useEffect, useState } from "react";
import { Table, Tag, Typography } from "antd";
import api from "@/lib/api";
import type { Order } from "@/lib/types/order";

const { Title, Text } = Typography;

const statusColors: Record<string, string> = {
  pending: "orange",
  paid: "green",
  failed: "red",
  refunded: "default",
};

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ orders: Order[]; total: number }>("/orders")
      .then(({ data }) => setOrders(data.orders))
      .finally(() => setLoading(false));
  }, []);

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
      <Title level={3} style={{ marginBottom: 4 }}>Orders</Title>
      <Text type="secondary" style={{ display: "block", marginBottom: 24 }}>
        Manage customer orders from your campaigns
      </Text>
      <Table rowKey="id" columns={columns} dataSource={orders} loading={loading} pagination={{ pageSize: 20 }} />
    </div>
  );
}
