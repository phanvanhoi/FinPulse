"use client";

import { Layout, Button, Dropdown, Avatar, Space } from "antd";
import { BellOutlined, LogoutOutlined, MenuOutlined, UserOutlined } from "@ant-design/icons";
import { useAuthStore } from "@/stores/auth-store";

const { Header: AntHeader } = Layout;

interface HeaderProps {
  showMenuButton?: boolean;
  onMenuClick?: () => void;
}

export default function Header({ showMenuButton = false, onMenuClick }: HeaderProps) {
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
        padding: showMenuButton ? "0 12px" : "0 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 16,
        position: "sticky",
        top: 0,
        zIndex: 99,
      }}
    >
      {showMenuButton ? (
        <Button type="text" icon={<MenuOutlined />} onClick={onMenuClick} aria-label="Open menu" />
      ) : (
        <span />
      )}
      <Space>
        <Button type="text" icon={<BellOutlined />} />
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Space style={{ cursor: "pointer" }}>
            <Avatar size="small" icon={<UserOutlined />} />
            <span>{user?.name || "User"}</span>
          </Space>
        </Dropdown>
      </Space>
    </AntHeader>
  );
}
