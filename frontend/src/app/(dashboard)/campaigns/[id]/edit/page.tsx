"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Spin,
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

export default function EditCampaignPage() {
  const params = useParams();
  const router = useRouter();
  const campaignId = params.id as string;
  const {
    currentCampaign,
    products,
    fetchCampaign,
    fetchProducts,
    updateCampaign,
    uploadDesign,
    publishCampaign,
    isLoading,
    isSaving,
  } = useCampaignStore();
  const [form] = Form.useForm();
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [printLocation, setPrintLocation] = useState("front");

  useEffect(() => {
    fetchProducts();
    fetchCampaign(campaignId).catch(() => router.push("/campaigns"));
  }, [campaignId, fetchCampaign, fetchProducts, router]);

  useEffect(() => {
    if (!currentCampaign || currentCampaign.id !== campaignId) return;
    const product = products.find((p) => p.id === currentCampaign.product_id) || null;
    setSelectedProduct(product);
    setPrintLocation(currentCampaign.print_location || "front");

    const variantPrices: Record<string, number> = {};
    currentCampaign.variants.forEach((v) => {
      variantPrices[v.variant_id] = Number(v.price);
    });

    form.setFieldsValue({
      title: currentCampaign.title,
      description: currentCampaign.description,
      retail_price: Number(currentCampaign.retail_price),
      print_location: currentCampaign.print_location || "front",
      variant_prices: variantPrices,
    });
  }, [currentCampaign, campaignId, products, form]);

  if (isLoading && !currentCampaign) {
    return (
      <div style={{ textAlign: "center", padding: 48 }}>
        <Spin />
      </div>
    );
  }

  if (!currentCampaign) return null;

  if (currentCampaign.status === "ended") {
    return (
      <Alert
        type="info"
        message="This campaign has ended and cannot be edited."
        action={<Button onClick={() => router.push("/campaigns")}>Back to campaigns</Button>}
      />
    );
  }

  const handleSave = async () => {
    const values = await form.validateFields();
    const variant_prices = Object.entries(values.variant_prices as Record<string, number>).map(
      ([variant_id, price]) => ({ variant_id, price: Number(price) })
    );
    await updateCampaign(campaignId, {
      title: values.title,
      description: values.description,
      retail_price: values.retail_price,
      print_location: values.print_location,
      variant_prices,
    });
    message.success("Campaign updated");
  };

  const handleDesignUpload = async (file: File, side: "front" | "back") => {
    try {
      await uploadDesign(campaignId, file, side);
      message.success(`${side === "front" ? "Front" : "Back"} design updated`);
    } catch {
      message.error("Upload failed");
    }
    return false;
  };

  const canPublish =
    currentCampaign.status === "draft" &&
    (!needsFrontDesign(printLocation) || currentCampaign.design_image_url) &&
    (!needsBackDesign(printLocation) || currentCampaign.design_back_url);

  return (
    <div style={{ maxWidth: 720 }}>
      <Title level={3} style={{ marginBottom: 8 }}>Edit Campaign</Title>
      <Text type="secondary" style={{ display: "block", marginBottom: 24 }}>
        {currentCampaign.status.toUpperCase()} — {currentCampaign.product_name}
      </Text>

      <Form form={form} layout="vertical">
        <Card style={{ marginBottom: 16 }}>
          <Form.Item label="Campaign Title" name="title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Description" name="description">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item label="Print Location" name="print_location">
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
                  label={v.name}
                  name={["variant_prices", v.id]}
                  rules={[{ required: true }]}
                >
                  <InputNumber min={1} precision={2} style={{ width: 200 }} />
                </Form.Item>
              ))}
            </>
          )}
          <Button type="primary" onClick={handleSave} loading={isSaving}>
            Save changes
          </Button>
        </Card>

        <Card title="Designs" style={{ marginBottom: 16 }}>
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            {needsFrontDesign(printLocation) && (
              <div>
                <Text strong style={{ display: "block", marginBottom: 8 }}>
                  Front design {currentCampaign.design_image_url ? "✓" : "(required)"}
                </Text>
                {currentCampaign.design_image_url && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={currentCampaign.design_image_url}
                    alt="Front design"
                    style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 4, marginBottom: 8 }}
                  />
                )}
                <Upload beforeUpload={(f) => handleDesignUpload(f, "front")} accept="image/*" maxCount={1}>
                  <Button icon={<UploadOutlined />} loading={isSaving}>Replace front design</Button>
                </Upload>
              </div>
            )}
            {needsBackDesign(printLocation) && (
              <div>
                <Text strong style={{ display: "block", marginBottom: 8 }}>
                  Back design {currentCampaign.design_back_url ? "✓" : "(required)"}
                </Text>
                {currentCampaign.design_back_url && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={currentCampaign.design_back_url}
                    alt="Back design"
                    style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 4, marginBottom: 8 }}
                  />
                )}
                <Upload beforeUpload={(f) => handleDesignUpload(f, "back")} accept="image/*" maxCount={1}>
                  <Button icon={<UploadOutlined />} loading={isSaving}>Replace back design</Button>
                </Upload>
              </div>
            )}
          </Space>
        </Card>

        <Space>
          {currentCampaign.status === "draft" && (
            <Button
              type="primary"
              disabled={!canPublish}
              loading={isSaving}
              onClick={async () => {
                try {
                  await publishCampaign(campaignId);
                  message.success("Campaign published");
                  router.push("/campaigns");
                } catch {
                  message.error("Publish failed — upload all required designs");
                }
              }}
            >
              Publish
            </Button>
          )}
          <Button onClick={() => router.push("/campaigns")}>Back</Button>
        </Space>
      </Form>
    </div>
  );
}
