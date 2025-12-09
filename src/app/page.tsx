'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function Home() {
  const router = useRouter();
  const [navigating, setNavigating] = useState<string | null>(null);

  const modules = [
    {
      id: 'progress-analyzer',
      name: 'Progress Analyzer',
      description: 'Track construction progress using AI-powered object detection',
      status: 'active' as const,
      route: '/projects/new',
      icon: (
        <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      id: 'floor-plan-generation',
      name: 'Floor Plan Generation',
      description: 'Generate architectural floor plans automatically',
      status: 'coming-soon' as const,
      route: '#',
      icon: (
        <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
    },
    {
      id: 'interior-designer',
      name: 'Interior Designer',
      description: 'AI-powered interior design recommendations',
      status: 'coming-soon' as const,
      route: '#',
      icon: (
        <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z" />
        </svg>
      ),
    },
  ];

  const handleModuleClick = async (module: typeof modules[0]) => {
    if (module.status === 'active') {
      setNavigating(module.id);
      // Add a small delay for smooth transition
      await new Promise(resolve => setTimeout(resolve, 300));
      router.push(module.route);
    }
  };

  return (
    <div className="page-container animate-fade-in">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-syte-gray-200 sticky top-0 z-10">
        <div className="content-container py-6">
          <div className="animate-slide-down">
            <h1 className="text-4xl font-bold text-syte-black mb-2">
              SyteScan
            </h1>
            <p className="text-lg text-syte-gray-600">
              AI-powered construction progress tracking platform
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="content-container">
        <div className="section-header animate-slide-up">
          <h2 className="section-title">
            Choose Your Module
          </h2>
          <p className="section-subtitle">
            Select from our suite of construction and design tools to streamline your workflow
          </p>
        </div>

        {/* Module Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {modules.map((module, index) => (
            <div
              key={module.id}
              className={`card relative transition-all duration-300 animate-slide-up ${
                module.status === 'active'
                  ? 'hover:shadow-2xl cursor-pointer transform hover:-translate-y-2 hover:scale-105'
                  : 'cursor-not-allowed opacity-75'
              }`}
              style={{ animationDelay: `${index * 100}ms` }}
              onClick={() => handleModuleClick(module)}
            >
              <div className="p-8">
                {/* Status Badge */}
                <div className="absolute top-4 right-4">
                  {module.status === 'active' ? (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                      Active
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-royal-cream-200 text-royal-cream-800 border border-royal-cream-300">
                      Coming Soon
                    </span>
                  )}
                </div>

                {/* Module Icon */}
                <div className={`mb-6 transition-colors duration-200 ${
                  module.status === 'active' 
                    ? 'text-blue-600' 
                    : 'text-syte-gray-400'
                }`}>
                  {module.icon}
                </div>

                {/* Module Content */}
                <h3 className="text-xl font-bold text-syte-black mb-3">
                  {module.name}
                </h3>
                <p className="text-syte-gray-600 mb-6 leading-relaxed">
                  {module.description}
                </p>

                {/* Action Button */}
                {module.status === 'active' ? (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-blue-600 font-medium group">
                      Get Started
                      <svg 
                        className="ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" 
                        fill="none" 
                        viewBox="0 0 24 24" 
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                    {navigating === module.id && (
                      <LoadingSpinner size="sm" color="blue" />
                    )}
                  </div>
                ) : (
                  <div className="text-syte-gray-400 font-medium">
                    Coming Soon
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer Info */}
        <div className="mt-16 text-center animate-fade-in">
          <div className="bg-white/60 backdrop-blur-sm rounded-lg p-6 border border-syte-gray-200 max-w-2xl mx-auto">
            <p className="text-syte-gray-600 leading-relaxed">
              Start with the <span className="font-semibold text-blue-600">Progress Analyzer</span> to track your construction project progress using AI-powered object detection.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}