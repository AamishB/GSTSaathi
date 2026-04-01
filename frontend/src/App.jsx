import { useEffect, useMemo, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Link,
  useLocation,
} from "react-router-dom";
import {
  ConfigProvider,
  Layout,
  Menu,
  Button,
  Typography,
  Space,
  Drawer,
  Grid,
  App as AntdApp,
} from "antd";
import {
  DashboardOutlined,
  UploadOutlined,
  SyncOutlined,
  ExportOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from "@ant-design/icons";

import useAuthStore from "./store/authStore";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import UploadPage from "./pages/UploadPage";
import ReconcilePage from "./pages/ReconcilePage";
import ExportPage from "./pages/ExportPage";
import SettingsPage from "./pages/SettingsPage";
import theme from "./theme";
import appLogo from "../assets/logo.png";

const { Header, Content, Sider } = Layout;
const { Title } = Typography;
const { useBreakpoint } = Grid;

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AppShell() {
  const location = useLocation();
  const { isAuthenticated, logout } = useAuthStore();
  const screens = useBreakpoint();
  const isMobile = !screens.lg;
  const [collapsed, setCollapsed] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const menuItems = [
    {
      key: "/dashboard",
      icon: <DashboardOutlined />,
      label: <Link to="/dashboard">Dashboard</Link>,
    },
    {
      key: "/upload",
      icon: <UploadOutlined />,
      label: <Link to="/upload">Upload</Link>,
    },
    {
      key: "/reconcile",
      icon: <SyncOutlined />,
      label: <Link to="/reconcile">Reconcile</Link>,
    },
    {
      key: "/export",
      icon: <ExportOutlined />,
      label: <Link to="/export">Export</Link>,
    },
    {
      key: "/settings",
      icon: <SettingOutlined />,
      label: <Link to="/settings">Settings</Link>,
    },
  ];

  const hideHeader = location.pathname === "/login" || !isAuthenticated;
  const selectedKeys = useMemo(() => [location.pathname], [location.pathname]);
  const desktopSiderWidth = collapsed ? 80 : 256;
  const hasDesktopSidebar = !hideHeader && !isMobile;

  const sidebarMenu = (
    <Menu
      mode="inline"
      selectedKeys={selectedKeys}
      items={menuItems}
      className="app-side-menu"
    />
  );

  return (
    <Layout className="app-layout">
      {!hideHeader && !isMobile ? (
        <Sider
          width={256}
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          className="app-sider"
          trigger={null}
        >
          <div className="sider-brand">
            <img src={appLogo} alt="GSTSaathi logo" className="brand-logo" />
            {!collapsed ? (
              <span className="sider-brand-text">GSTSaathi</span>
            ) : null}
          </div>
          {sidebarMenu}
        </Sider>
      ) : null}

      {!hideHeader && isMobile ? (
        <Drawer
          title="Navigation"
          placement="left"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          styles={{ body: { padding: 0 } }}
        >
          {sidebarMenu}
        </Drawer>
      ) : null}

      <Layout
        className={
          hasDesktopSidebar
            ? "app-main-layout with-fixed-sider"
            : "app-main-layout"
        }
        style={
          hasDesktopSidebar
            ? {
                marginLeft: desktopSiderWidth,
                transition: "margin-left 0.2s ease",
              }
            : undefined
        }
      >
        {!hideHeader && (
          <Header className="app-header app-topbar">
            <Space className="app-brand">
              <Button
                type="text"
                icon={
                  isMobile ? (
                    <MenuUnfoldOutlined />
                  ) : collapsed ? (
                    <MenuUnfoldOutlined />
                  ) : (
                    <MenuFoldOutlined />
                  )
                }
                onClick={() => {
                  if (isMobile) {
                    setDrawerOpen(true);
                  } else {
                    setCollapsed((prev) => !prev);
                  }
                }}
                aria-label="Toggle navigation"
              />
              <img src={appLogo} alt="GSTSaathi logo" className="brand-logo" />
              <Title level={4} style={{ margin: 0, color: "#262626" }}>
                GSTSaathi
              </Title>
              {!isMobile && (
                <Typography.Text type="secondary">
                  Compliance Workspace
                </Typography.Text>
              )}
            </Space>
            <Button icon={<LogoutOutlined />} onClick={logout}>
              Logout
            </Button>
          </Header>
        )}

        <Content
          className={
            hideHeader ? "app-content app-content-auth" : "app-content"
          }
        >
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/upload"
              element={
                <ProtectedRoute>
                  <UploadPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reconcile"
              element={
                <ProtectedRoute>
                  <ReconcilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/export"
              element={
                <ProtectedRoute>
                  <ExportPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

function App() {
  const { loadCurrentUser } = useAuthStore();

  useEffect(() => {
    loadCurrentUser();
  }, [loadCurrentUser]);

  return (
    <ConfigProvider theme={theme}>
      <AntdApp>
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <AppShell />
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
}

export default App;
