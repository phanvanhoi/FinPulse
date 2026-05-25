"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Typography,
  Card,
  Button,
  Tag,
  Space,
  Empty,
  Modal,
  Input,
  message,
  Spin,
} from "antd";
import {
  CheckCircleOutlined,
  PlusOutlined,
  DisconnectOutlined,
  ApiOutlined,
} from "@ant-design/icons";
import api from "@/lib/api";

const { Title, Text } = Typography;

interface ConnectionItem {
  id: string;
  provider: string;
  status: string;
  last_synced_at: string | null;
  error_message: string | null;
}

interface BurgerPrintsStatus {
  connected: boolean;
  connection_id: string | null;
  status: string | null;
  error_message: string | null;
}

const otherConnections = [
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
  const [loading, setLoading] = useState(true);
  const [connections, setConnections] = useState<ConnectionItem[]>([]);
  const [burgerPrints, setBurgerPrints] = useState<BurgerPrintsStatus | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadConnections = useCallback(async () => {
    setLoading(true);
    try {
      const [listRes, bpRes] = await Promise.all([
        api.get<{ connections: ConnectionItem[] }>("/connections"),
        api.get<BurgerPrintsStatus>("/connections/burgerprints/status"),
      ]);
      setConnections(listRes.data.connections);
      setBurgerPrints(bpRes.data);
    } catch {
      message.error("Failed to load connections");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConnections();
  }, [loadConnections]);

  const handleConnectBurgerPrints = async () => {
    if (!apiKey.trim()) {
      message.warning("Enter your BurgerPrints API key");
      return;
    }
    setSubmitting(true);
    try {
      await api.post("/connections/burgerprints", { api_key: apiKey.trim() });
      message.success("BurgerPrints connected");
      setModalOpen(false);
      setApiKey("");
      await loadConnections();
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Failed to connect BurgerPrints";
      message.error(detail);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDisconnectBurgerPrints = async () => {
    setSubmitting(true);
    try {
      await api.delete("/connections/burgerprints");
      message.success("BurgerPrints disconnected");
      await loadConnections();
    } catch {
      message.error("Failed to disconnect BurgerPrints");
    } finally {
      setSubmitting(false);
    }
  };

  const burgerPrintsConnected = burgerPrints?.connected ?? false;

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: 48 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        Connections
      </Title>
      <Text type="secondary" style={{ display: "block", marginBottom: 24 }}>
        Connect fulfillment, financial, and marketing accounts to power your store and dashboard.
      </Text>

      <Title level={5} style={{ marginBottom: 16 }}>
        Print-on-Demand Fulfillment
      </Title>
      <div
        style={{
          display: "grid",
          gap: 16,
          gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))",
          marginBottom: 32,
        }}
      >
        <Card size="small">
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 8,
                background: "#E85D04",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontWeight: 700,
                fontSize: 14,
              }}
            >
              BP
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <strong>BurgerPrints</strong>
                {burgerPrintsConnected ? (
                  <Tag icon={<CheckCircleOutlined />} color="success">
                    Connected
                  </Tag>
                ) : (
                  <Tag>Not connected</Tag>
                )}
              </div>
              <Text type="secondary" style={{ fontSize: 13 }}>
                POD fulfillment — submit paid orders for printing and shipping
              </Text>
              {burgerPrints?.error_message && (
                <Text type="danger" style={{ display: "block", fontSize: 12, marginTop: 4 }}>
                  {burgerPrints.error_message}
                </Text>
              )}
            </div>
            {burgerPrintsConnected ? (
              <Button
                danger
                icon={<DisconnectOutlined />}
                loading={submitting}
                onClick={handleDisconnectBurgerPrints}
              >
                Disconnect
              </Button>
            ) : (
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
                Connect
              </Button>
            )}
          </div>
        </Card>
      </div>

      <Title level={5} style={{ marginBottom: 16 }}>
        Finance & Marketing
      </Title>
      <div
        style={{
          display: "grid",
          gap: 16,
          gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))",
        }}
      >
        {otherConnections.map((conn) => {
          const linked = connections.find((c) => c.provider === conn.key);
          return (
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
                    {linked && (
                      <Tag icon={<CheckCircleOutlined />} color="success">
                        Connected
                      </Tag>
                    )}
                  </div>
                  <Text type="secondary" style={{ fontSize: 13 }}>
                    {conn.description}
                  </Text>
                </div>
                <Button type="primary" icon={<PlusOutlined />} disabled={conn.disabled}>
                  Connect
                </Button>
              </div>
            </Card>
          );
        })}
      </div>

      {!connections.length && !burgerPrintsConnected && (
        <Empty
          style={{ marginTop: 32 }}
          image={<ApiOutlined style={{ fontSize: 48, color: "#bbb" }} />}
          description="Connect BurgerPrints to enable automatic order fulfillment"
        />
      )}

      <Modal
        title="Connect BurgerPrints"
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false);
          setApiKey("");
        }}
        onOk={handleConnectBurgerPrints}
        confirmLoading={submitting}
        okText="Connect"
      >
        <Space direction="vertical" style={{ width: "100%" }} size="middle">
          <Text type="secondary">
            Get your API key from BurgerPrints Dashboard → Stores → Get API key for your
            fulfillment store.
          </Text>
          <Input.Password
            placeholder="Paste BurgerPrints API key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            onPressEnter={handleConnectBurgerPrints}
          />
        </Space>
      </Modal>
    </div>
  );
}
