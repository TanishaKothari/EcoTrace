'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Leaf, Search, Clock, BarChart3, User, LogOut } from 'lucide-react';
import { getUserInfo, isAuthenticated, logoutUser, UserInfo } from '@/utils/userToken';
import AuthModal from './AuthModal';

export default function Navigation() {
  const pathname = usePathname();
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const updateUserInfo = () => {
      const info = getUserInfo();
      setUserInfo(info);
      setAuthenticated(isAuthenticated());
    };

    updateUserInfo();

    // Listen for storage changes (when user logs in/out in another tab)
    window.addEventListener('storage', updateUserInfo);
    return () => window.removeEventListener('storage', updateUserInfo);
  }, []);

  const handleAuthSuccess = () => {
    const info = getUserInfo();
    setUserInfo(info);
    setAuthenticated(isAuthenticated());
  };

  const handleLogout = () => {
    logoutUser();
    setUserInfo(null);
    setAuthenticated(false);
  };

  const navItems = [
    {
      href: '/',
      label: 'Analyze',
      icon: Search,
      description: 'Search and analyze products'
    },
    {
      href: '/history',
      label: 'History',
      icon: Clock,
      description: 'View your eco journey'
    }
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">EcoTrace</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-green-100 text-green-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                  title={item.description}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Authentication Section */}
          <div className="flex items-center space-x-4">
            {/* Stats Badge (optional) */}
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-500">
              <BarChart3 className="w-4 h-4" />
              <span>Real-time Analysis</span>
            </div>

            {/* User Authentication */}
            {authenticated && userInfo ? (
              <div className="flex items-center space-x-3">
                <div className="hidden sm:block text-sm">
                  <span className="text-gray-600">Welcome, </span>
                  <span className="font-medium text-gray-900">
                    {userInfo.name || userInfo.email}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  title="Sign out"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:inline">Sign out</span>
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
              >
                <User className="w-4 h-4" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
      />
    </nav>
  );
}
