"use client";

import { DashboardHeader } from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Suspense } from "react";
import { BillingContent } from "@/components/billing/billing-content";

export default function BillingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader />

      <div className="flex">
        <Sidebar />

        <main className="flex-1">
          <Suspense fallback={<div className="p-6 lg:p-8">Loading...</div>}>
            <BillingContent />
          </Suspense>
        </main>
      </div>
    </div>
  );
}
