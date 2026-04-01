import React from "react";
import { Card, Button, Typography } from "antd";

const { Title, Paragraph, Text } = Typography;

function ExportPanel({
  icon,
  iconColor,
  title,
  description,
  includes,
  buttonText,
  buttonIcon,
  buttonLoading,
  onClick,
}) {
  return (
    <Card
      className="section-card soft-reveal"
      hoverable
      style={{ height: "100%" }}
      actions={[
        <Button
          type="primary"
          icon={buttonIcon}
          loading={buttonLoading}
          onClick={onClick}
        >
          {buttonText}
        </Button>,
      ]}
    >
      <div style={{ textAlign: "center", padding: "20px 0" }}>
        {React.cloneElement(icon, {
          style: { fontSize: 48, color: iconColor, marginBottom: 16 },
        })}
        <Title level={4}>{title}</Title>
        <Paragraph type="secondary">{description}</Paragraph>
        <div style={{ marginTop: 16, textAlign: "left" }}>
          <Text strong>Includes:</Text>
          <ul style={{ margin: "8px 0 0 20px", fontSize: 12 }}>
            {includes.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  );
}

export default ExportPanel;
