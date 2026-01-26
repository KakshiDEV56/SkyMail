"use client";

import { useState } from "react";
import { subscribersApi } from "@/lib/api/subscribers";
import { Mail, AlertCircle, CheckCircle, Loader2 } from "lucide-react";

interface SubscriptionFormProps {
  companyId: string;
  title?: string;
  subtitle?: string;
  placeholder?: string;
  buttonText?: string;
  theme?: "light" | "dark";
}

export default function SubscriptionForm({
  companyId,
  title = "Subscribe to Our Newsletter",
  subtitle = "Get the latest updates delivered to your inbox",
  placeholder = "Enter your email",
  buttonText = "Subscribe",
  theme = "light",
}: SubscriptionFormProps) {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<
    "idle" | "success" | "error" | "already_subscribed"
  >("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      setStatus("error");
      setMessage("Please enter a valid email");
      return;
    }

    setIsLoading(true);
    setStatus("idle");
    setMessage("");

    try {
      const response = await subscribersApi.subscribe(companyId, email);

      if (
        response.status === "subscribed" ||
        response.status === "resubscribed"
      ) {
        setStatus("success");
        setMessage("Thank you for subscribing! Check your email.");
        setEmail("");
      } else if (response.status === "already_subscribed") {
        setStatus("already_subscribed");
        setMessage("You're already subscribed to our newsletter.");
      } else {
        setStatus("error");
        setMessage(response.message || "Subscription failed. Please try again.");
      }
    } catch (error: any) {
      setStatus("error");
      setMessage(
        error.message || "An error occurred. Please try again later."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const isDark = theme === "dark";
  const bgColor = isDark ? "bg-gray-900" : "bg-white";
  const textColor = isDark ? "text-white" : "text-gray-900";
  const borderColor = isDark
    ? "border-gray-700 bg-gray-800"
    : "border-gray-300 bg-white";
  const inputBgColor = isDark ? "bg-gray-800 text-white" : "bg-white";
  const accentColor = "#2A8C9D";

  return (
    <div className={`w-full max-w-md mx-auto p-6 rounded-xl ${bgColor}`}>
      {/* Header */}
      <div className="text-center mb-6">
        <div className="flex items-center justify-center mb-4">
          <Mail
            className="w-8 h-8"
            style={{ color: accentColor }}
          />
        </div>
        <h2 className={`text-2xl font-bold ${textColor} mb-2`}>{title}</h2>
        <p className={`text-sm ${isDark ? "text-gray-400" : "text-gray-600"}`}>
          {subtitle}
        </p>
      </div>

      {/* Status Messages */}
      {status === "success" && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-green-800">{message}</p>
        </div>
      )}

      {status === "already_subscribed" && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-800">{message}</p>
        </div>
      )}

      {status === "error" && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{message}</p>
        </div>
      )}

      {/* Form */}
      {status !== "success" && (
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-2">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={placeholder}
              disabled={isLoading}
              className={`flex-1 px-4 py-3 rounded-lg border ${borderColor} ${inputBgColor} text-sm placeholder-gray-500 focus:outline-none focus:ring-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed`}
              style={{
                "--tw-ring-color": accentColor,
              } as any}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3 rounded-lg font-medium text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              style={{
                backgroundColor: accentColor,
                opacity: isLoading ? 0.8 : 1,
              }}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="hidden sm:inline">Loading...</span>
                </>
              ) : (
                buttonText
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 text-center">
            We respect your privacy. Unsubscribe at any time.
          </p>
        </form>
      )}
    </div>
  );
}
