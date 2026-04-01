import React from "react";
import { Breadcrumb, Typography } from "antd";
import { Link, useLocation } from "react-router-dom";

const { Title, Text } = Typography;

const PATH_LABELS = {
  dashboard: "Dashboard",
  upload: "Upload",
  reconcile: "Reconcile",
  export: "Export",
  settings: "Settings",
};

function buildBreadcrumbItems(pathname) {
  const segments = pathname.split("/").filter(Boolean);
  if (!segments.length) return [];

  const items = [{ title: <Link to="/dashboard">Home</Link> }];
  let currentPath = "";

  segments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    const label = PATH_LABELS[segment] || segment;
    const isLast = index === segments.length - 1;

    items.push({
      title: isLast ? (
        <span>{label}</span>
      ) : (
        <Link to={currentPath}>{label}</Link>
      ),
    });
  });

  return items;
}

function PageLayout({ title, subtitle, children, actions }) {
  const location = useLocation();
  const breadcrumbItems = buildBreadcrumbItems(location.pathname);

  return (
    <div className="page-container">
      <div className="page-header">
        <Breadcrumb items={breadcrumbItems} style={{ marginBottom: 10 }} />
        <div className="page-header-row">
          <div>
            <Title level={2} style={{ marginBottom: 8 }}>
              {title}
            </Title>
            {subtitle ? <Text type="secondary">{subtitle}</Text> : null}
          </div>
          {actions ? <div>{actions}</div> : null}
        </div>
      </div>
      {children}
    </div>
  );
}

export default PageLayout;
