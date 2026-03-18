import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ============= Employee API =============
export const employeeApi = {
  getEmployees: async (params: any = {}) => {
    const response = await api.get("/employees", { params });
    return response.data;
  },

  searchEmployees: async (filters: any, params: any = {}) => {
    const response = await api.post("/employees/search", filters, { params });
    return response.data;
  },

  getEmployee: async (id: string) => {
    const response = await api.get(`/employees/${id}`);
    return response.data;
  },

  getFilterOptions: async () => {
    const response = await api.get("/employees/filters/options");
    return response.data;
  },

  getAggregations: async (groupBy: string, params: any = {}) => {
    const response = await api.get(`/employees/aggregations/${groupBy}`, { params });
    return response.data;
  },

  exportEmployees: async (data: any) => {
    const response = await api.post("/employees/export", data, {
      responseType: "blob",
    });
    return response.data;
  },
};

// ============= Analytics API =============
export const analyticsApi = {
  getSummary: async () => {
    const response = await api.get("/analytics/summary");
    return response.data;
  },

  getHeadcount: async (params: any = {}) => {
    const response = await api.get("/analytics/headcount", { params });
    return response.data;
  },

  getDiversity: async (params: any = {}) => {
    const response = await api.get("/analytics/diversity", { params });
    return response.data;
  },

  getCompensation: async (params: any = {}) => {
    const response = await api.get("/analytics/compensation", { params });
    return response.data;
  },

  getPerformance: async (params: any = {}) => {
    const response = await api.get("/analytics/performance", { params });
    return response.data;
  },

  getAttrition: async (params: any = {}) => {
    const response = await api.get("/analytics/attrition", { params });
    return response.data;
  },

  getTrends: async (params: any) => {
    const response = await api.get("/analytics/trends", { params });
    return response.data;
  },

  getDistribution: async (field: string, params: any = {}) => {
    const response = await api.get(`/analytics/distribution/${field}`, { params });
    return response.data;
  },

  getChartData: async (chartType: string, params: any = {}) => {
    const response = await api.get(`/analytics/charts/${chartType}`, { params });
    return response.data;
  },
};

// ============= AI API =============
export const aiApi = {
  processQuery: async (query: string, context?: any) => {
    const response = await api.post("/ai/query", { query, context });
    return response.data;
  },

  semanticSearch: async (query: string, filters?: any, limit: number = 10) => {
    const response = await api.post("/ai/search", { query, filters, limit });
    return response.data;
  },

  predictAttrition: async (employeeIds: string[], includeExplanations: boolean = true) => {
    const response = await api.post("/ai/predict/attrition", {
      employee_ids: employeeIds,
      include_explanations: includeExplanations,
    });
    return response.data;
  },

  predictPerformance: async (employeeIds: string[], includeExplanations: boolean = true) => {
    const response = await api.post("/ai/predict/performance", {
      employee_ids: employeeIds,
      include_explanations: includeExplanations,
    });
    return response.data;
  },

  predictPromotion: async (employeeIds: string[], includeExplanations: boolean = true) => {
    const response = await api.post("/ai/predict/promotion", {
      employee_ids: employeeIds,
      include_explanations: includeExplanations,
    });
    return response.data;
  },

  getExplanation: async (employeeId: string, predictionType: string) => {
    const response = await api.get(`/ai/explain/${employeeId}/${predictionType}`);
    return response.data;
  },

  generateAnalysis: async (data: any, analysisType: string, focusAreas?: string[]) => {
    const response = await api.post("/ai/analyze", {
      data,
      analysis_type: analysisType,
      focus_areas: focusAreas,
    });
    return response.data;
  },

  chat: async (message: string, conversationId?: string) => {
    const response = await api.post("/ai/chat", { message, conversation_id: conversationId });
    return response.data;
  },

  getSuggestions: async (partialQuery?: string) => {
    const response = await api.get("/ai/suggestions", {
      params: { partial_query: partialQuery },
    });
    return response.data;
  },

  getInsights: async (params: any = {}) => {
    const response = await api.get("/ai/insights", { params });
    return response.data;
  },

  getModelsInfo: async () => {
    const response = await api.get("/ai/models/info");
    return response.data;
  },
};

// ============= Reports API =============
export const reportsApi = {
  generatePdf: async (params: any) => {
    const response = await api.post("/reports/pdf", null, {
      params,
      responseType: "blob",
    });
    return response.data;
  },

  generateWord: async (params: any) => {
    const response = await api.post("/reports/word", null, {
      params,
      responseType: "blob",
    });
    return response.data;
  },

  generateExcel: async (params: any) => {
    const response = await api.post("/reports/excel", null, {
      params,
      responseType: "blob",
    });
    return response.data;
  },

  getTemplates: async () => {
    const response = await api.get("/reports/templates");
    return response.data;
  },

  generateCustom: async (params: any) => {
    const response = await api.post("/reports/custom", null, {
      params,
      responseType: "blob",
    });
    return response.data;
  },
};

// ============= Health API =============
export const healthApi = {
  check: async () => {
    const response = await api.get("/health");
    return response.data;
  },

  detailed: async () => {
    const response = await api.get("/health/detailed");
    return response.data;
  },
};

export default api;
