import React from "react";
import { Spin, Typography } from "antd";

const { Text } = Typography;

function LoadingState({ message = "Loading...", minHeight = "40vh" }) {
  return (
    <div
      aria-live="polite"
      aria-busy="true"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 12,
        justifyContent: "center",
        alignItems: "center",
        minHeight,
      }}
    >
      <Spin size="large" />
      <Text type="secondary">{message}</Text>
    </div>
  );
}

export default LoadingState;
