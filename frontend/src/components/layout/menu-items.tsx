import {
  ApiOutlined,
  BulbOutlined,
  DashboardOutlined,
  DollarOutlined,
  RocketOutlined,
  SettingOutlined,
  ShopOutlined,
  ShoppingCartOutlined,
} from "@ant-design/icons";
import Link from "next/link";
import type { MenuProps } from "antd";

export const dashboardMenuItems: MenuProps["items"] = [
  { key: "/", icon: <DashboardOutlined />, label: <Link href="/">Dashboard</Link> },
  { key: "/finance", icon: <DollarOutlined />, label: <Link href="/finance">Finance</Link> },
  { key: "/marketing", icon: <RocketOutlined />, label: <Link href="/marketing">Marketing</Link> },
  { key: "/insights", icon: <BulbOutlined />, label: <Link href="/insights">AI Insights</Link> },
  { type: "divider" },
  { key: "/campaigns", icon: <ShopOutlined />, label: <Link href="/campaigns">Campaigns</Link> },
  { key: "/orders", icon: <ShoppingCartOutlined />, label: <Link href="/orders">Orders</Link> },
  { key: "/settings/store", icon: <SettingOutlined />, label: <Link href="/settings/store">Storefront</Link> },
  { key: "/settings/connections", icon: <ApiOutlined />, label: <Link href="/settings/connections">Connections</Link> },
];
