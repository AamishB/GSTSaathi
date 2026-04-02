const theme = {
  token: {
    colorPrimary: "#2d8b8b",
    colorInfo: "#4f9da6",
    colorSuccess: "#2f9e44",
    colorWarning: "#c7a34a",
    colorError: "#d64545",
    colorTextBase: "#1a2332",
    colorBgBase: "#f6fcf9",
    colorBgContainer: "#ffffff",
    colorBorder: "#d4e5df",
    colorBorderSecondary: "#deebe6",
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif",
    fontSize: 16,
    lineHeight: 1.5,
    borderRadius: 12,
    boxShadow: "0 10px 24px rgba(17, 41, 48, 0.08)",
    wireframe: false,
  },
  components: {
    Layout: {
      headerHeight: 64,
      headerBg: "#f7fcfa",
      bodyBg: "#edf6f3",
    },
    Menu: {
      itemBg: "transparent",
      itemHoverColor: "#2d8b8b",
      itemSelectedColor: "#2d8b8b",
      itemSelectedBg:
        "linear-gradient(90deg, rgba(199, 163, 74, 0.18) 0%, rgba(45, 139, 139, 0.12) 100%)",
      horizontalItemSelectedColor: "#2d8b8b",
      horizontalItemSelectedBg: "transparent",
      horizontalItemBorderRadius: 10,
    },
    Card: {
      borderRadiusLG: 14,
      colorBorderSecondary: "#d8e8e2",
      boxShadowTertiary: "0 12px 22px rgba(26, 55, 61, 0.08)",
    },
    Button: {
      controlHeight: 36,
      borderRadius: 10,
      fontWeight: 600,
      primaryShadow: "0 8px 18px rgba(45, 139, 139, 0.22)",
      colorPrimaryHover: "#257676",
      colorPrimaryActive: "#1e5f5f",
    },
    Input: {
      controlHeight: 36,
      borderRadius: 10,
      activeBorderColor: "#2d8b8b",
      activeShadow: "0 0 0 2px rgba(45, 139, 139, 0.18)",
    },
    Select: {
      controlHeight: 36,
      borderRadius: 10,
      optionSelectedBg: "#e6f4f1",
    },
    Table: {
      borderColor: "#d6e7e1",
      headerBg: "#f4f9f7",
      headerColor: "#262626",
      rowHoverBg: "#f1f8f5",
    },
    Breadcrumb: {
      itemColor: "#5f7577",
      lastItemColor: "#2b3f4b",
      linkColor: "#4c676f",
      linkHoverColor: "#2d8b8b",
    },
    Typography: {
      titleMarginBottom: "0.75em",
      titleMarginTop: "0.95em",
    },
  },
};

export default theme;
