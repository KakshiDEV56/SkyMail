"use client";

import { useState } from "react";
import { subscribersApi } from "@/lib/api/subscribers";
import { Loader2 } from "lucide-react";

interface MinimalFormProps {
  companyId: string;
}

/**
 * Minimal Subscribe Form - Clean and simple
 * Perfect for sidebars and footers
 */
export function MinimalSubscriptionForm({ companyId }: MinimalFormProps) {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await subscribersApi.subscribe(companyId, email);
      setStatus("success");
      setEmail("");
    } catch (error) {
      setStatus("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-2">
      {status === "success" ? (
        <p className="text-sm text-green-600 font-medium">
          ✓ Thanks for subscribing!
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email address"
            disabled={isLoading}
            className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? "..." : "Join"}
          </button>
        </form>
      )}
    </div>
  );
}

/**
 * Inline Subscribe Form - With description
 * Perfect for hero sections and main content
 */
export function InlineSubscriptionForm({ companyId }: MinimalFormProps) {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await subscribersApi.subscribe(companyId, email);
      setStatus("success");
      setMessage(response.message);
      setEmail("");
    } catch (error: any) {
      setStatus("error");
      setMessage(error.message || "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-8">
      <h3 className="text-2xl font-bold text-gray-900 mb-2">
        Subscribe to Our Newsletter
      </h3>
      <p className="text-gray-600 mb-6">
        Stay updated with our latest news and updates delivered to your inbox.
      </p>

      {status === "success" ? (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800 font-medium">{message}</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            disabled={isLoading}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <button
            type="submit"
            disabled={isLoading}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            {isLoading ? "Subscribing..." : "Subscribe"}
          </button>
          {status === "error" && (
            <p className="text-sm text-red-600">{message}</p>
          )}
        </form>
      )}
    </div>
  );
}

/**
 * Card Subscribe Form - Beautiful card design
 * Perfect for sidebars and feature sections
 */
export function CardSubscriptionForm({ companyId }: MinimalFormProps) {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await subscribersApi.subscribe(companyId, email);
      setStatus("success");
      setEmail("");
    } catch (error) {
      setStatus("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-8 border border-blue-200">
      <div className="text-center">
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          Get Updates
        </h3>
        <p className="text-gray-700 mb-6">
          Join thousands of subscribers
        </p>

        {status === "success" ? (
          <div className="p-3 bg-green-100 text-green-800 rounded-lg text-sm font-medium">
            ✓ Check your email!
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              disabled={isLoading}
              className="w-full px-4 py-3 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {isLoading ? "..." : "Subscribe"}
            </button>
            {status === "error" && (
              <p className="text-xs text-red-600">Try again</p>
            )}
          </form>
        )}
      </div>
    </div>
  );
}
