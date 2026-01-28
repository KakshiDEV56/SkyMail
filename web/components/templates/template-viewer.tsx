"use client";

import { useQuery } from "@tanstack/react-query";
import { templatesApi } from "@/lib/api/templates";
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react";

interface TemplateViewerProps {
  templateId: string;
  onBack?: () => void;
}

export function TemplateViewer({ templateId, onBack }: TemplateViewerProps) {
  const { data: template, isLoading, isError } = useQuery({
    queryKey: ["template", templateId],
    queryFn: () => templatesApi.getTemplate(templateId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-teal-600" size={32} />
      </div>
    );
  }

  if (isError || !template) {
    return (
      <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <AlertCircle size={20} />
        <p>Failed to load template</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        {onBack && (
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-teal-600 hover:text-teal-700"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Templates
          </button>
        )}
      </div>

      {/* Template Info */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{template.name}</h2>
          <p className="text-gray-600 mt-1">Subject: {template.subject}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div>
            <p className="text-sm font-medium text-gray-600">Status</p>
            <p className="text-sm font-semibold text-gray-900 mt-1">
              {template.is_active ? (
                <span className="text-green-600">Active</span>
              ) : (
                <span className="text-gray-500">Inactive</span>
              )}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Created</p>
            <p className="text-sm font-semibold text-gray-900 mt-1">
              {new Date(template.created_at).toLocaleDateString("en-IN")}
            </p>
          </div>
        </div>
      </div>

      {/* Variables - Show as Metadata List ONLY */}
      {template.constants && template.constants.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Required Variables
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            These variables will be replaced with actual data when sending campaigns.
          </p>
          <div className="flex flex-wrap gap-2">
            {template.constants.map((variable: string, index: number) => (
              <span
                key={index}
                className="px-3 py-1 bg-white border border-blue-300 text-blue-700 rounded-lg text-sm font-mono"
              >
                {variable}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* HTML Template Source - Show as code, not rendered */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Template Source (HTML)</h3>
        <p className="text-sm text-gray-600">
          This is the template that will be rendered when campaigns are sent. Variables like <code className="bg-gray-100 px-2 py-1 rounded text-red-600">customer_name</code> will be replaced with actual values.
        </p>
        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs font-mono max-h-96 overflow-y-auto">
          <code>{template.html_content}</code>
        </pre>
      </div>

      {/* Text Content */}
      {template.text_content && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Plain Text Version</h3>
          <pre className="bg-gray-50 p-4 rounded-lg border border-gray-200 text-sm overflow-x-auto whitespace-pre-wrap">
            {template.text_content}
          </pre>
        </div>
      )}

      {/* Assets */}
      {template.assets && template.assets.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Assets ({template.assets.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {template.assets.map((asset) => (
              <div
                key={asset.id}
                className="border border-gray-200 rounded-lg p-4 text-center"
              >
                <div className="bg-gray-100 rounded-lg p-4 mb-3 h-32 flex items-center justify-center">
                  <img
                    src={asset.file_url}
                    alt="Asset"
                    className="max-w-full max-h-full object-contain"
                  />
                </div>
                <a
                  href={asset.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-teal-600 hover:underline truncate block"
                >
                  View
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
