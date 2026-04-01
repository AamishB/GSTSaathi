import apiClient from "./axios";

export const getCompanyProfile = async () => {
  const response = await apiClient.get("/company/profile");
  return response.data;
};

export const updateCompanyProfile = async (payload) => {
  const response = await apiClient.put("/company/profile", payload);
  return response.data;
};
