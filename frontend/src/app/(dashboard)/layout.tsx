"use client";

import { useEffect } from "react";
import { Layout } from "antd";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { useAuthStore } from "@/stores/auth-store";
import { useRouter } from "next/navigation";

const { Content } = Layout;

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, fetchUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    fetchUser();
  }, [isAuthenticated, fetchUser, router]);

  if (!isAuthenticated) return null;

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sidebar />
      <Layout style={{ marginLeft: 240 }}>
        <Header />
        <Content style={{ padding: 24, background: "#f5f5f5" }}>{children}</Content>
      </Layout>
    </Layout>
  );
}
