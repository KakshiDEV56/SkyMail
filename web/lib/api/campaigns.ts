import apiClient from "@/lib/api-client";

export interface CampaignResponse {
  id: string;
  name: string;
  subject: string;
  status: "draft" | "scheduled" | "sending" | "sent" | "cancelled";
  template_id: string | null;
  scheduled_for: string | null;
  send_timezone: string | null;
  constants_values: Record<string, any>;
  created_at: string;
  updated_at: string;
  sent_at: string | null;
}

export interface CampaignListResponse {
  total: number;
  page: number;
  page_size: number;
  campaigns: CampaignResponse[];
}

export const campaignsApi = {
  /**
   * List all campaigns for the company
   */
  listCampaigns: async (
    limit: number = 20,
    skip: number = 0,
    status?: string
  ): Promise<CampaignListResponse> => {
    try {
      const params = new URLSearchParams();
      params.append("limit", limit.toString());
      params.append("skip", skip.toString());
      if (status) {
        params.append("status", status);
      }

      const response = await apiClient.get<CampaignListResponse>(
        `/api/campaigns?${params.toString()}`
      );

      return response.data;
    } catch (error) {
      console.error("Error fetching campaigns:", error);
      throw error;
    }
  },

  /**
   * Get campaign details
   */
  getCampaign: async (campaignId: string): Promise<CampaignResponse> => {
    try {
      const response = await apiClient.get<CampaignResponse>(
        `/api/campaigns/${campaignId}`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching campaign:", error);
      throw error;
    }
  },

  /**
   * Delete a campaign
   * Only draft and scheduled campaigns can be deleted
   */
  deleteCampaign: async (campaignId: string): Promise<void> => {
    try {
      await apiClient.delete(`/api/campaigns/${campaignId}`);
    } catch (error: any) {
      console.error("Error deleting campaign:", error);
      throw error;
    }
  },

  /**
   * Cancel a campaign
   * Only draft and scheduled campaigns can be cancelled
   */
  cancelCampaign: async (campaignId: string): Promise<CampaignResponse> => {
    try {
      const response = await apiClient.post<CampaignResponse>(
        `/api/campaigns/${campaignId}/cancel`,
        {}
      );
      return response.data;
    } catch (error) {
      console.error("Error cancelling campaign:", error);
      throw error;
    }
  },

  /**
   * Get campaign delivery status
   */
  getCampaignStatus: async (
    campaignId: string
  ): Promise<{
    id: string;
    status: string;
    sent_count: number;
    failed_count: number;
    total_recipients: number;
    scheduled_for: string | null;
    sent_at: string | null;
  }> => {
    try {
      const response = await apiClient.get(
        `/api/campaigns/${campaignId}/status`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching campaign status:", error);
      throw error;
    }
  },
};
