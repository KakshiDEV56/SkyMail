"use client";

import { useState, useEffect } from "react";
import { DashboardHeader } from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { ArrowLeft, AlertCircle, Check } from "lucide-react";
import Link from "next/link";
import apiClient from "@/lib/api-client";
import { useRouter } from "next/navigation";

interface Template {
  id: string;
  name: string;
  subject: string;
  constants: string[];
  html_content: string;
  text_content?: string;
}

interface ValidationError {
  field: string;
  message: string;
}

export default function CreateCampaignPage() {
  const router = useRouter();
  const [step, setStep] = useState<"template" | "constants" | "metadata" | "schedule" | "review">("template");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [constantsValues, setConstantsValues] = useState<Record<string, string>>({});
  const [campaignName, setCampaignName] = useState("");
  const [scheduledFor, setScheduledFor] = useState("");
  const [sendTimezone, setSendTimezone] = useState("UTC");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [previewData, setPreviewData] = useState<Record<string, string>>({});

  const SYSTEM_VARIABLES = ["company_name", "subscriber_email", "subscriber_username"];

  // Get custom constants (user-defined, not system variables)
  const getCustomConstants = (): string[] => {
    if (!selectedTemplate) return [];
    return selectedTemplate.constants.filter(
      (constant: string) => !SYSTEM_VARIABLES.includes(constant)
    );
  };

  // Get system variables that exist in template
  const getSystemVariables = (): string[] => {
    if (!selectedTemplate) return [];
    return selectedTemplate.constants.filter(
      (constant: string) => SYSTEM_VARIABLES.includes(constant)
    );
  };

  // Fetch templates on mount
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await apiClient.get("/api/newsletters/templates");
        setTemplates(response.data.items || response.data.templates || response.data || []);
        setIsLoading(false);
      } catch (error) {
        console.error("Failed to fetch templates:", error);
        setIsLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  // Handle template selection
  const handleSelectTemplate = (template: Template) => {
    setSelectedTemplate(template);
    // Initialize constants values
    const initialValues: Record<string, string> = {};
    template.constants.forEach((constant) => {
      initialValues[constant] = "";
    });
    setConstantsValues(initialValues);
    setStep("constants");
  };

  // Handle constant value change
  const handleConstantChange = (constant: string, value: string) => {
    setConstantsValues((prev) => ({
      ...prev,
      [constant]: value,
    }));
  };

  // Validate constants step
  const validateConstantsStep = (): boolean => {
    const errors: ValidationError[] = [];

    if (!selectedTemplate) {
      errors.push({ field: "template", message: "Template not selected" });
    }

    // Only validate custom constants (not system variables)
    const customConstants = getCustomConstants();
    customConstants.forEach((constant) => {
      if (!constantsValues[constant] || constantsValues[constant].trim() === "") {
        errors.push({ field: constant, message: `${constant} is required` });
      }
    });

    setValidationErrors(errors);
    return errors.length === 0;
  };

  // Validate metadata step
  const validateMetadataStep = (): boolean => {
    const errors: ValidationError[] = [];

    if (!campaignName.trim()) {
      errors.push({ field: "name", message: "Campaign name is required" });
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  // Validate schedule step
  const validateScheduleStep = (): boolean => {
    const errors: ValidationError[] = [];

    if (!scheduledFor) {
      errors.push({ field: "scheduled_for", message: "Scheduled time is required" });
    } else {
      const scheduled = new Date(scheduledFor);
      const now = new Date();
      if (scheduled <= now) {
        errors.push({ field: "scheduled_for", message: "Scheduled time must be in the future" });
      }
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  // Move to next step
  const handleNextStep = () => {
    if (step === "constants" && !validateConstantsStep()) return;
    if (step === "metadata" && !validateMetadataStep()) return;
    if (step === "schedule" && !validateScheduleStep()) return;

    if (step === "template") {
      setStep("constants");
    } else if (step === "constants") {
      setStep("metadata");
    } else if (step === "metadata") {
      setStep("schedule");
    } else if (step === "schedule") {
      // Generate preview data
      setPreviewData({
        subscriber_name: "John Doe",
        subscriber_email: "john@example.com",
        company_name: "Your Company",
        ...constantsValues,
      });
      setStep("review");
    }
  };

  // Submit campaign
  const handleSubmit = async () => {
    if (!selectedTemplate) return;

    setIsSubmitting(true);
    try {
      // Ensure scheduled_for is properly formatted as ISO string
      const scheduledDateTime = new Date(scheduledFor);
      if (isNaN(scheduledDateTime.getTime())) {
        throw new Error("Invalid scheduled date/time");
      }

      const payload = {
        name: campaignName,
        template_id: selectedTemplate.id,
        constants_values: constantsValues,
        scheduled_for: scheduledDateTime.toISOString(),
        send_timezone: sendTimezone || "UTC",
      };

      console.log("Submitting campaign:", payload);

      const response = await apiClient.post("/api/campaigns", payload);

      // Redirect to campaign details
      router.push(`/dashboard/campaigns/${response.data.id}`);
    } catch (error: any) {
      console.error("Failed to create campaign:", error);
      const message = error.response?.data?.detail || error.message || "Failed to create campaign";
      setValidationErrors([{ field: "submit", message }]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getErrorForField = (field: string) => {
    return validationErrors.find((e) => e.field === field)?.message;
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
                href="/dashboard/campaigns"
                className="flex items-center gap-2 text-[#2A8C9D] hover:text-[#1D7A89] mb-4"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Campaigns
              </Link>
              <h1 className="text-3xl font-bold text-[#180D39]">Create Campaign</h1>
              <p className="text-gray-600 mt-2">Step {["template", "constants", "metadata", "schedule", "review"].indexOf(step) + 1} of 5</p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-8">
              {/* Step 1: Select Template */}
              {step === "template" && (
                <div>
                  <h2 className="text-2xl font-bold text-[#180D39] mb-6">Select Template</h2>
                  {isLoading ? (
                    <div className="text-center py-12">
                      <div className="text-gray-500">Loading templates...</div>
                    </div>
                  ) : templates.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-gray-600 mb-4">No templates available</p>
                      <Link
                        href="/dashboard/templates"
                        className="text-[#2A8C9D] hover:text-[#1D7A89] font-medium"
                      >
                        Create a template first
                      </Link>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {templates.map((template) => (
                        <div
                          key={template.id}
                          onClick={() => handleSelectTemplate(template)}
                          className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                            selectedTemplate?.id === template.id
                              ? "border-[#2A8C9D] bg-blue-50"
                              : "border-gray-200 hover:border-[#2A8C9D]"
                          }`}
                        >
                          <h3 className="font-bold text-[#180D39]">{template.name}</h3>
                          <p className="text-sm text-gray-600 mt-1">Subject: {template.subject}</p>
                          <p className="text-sm text-gray-500 mt-2">
                            Constants: {template.constants.join(", ") || "None"}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="flex justify-end gap-4 mt-8">
                    <button
                      onClick={() => router.back()}
                      className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleNextStep}
                      disabled={!selectedTemplate}
                      className="px-6 py-2 bg-[#2A8C9D] text-white rounded-lg hover:bg-[#1D7A89] disabled:opacity-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}

              {/* Step 2: Fill Constants */}
              {step === "constants" && selectedTemplate && (
                <div>
                  <h2 className="text-2xl font-bold text-[#180D39] mb-2">Fill Template Constants</h2>
                  <p className="text-gray-600 mb-6">Configure custom variables for your campaign</p>

                  {validationErrors.length > 0 && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                      <div>
                        <h3 className="font-bold text-red-900">Please fix these errors:</h3>
                        <ul className="text-sm text-red-700 mt-2 space-y-1">
                          {validationErrors.map((error) => (
                            <li key={error.field}>• {error.message}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* System Variables - Auto-filled from Database */}
                  {getSystemVariables().length > 0 && (
                    <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <h3 className="text-sm font-semibold text-blue-900 mb-4">
                        🔒 System Variables (Auto-filled from Database)
                      </h3>
                      <div className="space-y-3">
                        {getSystemVariables().map((variable) => (
                          <div key={variable}>
                            <label className="block text-sm font-medium text-blue-900 mb-1">
                              {variable}
                            </label>
                            <div className="px-4 py-2 bg-white border border-blue-200 rounded-lg text-gray-700">
                              <span className="text-sm italic text-gray-600">
                                {variable === "company_name" && "Your company name from profile"}
                                {variable === "subscriber_email" && "Subscriber's email address"}
                                {variable === "subscriber_username" && "Subscriber's username"}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Custom Constants - User-defined */}
                  {getCustomConstants().length > 0 ? (
                    <div>
                      <h3 className="text-sm font-semibold text-[#180D39] mb-4">
                        📝 Custom Variables (Define your values)
                      </h3>
                      <div className="space-y-4">
                        {getCustomConstants().map((constant) => (
                          <div key={constant}>
                            <label className="block text-sm font-medium text-[#180D39] mb-2">
                              {constant} <span className="text-red-500">*</span>
                            </label>
                            <input
                              type="text"
                              value={constantsValues[constant] || ""}
                              onChange={(e) => handleConstantChange(constant, e.target.value)}
                              placeholder={`Enter value for ${constant}`}
                              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                                getErrorForField(constant)
                                  ? "border-red-300 focus:ring-red-200"
                                  : "border-gray-300 focus:ring-[#2A8C9D] focus:ring-opacity-20"
                              }`}
                            />
                            {getErrorForField(constant) && (
                              <p className="text-sm text-red-600 mt-1">{getErrorForField(constant)}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-sm text-green-800">
                        ✓ No custom variables needed. This template only uses system variables.
                      </p>
                    </div>
                  )}

                  <div className="flex justify-between gap-4 mt-8">
                    <button
                      onClick={() => {
                        setSelectedTemplate(null);
                        setStep("template");
                      }}
                      className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleNextStep}
                      className="px-6 py-2 bg-[#2A8C9D] text-white rounded-lg hover:bg-[#1D7A89]"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}

              {/* Step 3: Campaign Metadata */}
              {step === "metadata" && (
                <div>
                  <h2 className="text-2xl font-bold text-[#180D39] mb-6">Campaign Details</h2>

                  {validationErrors.length > 0 && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                      <div>
                        <h3 className="font-bold text-red-900">Please fix these errors:</h3>
                        <ul className="text-sm text-red-700 mt-2 space-y-1">
                          {validationErrors.map((error) => (
                            <li key={error.field}>• {error.message}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-[#180D39] mb-2">
                        Campaign Name <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={campaignName}
                        onChange={(e) => setCampaignName(e.target.value)}
                        placeholder="e.g., January Promo"
                        className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                          getErrorForField("name")
                            ? "border-red-300 focus:ring-red-200"
                            : "border-gray-300 focus:ring-[#2A8C9D] focus:ring-opacity-20"
                        }`}
                      />
                      {getErrorForField("name") && (
                        <p className="text-sm text-red-600 mt-1">{getErrorForField("name")}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-[#180D39] mb-2">
                        Subject (from template)
                      </label>
                      <div className="px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-700">
                        {selectedTemplate?.subject}
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between gap-4 mt-8">
                    <button
                      onClick={() => setStep("constants")}
                      className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleNextStep}
                      className="px-6 py-2 bg-[#2A8C9D] text-white rounded-lg hover:bg-[#1D7A89]"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}

              {/* Step 4: Schedule Campaign */}
              {step === "schedule" && (
                <div>
                  <h2 className="text-2xl font-bold text-[#180D39] mb-6">Schedule Campaign</h2>

                  {validationErrors.length > 0 && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                      <div>
                        <h3 className="font-bold text-red-900">Please fix these errors:</h3>
                        <ul className="text-sm text-red-700 mt-2 space-y-1">
                          {validationErrors.map((error) => (
                            <li key={error.field}>• {error.message}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-[#180D39] mb-2">
                        Schedule Time (UTC) <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="datetime-local"
                        value={scheduledFor}
                        onChange={(e) => setScheduledFor(e.target.value)}
                        className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                          getErrorForField("scheduled_for")
                            ? "border-red-300 focus:ring-red-200"
                            : "border-gray-300 focus:ring-[#2A8C9D] focus:ring-opacity-20"
                        }`}
                      />
                      {getErrorForField("scheduled_for") && (
                        <p className="text-sm text-red-600 mt-1">{getErrorForField("scheduled_for")}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-[#180D39] mb-2">
                        Timezone (for display)
                      </label>
                      <select
                        value={sendTimezone}
                        onChange={(e) => setSendTimezone(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2A8C9D] focus:ring-opacity-20"
                      >
                        <option>UTC</option>
                        <option>America/New_York</option>
                        <option>America/Los_Angeles</option>
                        <option>Europe/London</option>
                        <option>Asia/Tokyo</option>
                        <option>India/Standard</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex justify-between gap-4 mt-8">
                    <button
                      onClick={() => setStep("metadata")}
                      className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleNextStep}
                      className="px-6 py-2 bg-[#2A8C9D] text-white rounded-lg hover:bg-[#1D7A89]"
                    >
                      Review
                    </button>
                  </div>
                </div>
              )}

              {/* Step 5: Review & Submit */}
              {step === "review" && (
                <div>
                  <h2 className="text-2xl font-bold text-[#180D39] mb-6">Review Campaign</h2>

                  <div className="space-y-6">
                    {/* Campaign Info */}
                    <div className="border border-gray-200 rounded-lg p-4">
                      <h3 className="font-bold text-[#180D39] mb-4">Campaign Information</h3>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">Name</p>
                          <p className="font-medium text-[#180D39]">{campaignName}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Template</p>
                          <p className="font-medium text-[#180D39]">{selectedTemplate?.name}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Subject</p>
                          <p className="font-medium text-[#180D39]">{selectedTemplate?.subject}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Scheduled For</p>
                          <p className="font-medium text-[#180D39]">
                            {new Date(scheduledFor).toLocaleString()} {sendTimezone !== "UTC" ? sendTimezone : ""}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Constants Table */}
                    {getCustomConstants().length > 0 && (
                      <div className="border border-gray-200 rounded-lg p-4">
                        <h3 className="font-bold text-[#180D39] mb-4">Custom Variables</h3>
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-gray-200">
                              <th className="text-left py-2 px-3 text-gray-700 font-medium">Variable</th>
                              <th className="text-left py-2 px-3 text-gray-700 font-medium">Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            {getCustomConstants().map((constant) => (
                              <tr key={constant} className="border-b border-gray-100">
                                <td className="py-2 px-3 text-gray-600">{constant}</td>
                                <td className="py-2 px-3 font-medium text-[#180D39]">
                                  {constantsValues[constant]}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}

                    {/* System Variables Info */}
                    {getSystemVariables().length > 0 && (
                      <div className="border border-blue-200 bg-blue-50 rounded-lg p-4">
                        <h3 className="font-bold text-blue-900 mb-4">🔒 System Variables (Auto-filled)</h3>
                        <p className="text-sm text-blue-800 mb-3">
                          These variables will be automatically filled from the database when the campaign is sent:
                        </p>
                        <ul className="space-y-2">
                          {getSystemVariables().map((variable) => (
                            <li key={variable} className="text-sm text-blue-800">
                              <strong>{variable}</strong>
                              <span className="text-blue-700 ml-2">
                                {variable === "company_name" && "(Your company name)"}
                                {variable === "subscriber_email" && "(Subscriber's email)"}
                                {variable === "subscriber_username" && "(Subscriber's username)"}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Preview Section */}
                    <div className="border border-gray-200 rounded-lg p-4">
                      <h3 className="font-bold text-[#180D39] mb-4">Preview (Sample Data)</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        This is how the email will look for a sample subscriber. Actual emails will include the real subscriber's information.
                      </p>
                      <div className="bg-gray-50 p-4 rounded border border-gray-200 max-h-96 overflow-y-auto">
                        <div
                          dangerouslySetInnerHTML={{
                            __html: renderTemplate(selectedTemplate?.html_content || "", previewData),
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {validationErrors.some((e) => e.field === "submit") && (
                    <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                      <div>
                        <p className="text-red-700">
                          {validationErrors.find((e) => e.field === "submit")?.message}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between gap-4 mt-8">
                    <button
                      onClick={() => setStep("schedule")}
                      className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleSubmit}
                      disabled={isSubmitting}
                      className="px-6 py-2 bg-[#2A8C9D] text-white rounded-lg hover:bg-[#1D7A89] disabled:opacity-50 flex items-center gap-2"
                    >
                      {isSubmitting ? "Creating..." : "Create Campaign"}
                      {!isSubmitting && <Check className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

/**
 * Simple template rendering function
 * Replaces {{variable}} with actual values
 */
function renderTemplate(html: string, data: Record<string, string>): string {
  let result = html;
  Object.entries(data).forEach(([key, value]) => {
    result = result.replace(new RegExp(`{{\\s*${key}\\s*}}`, "g"), value);
  });
  return result;
}
