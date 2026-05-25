"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Layout, Menu } from "antd";
import {
  DashboardOutlined,
  DollarOutlined,
  RocketOutlined,
  BulbOutlined,
  SettingOutlined,
  ApiOutlined,
  ShopOutlined,
  ShoppingCartOutlined,
} from "@ant-design/icons";

const { Sider } = Layout;

const menuItems = [
  { key: "/", icon: <DashboardOutlined />, label: <Link href="/">Dashboard</Link> },
  { key: "/finance", icon: <DollarOutlined />, label: <Link href="/finance">Finance</Link> },
  { key: "/marketing", icon: <RocketOutlined />, label: <Link href="/marketing">Marketing</Link> },
  { key: "/insights", icon: <BulbOutlined />, label: <Link href="/insights">AI Insights</Link> },
  { type: "divider" as const },
  { key: "/campaigns", icon: <ShopOutlined />, label: <Link href="/campaigns">Campaigns</Link> },
  { key: "/orders", icon: <ShoppingCartOutlined />, label: <Link href="/orders">Orders</Link> },
  { key: "/settings/store", icon: <SettingOutlined />, label: <Link href="/settings/store">Storefront</Link> },
  { key: "/settings/connections", icon: <ApiOutlined />, label: <Link href="/settings/connections">Connections</Link> },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <Sider
      width={240}
      style={{ background: "#fff", borderRight: "1px solid #f0f0f0", height: "100vh", position: "fixed", left: 0 }}
    >
      <div style={{ padding: "20px 24px", borderBottom: "1px solid #f0f0f0" }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: "#1677ff" }}>FinPulse</h1>
        <p style={{ margin: 0, fontSize: 12, color: "#8c8c8c" }}>AI-Powered Business Dashboard</p>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[pathname]}
        items={menuItems}
        style={{ border: "none", marginTop: 8 }}
      />
    </Sider>
  );
}
