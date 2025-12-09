'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import ProjectForm from '@/components/ProjectForm';
import WorkflowStepper, { Step } from '@/components/ui/WorkflowStepper';
import StatusIndicator from '@/components/ui/StatusIndicator';
import PageTransition from '@/components/ui/PageTransition';

export default function NewProjectPage() {
  const router = useRouter();
  const [isRedirecting, setIsRedirecting] = useState(false);

  const steps: Step[] = [
    {
      id: 'project-setup',
      title: 'Project Setup',
      description: 'Create project',
      status: 'current'
    },
    {
      id: 'image-upload',
      title: 'Image Upload',
      description: 'Upload room images',
      status: 'upcoming'
    },
    {
      id: 'analysis',
      title: 'AI Analysis',
      description: 'Object detection',
      status: 'upcoming'
    },
    {
      id: 'results',
      title: 'Results',
      description: 'View progress',
      status: 'upcoming'
    }
  ];

  const handleSuccess = (projectId: string) => {
    console.log('Project created successfully, redirecting to:', `/projects/${projectId}/upload`);
    setIsRedirecting(true);
    
    // Redirect to upload page after a short delay
    setTimeout(() => {
      router.push(`/projects/${projectId}/upload`);
    }, 1000);
  };

  const handleError = (error: string) => {
    console.error('Project creation error:', error);
  };

  return (
    <div className="page-container">
      <div className="content-container">
        {/* Header */}
        <PageTransition>
          <div className="section-header">
            <h1 className="text-4xl font-bold text-syte-black mb-2">
              SyteScan Progress Analyzer
            </h1>
            <p className="text-xl text-syte-gray-600">
              Create a new project to track construction progress with AI
            </p>
          </div>
        </PageTransition>

        {/* Workflow Stepper */}
        <PageTransition className="mb-12">
          <WorkflowStepper steps={steps} />
        </PageTransition>

        {/* Redirect Status */}
        {isRedirecting && (
          <div className="mb-8 flex justify-center">
            <StatusIndicator 
              status="success" 
              message="Project created! Redirecting to image upload..." 
              className="animate-fade-in"
            />
          </div>
        )}

        {/* Project Form */}
        <ProjectForm onSuccess={handleSuccess} onError={handleError} />

        {/* Navigation */}
        <div className="mt-12 text-center">
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center text-syte-gray-600 hover:text-syte-black transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg px-3 py-2"
          >
            <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}