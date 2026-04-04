import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Typography,
  App as AntdApp,
  Alert,
  Row,
  Col,
  Select,
} from "antd";
import {
  InboxOutlined,
  UploadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons";
import useUploadStore from "../store/uploadStore";
import useAuthStore from "../store/authStore";
import UploadZone from "../components/organisms/UploadZone";
import DataTable from "../components/ui/DataTable";
import PageLayout from "../components/layout/PageLayout";

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const formatUploadDate = (value) => {
  if (!value) return "-";

  const raw = String(value);
  const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(raw);
  const normalized = hasTimezone ? raw : `${raw}Z`;
  const parsed = new Date(normalized);

  if (Number.isNaN(parsed.getTime())) {
    return "-";
  }

  return parsed.toLocaleString("en-IN");
};

function UploadPage() {
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const { isAuthenticated } = useAuthStore();
  const {
    uploadInvoices,
    uploadGSTR2B,
    uploading,
    uploadResult,
    uploadError,
    history,
    loadHistory,
    clearUploadResult,
  } = useUploadStore();

  const [turnoverSlab, setTurnoverSlab] = useState("1.5cr_to_5cr");
  const [uploadType, setUploadType] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    loadHistory();
  }, [isAuthenticated, navigate, loadHistory]);

  const historyColumns = [
    { title: "Batch ID", dataIndex: "batch_id", key: "batch_id" },
    {
      title: "Type",
      dataIndex: "type",
      key: "type",
      render: (value) => (value === "gstr2b" ? "GSTR-2B" : "Invoices"),
    },
    { title: "Count", dataIndex: "count", key: "count" },
    {
      title: "Total Value",
      dataIndex: "total_value",
      key: "total_value",
      render: (value) => `₹${(value || 0).toLocaleString("en-IN")}`,
    },
    {
      title: "Uploaded At",
      dataIndex: "created_at",
      key: "created_at",
      render: (value) => formatUploadDate(value),
    },
  ];

  const handleInvoiceUpload = async (file) => {
    setUploadType("invoices");
    clearUploadResult();
    try {
      const result = await uploadInvoices(file, turnoverSlab);
      if (result.success) {
        message.success(
          `Uploaded ${result.invoice_count} invoices successfully!`,
        );
        loadHistory();
      } else {
        message.error("Upload completed with errors");
      }
    } catch (err) {
      // Store handles error state.
    }
    return false;
  };

  const handleGSTR2BUpload = async (file) => {
    setUploadType("gstr2b");
    clearUploadResult();
    try {
      const result = await uploadGSTR2B(file);
      if (result.success) {
        message.success(
          `Uploaded ${result.entry_count} GSTR-2B entries successfully!`,
        );
        loadHistory();
      }
    } catch (err) {
      // Store handles error state.
    }
    return false;
  };

  if (!isAuthenticated) return null;

  return (
    <PageLayout
      title="Upload Documents"
      subtitle="Upload invoice and GSTR-2B files to start reconciliation workflows."
    >
      <div className="hero-panel soft-reveal">
        <Row gutter={[16, 16]}>
          <Col xs={24} md={16}>
            <Title level={4} style={{ marginTop: 0, marginBottom: 8 }}>
              Guided Upload Workflow
            </Title>
            <Text type="secondary">
              Step 1: Upload invoices. Step 2: Upload GSTR-2B. Step 3: Reconcile
              and export mismatch report.
            </Text>
          </Col>
          <Col xs={24} md={8}>
            <div className="kpi-item">
              <div className="kpi-label">Uploaded Batches</div>
              <div className="kpi-value">{history?.length || 0}</div>
            </div>
          </Col>
        </Row>
      </div>

      {uploadError && (
        <Alert
          message={uploadError}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {uploadResult && (
        <Card
          className="section-card"
          style={{ marginBottom: 24 }}
          styles={{ body: { padding: 16 } }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {uploadResult.success ? (
              <CheckCircleOutlined style={{ fontSize: 24, color: "#52c41a" }} />
            ) : (
              <CloseCircleOutlined style={{ fontSize: 24, color: "#ff4d4f" }} />
            )}
            <div>
              <Text strong>{uploadResult.message}</Text>
              {uploadResult.invoice_count !== undefined && (
                <Paragraph style={{ margin: 0, fontSize: 12 }}>
                  Total Invoices: {uploadResult.invoice_count} | Duplicates:{" "}
                  {uploadResult.duplicate_count || 0} | Total Value: ₹
                  {(uploadResult.total_value || 0).toLocaleString("en-IN")}
                </Paragraph>
              )}
              {uploadResult.entry_count !== undefined && (
                <Paragraph style={{ margin: 0, fontSize: 12 }}>
                  Total Entries: {uploadResult.entry_count} | Total ITC: ₹
                  {(uploadResult.total_itc || 0).toLocaleString("en-IN")}
                </Paragraph>
              )}
            </div>
          </div>
        </Card>
      )}

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card
            className="section-card soft-reveal"
            title="Invoice Register Upload"
          >
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">
                Upload your sales or purchase invoice register in Excel or CSV
                format.
              </Text>
            </div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>Turnover Slab:</Text>
              <Select
                value={turnoverSlab}
                onChange={setTurnoverSlab}
                style={{ width: "100%", marginTop: 8 }}
                disabled={uploading}
              >
                <Option value="below_1.5cr">Below ₹1.5 Crore</Option>
                <Option value="1.5cr_to_5cr">₹1.5 Crore - ₹5 Crore</Option>
                <Option value="above_5cr">Above ₹5 Crore</Option>
              </Select>
            </div>
            <UploadZone
              title=""
              description=""
              accept=".xlsx,.xls,.csv"
              onUpload={handleInvoiceUpload}
              disabled={uploading}
              icon={<InboxOutlined style={{ color: "#1890ff" }} />}
              hint="Supports Excel (.xlsx, .xls) and CSV files"
              uploading={uploading && uploadType === "invoices"}
              helper={{
                title: "Required Columns",
                content: (
                  <ul
                    className="muted-note"
                    style={{ margin: 0, paddingLeft: 20 }}
                  >
                    <li>invoice_number</li>
                    <li>invoice_date</li>
                    <li>supplier_gstin</li>
                    <li>supplier_name</li>
                    <li>recipient_gstin</li>
                    <li>recipient_name</li>
                    <li>taxable_value</li>
                    <li>total_value</li>
                    <li>place_of_supply</li>
                  </ul>
                ),
              }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card className="section-card soft-reveal" title="GSTR-2B Upload">
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">
                Upload GSTR-2B data downloaded from GST portal for matching.
              </Text>
            </div>
            <UploadZone
              title=""
              description=""
              accept=".json,.xlsx,.xls"
              onUpload={handleGSTR2BUpload}
              disabled={uploading}
              icon={<UploadOutlined style={{ color: "#52c41a" }} />}
              hint="Supports JSON (from GST portal) or Excel files"
              uploading={uploading && uploadType === "gstr2b"}
              helper={{
                title: "How to download GSTR-2B",
                content: (
                  <ol
                    className="muted-note"
                    style={{ margin: 0, paddingLeft: 20 }}
                  >
                    <li>Login to GST Portal (www.gst.gov.in)</li>
                    <li>
                      Go to Services -&gt; Returns -&gt; Returns Dashboard
                    </li>
                    <li>Select Financial Year and Month</li>
                    <li>Click on "Download" under GSTR-2B</li>
                    <li>Upload the downloaded file here</li>
                  </ol>
                ),
              }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        className="section-card soft-reveal"
        title="Upload History"
        style={{ marginTop: 24 }}
      >
        <DataTable
          columns={historyColumns}
          dataSource={history}
          rowKey={(row) => `${row.batch_id}-${row.type}`}
          pageSize={10}
        />
      </Card>
    </PageLayout>
  );
}

export default UploadPage;
