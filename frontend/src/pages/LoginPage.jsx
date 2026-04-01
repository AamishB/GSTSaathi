import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  App as AntdApp,
  Alert,
} from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import useAuthStore from "../store/authStore";
import appLogo from "../../assets/logo.png";

const { Title, Text } = Typography;

/**
 * LoginPage component for user authentication.
 */
function LoginPage() {
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const { login, register, loading, error, clearError } = useAuthStore();
  const [isRegister, setIsRegister] = useState(false);

  const onFinish = async (values) => {
    clearError();
    try {
      if (isRegister) {
        await register(values.email, values.password);
        message.success("Registration successful! Please login.");
        setIsRegister(false);
      } else {
        await login(values.email, values.password);
        message.success("Login successful!");
        navigate("/dashboard");
      }
    } catch (err) {
      // Error handled by store
    }
  };

  return (
    <div className="auth-page">
      <Card className="auth-card">
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div className="auth-brand">
            <img src={appLogo} alt="GSTSaathi logo" className="brand-logo" />
            <Title level={2} style={{ marginBottom: 0 }}>
              GSTSaathi
            </Title>
          </div>
          <Text className="auth-tagline" type="secondary">
            AI-assisted GST compliance workspace for finance teams
          </Text>
          <Title level={2} style={{ marginBottom: 8 }}>
            {isRegister ? "Create Account" : "Welcome Back"}
          </Title>
          <Text type="secondary">
            GST compliance made accurate and auditable
          </Text>
        </div>

        <div className="kpi-strip" style={{ marginBottom: 18 }}>
          <div className="kpi-item">
            <div className="kpi-label">Invoices</div>
            <div className="kpi-value">Validated</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Mismatch</div>
            <div className="kpi-value">Tracked</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Returns</div>
            <div className="kpi-value">Prepared</div>
          </div>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        <Form name="login" onFinish={onFinish} autoComplete="off" size="large">
          <Form.Item
            name="email"
            rules={[
              { required: true, message: "Please input your email!" },
              { type: "email", message: "Please enter a valid email!" },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Email"
              disabled={loading}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: "Please input your password!" }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password"
              disabled={loading}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
            >
              {isRegister ? "Register" : "Login"}
            </Button>
          </Form.Item>

          <div style={{ textAlign: "center" }}>
            <Text type="secondary">
              {isRegister
                ? "Already have an account?"
                : "Don't have an account?"}
            </Text>
            <br />
            <Button
              type="link"
              onClick={() => {
                setIsRegister(!isRegister);
                clearError();
              }}
              style={{ padding: 0 }}
            >
              {isRegister ? "Login here" : "Register here"}
            </Button>
          </div>
        </Form>

        <div className="glass-note" style={{ marginTop: 16 }}>
          <Text type="secondary">
            Includes: invoice validation, mismatch detection, and return export
            assistance.
          </Text>
        </div>
      </Card>
    </div>
  );
}

export default LoginPage;
