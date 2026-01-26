"use client";

import { DashboardHeader } from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { ArrowLeft, Plus, Trash2, AlertTriangle, Loader2 } from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import apiClient from "@/lib/api-client";
import { campaignsApi } from "@/lib/api/campaigns";

interface Campaign {
  id: string;
  name: string;
  subject: string;
  status: string;
  scheduled_for?: string;
  sent_at?: string;
  created_at: string;
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    campaignId: string | null;
    campaignName: string | null;
  }>({ open: false, campaignId: null, campaignName: null });
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get("/api/campaigns");
      
      // Handle different response formats
      let campaignsList: Campaign[] = [];
      
      if (response.data && Array.isArray(response.data.campaigns)) {
        campaignsList = response.data.campaigns;
      } else if (response.data && Array.isArray(response.data)) {
        campaignsList = response.data;
      } else if (Array.isArray(response.data)) {
        campaignsList = response.data;
      }
      
      setCampaigns(campaignsList);
      setError("");
    } catch (err) {
      console.error("Failed to fetch campaigns:", err);
      setCampaigns([]);
      setError("Failed to load campaigns");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteClick = (campaignId: string, campaignName: string) => {
    setDeleteDialog({
      open: true,
      campaignId,
      campaignName,
    });
  };

  const handleConfirmDelete = async () => {
    if (!deleteDialog.campaignId) return;

    try {
      setIsDeleting(true);
      await campaignsApi.deleteCampaign(deleteDialog.campaignId);
      
      // Remove from local state
      setCampaigns(
        campaigns.filter((c) => c.id !== deleteDialog.campaignId)
      );
      
      setDeleteDialog({ open: false, campaignId: null, campaignName: null });
      setError("");
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        "Failed to delete campaign";
      setError(errorMessage);
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
      draft: { bg: "bg-gray-100", text: "text-gray-700", label: "Draft" },
      scheduled: { bg: "bg-blue-100", text: "text-blue-700", label: "Scheduled" },
      sending: { bg: "bg-yellow-100", text: "text-yellow-700", label: "Sending" },
      sent: { bg: "bg-green-100", text: "text-green-700", label: "Sent" },
      cancelled: { bg: "bg-red-100", text: "text-red-700", label: "Cancelled" },
    };

    const config = statusConfig[status] || statusConfig.draft;
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const canDelete = (status: string) => {
    // Can only delete draft and scheduled campaigns
    return status === "draft" || status === "scheduled";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader />

      <div className="flex">
        <Sidebar />

        <main className="flex-1">
          <div className="p-6 lg:p-8">
            <div className="mb-8">
              <Link
                href="/dashboard"
                className="flex items-center gap-2 text-[#2A8C9D] hover:text-[#1D7A89] mb-4"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Overview
              </Link>
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-[#180D39]">Campaigns</h1>
                  <p className="text-gray-600 mt-2">Create and manage your email campaigns</p>
                </div>
                <Link href="/dashboard/campaigns/create">
                  <button className="bg-[#2A8C9D] hover:bg-[#1D7A89] text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Create Campaign
                  </button>
                </Link>
              </div>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}

            {isLoading ? (
              <div className="bg-white border border-gray-200 rounded-xl p-12 text-center">
                <div className="text-gray-500">Loading campaigns...</div>
              </div>
            ) : campaigns.length === 0 ? (
              <div className="bg-white border border-gray-200 rounded-xl p-12 text-center">
                <h2 className="text-2xl font-bold text-[#180D39] mb-4">No Campaigns Yet</h2>
                <p className="text-gray-600 mb-6">
                  Create your first campaign to start sending targeted emails.
                </p>
                <Link href="/dashboard/campaigns/create">
                  <button className="bg-[#2A8C9D] hover:bg-[#1D7A89] text-white px-6 py-2 rounded-lg font-medium inline-flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Create Campaign
                  </button>
                </Link>
              </div>
            ) : (
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="text-left py-4 px-6 font-bold text-[#180D39]">Name</th>
                        <th className="text-left py-4 px-6 font-bold text-[#180D39]">Subject</th>
                        <th className="text-left py-4 px-6 font-bold text-[#180D39]">Status</th>
                        <th className="text-left py-4 px-6 font-bold text-[#180D39]">Created</th>
                        <th className="text-left py-4 px-6 font-bold text-[#180D39]">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {campaigns.map((campaign, index) => (
                        <tr
                          key={campaign.id}
                          className={index !== campaigns.length - 1 ? "border-b border-gray-100" : ""}
                        >
                          <td className="py-4 px-6 text-[#180D39] font-medium">{campaign.name}</td>
                          <td className="py-4 px-6 text-gray-600 truncate max-w-xs">{campaign.subject}</td>
                          <td className="py-4 px-6">{getStatusBadge(campaign.status)}</td>
                          <td className="py-4 px-6 text-gray-600 text-sm">{formatDate(campaign.created_at)}</td>
                          <td className="py-4 px-6 flex items-center gap-3">
                            <Link href={`/dashboard/campaigns/${campaign.id}`}>
                              <button className="text-[#2A8C9D] hover:text-[#1D7A89] font-medium">
                                View
                              </button>
                            </Link>
                            {canDelete(campaign.status) && (
                              <button
                                onClick={() =>
                                  handleDeleteClick(campaign.id, campaign.name)
                                }
                                className="text-red-600 hover:text-red-700 font-medium"
                                title="Delete campaign"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Delete Confirmation Dialog */}
      {deleteDialog.open && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-start gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-lg font-bold text-gray-900">Delete Campaign</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Are you sure you want to delete <strong>{deleteDialog.campaignName}</strong>?
                </p>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-yellow-800">
                This action cannot be undone. All campaign data and send logs will be permanently deleted.
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() =>
                  setDeleteDialog({
                    open: false,
                    campaignId: null,
                    campaignName: null,
                  })
                }
                disabled={isDeleting}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isDeleting && <Loader2 className="w-4 h-4 animate-spin" />}
                {isDeleting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
