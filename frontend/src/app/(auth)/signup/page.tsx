"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button, Card, Form, Input, Typography, message } from "antd";
import { MailOutlined, LockOutlined, UserOutlined, BankOutlined } from "@ant-design/icons";
import { useAuthStore } from "@/stores/auth-store";
import { getApiErrorMessage } from "@/lib/api-error";

const { Title, Text } = Typography;

export default function SignupPage() {
  const [loading, setLoading] = useState(false);
  const { signup } = useAuthStore();
  const router = useRouter();

  const onFinish = async (values: {
    email: string;
    password: string;
    name: string;
    organization_name: string;
  }) => {
    setLoading(true);
    try {
      await signup(values.email, values.password, values.name, values.organization_name);
      message.success("Account created successfully!");
      router.push("/");
    } catch (err) {
      message.error(getApiErrorMessage(err, "Signup failed. Please try again."));
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
      <Card style={{ width: 420 }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <Title level={2} style={{ color: "#1677ff", marginBottom: 4 }}>
            FinPulse
          </Title>
          <Text type="secondary">Create your business dashboard</Text>
        </div>

        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="name" rules={[{ required: true, message: "Please enter your name" }]}>
            <Input prefix={<UserOutlined />} placeholder="Your Name" size="large" />
          </Form.Item>
          <Form.Item
            name="organization_name"
            rules={[{ required: true, message: "Please enter your company name" }]}
          >
            <Input prefix={<BankOutlined />} placeholder="Company Name" size="large" />
          </Form.Item>
          <Form.Item name="email" rules={[{ required: true, type: "email", message: "Please enter a valid email" }]}>
            <Input prefix={<MailOutlined />} placeholder="Work Email" size="large" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, min: 8, message: "Password must be at least 8 characters" }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              Create Account
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: "center" }}>
          <Text type="secondary">
            Already have an account? <Link href="/login">Sign in</Link>
          </Text>
        </div>
      </Card>
    </div>
  );
}
