import apiClient from "@/lib/api-client";

export interface CampaignResponse {
  id: string;
  name: string;
  status: "draft" | "scheduled" | "sending" | "sent" | "cancelled";
  scheduled_for: string;
  created_at: string;
}

export interface CampaignsListResponse {
  total: number;
  page: number;
  page_size: number;
  campaigns: CampaignResponse[];
}

export interface TemplateResponse {
  id: string;
  name: string;
  subject: string;
  is_active: boolean;
  created_at: string;
}

export interface TemplatesListResponse {
  status: string;
  templates: TemplateResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface CompanyProfileResponse {
  id: string;
  username: string;
  email: string;
  company_name: string;
  website_url?: string;
  profile_image_key?: string;
  is_verified: boolean;
  is_premium: boolean;
  subscription_tier: string;
  subscription_end_date?: string;
  max_subscribers: number;
  subscriber_count: number;
  created_at: string;
}

export interface CampaignStatusResponse {
  campaign_id: string;
  status: string;
  sent_count: number;
  failed_count: number;
  total_recipients: number;
  success_rate: number;
}

export const dashboardApi = {
  getProfile: async (): Promise<CompanyProfileResponse> => {
    try {
      const response = await apiClient.get("/api/auth/me");
      
      // Axios response structure: response.data contains the actual data
      const profileData = response?.data;
      
      // Ensure all required fields exist with defaults
      const profile: CompanyProfileResponse = {
        id: profileData?.id || '',
        username: profileData?.username || '',
        email: profileData?.email || '',
        company_name: profileData?.company_name || '',
        website_url: profileData?.website_url || undefined,
        profile_image_key: profileData?.profile_image_key || undefined,
        is_verified: profileData?.is_verified ?? false,
        is_premium: profileData?.is_premium ?? false,
        subscription_tier: profileData?.subscription_tier || 'free',
        subscription_end_date: profileData?.subscription_end_date || undefined,
        max_subscribers: profileData?.max_subscribers || 250,
        subscriber_count: profileData?.subscriber_count || 0,
        created_at: profileData?.created_at || new Date().toISOString(),
      };
      
      return profile;
    } catch (error: any) {
      console.error("Error fetching profile:", error);
      
      // Return safe defaults instead of throwing to prevent dashboard crash
      return {
        id: '',
        username: '',
        email: '',
        company_name: '',
        website_url: undefined,
        profile_image_key: undefined,
        is_verified: false,
        is_premium: false,
        subscription_tier: 'free',
        subscription_end_date: undefined,
        max_subscribers: 250,
        subscriber_count: 0,
        created_at: new Date().toISOString(),
      };
    }
  },

  getCampaigns: async (limit: number = 10, skip: number = 0): Promise<CampaignsListResponse> => {
    try {
      const response = await apiClient.get<CampaignsListResponse>("/api/campaigns", {
        params: { limit, skip },
      });
      
      // Handle different response formats
      if (response.data && typeof response.data === 'object') {
        // If response has campaigns array directly
        if (Array.isArray(response.data)) {
          return {
            campaigns: response.data,
            total: response.data.length,
            page: 1,
            page_size: limit,
          };
        }
        
        // If response has campaigns property
        if ('campaigns' in response.data) {
          return response.data as CampaignsListResponse;
        }
        
        // If response has items property (some backends use this)
        if ('items' in response.data) {
          const data = response.data as any;
          return {
            campaigns: data.items,
            total: data.total || data.items.length,
            page: data.page || 1,
            page_size: data.page_size || limit,
          };
        }
      }
      
      // Fallback: return empty list
      return {
        campaigns: [],
        total: 0,
        page: 1,
        page_size: limit,
      };
    } catch (error: any) {
      console.error("Error fetching campaigns:", error);
      // Return empty list on error instead of throwing
      return {
        campaigns: [],
        total: 0,
        page: 1,
        page_size: limit,
      };
    }
  },

  getTemplates: async (limit: number = 10, page: number = 1): Promise<TemplatesListResponse> => {
    try {
      const response = await apiClient.get<TemplatesListResponse>("/api/newsletters/templates", {
        params: { limit, page },
      });
      
      // Handle different response formats
      if (response.data && typeof response.data === 'object') {
        // If response has templates array directly
        if (Array.isArray(response.data)) {
          return {
            status: 'success',
            templates: response.data,
            total: response.data.length,
            page,
            limit,
          };
        }
        
        // If response has templates property
        if ('templates' in response.data) {
          return response.data as TemplatesListResponse;
        }
        
        // If response has items property (some backends use this)
        if ('items' in response.data) {
          const data = response.data as any;
          return {
            status: 'success',
            templates: data.items,
            total: data.total || data.items.length,
            page: data.page || page,
            limit: data.limit || limit,
          };
        }
      }
      
      // Fallback: return empty list
      return {
        status: 'success',
        templates: [],
        total: 0,
        page,
        limit,
      };
    } catch (error: any) {
      console.error("Error fetching templates:", error);
      // Return empty list on error instead of throwing
      return {
        status: 'success',
        templates: [],
        total: 0,
        page,
        limit,
      };
    }
  },

  getCampaignStatus: async (campaignId: string): Promise<CampaignStatusResponse> => {
    try {
      const response = await apiClient.get<CampaignStatusResponse>(`/campaigns/${campaignId}/status`);
      return response.data;
    } catch (error: any) {
      console.error("Error fetching campaign status:", error);
      throw error;
    }
  },
};
