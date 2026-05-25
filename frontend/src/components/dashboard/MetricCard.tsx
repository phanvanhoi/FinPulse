"use client";

import { Card, Statistic } from "antd";
import { ArrowUpOutlined, ArrowDownOutlined } from "@ant-design/icons";

interface MetricCardProps {
  title: string;
  value: number;
  prefix?: string;
  suffix?: string;
  precision?: number;
  changePct?: number | null;
  loading?: boolean;
}

export default function MetricCard({
  title,
  value,
  prefix = "",
  suffix = "",
  precision = 0,
  changePct,
  loading = false,
}: MetricCardProps) {
  const isPositive = changePct != null && changePct >= 0;

  return (
    <Card loading={loading} size="small">
      <Statistic
        title={title}
        value={value}
        prefix={prefix}
        suffix={
          changePct != null ? (
            <span style={{ fontSize: 14, color: isPositive ? "#52c41a" : "#ff4d4f" }}>
              {isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              {Math.abs(changePct).toFixed(1)}%
            </span>
          ) : (
            suffix
          )
        }
        precision={precision}
      />
    </Card>
  );
}
