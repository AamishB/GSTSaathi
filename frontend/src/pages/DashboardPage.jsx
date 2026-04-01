import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Row, Col, Typography, Alert, Progress } from "antd";
import {
  DollarOutlined,
  CheckCircleOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import useDashboardStore from "../store/dashboardStore";
import useAuthStore from "../store/authStore";
import MetricsCards from "../components/organisms/MetricsCards";
import ITCAtRiskWidget from "../components/organisms/ITCAtRiskWidget";
import LoadingState from "../components/ui/LoadingState";
import PageLayout from "../components/layout/PageLayout";

const { Title, Text } = Typography;

/**
 * DashboardPage component showing compliance metrics.
 */
function DashboardPage() {
  const navigate = useNavigate();
  const { loadMetrics, metrics, loading, error } = useDashboardStore();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    loadMetrics();
  }, [isAuthenticated, navigate]);

  if (loading && !metrics) {
    return <LoadingState message="Loading dashboard..." minHeight="60vh" />;
  }

  return (
    <PageLayout
      title="Compliance Dashboard"
      subtitle="Monitor tax liability, ITC availability, and reconciliation health."
    >
      <div className="hero-panel soft-reveal">
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} md={24}>
            <Title level={4} style={{ marginTop: 0, marginBottom: 8 }}>
              Command Center Snapshot
            </Title>
            <Text type="secondary">
              Use this summary to quickly spot tax exposure, leakage risk, and
              payment posture.
            </Text>
          </Col>
        </Row>

        <div className="kpi-strip" style={{ marginTop: 16 }}>
          <div className="kpi-item">
            <div className="kpi-label">ITC Available</div>
            <div className="kpi-value">
              ₹{(metrics?.itc_available || 0).toLocaleString("en-IN")}
            </div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">ITC At Risk</div>
            <div className="kpi-value" style={{ color: "#d9822b" }}>
              ₹{(metrics?.itc_at_risk || 0).toLocaleString("en-IN")}
            </div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Net GST Payable</div>
            <div className="kpi-value">
              ₹{(metrics?.net_gst_payable || 0).toLocaleString("en-IN")}
            </div>
          </div>
        </div>
      </div>

      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <MetricsCards metrics={metrics} />

      {/* Compliance Score Section */}
      <Card className="section-card" style={{ marginTop: 24 }}>
        <Title level={4} style={{ marginBottom: 16 }}>
          Compliance Overview
        </Title>
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={10}>
            <div style={{ textAlign: "center", padding: "20px 0" }}>
              <Progress
                type="dashboard"
                percent={Math.round(
                  ((metrics?.total_sales - (metrics?.itc_at_risk || 0)) /
                    (metrics?.total_sales || 1)) *
                    100,
                )}
                strokeColor={{
                  "0%": "#108ee9",
                  "100%": "#87d068",
                }}
                format={(percent) => `${percent}%`}
              />
              <div style={{ marginTop: 16 }}>
                <Text strong>Compliance Score</Text>
              </div>
            </div>
          </Col>
          <Col xs={24} lg={14}>
            <div style={{ padding: "20px 0" }}>
              <div style={{ marginBottom: 16 }}>
                <Text strong>Priority Insights</Text>
              </div>
              <ul style={{ listStyle: "none", padding: 0 }}>
                <li style={{ marginBottom: 8 }}>
                  <CheckCircleOutlined
                    style={{ color: "#52c41a", marginRight: 8 }}
                  />
                  Total ITC Available: ₹
                  {(metrics?.itc_available || 0).toLocaleString("en-IN")}
                </li>
                <li style={{ marginBottom: 8 }}>
                  <WarningOutlined
                    style={{ color: "#faad14", marginRight: 8 }}
                  />
                  ITC At Risk: ₹
                  {(metrics?.itc_at_risk || 0).toLocaleString("en-IN")}
                </li>
                <li style={{ marginBottom: 8 }}>
                  <DollarOutlined
                    style={{ color: "#1677ff", marginRight: 8 }}
                  />
                  Net GST Payable: ₹
                  {(metrics?.net_gst_payable || 0).toLocaleString("en-IN")}
                </li>
              </ul>
            </div>
          </Col>
        </Row>
      </Card>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={10}>
          <ITCAtRiskWidget value={metrics?.itc_at_risk || 0} />
        </Col>
        <Col xs={24} lg={14}>
          <Card className="section-card soft-reveal" style={{ height: "100%" }}>
            <Title level={5} style={{ marginTop: 0 }}>
              Recommended Next Action
            </Title>
            <Text type="secondary">
              Run reconciliation after every upload batch to keep ITC risk
              visible and supplier follow-ups timely.
            </Text>
          </Card>
        </Col>
      </Row>
    </PageLayout>
  );
}

export default DashboardPage;
