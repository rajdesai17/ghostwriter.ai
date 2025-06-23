import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { PenTool, ScrollText, Users, BarChart2 } from 'lucide-react';

export function MainLayout() {
  const location = useLocation();
  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="px-6 py-6 space-y-8">
          {/* Logo */}
          <Link to="/generate" className="flex items-center space-x-3">
            <div className="bg-gray-900 p-2 rounded-xl">
              <PenTool className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900 tracking-tight">Ghostwriter</span>
          </Link>

          {/* Navigation */}
          <nav className="space-y-1">
            <SidebarLink
              to="/generate"
              icon={ScrollText}
              label="Generate Posts"
              active={location.pathname.startsWith('/generate')}
            />
            <SidebarLink
              to="/profiles"
              icon={Users}
              label="Voice Profiles"
              active={location.pathname.startsWith('/profiles')}
            />
            <SidebarLink
              to="#"
              icon={BarChart2}
              label="Analytics"
              disabled
            />
          </nav>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 px-6 lg:px-10 py-10">
        <Outlet />
      </main>
    </div>
  );
}

interface SidebarLinkProps {
  to: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  active?: boolean;
  disabled?: boolean;
}

function SidebarLink({ to, icon: Icon, label, active, disabled }: SidebarLinkProps) {
  if (disabled) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm text-gray-400 cursor-not-allowed">
        <Icon className="h-4 w-4" />
        <span>{label}</span>
      </div>
    );
  }
  return (
    <Link
      to={to}
      className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
        active
          ? 'bg-orange-50 text-orange-600 shadow-sm'
          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
      }`}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </Link>
  );
}