"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Button,
  Card,
  DatePicker,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Steps,
  Typography,
  Upload,
  message,
} from "antd";
import { UploadOutlined } from "@ant-design/icons";
import { useCampaignStore } from "@/stores/campaign-store";
import type { Product } from "@/lib/types/campaign";

const { Title, Text } = Typography;
const { TextArea } = Input;

function needsBackDesign(printLocation: string) {
  return printLocation === "back" || printLocation === "both";
}

function needsFrontDesign(printLocation: string) {
  return printLocation === "front" || printLocation === "both";
}

export default function NewCampaignPage() {
  const router = useRouter();
  const { products, fetchProducts, createCampaign, uploadDesign, publishCampaign, isSaving } = useCampaignStore();
  const [step, setStep] = useState(0);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [campaignId, setCampaignId] = useState<string | null>(null);
  const [printLocation, setPrintLocation] = useState("front");
  const [frontUploaded, setFrontUploaded] = useState(false);
  const [backUploaded, setBackUploaded] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleProductChange = (productId: string) => {
    const product = products.find((p) => p.id === productId) || null;
    setSelectedProduct(product);
    if (product) {
      const prices: Record<string, number> = {};
      product.variants.forEach((v) => {
        prices[v.id] = Number(v.base_price) + 10;
      });
      form.setFieldsValue({
        variant_prices: prices,
        retail_price: Number(product.variants[0]?.base_price || 0) + 10,
      });
    }
  };

  const handleCreate = async () => {
    const values = await form.validateFields(["title", "product_id", "description", "retail_price", "variant_prices", "print_location"]);
    const variant_prices = Object.entries(values.variant_prices as Record<string, number>).map(([variant_id, price]) => ({
      variant_id,
      price: Number(price),
    }));

    const location = values.print_location || "front";
    setPrintLocation(location);

    const payload = {
      title: values.title,
      product_id: values.product_id,
      description: values.description,
      retail_price: values.retail_price,
      print_location: location,
      variant_prices,
      starts_at: values.date_range?.[0]?.toDate?.()?.toISOString?.(),
      ends_at: values.date_range?.[1]?.toDate?.()?.toISOString?.(),
    };

    const campaign = await createCampaign(payload);
    setCampaignId(campaign.id);
    setStep(1);
    message.success("Campaign created — now upload your design");
  };

  const handleDesignUpload = async (file: File, side: "front" | "back") => {
    if (!campaignId) return false;
    try {
      await uploadDesign(campaignId, file, side);
      if (side === "front") setFrontUploaded(true);
      else setBackUploaded(true);
      message.success(`${side === "front" ? "Front" : "Back"} design uploaded`);
    } catch {
      message.error("Failed to upload design");
    }
    return false;
  };

  const designsReady =
    (!needsFrontDesign(printLocation) || frontUploaded) &&
    (!needsBackDesign(printLocation) || backUploaded);

  const handlePublish = async () => {
    if (!campaignId) return;
    if (!designsReady) {
      message.error("Upload all required designs before publishing");
      return;
    }
    try {
      await publishCampaign(campaignId);
      message.success("Campaign is live!");
      router.push("/campaigns");
    } catch {
      message.error("Publish failed — make sure all designs are uploaded");
    }
  };

  return (
    <div style={{ maxWidth: 720 }}>
      <Title level={3} style={{ marginBottom: 24 }}>Create Sales Campaign</Title>
      <Steps
        current={step}
        style={{ marginBottom: 32 }}
        items={[
          { title: "Product & Pricing" },
          { title: "Upload Design" },
          { title: "Publish" },
        ]}
      />

      <Form form={form} layout="vertical">
        {step === 0 && (
          <Card>
            <Form.Item label="Campaign Title" name="title" rules={[{ required: true }]}>
              <Input placeholder="Summer Collection 2026" />
            </Form.Item>
            <Form.Item label="Product" name="product_id" rules={[{ required: true }]}>
              <Select placeholder="Select a product" onChange={handleProductChange}>
                {products.map((p) => (
                  <Select.Option key={p.id} value={p.id}>{p.name}</Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item label="Description" name="description">
              <TextArea rows={3} placeholder="Tell your customers about this campaign..." />
            </Form.Item>
            <Form.Item label="Print Location" name="print_location" initialValue="front">
              <Select onChange={(v) => setPrintLocation(v)}>
                <Select.Option value="front">Front only</Select.Option>
                <Select.Option value="back">Back only</Select.Option>
                <Select.Option value="both">Front and back</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item label="Base Retail Price ($)" name="retail_price" rules={[{ required: true }]}>
              <InputNumber min={1} precision={2} style={{ width: 200 }} />
            </Form.Item>
            {selectedProduct && (
              <>
                <Text strong style={{ display: "block", marginBottom: 12 }}>Price per Size ($)</Text>
                {selectedProduct.variants.map((v) => (
                  <Form.Item
                    key={v.id}
                    label={`${v.name} (base $${v.base_price})`}
                    name={["variant_prices", v.id]}
                    rules={[{ required: true }]}
                  >
                    <InputNumber min={1} precision={2} style={{ width: 200 }} />
                  </Form.Item>
                ))}
              </>
            )}
            <Form.Item label="Campaign Duration (optional)" name="date_range">
              <DatePicker.RangePicker showTime style={{ width: "100%" }} />
            </Form.Item>
            <Button type="primary" onClick={handleCreate} loading={isSaving}>
              Continue
            </Button>
          </Card>
        )}

        {step === 1 && (
          <Card>
            <Text type="secondary" style={{ display: "block", marginBottom: 16 }}>
              Upload artwork for each print side selected above.
            </Text>
            <Space direction="vertical" size="large" style={{ width: "100%" }}>
              {needsFrontDesign(printLocation) && (
                <div>
                  <Text strong>Front design {frontUploaded && "✓"}</Text>
                  <Upload
                    beforeUpload={(file) => handleDesignUpload(file, "front")}
                    accept="image/*"
                    maxCount={1}
                    listType="picture"
                  >
                    <Button icon={<UploadOutlined />} loading={isSaving}>Upload front design</Button>
                  </Upload>
                </div>
              )}
              {needsBackDesign(printLocation) && (
                <div>
                  <Text strong>Back design {backUploaded && "✓"}</Text>
                  <Upload
                    beforeUpload={(file) => handleDesignUpload(file, "back")}
                    accept="image/*"
                    maxCount={1}
                    listType="picture"
                  >
                    <Button icon={<UploadOutlined />} loading={isSaving}>Upload back design</Button>
                  </Upload>
                </div>
              )}
              <Button type="primary" disabled={!designsReady} onClick={() => setStep(2)}>
                Continue to publish
              </Button>
            </Space>
          </Card>
        )}

        {step === 2 && (
          <Card>
            <Space direction="vertical" size="large">
              <Text>Your campaign is ready to go live. Once published, customers can purchase via your storefront.</Text>
              <Space>
                <Button type="primary" onClick={handlePublish} loading={isSaving} disabled={!designsReady}>
                  Publish Campaign
                </Button>
                <Button onClick={() => router.push("/campaigns")}>Save as Draft</Button>
              </Space>
            </Space>
          </Card>
        )}
      </Form>
    </div>
  );
}
