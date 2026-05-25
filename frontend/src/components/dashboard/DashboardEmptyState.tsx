"use client";

import Link from "next/link";
import { Button, Empty } from "antd";
import { RocketOutlined, ShopOutlined } from "@ant-design/icons";

export default function DashboardEmptyState() {
  return (
    <Empty
      image={<ShopOutlined style={{ fontSize: 56, color: "#1677ff" }} />}
      description={
        <div>
          <p style={{ fontSize: 16, fontWeight: 500 }}>No sales yet</p>
          <p style={{ color: "#8c8c8c" }}>Create a campaign and share your storefront link to start selling.</p>
        </div>
      }
      style={{ padding: "48px 0" }}
    >
      <Link href="/campaigns/new">
        <Button type="primary" icon={<RocketOutlined />} size="large">
          Create Campaign
        </Button>
      </Link>
    </Empty>
  );
}
