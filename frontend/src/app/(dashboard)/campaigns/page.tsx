"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Button, Card, Empty, Space, Table, Tag, Typography } from "antd";
import { PlusOutlined, RocketOutlined } from "@ant-design/icons";
import { useCampaignStore } from "@/stores/campaign-store";
import type { Campaign } from "@/lib/types/campaign";

const { Title, Text } = Typography;

const statusColors: Record<string, string> = {
  draft: "default",
  live: "green",
  ended: "red",
};

export default function CampaignsPage() {
  const { campaigns, isLoading, fetchCampaigns, publishCampaign, endCampaign } = useCampaignStore();

  useEffect(() => {
    fetchCampaigns();
  }, [fetchCampaigns]);

  const columns = [
    {
      title: "Campaign",
      dataIndex: "title",
      key: "title",
      render: (title: string, record: Campaign) => (
        <Space>
          {record.design_image_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={record.design_image_url} alt="" style={{ width: 40, height: 40, objectFit: "cover", borderRadius: 4 }} />
          )}
          <div>
            <Text strong>{title}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: 12 }}>{record.product_name}</Text>
          </div>
        </Space>
      ),
    },
    {
      title: "Price",
      dataIndex: "retail_price",
      key: "retail_price",
      render: (v: number) => `$${Number(v).toFixed(2)}`,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>,
    },
    {
      title: "Sold",
      dataIndex: "units_sold",
      key: "units_sold",
    },
    {
      title: "Actions",
      key: "actions",
      render: (_: unknown, record: Campaign) => (
        <Space>
          {record.status === "draft" && (
            <Button size="small" type="primary" onClick={() => publishCampaign(record.id)}>
              Publish
            </Button>
          )}
          {record.status === "live" && (
            <>
              <Link href={`/campaign/${record.slug}`} target="_blank">
                <Button size="small">View</Button>
              </Link>
              <Button size="small" danger onClick={() => endCampaign(record.id)}>
                End
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <Title level={3} style={{ marginBottom: 4 }}>Sales Campaigns</Title>
          <Text type="secondary">Create and manage your product campaigns</Text>
        </div>
        <Link href="/campaigns/new">
          <Button type="primary" icon={<PlusOutlined />}>New Campaign</Button>
        </Link>
      </div>

      {campaigns.length === 0 && !isLoading ? (
        <Card>
          <Empty
            image={<RocketOutlined style={{ fontSize: 48, color: "#1677ff" }} />}
            description="No campaigns yet. Create your first sales campaign!"
          >
            <Link href="/campaigns/new">
              <Button type="primary">Create Campaign</Button>
            </Link>
          </Empty>
        </Card>
      ) : (
        <Table rowKey="id" columns={columns} dataSource={campaigns} loading={isLoading} pagination={false} />
      )}
    </div>
  );
}
