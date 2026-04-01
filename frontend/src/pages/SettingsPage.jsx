import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Form,
  Input,
  Button,
  Select,
  Typography,
  App as AntdApp,
  Alert,
  Row,
  Col,
} from "antd";
import { SaveOutlined, UserOutlined, BankOutlined } from "@ant-design/icons";
import useAuthStore from "../store/authStore";
import { getCompanyProfile, updateCompanyProfile } from "../api/company";
import PageLayout from "../components/layout/PageLayout";

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

/**
 * SettingsPage component for company profile management.
 */
function SettingsPage() {
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const { isAuthenticated, user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const loadProfile = async () => {
      if (!isAuthenticated) return;
      setProfileLoading(true);
      try {
        const profile = await getCompanyProfile();
        form.setFieldsValue(profile);
      } catch (error) {
        // 404 is expected for first-time setup.
        if (error?.response?.status !== 404) {
          message.error("Failed to load company profile");
        }
      } finally {
        setProfileLoading(false);
      }
    };

    loadProfile();
  }, [isAuthenticated, form]);

  const handleSave = async (values) => {
    setLoading(true);
    try {
      const payload = {
        ...values,
        gstin: values.gstin?.toUpperCase(),
      };
      await updateCompanyProfile(payload);
      message.success("Company profile saved successfully!");
    } catch (error) {
      message.error(
        error?.response?.data?.detail || "Failed to save company profile",
      );
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <PageLayout
      title="Settings"
      subtitle="Manage user profile, company profile, and compliance defaults."
    >
      <div className="hero-panel soft-reveal">
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} md={16}>
            <Title level={4} style={{ marginTop: 0, marginBottom: 8 }}>
              Compliance Configuration Center
            </Title>
            <Text type="secondary">
              Keep business profile data accurate to reduce validation failures
              during uploads and return generation.
            </Text>
          </Col>
          <Col xs={24} md={8}>
            <div className="glass-note">
              <Text type="secondary">Signed-in User</Text>
              <Title level={5} style={{ margin: "6px 0 0" }}>
                {user?.email || "-"}
              </Title>
            </div>
          </Col>
        </Row>
      </div>

      <Row gutter={[24, 24]}>
        {/* User Profile */}
        <Col xs={24} lg={12}>
          <Card
            className="section-card soft-reveal"
            title={
              <span>
                <UserOutlined style={{ marginRight: 8 }} />
                User Profile
              </span>
            }
          >
            <Form layout="vertical" initialValues={{ email: user?.email }}>
              <Form.Item label="Email">
                <Input disabled value={user?.email} />
              </Form.Item>
              <Form.Item label="Role">
                <Input disabled value={user?.role || "admin"} />
              </Form.Item>
              <Alert
                message="Password Change"
                description="Password change functionality will be available in the next update."
                type="info"
                showIcon
              />
            </Form>
          </Card>
        </Col>

        {/* Company Profile */}
        <Col xs={24} lg={12}>
          <Card
            className="section-card soft-reveal"
            title={
              <span>
                <BankOutlined style={{ marginRight: 8 }} />
                Company Profile
              </span>
            }
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
              disabled={profileLoading}
              initialValues={{
                turnover_slab: "1.5cr_to_5cr",
                filing_frequency: "monthly",
              }}
            >
              <Form.Item
                name="gstin"
                label="GSTIN"
                rules={[
                  { required: true, message: "Please enter GSTIN" },
                  { len: 15, message: "GSTIN must be exactly 15 characters" },
                ]}
              >
                <Input placeholder="Enter 15-character GSTIN" maxLength={15} />
              </Form.Item>

              <Form.Item
                name="legal_name"
                label="Legal Name"
                rules={[{ required: true, message: "Please enter legal name" }]}
              >
                <Input placeholder="Enter legal name as per GST registration" />
              </Form.Item>

              <Form.Item name="trade_name" label="Trade Name">
                <Input placeholder="Enter trade name (if different)" />
              </Form.Item>

              <Form.Item
                name="address"
                label="Registered Address"
                rules={[{ required: true, message: "Please enter address" }]}
              >
                <TextArea rows={3} placeholder="Enter registered address" />
              </Form.Item>

              <Form.Item
                name="state_code"
                label="State Code"
                rules={[
                  { required: true, message: "Please select state code" },
                ]}
              >
                <Select placeholder="Select state code">
                  <Option value="01">01 - Jammu and Kashmir</Option>
                  <Option value="02">02 - Himachal Pradesh</Option>
                  <Option value="03">03 - Punjab</Option>
                  <Option value="04">04 - Chandigarh</Option>
                  <Option value="05">05 - Uttarakhand</Option>
                  <Option value="06">06 - Haryana</Option>
                  <Option value="07">07 - Delhi</Option>
                  <Option value="08">08 - Rajasthan</Option>
                  <Option value="09">09 - Uttar Pradesh</Option>
                  <Option value="10">10 - Bihar</Option>
                  <Option value="11">11 - Sikkim</Option>
                  <Option value="12">12 - Arunachal Pradesh</Option>
                  <Option value="13">13 - Nagaland</Option>
                  <Option value="14">14 - Manipur</Option>
                  <Option value="15">15 - Mizoram</Option>
                  <Option value="16">16 - Tripura</Option>
                  <Option value="17">17 - Meghalaya</Option>
                  <Option value="18">18 - Assam</Option>
                  <Option value="19">19 - West Bengal</Option>
                  <Option value="20">20 - Jharkhand</Option>
                  <Option value="21">21 - Odisha</Option>
                  <Option value="22">22 - Chhattisgarh</Option>
                  <Option value="23">23 - Madhya Pradesh</Option>
                  <Option value="24">24 - Gujarat</Option>
                  <Option value="25">
                    25 - Daman and Diu / Dadra and Nagar Haveli
                  </Option>
                  <Option value="26">
                    26 - Dadra and Nagar Haveli and Daman and Diu
                  </Option>
                  <Option value="27">27 - Maharashtra</Option>
                  <Option value="28">28 - Andhra Pradesh (Old)</Option>
                  <Option value="29">29 - Karnataka</Option>
                  <Option value="30">30 - Goa</Option>
                  <Option value="31">31 - Lakshadweep</Option>
                  <Option value="32">32 - Kerala</Option>
                  <Option value="33">33 - Tamil Nadu</Option>
                  <Option value="34">34 - Puducherry</Option>
                  <Option value="35">35 - Andaman and Nicobar Islands</Option>
                  <Option value="36">36 - Telangana</Option>
                  <Option value="37">37 - Andhra Pradesh (New)</Option>
                  <Option value="38">38 - Ladakh</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="turnover_slab"
                label="Turnover Slab"
                rules={[
                  { required: true, message: "Please select turnover slab" },
                ]}
              >
                <Select placeholder="Select annual turnover">
                  <Option value="below_1.5cr">Below ₹1.5 Crore</Option>
                  <Option value="1.5cr_to_5cr">₹1.5 Crore - ₹5 Crore</Option>
                  <Option value="above_5cr">Above ₹5 Crore</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="filing_frequency"
                label="Filing Frequency"
                rules={[
                  { required: true, message: "Please select filing frequency" },
                ]}
              >
                <Select placeholder="Select filing frequency">
                  <Option value="monthly">Monthly (GSTR-1 by 11th)</Option>
                  <Option value="quarterly">Quarterly (QRMP Scheme)</Option>
                </Select>
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={loading}
                  block
                >
                  Save Company Profile
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>

      {/* Compliance Settings */}
      <Card
        className="section-card soft-reveal"
        title="Compliance Controls"
        style={{ marginTop: 24 }}
      >
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card type="inner" title="HSN Code Requirements">
              <Text type="secondary">
                Based on your turnover slab, HSN code requirements:
              </Text>
              <ul style={{ marginTop: 8, fontSize: 13 }}>
                <li>Below ₹1.5Cr: HSN optional</li>
                <li>₹1.5Cr - ₹5Cr: 4-digit HSN mandatory</li>
                <li>Above ₹5Cr: 6-digit HSN mandatory</li>
              </ul>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card type="inner" title="Due Dates">
              <Text type="secondary">Monthly filing due dates:</Text>
              <ul style={{ marginTop: 8, fontSize: 13 }}>
                <li>GSTR-1: 11th of next month</li>
                <li>GSTR-3B: 20th/22nd/24th of next month</li>
                <li>GSTR-9: 31st December (annual)</li>
              </ul>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card type="inner" title="E-Invoicing">
              <Text type="secondary">
                E-invoicing is mandatory for businesses with turnover above ₹5
                Crore.
              </Text>
              <Alert
                message="Coming Soon"
                description="E-invoice IRN generation will be available in Phase 2."
                type="info"
                showIcon
                style={{ marginTop: 8 }}
              />
            </Card>
          </Col>
        </Row>
      </Card>

      {/* Data Management */}
      <Card
        className="section-card soft-reveal"
        title="Data Management"
        style={{ marginTop: 24 }}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} md={6}>
            <Button block icon={<SaveOutlined />}>
              Backup Data
            </Button>
            <Text
              type="secondary"
              style={{ fontSize: 12, display: "block", marginTop: 4 }}
            >
              Download all data
            </Text>
          </Col>
          <Col xs={24} md={6}>
            <Button block disabled icon={<SaveOutlined />}>
              Restore Data
            </Button>
            <Text
              type="secondary"
              style={{ fontSize: 12, display: "block", marginTop: 4 }}
            >
              Coming soon
            </Text>
          </Col>
          <Col xs={24} md={6}>
            <Button block danger disabled>
              Delete All Data
            </Button>
            <Text
              type="secondary"
              style={{ fontSize: 12, display: "block", marginTop: 4 }}
            >
              Permanent action
            </Text>
          </Col>
        </Row>
      </Card>
    </PageLayout>
  );
}

export default SettingsPage;
