import React from "react";
import { Tag } from "antd";

const STATUS_COLOR_MAP = {
  success: "green",
  warning: "orange",
  error: "red",
  info: "cyan",
  default: "default",
  matched: "green",
  mismatched: "orange",
  missing_in_gstr2b: "red",
  value_mismatch: "orange",
  gstin_error: "volcano",
  timing_diff: "cyan",
};

function normalizeLabel(value) {
  if (!value) return "UNKNOWN";
  return String(value).replace(/_/g, " ").toUpperCase();
}

function StatusBadge({ status = "default", label, bordered = false }) {
  const color = STATUS_COLOR_MAP[status] || STATUS_COLOR_MAP.default;

  return (
    <Tag color={color} bordered={bordered}>
      {label || normalizeLabel(status)}
    </Tag>
  );
}

export default StatusBadge;
