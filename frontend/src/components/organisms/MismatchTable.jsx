import React from "react";
import { Typography } from "antd";
import StatusBadge from "../ui/StatusBadge";
import DataTable from "../ui/DataTable";

const { Text } = Typography;

function statusColor(status) {
  switch (status) {
    case "matched":
      return "green";
    case "missing_in_gstr2b":
      return "red";
    case "value_mismatch":
      return "orange";
    case "gstin_error":
      return "volcano";
    case "timing_diff":
      return "cyan";
    default:
      return "default";
  }
}

function actionText(status) {
  switch (status) {
    case "matched":
      return "No action needed";
    case "missing_in_gstr2b":
      return "Contact supplier";
    case "value_mismatch":
      return "Verify with supplier";
    case "gstin_error":
      return "Verify GSTIN";
    case "timing_diff":
      return "Check period";
    default:
      return "Review";
  }
}

function MismatchTable({ dataSource, loading }) {
  const columns = [
    {
      title: "Invoice No",
      dataIndex: "invoice_number",
      key: "invoice_number",
      fixed: "left",
      width: 150,
    },
    {
      title: "Date",
      dataIndex: "invoice_date",
      key: "invoice_date",
      width: 100,
    },
    {
      title: "Supplier GSTIN",
      dataIndex: "supplier_gstin",
      key: "supplier_gstin",
      width: 150,
    },
    {
      title: "Taxable Value",
      dataIndex: "taxable_value",
      key: "taxable_value",
      width: 120,
      render: (value) =>
        `₹${(value || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`,
    },
    {
      title: "Match Status",
      dataIndex: "match_status",
      key: "match_status",
      width: 150,
      render: (status) => (
        <StatusBadge
          status={statusColor(status)}
          label={status?.replace(/_/g, " ").toUpperCase()}
        />
      ),
    },
    {
      title: "Confidence",
      dataIndex: "match_confidence",
      key: "match_confidence",
      width: 100,
      render: (confidence) => (
        <StatusBadge
          status={confidence === "exact" ? "success" : "warning"}
          label={confidence?.toUpperCase()}
        />
      ),
    },
    {
      title: "Value Diff",
      dataIndex: "taxable_value_diff",
      key: "taxable_value_diff",
      width: 100,
      render: (diff) => (diff ? `₹${diff.toLocaleString("en-IN")}` : "-"),
    },
    {
      title: "Action Required",
      key: "action",
      width: 150,
      render: (_, record) => (
        <Text type={record.match_status === "matched" ? "secondary" : "danger"}>
          {actionText(record.match_status)}
        </Text>
      ),
    },
  ];

  return (
    <DataTable
      columns={columns}
      dataSource={dataSource}
      rowKey="id"
      loading={loading}
      pageSize={20}
      scroll={{ x: 1000 }}
    />
  );
}

export default MismatchTable;
