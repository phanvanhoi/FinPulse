"use client";

import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  message,
  Select,
  Space,
  Switch,
  Tabs,
  Tag,
  Typography,
  Upload,
} from "antd";
import { CopyOutlined, LinkOutlined, UploadOutlined } from "@ant-design/icons";
import type { UploadFile } from "antd/es/upload/interface";
import { useStoreSettingsStore } from "@/stores/store-settings-store";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const DEFAULT_EMAIL_SUBJECT = "You left something in your cart!";
const DEFAULT_EMAIL_BODY =
  "Hi there,\n\nYou started checkout but didn't finish your order. Your items are still waiting — complete your purchase before they're gone!\n\n[Checkout Link]";

export default function StoreSettingsPage() {
  const {
    store,
    domainVerification,
    isLoading,
    isSaving,
    error,
    fetchStore,
    updateStore,
    uploadLogo,
    setDomain,
    verifyDomain,
    fetchDomainVerification,
  } = useStoreSettingsStore();

  const [form] = Form.useForm();
  const [domainInput, setDomainInput] = useState("");
  const [logoFileList, setLogoFileList] = useState<UploadFile[]>([]);

  useEffect(() => {
    fetchStore();
    fetchDomainVerification();
  }, [fetchStore, fetchDomainVerification]);

  useEffect(() => {
    if (store) {
      form.setFieldsValue({
        name: store.name,
        tips_enabled: store.tips_enabled,
        tip_options: store.tip_options,
        facebook_pixel_id: store.facebook_pixel_id,
        google_analytics_id: store.google_analytics_id,
        abandoned_checkout_enabled: store.abandoned_checkout_enabled,
        abandoned_checkout_delay_minutes: store.abandoned_checkout_delay_minutes,
        abandoned_checkout_email_subject: store.abandoned_checkout_email_subject || DEFAULT_EMAIL_SUBJECT,
        abandoned_checkout_email_body: store.abandoned_checkout_email_body || DEFAULT_EMAIL_BODY,
      });
      setDomainInput(store.custom_domain || "");
    }
  }, [store, form]);

  const handleSaveGeneral = async () => {
    const values = await form.validateFields(["name"]);
    await updateStore({ name: values.name });
    message.success("Store name saved");
  };

  const handleSaveTips = async () => {
    const values = await form.validateFields(["tips_enabled", "tip_options"]);
    await updateStore({
      tips_enabled: values.tips_enabled,
      tip_options: values.tip_options,
    });
    message.success("Tip settings saved");
  };

  const handleSaveTracking = async () => {
    const values = await form.validateFields(["facebook_pixel_id", "google_analytics_id"]);
    await updateStore({
      facebook_pixel_id: values.facebook_pixel_id || null,
      google_analytics_id: values.google_analytics_id || null,
    });
    message.success("Tracking settings saved");
  };

  const handleSaveAbandoned = async () => {
    const values = await form.validateFields([
      "abandoned_checkout_enabled",
      "abandoned_checkout_delay_minutes",
      "abandoned_checkout_email_subject",
      "abandoned_checkout_email_body",
    ]);
    await updateStore(values);
    message.success("Abandoned checkout settings saved");
  };

  const handleLogoUpload = async (file: File) => {
    try {
      await uploadLogo(file);
      message.success("Logo uploaded");
      setLogoFileList([]);
    } catch {
      message.error("Failed to upload logo");
    }
    return false;
  };

  const handleSetDomain = async () => {
    if (!domainInput.trim()) {
      message.warning("Enter a domain first");
      return;
    }
    try {
      await setDomain(domainInput.trim());
      message.success("Domain configured — add DNS record to verify");
    } catch {
      message.error("Failed to set domain");
    }
  };

  const handleVerifyDomain = async () => {
    try {
      await verifyDomain();
      message.success("Domain verified successfully");
    } catch {
      message.error(error || "Domain verification failed");
    }
  };

  const storefrontUrl =
    typeof window !== "undefined" && store
      ? `${window.location.origin}/store/${store.slug}`
      : store
        ? `/store/${store.slug}`
        : "";

  const domainStatusColor =
    store?.domain_verification_status === "verified"
      ? "green"
      : store?.domain_verification_status === "pending"
        ? "orange"
        : "default";

  const tabItems = [
    {
      key: "branding",
      label: "Branding",
      children: (
        <Card loading={isLoading}>
          <Form form={form} layout="vertical">
            <Form.Item label="Store Name" name="name" rules={[{ required: true, message: "Store name is required" }]}>
              <Input placeholder="My Store" />
            </Form.Item>
            <Form.Item label="Store Logo">
              <Space direction="vertical" size="middle">
                {store?.logo_url && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={store.logo_url} alt="Store logo" style={{ maxHeight: 80, maxWidth: 200, objectFit: "contain" }} />
                )}
                <Upload
                  fileList={logoFileList}
                  beforeUpload={handleLogoUpload}
                  onChange={({ fileList }) => setLogoFileList(fileList)}
                  accept="image/png,image/jpeg,image/webp,image/svg+xml"
                  maxCount={1}
                >
                  <Button icon={<UploadOutlined />} loading={isSaving}>
                    Upload Logo
                  </Button>
                </Upload>
                <Text type="secondary">PNG, JPG, WebP or SVG. Max 2MB.</Text>
              </Space>
            </Form.Item>
            {store && (
              <Alert
                type="info"
                showIcon
                icon={<LinkOutlined />}
                message="Storefront URL"
                description={
                  <a href={storefrontUrl} target="_blank" rel="noreferrer">
                    {storefrontUrl}
                  </a>
                }
                style={{ marginBottom: 16 }}
              />
            )}
            <Button type="primary" onClick={handleSaveGeneral} loading={isSaving}>
              Save Branding
            </Button>
          </Form>
        </Card>
      ),
    },
    {
      key: "domain",
      label: "Custom Domain",
      children: (
        <Card loading={isLoading}>
          <Paragraph type="secondary">
            Connect your own domain to your storefront. After adding the domain, configure the DNS TXT record below to verify ownership.
          </Paragraph>
          <Space.Compact style={{ width: "100%", maxWidth: 480, marginBottom: 16 }}>
            <Input
              placeholder="shop.yourdomain.com"
              value={domainInput}
              onChange={(e) => setDomainInput(e.target.value)}
            />
            <Button type="primary" onClick={handleSetDomain} loading={isSaving}>
              Save Domain
            </Button>
          </Space.Compact>
          {store?.custom_domain && (
            <Space direction="vertical" style={{ width: "100%" }}>
              <div>
                <Text strong>{store.custom_domain}</Text>{" "}
                <Tag color={domainStatusColor}>{store.domain_verification_status.toUpperCase()}</Tag>
              </div>
              {domainVerification?.instructions && store.domain_verification_status !== "verified" && (
                <Alert
                  type="warning"
                  message="DNS Verification Required"
                  description={
                    <Space direction="vertical">
                      <Text>{domainVerification.instructions}</Text>
                      {domainVerification.dns_record_name && (
                        <Text copyable={{ text: domainVerification.dns_record_name }}>
                          Record: {domainVerification.dns_record_name}
                        </Text>
                      )}
                      {domainVerification.dns_record_value && (
                        <Text copyable={{ icon: <CopyOutlined />, text: domainVerification.dns_record_value }}>
                          Value: {domainVerification.dns_record_value}
                        </Text>
                      )}
                    </Space>
                  }
                />
              )}
              {store.domain_verification_status !== "verified" && (
                <Button onClick={handleVerifyDomain} loading={isSaving}>
                  Verify Domain
                </Button>
              )}
            </Space>
          )}
        </Card>
      ),
    },
    {
      key: "tips",
      label: "Tips",
      children: (
        <Card loading={isLoading}>
          <Form form={form} layout="vertical">
            <Form.Item label="Enable Tips at Checkout" name="tips_enabled" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item
              label="Tip Options (%)"
              name="tip_options"
              rules={[{ required: true, message: "Add at least one tip option" }]}
            >
              <Select mode="tags" placeholder="e.g. 10, 15, 20" tokenSeparators={[","]} />
            </Form.Item>
            <Button type="primary" onClick={handleSaveTips} loading={isSaving}>
              Save Tips
            </Button>
          </Form>
        </Card>
      ),
    },
    {
      key: "tracking",
      label: "Tracking",
      children: (
        <Card loading={isLoading}>
          <Form form={form} layout="vertical">
            <Form.Item label="Facebook Pixel ID" name="facebook_pixel_id">
              <Input placeholder="123456789012345" />
            </Form.Item>
            <Form.Item label="Google Analytics Measurement ID" name="google_analytics_id">
              <Input placeholder="G-XXXXXXXXXX" />
            </Form.Item>
            <Button type="primary" onClick={handleSaveTracking} loading={isSaving}>
              Save Tracking
            </Button>
          </Form>
        </Card>
      ),
    },
    {
      key: "abandoned",
      label: "Abandoned Checkout",
      children: (
        <Card loading={isLoading}>
          <Form form={form} layout="vertical">
            <Form.Item label="Enable Abandoned Checkout Recovery" name="abandoned_checkout_enabled" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label="Send Email After (minutes)" name="abandoned_checkout_delay_minutes">
              <InputNumber min={15} max={1440} style={{ width: 200 }} />
            </Form.Item>
            <Form.Item label="Email Subject" name="abandoned_checkout_email_subject">
              <Input />
            </Form.Item>
            <Form.Item label="Email Body" name="abandoned_checkout_email_body">
              <TextArea rows={6} />
            </Form.Item>
            <Button type="primary" onClick={handleSaveAbandoned} loading={isSaving}>
              Save Abandoned Checkout
            </Button>
          </Form>
        </Card>
      ),
    },
  ];

  return (
    <div>
      <Title level={3} style={{ marginBottom: 8 }}>
        Storefront Setup
      </Title>
      <Text type="secondary" style={{ display: "block", marginBottom: 24 }}>
        Configure your store branding, domain, tips, tracking pixels, and abandoned checkout recovery.
      </Text>
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} closable />}
      <Tabs items={tabItems} />
    </div>
  );
}
