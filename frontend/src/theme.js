const theme = {
  token: {
    colorPrimary: "#2d8b8b",
    colorInfo: "#4f9da6",
    colorSuccess: "#2f9e44",
    colorWarning: "#c7a34a",
    colorError: "#d64545",
    colorTextBase: "#1a2332",
    colorBgBase: "#f1faee",
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif",
    fontSize: 16,
    lineHeight: 1.5,
    borderRadius: 10,
    boxShadow: "0 6px 20px rgba(17, 24, 39, 0.06)",
    wireframe: false,
  },
  components: {
    Layout: {
      headerHeight: 64,
      headerBg: "#f1faee",
      bodyBg: "#eef6f3",
    },
    Menu: {
      itemBg: "transparent",
      itemHoverColor: "#2d8b8b",
      itemSelectedColor: "#2d8b8b",
      itemSelectedBg: "rgba(199, 163, 74, 0.16)",
      horizontalItemSelectedColor: "#2d8b8b",
      horizontalItemSelectedBg: "transparent",
      horizontalItemBorderRadius: 8,
    },
    Card: {
      borderRadiusLG: 12,
      colorBorderSecondary: "#d6e5e3",
      boxShadowTertiary: "0 6px 18px rgba(26, 35, 50, 0.08)",
    },
    Button: {
      controlHeight: 36,
      borderRadius: 8,
      fontWeight: 600,
      primaryShadow: "none",
      colorPrimaryHover: "#257676",
      colorPrimaryActive: "#1e5f5f",
    },
    Input: {
      controlHeight: 36,
      borderRadius: 8,
      activeBorderColor: "#2d8b8b",
      activeShadow: "0 0 0 2px rgba(45, 139, 139, 0.18)",
    },
    Select: {
      controlHeight: 36,
      borderRadius: 8,
      optionSelectedBg: "#e5f3f2",
    },
    Table: {
      borderColor: "#d6e5e3",
      headerBg: "#f8f5eb",
      headerColor: "#262626",
      rowHoverBg: "#f3f9f7",
    },
    Typography: {
      titleMarginBottom: "0.75em",
      titleMarginTop: "0.95em",
    },
  },
};

export default theme;
