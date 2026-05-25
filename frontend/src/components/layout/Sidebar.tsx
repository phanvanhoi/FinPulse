"use client";

import { usePathname } from "next/navigation";
import { Layout, Menu } from "antd";
import { dashboardMenuItems } from "@/components/layout/menu-items";

const { Sider } = Layout;

interface SidebarProps {
  collapsed?: boolean;
}

export default function Sidebar({ collapsed = false }: SidebarProps) {
  const pathname = usePathname();

  return (
    <Sider
      width={240}
      collapsed={collapsed}
      collapsedWidth={0}
      trigger={null}
      breakpoint="md"
      style={{
        background: "#fff",
        borderRight: "1px solid #f0f0f0",
        height: "100vh",
        position: "fixed",
        left: 0,
        zIndex: 100,
      }}
    >
      <div style={{ padding: "20px 24px", borderBottom: "1px solid #f0f0f0" }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: "#1677ff" }}>FinPulse</h1>
        {!collapsed && (
          <p style={{ margin: 0, fontSize: 12, color: "#8c8c8c" }}>Seller Dashboard</p>
        )}
      </div>
      <Menu
        mode="inline"
        selectedKeys={[pathname]}
        items={dashboardMenuItems}
        style={{ border: "none", marginTop: 8 }}
      />
    </Sider>
  );
}
