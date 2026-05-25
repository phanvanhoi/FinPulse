"use client";

import Link from "next/link";
import { Alert, Button } from "antd";
import { CheckCircleOutlined, RightOutlined } from "@ant-design/icons";
import type { SetupStatus, StoreSummary } from "@/lib/types";

interface SetupChecklistProps {
  setup: SetupStatus;
  store: StoreSummary | null;
}

export default function SetupChecklist({ setup, store }: SetupChecklistProps) {
  const steps = [
    {
      done: setup.has_logo,
      label: "Upload store logo",
      href: "/settings/store",
    },
    {
      done: setup.has_live_campaign,
      label: "Publish your first campaign",
      href: "/campaigns/new",
    },
    {
      done: setup.has_paid_order,
      label: "Get your first paid order",
      href: store ? store.storefront_url : "/campaigns",
      external: Boolean(store),
    },
  ];

  const completed = steps.filter((s) => s.done).length;
  if (completed === steps.length) return null;

  return (
    <Alert
      type="info"
      showIcon
      style={{ marginBottom: 24 }}
      message={`Get started (${completed}/${steps.length} complete)`}
      description={
        <div style={{ marginTop: 8 }}>
          {steps.map((step) => (
            <div key={step.label} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
              <CheckCircleOutlined style={{ color: step.done ? "#52c41a" : "#d9d9d9" }} />
              {step.done ? (
                <span style={{ color: "#8c8c8c", textDecoration: "line-through" }}>{step.label}</span>
              ) : step.external && store ? (
                <a href={store.storefront_url} target="_blank" rel="noreferrer">
                  {step.label} <RightOutlined />
                </a>
              ) : (
                <Link href={step.href}>{step.label} <RightOutlined /></Link>
              )}
            </div>
          ))}
        </div>
      }
    />
  );
}
