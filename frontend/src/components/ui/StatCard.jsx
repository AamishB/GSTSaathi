import React from "react";
import { Card, Statistic } from "antd";

function StatCard({
  title,
  value,
  precision,
  prefix,
  suffix,
  valueColor,
  className,
}) {
  const formatValue = (rawValue) => {
    const numericValue = Number(rawValue ?? 0);
    if (!Number.isFinite(numericValue)) {
      return "0";
    }

    if (typeof precision === "number") {
      return numericValue.toLocaleString("en-IN", {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision,
      });
    }

    return numericValue.toLocaleString("en-IN");
  };

  return (
    <Card className={className || "section-card"}>
      <Statistic
        title={title}
        value={value}
        precision={precision}
        formatter={formatValue}
        prefix={prefix}
        suffix={suffix}
        valueStyle={valueColor ? { color: valueColor } : undefined}
      />
    </Card>
  );
}

export default StatCard;
