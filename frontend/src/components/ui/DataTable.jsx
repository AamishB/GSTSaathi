import React from "react";
import { Table } from "antd";
import EmptyState from "./EmptyState";

function DataTable({
  columns,
  dataSource,
  rowKey = "id",
  loading = false,
  pageSize = 10,
  scroll,
  ...rest
}) {
  return (
    <Table
      className="section-card"
      columns={columns}
      dataSource={dataSource}
      rowKey={rowKey}
      loading={loading}
      pagination={{
        pageSize,
        showSizeChanger: true,
        showTotal: (total) => `Total ${total} records`,
      }}
      locale={{
        emptyText: <EmptyState description="No records available yet" />,
      }}
      scroll={scroll}
      {...rest}
    />
  );
}

export default DataTable;
