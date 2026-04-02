import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Button,
  Alert,
  Space,
  Select,
  App as AntdApp,
  Row,
  Col,
  Progress,
  Typography,
} from "antd";
import {
  SyncOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  DownloadOutlined,
  MessageOutlined,
} from "@ant-design/icons";
import useReconcileStore from "../store/reconcileStore";
import useAuthStore from "../store/authStore";
import { exportMismatchReport } from "../api/export";
import MismatchTable from "../components/organisms/MismatchTable";
import StatCard from "../components/ui/StatCard";
import DataTable from "../components/ui/DataTable";
import EmptyState from "../components/ui/EmptyState";
import StatusBadge from "../components/ui/StatusBadge";
import PageLayout from "../components/layout/PageLayout";

const { Title } = Typography;
const { Option } = Select;

/**
 * ReconcilePage component for viewing reconciliation results.
 */
function ReconcilePage() {
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const { isAuthenticated } = useAuthStore();
  const {
    reconciling,
    reconciliationStatus,
    reconciliationResults,
    reconciliationLog,
    statistics,
    sendingWhatsApp,
    error,
    runReconciliation,
    loadResults,
    loadReconciliationLog,
    sendWhatsAppReminders,
    clearResults,
  } = useReconcileStore();

  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    loadResults(statusFilter);
    loadReconciliationLog();
  }, [
    isAuthenticated,
    statusFilter,
    navigate,
    loadResults,
    loadReconciliationLog,
  ]);

  const handleRunReconciliation = async () => {
    try {
      await runReconciliation();
      loadResults(statusFilter);
      loadReconciliationLog();
    } catch (err) {
      // Error handled by store
    }
  };

  const handleExportReport = async () => {
    try {
      await exportMismatchReport(statusFilter);
      message.success("Mismatch report downloaded successfully!");
    } catch (err) {
      message.error("Failed to export report");
    }
  };

  const handleSendWhatsApp = async () => {
    try {
      const result = await sendWhatsAppReminders([], "hi");
      message.success(result.message || "WhatsApp reminders sent successfully!");
    } catch (err) {
      message.error(err.response?.data?.detail || "Failed to send WhatsApp reminders");
    }
  };

  const hasMissingInGstr2b = reconciliationResults.some(
    (item) => item.match_status === "missing_in_gstr2b",
  );

  const logColumns = [
    {
      title: "Run Time",
      dataIndex: "created_at",
      key: "created_at",
      render: (value) => new Date(value).toLocaleString("en-IN"),
    },
    { title: "Job ID", dataIndex: "job_id", key: "job_id" },
    { title: "Matched", dataIndex: "matched_count", key: "matched_count" },
    { title: "Mismatched", dataIndex: "mismatch_count", key: "mismatch_count" },
    {
      title: "ITC At Risk",
      dataIndex: "itc_at_risk",
      key: "itc_at_risk",
      render: (value) => `₹${(value || 0).toLocaleString("en-IN")}`,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => <StatusBadge status={status} />,
    },
  ];

  if (!isAuthenticated) {
    return null;
  }

  return (
    <PageLayout
      title="Reconciliation"
      subtitle="Run matching and review mismatches with action-ready summaries."
      actions={
        <Space wrap>
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 150 }}
            disabled={reconciling}
          >
            <Option value="all">All</Option>
            <Option value="matched">Matched</Option>
            <Option value="mismatched">Mismatched</Option>
          </Select>
          <Button
            type="primary"
            icon={<SyncOutlined spin={reconciling} />}
            onClick={handleRunReconciliation}
            loading={reconciling}
          >
            {reconciling ? "Reconciling..." : "Run Reconciliation"}
          </Button>
          {statistics?.mismatchCount > 0 && (
            <Button icon={<DownloadOutlined />} onClick={handleExportReport}>
              Export Report
            </Button>
          )}
          {hasMissingInGstr2b && (
            <Button
              icon={<MessageOutlined />}
              onClick={handleSendWhatsApp}
              loading={sendingWhatsApp}
            >
              Send WhatsApp Reminders
            </Button>
          )}
        </Space>
      }
    >
      <div className="hero-panel soft-reveal">
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} md={16}>
            <Title level={4} style={{ marginTop: 0, marginBottom: 8 }}>
              Match Health and Risk
            </Title>
            <Typography.Text type="secondary">
              Prioritize missing and mismatched invoices, then export actionable
              reports for supplier follow-up.
            </Typography.Text>
          </Col>
          <Col xs={24} md={8}>
            <div className="glass-note">
              <Typography.Text type="secondary">Match Rate</Typography.Text>
              <Progress
                percent={
                  statistics?.total
                    ? Math.round(
                        ((statistics?.matchedCount || 0) / statistics.total) *
                          100,
                      )
                    : 0
                }
                size="small"
                strokeColor="#52c41a"
                style={{ marginTop: 8 }}
              />
            </div>
          </Col>
        </Row>
      </div>

      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <StatCard
            title="Total Invoices"
            value={statistics?.total || 0}
            valueColor="#1677ff"
          />
        </Col>
        <Col xs={24} sm={8}>
          <StatCard
            title="Matched"
            value={statistics?.matchedCount || 0}
            prefix={<CheckCircleOutlined />}
            valueColor="#52c41a"
          />
        </Col>
        <Col xs={24} sm={8}>
          <StatCard
            title="Mismatched"
            value={statistics?.mismatchCount || 0}
            prefix={<WarningOutlined />}
            valueColor="#fa8c16"
          />
        </Col>
      </Row>

      {/* Results Table */}
      <Card className="section-card soft-reveal" title="Mismatch Review Table">
        {reconciliationResults?.length ? (
          <MismatchTable
            dataSource={reconciliationResults}
            loading={reconciling}
          />
        ) : (
          <EmptyState
            description="No reconciliation rows found. Run reconciliation to generate results."
            actionLabel="Run Reconciliation"
            onAction={handleRunReconciliation}
          />
        )}
      </Card>

      <Card
        className="section-card soft-reveal"
        title="Reconciliation Log"
        style={{ marginTop: 24 }}
      >
        <DataTable
          columns={logColumns}
          dataSource={reconciliationLog}
          rowKey="id"
          pageSize={10}
        />
      </Card>
    </PageLayout>
  );
}

export default ReconcilePage;
