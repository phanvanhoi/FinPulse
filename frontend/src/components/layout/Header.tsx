"use client";

import { Layout, Button, Dropdown, Avatar, Badge, Space } from "antd";
import { BellOutlined, UserOutlined, LogoutOutlined } from "@ant-design/icons";
import { useAuthStore } from "@/stores/auth-store";

const { Header: AntHeader } = Layout;

export default function Header() {
  const { user, logout } = useAuthStore();

  const userMenuItems = [
    { key: "profile", label: "Profile", icon: <UserOutlined /> },
    { type: "divider" as const },
    { key: "logout", label: "Logout", icon: <LogoutOutlined />, danger: true, onClick: logout },
  ];

  return (
    <AntHeader
      style={{
        background: "#fff",
        borderBottom: "1px solid #f0f0f0",
        padding: "0 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-end",
        gap: 16,
      }}
    >
      <Badge count={3} size="small">
        <Button type="text" icon={<BellOutlined />} />
      </Badge>
      <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
        <Space style={{ cursor: "pointer" }}>
          <Avatar size="small" icon={<UserOutlined />} />
          <span>{user?.name || "User"}</span>
        </Space>
      </Dropdown>
    </AntHeader>
  );
}
