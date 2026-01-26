"use client";

import { useState, useEffect } from "react";
import { DashboardHeader } from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Mail, Download, Trash2, Loader2, Search, Code } from "lucide-react";
import apiClient from "@/lib/api-client";
import Link from "next/link";

interface Subscriber {
  id: string;
  email: string;
  is_subscribed: boolean;
  subscribed_at: string;
  unsubscribed_at?: string;
}

interface SubscribersResponse {
  total: number;
  page: number;
  page_size: number;
  subscribers: Subscriber[];
}

export default function SubscribersPage() {
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [searchEmail, setSearchEmail] = useState("");

  useEffect(() => {
    fetchSubscribers();
  }, [page, pageSize, searchEmail]);

  const fetchSubscribers = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: pageSize.toString(),
      });

      if (searchEmail) {
        params.append("email", searchEmail);
      }

      const response = await apiClient.get<SubscribersResponse>(
        `/api/subscribers?${params.toString()}`
      );

      setSubscribers(response.data.subscribers || []);
      setTotal(response.data.total || 0);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to load subscribers"
      );
      setSubscribers([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteSubscriber = async (subscriberId: string) => {
    if (!confirm("Are you sure you want to delete this subscriber?")) {
      return;
    }

    try {
      await apiClient.delete(`/api/subscribers/${subscriberId}`);
      setSubscribers(subscribers.filter((s) => s.id !== subscriberId));
      setTotal(total - 1);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to delete subscriber");
    }
  };

  const handleExportCSV = () => {
    // Create CSV content
    const headers = ["Email", "Status", "Subscribed At", "Unsubscribed At"];
    const rows = subscribers.map((s) => [
      s.email,
      s.is_subscribed ? "Subscribed" : "Unsubscribed",
      new Date(s.subscribed_at).toLocaleString(),
      s.unsubscribed_at
        ? new Date(s.unsubscribed_at).toLocaleString()
        : "N/A",
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
    ].join("\n");

    // Download
    const element = document.createElement("a");
    element.setAttribute(
      "href",
      "data:text/csv;charset=utf-8," + encodeURIComponent(csvContent)
    );
    element.setAttribute("download", "subscribers.csv");
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader />

      <div className="flex">
        <Sidebar />

        {/* Main Content */}
        <div className="flex-1 p-8">
          <div className="max-w-6xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold text-[#180D39] mb-2">
                  Subscribers
                </h1>
                <p className="text-gray-600">
                  Manage your newsletter subscribers ({total} total)
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href="/dashboard/subscribers/code-snippets"
                  className="flex items-center gap-2 px-6 py-2 border border-[#2A8C9D] text-[#2A8C9D] rounded-lg hover:bg-[#2A8C9D] hover:text-white transition"
                >
                  <Code className="w-4 h-4" />
                  Code Snippets
                </Link>
                {subscribers.length > 0 && (
                  <button
                    onClick={handleExportCSV}
                    className="flex items-center gap-2 px-6 py-2 bg-[#2A8C9D] text-white rounded-lg hover:bg-[#1D7A89] transition"
                  >
                    <Download className="w-4 h-4" />
                    Export CSV
                  </button>
                )}
              </div>
            </div>

            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  placeholder="Search by email..."
                  value={searchEmail}
                  onChange={(e) => {
                    setSearchEmail(e.target.value);
                    setPage(1);
                  }}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2A8C9D]"
                />
              </div>
            </div>

            {/* Content */}
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-[#2A8C9D] animate-spin" />
              </div>
            ) : error ? (
              <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-800">
                {error}
              </div>
            ) : subscribers.length === 0 ? (
              <div className="text-center py-12">
                <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No Subscribers Yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Start by adding subscription forms to your website.
                </p>
                <Link
                  href="/dashboard/subscribers/code-snippets"
                  className="inline-flex items-center gap-2 px-6 py-2 bg-[#2A8C9D] text-white rounded-lg hover:bg-[#1D7A89] transition"
                >
                  Get Code Snippets
                </Link>
              </div>
            ) : (
              <>
                {/* Table */}
                <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">
                          Email
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">
                          Status
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">
                          Subscribed At
                        </th>
                        <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {subscribers.map((subscriber) => (
                        <tr
                          key={subscriber.id}
                          className="border-b hover:bg-gray-50 transition"
                        >
                          <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                            {subscriber.email}
                          </td>
                          <td className="px-6 py-4 text-sm">
                            <span
                              className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                                subscriber.is_subscribed
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {subscriber.is_subscribed
                                ? "Subscribed"
                                : "Unsubscribed"}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {new Date(subscriber.subscribed_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() =>
                                handleDeleteSubscriber(subscriber.id)
                              }
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                              title="Delete subscriber"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                <div className="mt-6 flex items-center justify-between">
                  <p className="text-sm text-gray-600">
                    Showing {(page - 1) * pageSize + 1} to{" "}
                    {Math.min(page * pageSize, total)} of {total}
                  </p>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPage(page - 1)}
                      disabled={page === 1}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      Previous
                    </button>

                    <div className="flex items-center gap-1">
                      {Array.from({ length: totalPages }, (_, i) => i + 1)
                        .slice(
                          Math.max(0, page - 2),
                          Math.min(totalPages, page + 1)
                        )
                        .map((p) => (
                          <button
                            key={p}
                            onClick={() => setPage(p)}
                            className={`px-3 py-2 rounded-lg transition ${
                              page === p
                                ? "bg-[#2A8C9D] text-white"
                                : "border border-gray-300 hover:bg-gray-50"
                            }`}
                          >
                            {p}
                          </button>
                        ))}
                    </div>

                    <button
                      onClick={() => setPage(page + 1)}
                      disabled={page === totalPages}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
