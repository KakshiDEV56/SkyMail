"use client";

import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { templatesApi } from "@/lib/api/templates";
import { Loader2, AlertCircle, Upload, X, Eye, Edit3, ArrowLeft } from "lucide-react";

interface TemplateEditorProps {
  templateId?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function TemplateEditor({ templateId, onSuccess, onCancel }: TemplateEditorProps) {
  const [templateName, setTemplateName] = useState("");
  const [templateSubject, setTemplateSubject] = useState("");
  const [htmlContent, setHtmlContent] = useState("");
  const [textContent, setTextContent] = useState("");
  const [constants, setConstants] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewMode, setPreviewMode] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const queryClient = useQueryClient();

  // Load existing template if editing
  const { data: existingTemplate, isLoading: templateLoading } = useQuery({
    queryKey: ["template", templateId],
    queryFn: () => templatesApi.getTemplate(templateId!),
    enabled: !!templateId,
  });

  useEffect(() => {
    if (existingTemplate) {
      setTemplateName(existingTemplate.name);
      setTemplateSubject(existingTemplate.subject);
      setHtmlContent(existingTemplate.html_content);
      setTextContent(existingTemplate.text_content || "");
      
      // Parse constants - handle both array and string formats
      if (Array.isArray(existingTemplate.constants)) {
        setConstants(existingTemplate.constants.join(", "));
      } else if (typeof existingTemplate.constants === "string") {
        try {
          // Try to parse as JSON
          const parsed = JSON.parse(existingTemplate.constants);
          if (Array.isArray(parsed)) {
            setConstants(parsed.join(", "));
          } else {
            setConstants(existingTemplate.constants);
          }
        } catch (e) {
          // If parsing fails, use as-is
          setConstants(existingTemplate.constants);
        }
      } else {
        setConstants("");
      }
    }
  }, [existingTemplate]);

  // Mutation for create/update
  const mutation = useMutation({
    mutationFn: async () => {
      const formData = new FormData();
      formData.append("name", templateName);
      formData.append("subject", templateSubject);
      formData.append("html_content", htmlContent);
      if (textContent) formData.append("text_content", textContent);

      if (constants.trim()) {
        const constantsList = constants
          .split(",")
          .map((v) => v.trim())
          .filter((v) => v);
        // Send as comma-separated string
        formData.append("constants", constantsList.join(","));
      } else {
        // Send empty string if no constants
        formData.append("constants", "");
      }

      selectedFiles.forEach((file) => {
        formData.append("files", file);
      });

      if (templateId) {
        return templatesApi.updateTemplate(templateId, formData);
      } else {
        return templatesApi.createTemplate(formData);
      }
    },
    onSuccess: () => {
      setSuccessMessage(
        templateId ? "Template updated successfully!" : "Template created successfully!"
      );
      
      // Invalidate templates list cache to refresh the list view
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      
      // If updating, also invalidate the individual template cache
      if (templateId) {
        queryClient.invalidateQueries({ queryKey: ["template", templateId] });
      }
      
      setTimeout(() => {
        onSuccess?.();
      }, 1500);
    },
    onError: (error: any) => {
      let errorMsg = "Failed to save template. Please try again.";
      
      // Handle different error response formats
      if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      } else if (Array.isArray(error.response?.data)) {
        // Pydantic validation errors are arrays of objects
        errorMsg = error.response.data
          .map((e: any) => e.msg || e.message || "Unknown error")
          .join(", ");
      } else if (typeof error.response?.data === 'string') {
        errorMsg = error.response.data;
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      setErrorMessage(errorMsg);
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      setSelectedFiles((prev) => [...prev, ...files]);
      setErrorMessage("");
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add("bg-teal-50");
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.currentTarget.classList.remove("bg-teal-50");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove("bg-teal-50");
    const files = Array.from(e.dataTransfer.files);
    setSelectedFiles((prev) => [...prev, ...files]);
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handlePublish = () => {
    // Validate required fields
    if (!templateName.trim()) {
      setErrorMessage("Template name is required");
      return;
    }
    if (!templateSubject.trim()) {
      setErrorMessage("Email subject is required");
      return;
    }
    if (!htmlContent.trim()) {
      setErrorMessage("HTML content is required");
      return;
    }
    
    setErrorMessage("");
    setSuccessMessage("");

    if (!templateName.trim()) {
      setErrorMessage("Template name is required");
      return;
    }
    if (!templateSubject.trim()) {
      setErrorMessage("Template subject is required");
      return;
    }
    if (!htmlContent.trim()) {
      setErrorMessage("HTML content is required");
      return;
    }

    mutation.mutate();
  };

  const isLoading = templateLoading || mutation.isPending;

  if (templateLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-teal-600" size={32} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {templateId ? "Edit Template" : "Create Template"}
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            {templateId
              ? "Update your newsletter template"
              : "Design your newsletter template"}
          </p>
        </div>
        <button
          onClick={() => setPreviewMode(!previewMode)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
        >
          {previewMode ? (
            <>
              <Edit3 size={18} />
              Edit Mode
            </>
          ) : (
            <>
              <Eye size={18} />
              Preview Mode
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {errorMessage && typeof errorMessage === 'string' && (
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          <AlertCircle size={20} />
          <p>{errorMessage}</p>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-lg p-4 text-green-700">
          <p>{successMessage}</p>
        </div>
      )}

      {previewMode ? (
        // Preview Mode
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{templateName || "Untitled"}</h2>
              <p className="text-gray-600 mt-1">
                Subject: {templateSubject || "No subject"}
              </p>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">HTML Template Source</h3>
            <p className="text-sm text-gray-600">
              Variables like {`{{customer_name}}`} will be replaced with actual data when sending campaigns.
            </p>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto border border-gray-300 text-sm">
              <code>{htmlContent || "<p>Your HTML content will appear here</p>"}</code>
            </pre>
          </div>

          {textContent && (
            <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Plain Text Version</h3>
              <pre className="bg-gray-50 p-4 rounded-lg border border-gray-200 text-sm overflow-x-auto whitespace-pre-wrap">
                {textContent}
              </pre>
            </div>
          )}

          {constants && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Template Constants
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                These constants can be defined when creating a campaign using this template.
              </p>
              <div className="flex flex-wrap gap-2">
                {constants
                  .split(",")
                  .map((v) => v.trim())
                  .filter((v) => v)
                  .map((v, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-50 border border-blue-300 text-blue-700 rounded-lg text-sm font-mono"
                    >
                      {v}
                    </span>
                  ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        // Edit Mode
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form Section */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Template Name *
                </label>
                <input
                  type="text"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  placeholder="e.g., Weekly Newsletter"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              {/* Subject */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Email Subject *
                </label>
                <input
                  type="text"
                  value={templateSubject}
                  onChange={(e) => setTemplateSubject(e.target.value)}
                  placeholder="e.g., Hello {{name}}, here's this week's news!"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use variables like {`{{name}}, {{company}}`} to personalize
                </p>
              </div>

              {/* Constants */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Template Constants/Variables (comma-separated)
                </label>
                <input
                  type="text"
                  value={constants}
                  onChange={(e) => setConstants(e.target.value)}
                  placeholder="e.g., price, discount, offer_code"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  List custom variables/constants that will be replaced in this template. (System variables like company_name, subscriber_email are auto-filled)
                </p>
              </div>

              {/* HTML Content */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  HTML Content *
                </label>
                <textarea
                  value={htmlContent}
                  onChange={(e) => setHtmlContent(e.target.value)}
                  placeholder="Enter HTML content for your template"
                  rows={12}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              {/* Text Content */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Plain Text Content (Optional)
                </label>
                <textarea
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Enter plain text version (used as fallback for email clients)"
                  rows={8}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Upload Assets</h3>

              {/* Drag & Drop */}
              <label htmlFor="file-input-assets" className="block">
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-teal-500 transition"
                >
                  <Upload size={32} className="mx-auto text-gray-400 mb-2" />
                  <p className="text-sm font-medium text-gray-900">
                    Drop files here or click to upload
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    PNG, JPG, GIF up to 5MB each
                  </p>
                </div>
              </label>
              <input
                id="file-input-assets"
                type="file"
                onChange={handleFileSelect}
                multiple
                accept="image/*"
                className="hidden"
              />

              {/* Selected Files */}
              {selectedFiles.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-900">
                    Selected Files ({selectedFiles.length})
                  </p>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {selectedFiles.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between bg-gray-50 p-3 rounded-lg border border-gray-200"
                      >
                        <span className="text-sm text-gray-700 truncate">
                          {file.name}
                        </span>
                        <button
                          onClick={() => handleRemoveFile(index)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X size={18} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        <button
          onClick={onCancel}
          className="px-6 py-2 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition"
        >
          Cancel
        </button>
        <button
          onClick={handlePublish}
          disabled={isLoading}
          className="px-6 py-2 rounded-lg bg-teal-600 text-white font-medium hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
        >
          {isLoading && <Loader2 size={18} className="animate-spin" />}
          {templateId ? "Update Template" : "Publish Template"}
        </button>
      </div>
    </div>
  );
}
