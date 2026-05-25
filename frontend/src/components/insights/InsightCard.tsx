"use client";

import { Card, Tag } from "antd";
import {
  InfoCircleOutlined,
  WarningOutlined,
  AlertOutlined,
  DollarOutlined,
  RocketOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import type { Insight } from "@/lib/types";

const severityConfig = {
  info: { color: "blue", icon: <InfoCircleOutlined /> },
  warning: { color: "orange", icon: <WarningOutlined /> },
  critical: { color: "red", icon: <AlertOutlined /> },
};

const categoryConfig = {
  financial: { color: "green", icon: <DollarOutlined />, label: "Financial" },
  marketing: { color: "purple", icon: <RocketOutlined />, label: "Marketing" },
  blended: { color: "geekblue", icon: <ThunderboltOutlined />, label: "Blended" },
};

interface InsightCardProps {
  insight: Insight;
  onDismiss?: (id: string) => void;
}

export default function InsightCard({ insight, onDismiss }: InsightCardProps) {
  const severity = severityConfig[insight.severity as keyof typeof severityConfig] || severityConfig.info;
  const category = categoryConfig[insight.category as keyof typeof categoryConfig] || categoryConfig.blended;

  return (
    <Card
      size="small"
      style={{
        marginBottom: 12,
        borderLeft: `3px solid ${severity.color === "blue" ? "#1677ff" : severity.color === "orange" ? "#faad14" : "#ff4d4f"}`,
        opacity: insight.is_read ? 0.8 : 1,
      }}
      extra={
        onDismiss && (
          <a onClick={() => onDismiss(insight.id)} style={{ fontSize: 12 }}>
            Dismiss
          </a>
        )
      }
    >
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <Tag color={severity.color} icon={severity.icon}>
          {insight.severity.toUpperCase()}
        </Tag>
        <Tag color={category.color} icon={category.icon}>
          {category.label}
        </Tag>
        <span style={{ marginLeft: "auto", fontSize: 12, color: "#8c8c8c" }}>
          {new Date(insight.generated_at).toLocaleDateString()}
        </span>
      </div>
      <h4 style={{ margin: "0 0 8px" }}>{insight.title}</h4>
      <p style={{ margin: 0, color: "#595959", fontSize: 14 }}>{insight.body_markdown}</p>
    </Card>
  );
}
