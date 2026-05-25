"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  Button,
  Divider,
  Form,
  Input,
  InputNumber,
  Modal,
  Radio,
  Select,
  Space,
  Spin,
  Typography,
  message,
} from "antd";
import axios from "axios";
import { getSessionId } from "@/lib/session";
import {
  TrackingPageView,
  trackAddToCart,
  trackInitiateCheckout,
} from "@/components/tracking/TrackingPixels";
import type { PublicCampaign } from "@/lib/types/campaign";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const { Title, Text, Paragraph } = Typography;

interface PaymentConfig {
  card_enabled: boolean;
  paypal_enabled: boolean;
  mock_enabled: boolean;
}

export default function PublicCampaignPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [campaign, setCampaign] = useState<PublicCampaign | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [paymentConfig, setPaymentConfig] = useState<PaymentConfig | null>(null);
  const [form] = Form.useForm();
  const [selectedVariant, setSelectedVariant] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    axios
      .get<PublicCampaign>(`${API_URL}/api/v1/campaigns/public/${slug}`)
      .then(({ data }) => {
        setCampaign(data);
        setSelectedVariant(data.variants[0]?.variant_id || null);
      })
      .catch(() => message.error("Campaign not found"))
      .finally(() => setLoading(false));

    axios
      .get<PaymentConfig>(`${API_URL}/api/v1/payments/config`)
      .then(({ data }) => setPaymentConfig(data))
      .catch(() => setPaymentConfig({ card_enabled: false, paypal_enabled: false, mock_enabled: true }));
  }, [slug]);

  const selectedPrice = campaign?.variants.find((v) => v.variant_id === selectedVariant)?.price || 0;
  const subtotal = selectedPrice * quantity;

  const handleBuyNow = () => {
    trackInitiateCheckout(subtotal);
    setCheckoutOpen(true);
  };

  const handleEmailBlur = async () => {
    const email = form.getFieldValue("email");
    if (!email || !campaign) return;
    try {
      await axios.post(`${API_URL}/api/v1/cart/${slug}/save-email`, {
        session_id: getSessionId(),
        customer_email: email,
      });
    } catch {
      // Non-blocking — used for abandoned cart recovery
    }
  };

  const handleCheckout = async () => {
    if (!campaign || !selectedVariant) return;
    const values = await form.validateFields();
    setSubmitting(true);

    try {
      const sessionId = getSessionId();
      await axios.post(`${API_URL}/api/v1/cart/add`, {
        campaign_slug: slug,
        session_id: sessionId,
        items: [{ variant_id: selectedVariant, quantity }],
      });
      trackAddToCart(subtotal);

      const { data } = await axios.post(`${API_URL}/api/v1/cart/${slug}/checkout`, {
        session_id: sessionId,
        customer_email: values.email,
        customer_name: values.name,
        shipping: {
          street_address: values.street_address,
          apt_suite_other: values.apt_suite_other || "",
          city: values.city,
          state: values.state,
          zipcode: values.zipcode,
          country: values.country || "US",
          phone_number: values.phone,
        },
        tip_percent: values.tip_percent,
        payment_method: values.payment_method || "card",
      });

      if (data.checkout_url.includes("mock=true")) {
        await axios.post(`${API_URL}/api/v1/orders/complete?order_id=${data.order_id}&mock=true`);
        window.location.href = `/checkout/success?order_id=${data.order_id}&mock=true`;
      } else {
        window.location.href = data.checkout_url;
      }
    } catch {
      message.error("Checkout failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!campaign) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Title level={3}>Campaign not found</Title>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#fafafa" }}>
      <TrackingPageView
        facebookPixelId={campaign.facebook_pixel_id}
        googleAnalyticsId={campaign.google_analytics_id}
      />

      <header style={{ background: "#fff", borderBottom: "1px solid #f0f0f0", padding: "16px 24px" }}>
        {campaign.store_logo_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={campaign.store_logo_url} alt={campaign.store_name} style={{ height: 36 }} />
        ) : (
          <Text strong style={{ fontSize: 18 }}>{campaign.store_name}</Text>
        )}
      </header>

      <main style={{ maxWidth: 960, margin: "0 auto", padding: "32px 24px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
          <div>
            {campaign.design_image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={campaign.design_image_url}
                alt={campaign.title}
                style={{ width: "100%", borderRadius: 12, border: "1px solid #f0f0f0" }}
              />
            ) : (
              <div style={{ aspectRatio: "1", background: "#f0f0f0", borderRadius: 12 }} />
            )}
          </div>
          <div>
            <Title level={2}>{campaign.title}</Title>
            <Text type="secondary">{campaign.product_name}</Text>
            {campaign.description && <Paragraph style={{ marginTop: 16 }}>{campaign.description}</Paragraph>}

            <Divider />

            <Space direction="vertical" style={{ width: "100%" }} size="middle">
              <div>
                <Text strong>Size</Text>
                <Select
                  style={{ width: "100%", marginTop: 8 }}
                  value={selectedVariant}
                  onChange={setSelectedVariant}
                  options={campaign.variants.map((v) => ({
                    value: v.variant_id,
                    label: `${v.variant_name} — $${Number(v.price).toFixed(2)}`,
                  }))}
                />
              </div>
              <div>
                <Text strong>Quantity</Text>
                <InputNumber min={1} max={99} value={quantity} onChange={(v) => setQuantity(v || 1)} style={{ marginLeft: 16 }} />
              </div>
              <Title level={3} style={{ margin: 0 }}>${subtotal.toFixed(2)}</Title>
              <Button type="primary" size="large" block onClick={handleBuyNow}>
                Buy Now
              </Button>
            </Space>
          </div>
        </div>
      </main>

      <Modal title="Checkout" open={checkoutOpen} onCancel={() => setCheckoutOpen(false)} footer={null} destroyOnHidden>
        <Form form={form} layout="vertical" onFinish={handleCheckout}>
          <Form.Item label="Email" name="email" rules={[{ required: true, type: "email" }]}>
            <Input placeholder="you@example.com" onBlur={handleEmailBlur} />
          </Form.Item>
          <Form.Item label="Full Name" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Phone" name="phone" rules={[{ required: true }]}>
            <Input placeholder="+1 555 123 4567" />
          </Form.Item>
          <Form.Item label="Street Address" name="street_address" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Apt / Suite" name="apt_suite_other">
            <Input />
          </Form.Item>
          <Form.Item label="City" name="city" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="State" name="state" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="ZIP Code" name="zipcode" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Country" name="country" initialValue="US" rules={[{ required: true }]}>
            <Input maxLength={2} />
          </Form.Item>
          {campaign.tips_enabled && (
            <Form.Item label="Add a tip?" name="tip_percent">
              <Radio.Group>
                <Radio value={undefined}>No tip</Radio>
                {campaign.tip_options.map((tip) => (
                  <Radio key={tip} value={tip}>{tip}%</Radio>
                ))}
              </Radio.Group>
            </Form.Item>
          )}
          {paymentConfig && (paymentConfig.card_enabled || paymentConfig.paypal_enabled) && (
            <Form.Item
              label="Payment method"
              name="payment_method"
              initialValue={paymentConfig.card_enabled ? "card" : "paypal"}
              rules={[{ required: true }]}
            >
              <Radio.Group>
                {paymentConfig.card_enabled && (
                  <Radio value="card">Credit / Debit Card (Visa, Mastercard, Amex)</Radio>
                )}
                {paymentConfig.paypal_enabled && (
                  <Radio value="paypal">PayPal</Radio>
                )}
              </Radio.Group>
            </Form.Item>
          )}
          {paymentConfig?.mock_enabled && !paymentConfig.card_enabled && !paymentConfig.paypal_enabled && (
            <Text type="secondary" style={{ display: "block", marginBottom: 12 }}>
              Test mode — no payment gateway configured on server.
            </Text>
          )}
          <Divider />
          <Space style={{ width: "100%", justifyContent: "space-between" }}>
            <Text strong>Total: ${subtotal.toFixed(2)}</Text>
            <Button type="primary" htmlType="submit" loading={submitting}>
              Place Order
            </Button>
          </Space>
        </Form>
      </Modal>
    </div>
  );
}
