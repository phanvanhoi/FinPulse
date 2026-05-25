"use client";

import Link from "next/link";
import { Button, Card, Col, Row, Typography } from "antd";
import { ArrowRightOutlined, DollarOutlined, RocketOutlined } from "@ant-design/icons";
import type { FinanceSnapshot, MarketingSnapshot } from "@/lib/types";

const { Text, Title } = Typography;

interface FinanceMarketingWidgetsProps {
  finance: FinanceSnapshot | null;
  marketing: MarketingSnapshot | null;
  loading?: boolean;
}

export default function FinanceMarketingWidgets({ finance, marketing, loading }: FinanceMarketingWidgetsProps) {
  return (
    <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
      <Col xs={24} md={12}>
        <Card loading={loading} title={<><DollarOutlined /> Finance</>} extra={finance?.source === "accounting" ? "Accounting" : "Store sales"}>
          {finance ? (
            <>
              <Title level={4} style={{ margin: "0 0 4px" }}>
                ${Number(finance.revenue).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </Title>
              <Text type="secondary" style={{ display: "block", marginBottom: 12 }}>
                {finance.detail}
              </Text>
              {finance.net_income != null && (
                <Text style={{ display: "block" }}>Net income: ${Number(finance.net_income).toFixed(2)}</Text>
              )}
              {finance.cash_on_hand != null && (
                <Text style={{ display: "block" }}>Cash on hand: ${Number(finance.cash_on_hand).toFixed(2)}</Text>
              )}
            </>
          ) : (
            <Text type="secondary">No financial data yet</Text>
          )}
          <Link href="/finance" style={{ marginTop: 12, display: "inline-block" }}>
            <Button type="link" icon={<ArrowRightOutlined />} style={{ padding: 0 }}>
              Open Finance
            </Button>
          </Link>
        </Card>
      </Col>
      <Col xs={24} md={12}>
        <Card loading={loading} title={<><RocketOutlined /> Marketing</>} extra={marketing?.source === "ads" ? "Ad platforms" : "Sales campaigns"}>
          {marketing ? (
            <>
              <Text style={{ display: "block" }}>
                {marketing.source === "ads" ? "Active ad campaigns" : "Live sales campaigns"}:{" "}
                <strong>{marketing.live_campaigns}</strong>
              </Text>
              <Text style={{ display: "block" }}>Units sold: <strong>{marketing.units_sold}</strong></Text>
              {marketing.ad_spend != null && (
                <Text style={{ display: "block" }}>Ad spend: ${Number(marketing.ad_spend).toFixed(2)}</Text>
              )}
              {marketing.overall_roas != null && (
                <Text style={{ display: "block" }}>ROAS: {Number(marketing.overall_roas).toFixed(1)}x</Text>
              )}
              <Text type="secondary" style={{ display: "block", marginTop: 8 }}>
                {marketing.detail}
              </Text>
            </>
          ) : (
            <Text type="secondary">No marketing data yet</Text>
          )}
          <Link href={marketing?.source === "ads" ? "/marketing" : "/campaigns"} style={{ marginTop: 12, display: "inline-block" }}>
            <Button type="link" icon={<ArrowRightOutlined />} style={{ padding: 0 }}>
              {marketing?.source === "ads" ? "Open Marketing" : "Manage Campaigns"}
            </Button>
          </Link>
        </Card>
      </Col>
    </Row>
  );
}
