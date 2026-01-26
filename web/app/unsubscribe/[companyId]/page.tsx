"use client";

import { useState } from "react";
import { subscribersApi } from "@/lib/api/subscribers";
import { AlertCircle, CheckCircle, Loader2, Mail } from "lucide-react";
import { useSearchParams } from "next/navigation";

interface UnsubscribePageProps {
  params: {
    companyId: string;
  };
}

export default function UnsubscribePage({
  params,
}: UnsubscribePageProps) {
  const searchParams = useSearchParams();
  const prefilledEmail = searchParams.get("email") || "";
  const { companyId } = params;

  const [email, setEmail] = useState(prefilledEmail);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<
    "idle" | "success" | "error" | "not_found"
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
      const response = await subscribersApi.unsubscribe(companyId, email);

      if (response.status === "success" || response.status === "unsubscribed") {
        setStatus("success");
        setMessage(response.message || "You have been unsubscribed successfully.");
        setEmail("");
      } else {
        setStatus("not_found");
        setMessage(response.message || "Email not found in our records.");
      }
    } catch (error: any) {
      if (
        error.message.includes("404") ||
        error.message.includes("not found")
      ) {
        setStatus("not_found");
        setMessage("Email not found in our records.");
      } else {
        setStatus("error");
        setMessage(
          error.message || "An error occurred. Please try again later."
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Mail className="w-12 h-12 text-gray-400" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Unsubscribe
          </h1>
          <p className="text-gray-600">
            We're sorry to see you go. Enter your email to unsubscribe from our
            newsletter.
          </p>
        </div>

        {/* Status Messages */}
        {status === "success" && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-green-900 mb-1">
                  Unsubscribed Successfully
                </h3>
                <p className="text-sm text-green-800">{message}</p>
              </div>
            </div>
            <p className="text-sm text-green-700 mt-4">
              You can resubscribe anytime if you change your mind.
            </p>
          </div>
        )}

        {status === "not_found" && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-yellow-900 mb-1">
                  Not Found
                </h3>
                <p className="text-sm text-yellow-800">{message}</p>
              </div>
            </div>
          </div>
        )}

        {status === "error" && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                <p className="text-sm text-red-800">{message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Form */}
        {status !== "success" && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                disabled={isLoading}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Unsubscribing...
                </>
              ) : (
                "Unsubscribe"
              )}
            </button>

            <p className="text-xs text-gray-500 text-center">
              Your email will be removed from our mailing list immediately.
            </p>
          </form>
        )}

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            This unsubscribe page is powered by{" "}
            <span className="font-semibold text-gray-700">SkyMail</span>
          </p>
        </div>
      </div>
    </div>
  );
}
