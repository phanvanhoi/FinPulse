"use client";

import Link from "next/link";
import { Alert, Button } from "antd";
import { CheckCircleOutlined, RightOutlined } from "@ant-design/icons";
import type { SetupStatus } from "@/lib/types";

interface FulfillmentSetupChecklistProps {
  setup: SetupStatus;
}

export default function FulfillmentSetupChecklist({ setup }: FulfillmentSetupChecklistProps) {
  const steps = [
    {
      done: setup.burgerprints_connected,
      label: "Connect BurgerPrints API key",
      href: "/settings/connections",
    },
    {
      done: setup.has_burgerprints_catalog,
      label: "Import BurgerPrints product SKUs",
      href: "/settings/connections",
      hint: "Run SKU import script on server (see user guide)",
    },
    {
      done: setup.has_live_campaign,
      label: "Publish a campaign with POD products",
      href: "/campaigns/new",
    },
  ];

  const completed = steps.filter((s) => s.done).length;
  if (completed === steps.length) return null;

  return (
    <Alert
      type="warning"
      showIcon
      style={{ marginBottom: 24 }}
      message={`Fulfillment setup (${completed}/${steps.length} complete)`}
      description={
        <div style={{ marginTop: 8 }}>
          <p style={{ margin: "0 0 8px", color: "#595959" }}>
            Connect printing & fulfillment so paid orders auto-submit to BurgerPrints.
          </p>
          {steps.map((step) => (
            <div key={step.label} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
              <CheckCircleOutlined style={{ color: step.done ? "#52c41a" : "#d9d9d9" }} />
              {step.done ? (
                <span style={{ color: "#8c8c8c", textDecoration: "line-through" }}>{step.label}</span>
              ) : (
                <Link href={step.href}>
                  {step.label} <RightOutlined />
                </Link>
              )}
            </div>
          ))}
          <Link href="/settings/connections">
            <Button size="small" type="primary" style={{ marginTop: 8 }}>
              Open Connections
            </Button>
          </Link>
        </div>
      }
    />
  );
}
