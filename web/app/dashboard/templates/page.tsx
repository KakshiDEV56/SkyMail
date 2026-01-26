"use client";

import { useState } from "react";
import { DashboardHeader } from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TemplateEditor } from "@/components/templates/template-editor-improved";
import { TemplateList } from "@/components/templates/template-list";
import { TemplateViewer } from "@/components/templates/template-viewer";
import { ArrowLeft, Plus } from "lucide-react";
import Link from "next/link";

export default function TemplatesPage() {
  const [mode, setMode] = useState<"list" | "editor" | "viewer">("list");
  const [editingTemplateId, setEditingTemplateId] = useState<string | null>(null);
  const [viewingTemplateId, setViewingTemplateId] = useState<string | null>(null);

  const handleCreateNew = () => {
    setEditingTemplateId(null);
    setMode("editor");
  };

  const handleEditTemplate = (templateId: string) => {
    setEditingTemplateId(templateId);
    setMode("editor");
  };

  const handleViewTemplate = (templateId: string) => {
    setViewingTemplateId(templateId);
    setMode("viewer");
  };

  const handleTemplateSuccess = () => {
    setMode("list");
    setEditingTemplateId(null);
    // React Query cache invalidation will handle the UI update
  };

  const handleCancel = () => {
    setMode("list");
    setEditingTemplateId(null);
  };

  const handleBackFromViewer = () => {
    setMode("list");
    setViewingTemplateId(null);
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
                  <h1 className="text-3xl font-bold text-[#180D39]">
                    Newsletter Templates
                  </h1>
                  <p className="text-gray-600 mt-2">
                    {mode === "editor"
                      ? editingTemplateId
                        ? "Edit your newsletter template"
                        : "Design your newsletter template"
                      : mode === "viewer"
                        ? "View template details"
                        : "Design beautiful email templates for your campaigns"}
                  </p>
                </div>
                {mode === "list" && (
                  <button
                    onClick={handleCreateNew}
                    className="bg-[#2A8C9D] hover:bg-[#1D7A89] text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    Create Template
                  </button>
                )}
              </div>
            </div>

            {mode === "editor" && (
              <TemplateEditor
                templateId={editingTemplateId || undefined}
                onSuccess={handleTemplateSuccess}
                onCancel={handleCancel}
              />
            )}

            {mode === "viewer" && viewingTemplateId && (
              <TemplateViewer
                templateId={viewingTemplateId}
                onBack={handleBackFromViewer}
              />
            )}

            {mode === "list" && (
              <TemplateList
                onEdit={handleEditTemplate}
                onView={handleViewTemplate}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
