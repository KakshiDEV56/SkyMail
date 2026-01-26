import apiClient from "@/lib/api-client";

export interface SubscribeRequest {
  email: string;
}

export interface SubscribeResponse {
  status: "subscribed" | "already_subscribed" | "resubscribed" | "error";
  message: string;
  subscriber_id?: string;
  email?: string;
  code?: string;
  max_subscribers?: number;
  current_subscribers?: number;
}

export interface UnsubscribeRequest {
  email: string;
}

export interface UnsubscribeResponse {
  status: string;
  message: string;
  code?: string;
}

export const subscribersApi = {
  /**
   * Subscribe to a company's newsletter
   * This is a PUBLIC endpoint - no authentication required
   * @param companyId - The company ID
   * @param email - Email to subscribe
   * @param origin - Optional origin header (usually set by browser)
   */
  subscribe: async (
    companyId: string,
    email: string
  ): Promise<SubscribeResponse> => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${backendUrl}/public/companies/${companyId}/subscribe`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        // Handle error responses
        if (response.status === 403 && data.error === "upgrade_required") {
          throw new Error(
            `Subscription limit reached. Maximum subscribers for this plan: ${data.max_subscribers}`
          );
        }
        throw new Error(data.detail || "Failed to subscribe");
      }

      return data;
    } catch (error: any) {
      console.error("Subscribe error:", error);
      throw error;
    }
  },

  /**
   * Unsubscribe from a company's newsletter
   * This is a PUBLIC endpoint - no authentication required
   * @param companyId - The company ID
   * @param email - Email to unsubscribe
   */
  unsubscribe: async (
    companyId: string,
    email: string
  ): Promise<UnsubscribeResponse> => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${backendUrl}/public/companies/${companyId}/unsubscribe`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to unsubscribe");
      }

      return data;
    } catch (error: any) {
      console.error("Unsubscribe error:", error);
      throw error;
    }
  },

  /**
   * List subscribers for the authenticated company
   * This is a PROTECTED endpoint - requires authentication
   * @param page - Page number (default: 1)
   * @param limit - Items per page (default: 20)
   * @param email - Optional email search filter
   */
  listSubscribers: async (
    page: number = 1,
    limit: number = 20,
    email?: string
  ): Promise<{
    subscribers: Subscriber[];
    total: number;
    page: number;
    page_size: number;
  }> => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    if (email) {
      params.append("email", email);
    }

    const response = await apiClient.get(
      `/api/subscribers?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Delete a subscriber
   * This is a PROTECTED endpoint - requires authentication
   * @param subscriberId - UUID of the subscriber to delete
   */
  deleteSubscriber: async (subscriberId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/api/subscribers/${subscriberId}`);
    return response.data;
  },
};

interface Subscriber {
  id: string;
  email: string;
  is_subscribed: boolean;
  subscribed_at: string;
  unsubscribed_at?: string;
}
