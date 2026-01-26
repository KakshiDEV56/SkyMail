"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { templatesApi } from "@/lib/api/templates";
import { Loader2, Trash2, Edit, Eye, AlertTriangle, Calendar, Info } from "lucide-react";
import { useState } from "react";

interface TemplateListProps {
  onEdit?: (templateId: string) => void;
  onView?: (templateId: string) => void;
}

interface AffectedCampaign {
  id: string;
  name: string;
  status: string;
  scheduled_for: string | null;
}

export function TemplateList({
  onEdit,
  onView,
}: TemplateListProps) {
  const queryClient = useQueryClient();
  const [errorMessage, setErrorMessage] = useState("");
  const [deleteConfirmDialog, setDeleteConfirmDialog] = useState<{
    open: boolean;
    templateId: string | null;
    templateName: string | null;
    affectedCampaigns: AffectedCampaign[];
  }>({
    open: false,
    templateId: null,
    templateName: null,
    affectedCampaigns: [],
  });

  const { data: templatesData, isLoading } = useQuery({
    queryKey: ["templates"],
    queryFn: () => templatesApi.listTemplates(1, 20),
  });

  const deleteTemplateMutation = useMutation({
    mutationFn: (templateId: string) => templatesApi.deleteTemplate(templateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      setErrorMessage("");
      setDeleteConfirmDialog({
        open: false,
        templateId: null,
        templateName: null,
        affectedCampaigns: [],
      });
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to delete template"
      );
    },
  });

  const handleDeleteClick = (templateId: string, templateName: string) => {
    // Show confirmation dialog - deletion happens when user confirms
    setDeleteConfirmDialog({
      open: true,
      templateId,
      templateName,
      affectedCampaigns: [], // We'll populate this after deletion with the API response info
    });
  };

  const confirmDelete = () => {
    if (deleteConfirmDialog.templateId) {
      deleteTemplateMutation.mutate(deleteConfirmDialog.templateId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-teal-600" size={32} />
      </div>
    );
  }

  if (!templatesData || !templatesData.items || templatesData.items.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No Templates Yet
        </h3>
        <p className="text-gray-600">
          Create your first newsletter template to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Error Message */}
      {errorMessage && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {errorMessage}
        </div>
      )}

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templatesData.items.map((template) => (
          <div
            key={template.id}
            className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
          >
            {/* Template Header */}
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900 truncate">
                {template.name}
              </h3>
              <p className="text-sm text-gray-600 truncate mt-1">
                {template.subject}
              </p>
            </div>

            {/* Status Badge */}
            <div className="mb-4">
              <span
                className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                  template.is_active
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-700"
                }`}
              >
                {template.is_active ? "Active" : "Inactive"}
              </span>
            </div>

            {/* Metadata */}
            <div className="text-xs text-gray-500 mb-4">
              Updated {new Date(template.updated_at).toLocaleDateString("en-IN")}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => onView && onView(template.id)}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 border border-teal-300 text-teal-600 rounded-lg hover:bg-teal-50 transition-colors text-sm font-medium"
              >
                <Eye className="w-4 h-4" />
                View
              </button>
              <button
                onClick={() => onEdit && onEdit(template.id)}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={() => handleDeleteClick(template.id, template.name)}
                disabled={deleteTemplateMutation.isPending}
                className="flex items-center justify-center px-3 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Info */}
      {templatesData.total > 0 && (
        <div className="text-sm text-gray-600 text-center">
          Showing {templatesData.items.length} of {templatesData.total} templates
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deleteConfirmDialog.open && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-start gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-lg font-bold text-gray-900">Delete Template</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Are you sure you want to delete <strong>{deleteConfirmDialog.templateName}</strong>?
                </p>
              </div>
            </div>

            {/* Affected Campaigns Warning */}
            {deleteConfirmDialog.affectedCampaigns && deleteConfirmDialog.affectedCampaigns.length > 0 && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
                <div className="flex items-start gap-2 mb-3">
                  <Info className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-orange-900">
                      ⚠️ {deleteConfirmDialog.affectedCampaigns.length} Campaign(s) will be deleted
                    </p>
                    <p className="text-sm text-orange-800 mt-1">
                      The following campaigns use this template and will be permanently deleted:
                    </p>
                  </div>
                </div>

                {/* List of Affected Campaigns */}
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {deleteConfirmDialog.affectedCampaigns.map((campaign) => (
                    <div
                      key={campaign.id}
                      className="bg-white rounded p-3 border border-orange-100"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 truncate">
                            {campaign.name}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                              campaign.status === 'scheduled'
                                ? 'bg-blue-100 text-blue-700'
                                : campaign.status === 'sent'
                                ? 'bg-green-100 text-green-700'
                                : campaign.status === 'sending'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}>
                              {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                      {campaign.scheduled_for && (
                        <div className="flex items-center gap-1 text-xs text-gray-600 mt-2">
                          <Calendar className="w-3 h-3" />
                          {new Date(campaign.scheduled_for).toLocaleString("en-IN")}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Affected Campaigns */}
            {deleteConfirmDialog.affectedCampaigns && deleteConfirmDialog.affectedCampaigns.length === 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-green-800">
                  ✓ No campaigns are using this template. It's safe to delete.
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() =>
                  setDeleteConfirmDialog({
                    open: false,
                    templateId: null,
                    templateName: null,
                    affectedCampaigns: [],
                  })
                }
                disabled={deleteTemplateMutation.isPending}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                disabled={deleteTemplateMutation.isPending}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {deleteTemplateMutation.isPending && (
                  <Loader2 className="w-4 h-4 animate-spin" />
                )}
                {deleteTemplateMutation.isPending ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
