"use client";

import { Typography, Card, Button, Tag, Space, Empty } from "antd";
import {
  ApiOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
} from "@ant-design/icons";

const { Title, Text } = Typography;

const availableConnections = [
  {
    key: "quickbooks",
    name: "QuickBooks Online",
    description: "Sync your financial data - P&L, balance sheet, invoices, and expenses",
    icon: "QB",
    color: "#2CA01C",
  },
  {
    key: "google_ads",
    name: "Google Ads",
    description: "Sync campaign performance, spend, conversions, and ROAS data",
    icon: "GA",
    color: "#4285F4",
  },
  {
    key: "xero",
    name: "Xero",
    description: "Coming soon - Sync your Xero accounting data",
    icon: "XE",
    color: "#13B5EA",
    disabled: true,
  },
  {
    key: "meta_ads",
    name: "Meta Ads (Facebook & Instagram)",
    description: "Coming soon - Sync your Meta advertising data",
    icon: "MA",
    color: "#1877F2",
    disabled: true,
  },
];

export default function ConnectionsPage() {
  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        Connections
      </Title>
      <Text type="secondary" style={{ display: "block", marginBottom: 24 }}>
        Connect your financial and marketing accounts to power your dashboard and AI insights.
      </Text>

      <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))" }}>
        {availableConnections.map((conn) => (
          <Card key={conn.key} size="small">
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 8,
                  background: conn.color,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#fff",
                  fontWeight: 700,
                  fontSize: 16,
                }}
              >
                {conn.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <strong>{conn.name}</strong>
                  {conn.disabled && <Tag>Coming Soon</Tag>}
                </div>
                <Text type="secondary" style={{ fontSize: 13 }}>
                  {conn.description}
                </Text>
              </div>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                disabled={conn.disabled}
              >
                Connect
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
