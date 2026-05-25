"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button, Card, Form, Input, Typography, message } from "antd";
import { MailOutlined, LockOutlined } from "@ant-design/icons";
import { useAuthStore } from "@/stores/auth-store";
import { getApiErrorMessage } from "@/lib/api-error";

const { Title, Text } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const { login } = useAuthStore();
  const router = useRouter();

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.email, values.password);
      router.push("/");
    } catch (err) {
      message.error(getApiErrorMessage(err, "Invalid email or password"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f5f5f5",
      }}
    >
      <Card style={{ width: 400 }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <Title level={2} style={{ color: "#1677ff", marginBottom: 4 }}>
            FinPulse
          </Title>
          <Text type="secondary">Sign in to your dashboard</Text>
        </div>

        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="email" rules={[{ required: true, type: "email", message: "Please enter a valid email" }]}>
            <Input prefix={<MailOutlined />} placeholder="Email" size="large" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: "Please enter your password" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Password" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              Sign In
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: "center" }}>
          <Text type="secondary">
            Don&apos;t have an account? <Link href="/signup">Sign up</Link>
          </Text>
        </div>
      </Card>
    </div>
  );
}
