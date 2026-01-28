"use client";

import { RazorpayCheckout } from "@/components/billing/razorpay-checkout";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export function BillingContent() {
  const searchParams = useSearchParams();
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  useEffect(() => {
    if (searchParams.get("status") === "success") {
      setPaymentSuccess(true);
      // Clear the status from URL
      window.history.replaceState({}, document.title, "/dashboard/billing");
    }
  }, [searchParams]);

  return (
    <div className="p-6 lg:p-8">
      <div className="mb-8">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 text-[#2A8C9D] hover:text-[#1D7A89] mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Overview
        </Link>
        <h1 className="text-3xl font-bold text-[#180D39]">Billing & Subscriptions</h1>
        <p className="text-gray-600 mt-2">Manage your plan, invoices, and billing information</p>
      </div>

      {/* Success Message */}
      {paymentSuccess && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 text-green-700">
          <h3 className="font-semibold mb-1">Payment Successful!</h3>
          <p>Your premium subscription has been activated. You now have access to all premium features.</p>
        </div>
      )}

      {/* Razorpay Checkout Component */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RazorpayCheckout />
        </div>

        {/* Billing Info Sidebar */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Need Help?</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <p>• Payment issues? Contact our support team</p>
              <p>• Questions about plans? Check our pricing page</p>
              <p>• Want a refund? We offer 30-day money-back guarantee</p>
            </div>
          </div>

          <div className="bg-gradient-to-br from-teal-50 to-blue-50 border border-teal-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-teal-900 mb-3">Pro Tips</h3>
            <ul className="space-y-2 text-sm text-teal-800">
              <li>✓ Upgrade anytime, cancel anytime</li>
              <li>✓ All features included, no hidden fees</li>
              <li>✓ Premium support with every subscription</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
