"use client";

import { useEffect, useState } from "react";
import { Drawer, Grid, Layout } from "antd";
import { MenuOutlined } from "@ant-design/icons";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { dashboardMenuItems } from "@/components/layout/menu-items";
import { useAuthStore } from "@/stores/auth-store";
import { usePathname, useRouter } from "next/navigation";
import { Menu } from "antd";

const { Content } = Layout;
const SIDEBAR_WIDTH = 240;

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, fetchUser } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();
  const screens = Grid.useBreakpoint();
  const isMobile = !screens.md;
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    fetchUser();
  }, [isAuthenticated, fetchUser, router]);

  useEffect(() => {
    setDrawerOpen(false);
  }, [pathname]);

  if (!isAuthenticated) return null;

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {!isMobile && <Sidebar />}
      <Drawer
        title="FinPulse"
        placement="left"
        open={isMobile && drawerOpen}
        onClose={() => setDrawerOpen(false)}
        styles={{ body: { padding: 0 } }}
        width={SIDEBAR_WIDTH}
      >
        <Menu mode="inline" selectedKeys={[pathname]} items={dashboardMenuItems} style={{ border: "none" }} />
      </Drawer>
      <Layout style={{ marginLeft: isMobile ? 0 : SIDEBAR_WIDTH, transition: "margin-left 0.2s" }}>
        <Header
          showMenuButton={isMobile}
          onMenuClick={() => setDrawerOpen(true)}
        />
        <Content
          style={{
            padding: isMobile ? 16 : 24,
            background: "#f5f5f5",
            minHeight: "calc(100vh - 64px)",
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}
