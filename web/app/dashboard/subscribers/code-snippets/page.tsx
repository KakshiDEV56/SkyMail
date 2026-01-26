"use client";

import { useState, useEffect } from "react";
import { DashboardHeader } from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Copy, Check, AlertCircle, Loader2, Mail } from "lucide-react";
import apiClient from "@/lib/api-client";

interface CodeSnippet {
  id: string;
  name: string;
  description: string;
  code: string;
  language: string;
}

interface CompanyProfile {
  id: string;
  website_url?: string;
}

export default function SubscribeCodeSnippetsPage() {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("react");
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"preview" | "code">("preview");

  // Fetch company profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await apiClient.get("/api/auth/me");
        setProfile(response.data);
      } catch (error) {
        console.error("Failed to fetch profile:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#2A8C9D] animate-spin" />
      </div>
    );
  }

  const companyId = profile?.id || "COMPANY_ID_NOT_FOUND";
  const websiteUrl = profile?.website_url || "YOUR_SITE_URL";

  const generateSnippets = (cId: string, wsUrl: string): CodeSnippet[] => [
    {
      id: "react",
      name: "React Component",
      description: "Ready-to-use React component with hooks",
      language: "jsx",
      code: `import { useState } from 'react';

export default function NewsletterSection() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('success');

  const handleSubscribe = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(
        '/public/companies/${cId}/subscribe',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email }),
          credentials: 'include',
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage('Thanks for subscribing! Check your email.');
        setMessageType('success');
        setEmail('');
      } else {
        setMessage(data.detail || 'Subscription failed');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('An error occurred. Please try again.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h3 className="text-xl font-bold mb-2">Subscribe to Our Newsletter</h3>
      <p className="text-gray-600 mb-4">Get the latest updates delivered to your inbox</p>
      
      <form onSubmit={handleSubscribe} className="space-y-4">
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Subscribing...' : 'Subscribe'}
        </button>
      </form>

      {message && (
        <p className={\`mt-4 text-sm \${messageType === 'success' ? 'text-green-600' : 'text-red-600'}\`}>
          {message}
        </p>
      )}
    </div>
  );
}`,
    },
    {
      id: "html",
      name: "HTML Form",
      description: "Plain HTML form that you can embed anywhere",
      language: "html",
      code: `<form id="newsletter-form" class="newsletter-form">
  <div class="form-group">
    <input 
      type="email" 
      id="email" 
      placeholder="Enter your email"
      required
    />
    <button type="submit">Subscribe</button>
  </div>
  <p id="status-message"></p>
</form>

<script>
const form = document.getElementById('newsletter-form');
const statusMessage = document.getElementById('status-message');
const COMPANY_ID = '${cId}';

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  
  try {
    const response = await fetch(
      \`/public/companies/\${COMPANY_ID}/subscribe\`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      }
    );
    
    const data = await response.json();
    
    if (response.ok) {
      statusMessage.textContent = 'Thanks for subscribing!';
      statusMessage.className = 'success';
      form.reset();
    } else {
      statusMessage.textContent = data.detail || 'Subscription failed';
      statusMessage.className = 'error';
    }
  } catch (error) {
    statusMessage.textContent = 'An error occurred';
    statusMessage.className = 'error';
  }
});
</script>`,
    },
    {
      id: "javascript",
      name: "Vanilla JavaScript",
      description: "Simple JavaScript for plain websites",
      language: "javascript",
      code: `// Initialize subscription form
const COMPANY_ID = '${cId}';

function initNewsletter() {
  const form = document.querySelector('[data-newsletter-form]');
  const emailInput = form.querySelector('input[type="email"]');
  const submitBtn = form.querySelector('button[type="submit"]');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Subscribing...';
    
    try {
      const response = await fetch(
        \`/public/companies/\${COMPANY_ID}/subscribe\`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            email: emailInput.value 
          }),
        }
      );
      
      const data = await response.json();
      
      if (data.status === 'subscribed' || data.status === 'resubscribed') {
        form.innerHTML = '<p class="success">✓ Check your email!</p>';
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Something went wrong. Please try again.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Subscribe';
    }
  });
}

// Call when DOM is ready
document.addEventListener('DOMContentLoaded', initNewsletter);`,
    },
    {
      id: "vue",
      name: "Vue 3 Component",
      description: "Vue 3 Composition API component",
      language: "vue",
      code: `<template>
  <div class="newsletter-form">
    <h2>Subscribe to Our Newsletter</h2>
    
    <form @submit.prevent="handleSubmit" v-if="!isSuccess">
      <input 
        v-model="email"
        type="email"
        placeholder="your@email.com"
        :disabled="isLoading"
      />
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Subscribing...' : 'Subscribe' }}
      </button>
    </form>
    
    <div v-else class="success-message">
      ✓ Thank you for subscribing!
    </div>
    
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const COMPANY_ID = '${cId}';
const email = ref('');
const isLoading = ref(false);
const isSuccess = ref(false);
const error = ref('');

const handleSubmit = async () => {
  isLoading.value = true;
  error.value = '';
  
  try {
    const response = await fetch(
      \`/public/companies/\${COMPANY_ID}/subscribe\`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.value }),
      }
    );
    
    const data = await response.json();
    
    if (response.ok) {
      isSuccess.value = true;
      email.value = '';
    } else {
      error.value = data.detail || 'Subscription failed';
    }
  } catch (err) {
    error.value = 'An error occurred';
  } finally {
    isLoading.value = false;
  }
};
</script>`,
    },
    {
      id: "curl",
      name: "cURL Request",
      description: "Test subscription with cURL command",
      language: "bash",
      code: `# Subscribe to newsletter
curl -X POST \\
  '${wsUrl}/public/companies/${cId}/subscribe' \\
  -H 'Content-Type: application/json' \\
  -H 'Origin: ${wsUrl}' \\
  -d '{
    "email": "USER_EMAIL"
  }'

# Unsubscribe from newsletter
curl -X POST \\
  '${wsUrl}/public/companies/${cId}/unsubscribe' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "email": "USER_EMAIL"
  }'`,
    },
    {
      id: "nextjs",
      name: "Next.js API Route",
      description: "Backend API route for Next.js",
      language: "typescript",
      code: `// pages/api/newsletter.ts
import type { NextApiRequest, NextApiResponse } from 'next';

type ResponseData = {
  success: boolean;
  message: string;
};

const COMPANY_ID = '${cId}';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      message: 'Method not allowed' 
    });
  }

  const { email } = req.body;

  try {
    const response = await fetch(
      \`\${process.env.NEXT_PUBLIC_API_URL}/public/companies/\${COMPANY_ID}/subscribe\`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Origin': process.env.NEXT_PUBLIC_WEBSITE_URL || '',
        },
        body: JSON.stringify({ email }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      res.status(200).json({ 
        success: true, 
        message: data.message 
      });
    } else {
      res.status(response.status).json({ 
        success: false, 
        message: data.detail || 'Failed to subscribe' 
      });
    }
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error' 
    });
  }
}`,
    },
  ];

  const snippets = generateSnippets(companyId, websiteUrl);

  const handleCopy = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const snippet = snippets.find((s) => s.id === selectedTemplate) || snippets[0];

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader />

      <div className="flex">
        <Sidebar />

        {/* Main Content */}
        <div className="flex-1 p-8">
          <div className="max-w-6xl">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-[#180D39] mb-2">
                Newsletter Subscription
              </h1>
              <p className="text-gray-600">
                Get code snippets to embed subscription forms on your website
              </p>
            </div>

            {/* Important Note - Only show if website URL is not set */}
            {!websiteUrl || websiteUrl === "YOUR_SITE_URL" ? (
              <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-blue-900">
                    Update Your Website URL
                  </h3>
                  <p className="text-sm text-blue-800 mt-1">
                    Make sure to update your website URL in{" "}
                    <a href="/dashboard/profile" className="underline font-medium">
                      profile settings
                    </a>{" "}
                    for origin validation to work correctly.
                  </p>
                </div>
              </div>
            ) : null}

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Sidebar - Template List */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-xl border border-gray-200 p-6 sticky top-8">
                  <h2 className="font-bold text-[#180D39] mb-4">Templates</h2>
                  <div className="space-y-2">
                    {snippets.map((s) => (
                      <button
                        key={s.id}
                        onClick={() => {
                          setSelectedTemplate(s.id);
                          setViewMode("preview");
                        }}
                        className={`w-full text-left px-4 py-3 rounded-lg transition ${
                          selectedTemplate === s.id
                            ? "bg-[#2A8C9D] text-white shadow-lg"
                            : "bg-gray-100 text-gray-900 hover:bg-gray-200"
                        }`}
                      >
                        <div className="font-medium text-sm">{s.name}</div>
                        <div
                          className={`text-xs mt-1 ${
                            selectedTemplate === s.id
                              ? "text-blue-100"
                              : "text-gray-600"
                          }`}
                        >
                          {s.description}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Main Content - Preview & Code */}
              <div className="lg:col-span-3">
                <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-lg">
                  {/* Header with Toggle */}
                  <div className="px-6 py-4 bg-gradient-to-r from-[#180D39] to-[#2A8C9D] text-white">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h2 className="font-bold text-xl">{snippet.name}</h2>
                        <p className="text-blue-100 text-sm mt-1">
                          {snippet.description}
                        </p>
                      </div>
                      <button
                        onClick={() => handleCopy(snippet.code, snippet.id)}
                        className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg flex items-center gap-2 transition border border-white/30"
                      >
                        {copiedId === snippet.id ? (
                          <>
                            <Check className="w-4 h-4" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" />
                            Copy Code
                          </>
                        )}
                      </button>
                    </div>

                    {/* View Mode Toggle */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => setViewMode("preview")}
                        className={`px-4 py-2 rounded-lg font-medium transition ${
                          viewMode === "preview"
                            ? "bg-white text-[#2A8C9D]"
                            : "bg-white/20 text-white hover:bg-white/30"
                        }`}
                      >
                        Preview
                      </button>
                      <button
                        onClick={() => setViewMode("code")}
                        className={`px-4 py-2 rounded-lg font-medium transition ${
                          viewMode === "code"
                            ? "bg-white text-[#2A8C9D]"
                            : "bg-white/20 text-white hover:bg-white/30"
                        }`}
                      >
                        Code
                      </button>
                    </div>
                  </div>

                  {/* Preview Mode */}
                  {viewMode === "preview" && (
                    <div className="p-8 bg-gradient-to-br from-gray-50 to-gray-100 min-h-96 flex items-center justify-center">
                      <div className="w-full max-w-md">
                        {snippet.id === "react" && (
                          <div className="bg-white rounded-xl p-8 shadow-xl border border-gray-200">
                            <div className="text-center mb-6">
                              <div className="w-12 h-12 bg-[#2A8C9D] rounded-full flex items-center justify-center mx-auto mb-4">
                                <Mail className="w-6 h-6 text-white" />
                              </div>
                              <h2 className="text-2xl font-bold text-[#180D39] mb-2">
                                Subscribe
                              </h2>
                              <p className="text-gray-600 text-sm">
                                Get the latest updates delivered to your inbox
                              </p>
                            </div>
                            <div className="space-y-3">
                              <input
                                type="email"
                                placeholder="your@email.com"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2A8C9D]"
                              />
                              <button className="w-full px-4 py-3 bg-[#2A8C9D] text-white rounded-lg font-medium hover:bg-[#1D7A89] transition">
                                Subscribe
                              </button>
                              <p className="text-xs text-gray-500 text-center">
                                We respect your privacy. Unsubscribe at any time.
                              </p>
                            </div>
                          </div>
                        )}

                        {snippet.id === "html" && (
                          <div className="bg-white rounded-xl p-8 shadow-xl border border-gray-200">
                            <div className="text-center mb-6">
                              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Mail className="w-6 h-6 text-white" />
                              </div>
                              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                                Newsletter
                              </h2>
                              <p className="text-gray-600 text-sm">
                                Stay updated with latest news
                              </p>
                            </div>
                            <div className="space-y-3">
                              <input
                                type="email"
                                placeholder="Enter your email"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                              />
                              <button className="w-full px-4 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition">
                                Subscribe
                              </button>
                            </div>
                          </div>
                        )}

                        {snippet.id === "javascript" && (
                          <div className="bg-white rounded-xl p-8 shadow-xl border border-gray-200">
                            <div className="text-center mb-6">
                              <div className="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Mail className="w-6 h-6 text-white" />
                              </div>
                              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                                Join Us
                              </h2>
                              <p className="text-gray-600 text-sm">
                                Sign up for updates
                              </p>
                            </div>
                            <div className="space-y-3">
                              <input
                                type="email"
                                placeholder="your email"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                              />
                              <button className="w-full px-4 py-3 bg-yellow-500 text-white rounded-lg font-medium hover:bg-yellow-600 transition">
                                Subscribe
                              </button>
                            </div>
                          </div>
                        )}

                        {snippet.id === "vue" && (
                          <div className="bg-white rounded-xl p-8 shadow-xl border border-gray-200">
                            <div className="text-center mb-6">
                              <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Mail className="w-6 h-6 text-white" />
                              </div>
                              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                                Subscribe Today
                              </h2>
                              <p className="text-gray-600 text-sm">
                                Never miss an update
                              </p>
                            </div>
                            <div className="space-y-3">
                              <input
                                type="email"
                                placeholder="your@email.com"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                              />
                              <button className="w-full px-4 py-3 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition">
                                Subscribe
                              </button>
                            </div>
                          </div>
                        )}

                        {(snippet.id === "curl" || snippet.id === "nextjs") && (
                          <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-8 text-center">
                            <p className="text-gray-700 font-medium">
                              📝 This template doesn't have a visual preview
                            </p>
                            <p className="text-gray-600 text-sm mt-2">
                              Copy the code and integrate it into your project
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Code Mode */}
                  {viewMode === "code" && (
                    <div className="p-6 bg-gray-900 overflow-x-auto">
                      <pre className="text-sm text-gray-100 font-mono leading-relaxed">
                        <code>{snippet.code}</code>
                      </pre>
                    </div>
                  )}
                </div>

                {/* Additional Info */}
                <div className="mt-6 p-6 bg-white rounded-xl border border-gray-200 shadow-sm">
                  <h3 className="font-bold text-[#180D39] mb-4">
                    📧 Unsubscribe Link for Emails
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Copy this link into your email footer to allow unsubscribing:
                  </p>
                  <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg border border-gray-200 overflow-x-auto">
                    <code className="text-xs text-gray-800 font-mono">
                      {`${websiteUrl}/unsubscribe/${companyId}?email=USER_EMAIL`}
                    </code>
                  </div>
                  <p className="text-xs text-gray-500 mt-3">
                    ℹ️ Replace <code className="bg-gray-100 px-2 py-1 rounded">USER_EMAIL</code> with the actual subscriber's email in your email template.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
