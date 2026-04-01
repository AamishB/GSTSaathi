import React from "react";
import { Card, Typography, Progress } from "antd";
import Dragger from "antd/es/upload/Dragger";

const { Title, Text } = Typography;

function UploadZone({
  title,
  description,
  accept,
  onUpload,
  disabled,
  icon,
  hint,
  uploading,
  helper,
}) {
  return (
    <Card
      className="section-card soft-reveal"
      title={title}
      style={{ height: "100%" }}
    >
      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">{description}</Text>
      </div>

      <Dragger
        name="file"
        accept={accept}
        multiple={false}
        beforeUpload={onUpload}
        showUploadList={{ showPreviewIcon: false }}
        disabled={disabled}
      >
        <p className="ant-upload-drag-icon">{icon}</p>
        <p className="ant-upload-text">
          Click or drag file to this area to upload
        </p>
        <p className="ant-upload-hint">{hint}</p>
      </Dragger>

      {uploading && (
        <Progress percent={80} status="active" style={{ marginTop: 16 }} />
      )}

      {helper && (
        <Card type="inner" style={{ marginTop: 16, background: "#fafafa" }}>
          <Title level={5} style={{ marginBottom: 8 }}>
            {helper.title}
          </Title>
          {helper.content}
        </Card>
      )}
    </Card>
  );
}

export default UploadZone;
