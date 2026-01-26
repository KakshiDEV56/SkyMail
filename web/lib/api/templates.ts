import apiClient from "@/lib/api-client";

export interface TemplateAsset {
  id: string;
  template_id?: string;
  file_url: string;
  file_type?: string;
  created_at: string;
}

export interface TemplateResponse {
  id: string;
  company_id: string;
  name: string;
  subject: string;
  html_content: string;
  text_content?: string;
  constants: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
  assets: TemplateAsset[];
}

export interface TemplateListItem {
  id: string;
  name: string;
  subject: string;
  constants: string[];
  is_active: boolean;
  updated_at: string;
}

export interface TemplateListResponse {
  items: TemplateListItem[];
  total: number;
  page: number;
  limit: number;
}

export interface TemplateVersionResponse {
  id: string;
  template_id: string;
  subject: string;
  html_content: string;
  text_content?: string;
  constants: string[];
  created_at: string;
}

export const templatesApi = {
  createTemplate: async (
    formData: FormData
  ): Promise<TemplateResponse> => {
    const response = await apiClient.post<TemplateResponse>(
      "/api/newsletters/templates",
      formData
    );
    return response.data;
  },

  updateTemplate: async (
    templateId: string,
    formData: FormData
  ): Promise<TemplateResponse> => {
    const response = await apiClient.put<TemplateResponse>(
      `/api/newsletters/templates/${templateId}`,
      formData
    );
    return response.data;
  },

  getTemplate: async (templateId: string): Promise<TemplateResponse> => {
    const response = await apiClient.get<any>(
      `/api/newsletters/templates/${templateId}`
    );
    const data = response.data;
    if (!data) {
      throw new Error("Template not found");
    }
    
    // Parse variables - handle both array and JSON string formats
    let parsedVariables: string[] = [];
    if (data.variables) {
      if (Array.isArray(data.variables)) {
        parsedVariables = data.variables;
      } else if (typeof data.variables === "string") {
        try {
          // Try to parse as JSON string
          parsedVariables = JSON.parse(data.variables);
          if (!Array.isArray(parsedVariables)) {
            parsedVariables = [];
          }
        } catch (e) {
          // If parsing fails, treat as comma-separated string
          parsedVariables = data.variables
            .split(",")
            .map((v: string) => v.trim())
            .filter((v: string) => v);
        }
      }
    }
    
    return {
      ...data,
      variables: parsedVariables,
    };
  },

  listTemplates: async (
    page: number = 1,
    limit: number = 20
  ): Promise<TemplateListResponse> => {
    const response = await apiClient.get<any>(
      "/api/newsletters/templates",
      {
        params: { page, limit },
      }
    );
    // Handle both direct response and nested 'data' structure
    const data = response.data;
    if (!data) {
      return { items: [], total: 0, page, limit };
    }
    // If response has 'templates' field (direct array), wrap it
    if (Array.isArray(data.templates)) {
      return {
        items: data.templates,
        total: data.templates.length,
        page,
        limit,
      };
    }
    // If response has 'items' field, return as-is
    if (Array.isArray(data.items)) {
      return data as TemplateListResponse;
    }
    return { items: [], total: 0, page, limit };
  },

  deleteTemplate: async (
    templateId: string
  ): Promise<{
    message: string;
    affected_campaigns: Array<{
      id: string;
      name: string;
      status: string;
      scheduled_for: string | null;
    }>;
    deleted_campaigns_count: number;
  }> => {
    const response = await apiClient.delete(
      `/api/newsletters/templates/${templateId}`
    );
    return response.data;
  },

  getTemplateVersions: async (
    templateId: string
  ): Promise<TemplateVersionResponse[]> => {
    const response = await apiClient.get<{ versions: TemplateVersionResponse[] }>(
      `/api/newsletters/templates/${templateId}/versions`
    );
    return response.data.versions;
  },

  deactivateTemplate: async (templateId: string): Promise<TemplateResponse> => {
    const response = await apiClient.patch<TemplateResponse>(
      `/api/newsletters/templates/${templateId}/deactivate`
    );
    return response.data;
  },
};
