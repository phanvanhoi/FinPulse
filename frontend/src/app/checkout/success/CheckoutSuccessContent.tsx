"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Button, Card, Result, Spin, Typography } from "antd";
import axios from "axios";
import Link from "next/link";
import { TrackingPageView, trackPurchase } from "@/components/tracking/TrackingPixels";
import type { Order } from "@/lib/types/order";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const { Text } = Typography;

export default function CheckoutSuccessContent() {
  const searchParams = useSearchParams();
  const orderId = searchParams.get("order_id");
  const isMock = searchParams.get("mock") === "true";
  const isPayPal = searchParams.get("provider") === "paypal";
  const paypalToken = searchParams.get("token");
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const purchaseTracked = useRef(false);

  useEffect(() => {
    if (!orderId) {
      setLoading(false);
      return;
    }

    const complete = async () => {
      if (isMock) {
        await axios.post(`${API_URL}/api/v1/orders/complete?order_id=${orderId}&mock=true`);
      } else if (isPayPal && paypalToken) {
        await axios.post(
          `${API_URL}/api/v1/orders/paypal/capture?order_id=${orderId}&token=${encodeURIComponent(paypalToken)}`
        );
      }
      const { data } = await axios.get<Order>(`${API_URL}/api/v1/orders/public/${orderId}`);
      setOrder(data);
      setLoading(false);
    };

    complete().catch(() => setLoading(false));
  }, [orderId, isMock, isPayPal, paypalToken]);

  useEffect(() => {
    if (order && order.status === "paid" && !purchaseTracked.current) {
      trackPurchase(Number(order.total), order.id);
      purchaseTracked.current = true;
    }
  }, [order]);

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!order) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Result status="error" title="Order not found" />
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#fafafa", padding: 48 }}>
      <TrackingPageView
        facebookPixelId={order.facebook_pixel_id}
        googleAnalyticsId={order.google_analytics_id}
      />
      <Card style={{ maxWidth: 560, margin: "0 auto" }}>
        <Result
          status="success"
          title="Order Confirmed!"
          subTitle={`Thank you! A confirmation will be sent to ${order.customer_email}`}
        />
        <div style={{ background: "#f5f5f5", borderRadius: 8, padding: 16, marginBottom: 24 }}>
          <Text strong>Order #{order.id.slice(0, 8)}</Text>
          {order.items.map((item, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
              <Text>
                {item.product_name} ({item.variant_name}) x{item.quantity}
              </Text>
              <Text>${Number(item.line_total).toFixed(2)}</Text>
            </div>
          ))}
          {Number(order.tip_amount) > 0 && (
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
              <Text>Tip</Text>
              <Text>${Number(order.tip_amount).toFixed(2)}</Text>
            </div>
          )}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginTop: 12,
              borderTop: "1px solid #e8e8e8",
              paddingTop: 12,
            }}
          >
            <Text strong>Total</Text>
            <Text strong>${Number(order.total).toFixed(2)}</Text>
          </div>
        </div>
        {order.campaign_slug && (
          <Link href={`/campaign/${order.campaign_slug}`} style={{ display: "block", marginBottom: 12 }}>
            <Button block>Continue Shopping</Button>
          </Link>
        )}
        <Link href="/">
          <Button type="primary" block>
            Back to Home
          </Button>
        </Link>
      </Card>
    </div>
  );
}
