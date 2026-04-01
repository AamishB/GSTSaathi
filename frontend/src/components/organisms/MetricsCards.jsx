import React from "react";
import { Row, Col } from "antd";
import {
  DollarOutlined,
  ShoppingOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  RiseOutlined,
} from "@ant-design/icons";
import StatCard from "../ui/StatCard";

function MetricsCards({ metrics }) {
  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} lg={8}>
        <StatCard
          className="section-card soft-reveal"
          title="Total Sales (Outward Supplies)"
          value={metrics?.total_sales || 0}
          precision={2}
          prefix={<DollarOutlined />}
          suffix="₹"
          valueColor="#52c41a"
        />
      </Col>
      <Col xs={24} sm={12} lg={8}>
        <StatCard
          className="section-card soft-reveal"
          title="Total Purchases (Inward Supplies)"
          value={metrics?.total_purchases || 0}
          precision={2}
          prefix={<ShoppingOutlined />}
          suffix="₹"
          valueColor="#1677ff"
        />
      </Col>
      <Col xs={24} sm={12} lg={8}>
        <StatCard
          className="section-card soft-reveal"
          title="Output GST Liability"
          value={metrics?.output_gst || 0}
          precision={2}
          prefix={<FileTextOutlined />}
          suffix="₹"
          valueColor="#ff4d4f"
        />
      </Col>
      <Col xs={24} sm={12} lg={8}>
        <StatCard
          className="section-card soft-reveal"
          title="ITC Available"
          value={metrics?.itc_available || 0}
          precision={2}
          prefix={<CheckCircleOutlined />}
          suffix="₹"
          valueColor="#52c41a"
        />
      </Col>
      <Col xs={24} sm={12} lg={8}>
        <StatCard
          className="section-card soft-reveal"
          title="Net GST Payable"
          value={metrics?.net_gst_payable || 0}
          precision={2}
          prefix={<RiseOutlined />}
          suffix="₹"
          valueColor={
            (metrics?.net_gst_payable || 0) > 0 ? "#ff4d4f" : "#52c41a"
          }
        />
      </Col>
    </Row>
  );
}

export default MetricsCards;
