"use client";

import { useMemo, useState } from "react";
import { Input, Modal, Select, Space, Typography, message } from "antd";
import { CopyOutlined } from "@ant-design/icons";
import { buildCampaignShareUrl } from "@/lib/campaign-url";

const { Text } = Typography;

interface ShareCampaignModalProps {
  open: boolean;
  slug: string;
  title: string;
  onClose: () => void;
}

const UTM_SOURCES = [
  { label: "Facebook", value: "facebook" },
  { label: "Instagram", value: "instagram" },
  { label: "Email", value: "email" },
  { label: "Direct share", value: "finpulse" },
];

const UTM_MEDIUMS = [
  { label: "Social post", value: "social" },
  { label: "Paid ad", value: "cpc" },
  { label: "Newsletter", value: "email" },
  { label: "Link share", value: "share" },
];

export default function ShareCampaignModal({ open, slug, title, onClose }: ShareCampaignModalProps) {
  const [source, setSource] = useState("finpulse");
  const [medium, setMedium] = useState("share");

  const shareUrl = useMemo(
    () => buildCampaignShareUrl(slug, { source, medium }),
    [slug, source, medium]
  );

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      message.success("Campaign link copied");
    } catch {
      message.error("Could not copy link");
    }
  };

  return (
    <Modal
      title={`Share: ${title}`}
      open={open}
      onCancel={onClose}
      onOk={copyLink}
      okText="Copy link"
      okButtonProps={{ icon: <CopyOutlined /> }}
    >
      <Space direction="vertical" size="middle" style={{ width: "100%" }}>
        <div>
          <Text type="secondary">Traffic source</Text>
          <Select
            style={{ width: "100%", marginTop: 4 }}
            value={source}
            options={UTM_SOURCES}
            onChange={setSource}
          />
        </div>
        <div>
          <Text type="secondary">Medium</Text>
          <Select
            style={{ width: "100%", marginTop: 4 }}
            value={medium}
            options={UTM_MEDIUMS}
            onChange={setMedium}
          />
        </div>
        <div>
          <Text type="secondary">Share URL (with UTM tracking)</Text>
          <Input.TextArea value={shareUrl} readOnly rows={3} style={{ marginTop: 4 }} />
        </div>
      </Space>
    </Modal>
  );
}
