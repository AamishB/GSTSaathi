import React from "react";
import { Empty, Button } from "antd";

function EmptyState({
  description,
  actionLabel,
  onAction,
  image = Empty.PRESENTED_IMAGE_SIMPLE,
}) {
  return (
    <Empty
      image={image}
      description={description || "No records found"}
      style={{ padding: "16px 0" }}
    >
      {actionLabel && onAction ? (
        <Button type="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </Empty>
  );
}

export default EmptyState;
