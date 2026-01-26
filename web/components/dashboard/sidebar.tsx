"use client";

import Link from "next/link";
import { LayoutDashboard, Mail, Settings, TrendingUp, Users, CreditCard } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    {
      icon: LayoutDashboard,
      label: "Overview",
      href: "/dashboard",
    },
    {
      icon: Mail,
      label: "Campaigns",
      href: "/dashboard/campaigns",
    },
    {
      icon: TrendingUp,
      label: "Templates",
      href: "/dashboard/templates",
    },
    {
      icon: Users,
      label: "Subscribers",
      href: "/dashboard/subscribers",
      submenu: [
        { label: "Manage Subscribers", href: "/dashboard/subscribers" },
        { label: "Code Snippets", href: "/dashboard/subscribers/code-snippets" },
      ],
    },
    {
      icon: CreditCard,
      label: "Billing",
      href: "/dashboard/billing",
    },
    {
      icon: Settings,
      label: "Settings",
      href: "/dashboard/settings",
    },
  ];

  return (
    <aside className="hidden md:flex w-64 bg-[#180D39] text-white flex-col">
      {/* Top Section */}
      <div className="p-6 border-b border-white/10">
        <h2 className="text-lg font-bold">Menu</h2>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const isActive =
            pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                isActive
                  ? "bg-[#2A8C9D] text-white shadow-md"
                  : "text-gray-300 hover:bg-white/10"
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className="p-4 border-t border-white/10">
        <div className="bg-[#2A8C9D]/20 border border-[#2A8C9D]/30 rounded-lg p-4">
          <p className="text-sm text-gray-300 mb-3">Need Help?</p>
          <a
            href="#"
            className="text-sm font-medium text-[#2A8C9D] hover:text-white transition-colors"
          >
            View Documentation →
          </a>
        </div>
      </div>
    </aside>
  );
}
