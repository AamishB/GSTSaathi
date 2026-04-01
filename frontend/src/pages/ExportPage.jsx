import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Button,
  Typography,
  Alert,
  Row,
  Col,
  DatePicker,
  App as AntdApp,
} from "antd";
import {
  DownloadOutlined,
  TableOutlined,
  FileExcelOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import dayjs from "dayjs";
import useAuthStore from "../store/authStore";
import { exportGSTR1, exportGSTR3B, exportMismatchReport } from "../api/export";
import ExportPanel from "../components/organisms/ExportPanel";
import PageLayout from "../components/layout/PageLayout";

const { Title, Text } = Typography;

/**
 * ExportPage component for downloading GST return files.
 */
function ExportPage() {
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const { isAuthenticated } = useAuthStore();
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const [exporting, setExporting] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);

  const handleExportGSTR1 = async () => {
    setExporting("gstr1");
    try {
      const month = selectedMonth.format("MM");
      const year = selectedMonth.format("YYYY");
      await exportGSTR1(month, parseInt(year));
      message.success("GSTR-1 JSON downloaded successfully!");
    } catch (err) {
      message.error("Failed to export GSTR-1");
    } finally {
      setExporting(null);
    }
  };

  const handleExportGSTR3B = async () => {
    setExporting("gstr3b");
    try {
      const month = selectedMonth.format("MM");
      const year = selectedMonth.format("YYYY");
      await exportGSTR3B(month, parseInt(year));
      message.success("GSTR-3B Excel downloaded successfully!");
    } catch (err) {
      message.error("Failed to export GSTR-3B");
    } finally {
      setExporting(null);
    }
  };

  const handleExportMismatchReport = async () => {
    setExporting("mismatch");
    try {
      await exportMismatchReport("all");
      message.success("Mismatch report downloaded successfully!");
    } catch (err) {
      message.error("Failed to export mismatch report");
    } finally {
      setExporting(null);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <PageLayout
      title="Export Returns"
      subtitle="Generate GSTR files and reconciliation reports for your selected tax period."
    >
      <div className="hero-panel soft-reveal">
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} md={16}>
            <Title level={4} style={{ marginTop: 0, marginBottom: 8 }}>
              Return Pack Generator
            </Title>
            <Text type="secondary">
              Pick a filing period and generate filing-ready exports with one
              click.
            </Text>
          </Col>
          <Col xs={24} md={8}>
            <div className="glass-note">
              <Text strong>Tax Period</Text>
              <DatePicker
                picker="month"
                value={selectedMonth}
                onChange={setSelectedMonth}
                format="MMMM YYYY"
                style={{ width: "100%", marginTop: 8 }}
              />
            </div>
          </Col>
        </Row>
      </div>

      <Alert
        message="Period Confirmation"
        description="Verify the tax period before generating filing outputs for this cycle."
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Row gutter={[24, 24]}>
        {/* GSTR-1 Export */}
        <Col xs={24} lg={8}>
          <ExportPanel
            icon={<FileTextOutlined />}
            iconColor="#1890ff"
            title="GSTR-1"
            description="Statement of outward supplies"
            includes={[
              "B2B Invoices (Table 4)",
              "B2C Large Invoices (Table 5)",
              "B2C Small Invoices (Table 7)",
              "HSN Summary (Table 12)",
            ]}
            buttonText="Download JSON"
            buttonIcon={<DownloadOutlined />}
            buttonLoading={exporting === "gstr1"}
            onClick={handleExportGSTR1}
          />
        </Col>

        {/* GSTR-3B Export */}
        <Col xs={24} lg={8}>
          <ExportPanel
            icon={<TableOutlined />}
            iconColor="#52c41a"
            title="GSTR-3B"
            description="Monthly summary return"
            includes={[
              "Outward Supplies (Table 3.1)",
              "ITC Claimed (Table 4)",
              "Interest and Late Fee (Table 5.1)",
              "Net GST Payable",
            ]}
            buttonText="Download Excel"
            buttonIcon={<FileExcelOutlined />}
            buttonLoading={exporting === "gstr3b"}
            onClick={handleExportGSTR3B}
          />
        </Col>

        {/* Mismatch Report Export */}
        <Col xs={24} lg={8}>
          <ExportPanel
            icon={<CheckCircleOutlined />}
            iconColor="#faad14"
            title="Mismatch Report"
            description="Reconciliation summary"
            includes={[
              "Missing Invoices",
              "Value Mismatches",
              "Supplier-wise Summary",
              "ITC At Risk",
            ]}
            buttonText="Download Excel"
            buttonIcon={<DownloadOutlined />}
            buttonLoading={exporting === "mismatch"}
            onClick={handleExportMismatchReport}
          />
        </Col>
      </Row>

      {/* Important Notes */}
      <Card
        className="section-card soft-reveal"
        title="Filing Notes"
        style={{ marginTop: 24 }}
      >
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          <li style={{ marginBottom: 8 }}>
            <Text strong>GSTR-1:</Text> Upload this JSON file to the GST portal
            offline tool for filing
          </li>
          <li style={{ marginBottom: 8 }}>
            <Text strong>GSTR-3B:</Text> Use this Excel file to review before
            filing on GST portal
          </li>
          <li style={{ marginBottom: 8 }}>
            <Text strong>Mismatch Report:</Text> Share with suppliers for
            follow-up on pending invoices
          </li>
          <li>
            <Text strong type="warning">
              Note:
            </Text>{" "}
            Always verify the data before filing on the GST portal
          </li>
        </ul>
      </Card>
    </PageLayout>
  );
}

export default ExportPage;
