import React from "react";
import { Card, Statistic, Typography } from "antd";
import { WarningOutlined } from "@ant-design/icons";

const { Text } = Typography;

function ITCAtRiskWidget({ value }) {
  const formatValue = (rawValue) => {
    const numericValue = Number(rawValue ?? 0);
    if (!Number.isFinite(numericValue)) {
      return "0.00";
    }

    return numericValue.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  return (
    <Card
      className="section-card"
      style={{ borderColor: "#fa8c16", borderWidth: 2 }}
    >
      <Statistic
        title={
          <Text strong style={{ color: "#fa8c16" }}>
            ITC At Risk
          </Text>
        }
        value={value || 0}
        precision={2}
        formatter={formatValue}
        prefix={<WarningOutlined />}
        suffix="₹"
        valueStyle={{ color: "#fa8c16" }}
      />
      <div style={{ marginTop: 8 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          Invoices missing in GSTR-2B
        </Text>
      </div>
    </Card>
  );
}

export default ITCAtRiskWidget;
