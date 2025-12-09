'use client';

import React from 'react';

export interface Step {
  id: string;
  title: string;
  description?: string;
  status: 'completed' | 'current' | 'upcoming';
}

interface WorkflowStepperProps {
  steps: Step[];
  className?: string;
}

export const WorkflowStepper: React.FC<WorkflowStepperProps> = ({
  steps,
  className = ''
}) => {
  return (
    <nav className={`mb-8 ${className}`} aria-label="Progress">
      <ol className="flex items-center justify-center space-x-4 md:space-x-8">
        {steps.map((step, stepIdx) => (
          <li key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              {/* Step Circle */}
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-300 ${
                  step.status === 'completed'
                    ? 'bg-blue-600 border-blue-600 text-white'
                    : step.status === 'current'
                    ? 'bg-blue-50 border-blue-600 text-blue-600'
                    : 'bg-white border-syte-gray-300 text-syte-gray-400'
                }`}
              >
                {step.status === 'completed' ? (
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <span className="text-sm font-medium">{stepIdx + 1}</span>
                )}
              </div>
              
              {/* Step Label */}
              <div className="mt-2 text-center">
                <p
                  className={`text-sm font-medium transition-colors duration-300 ${
                    step.status === 'current'
                      ? 'text-blue-600'
                      : step.status === 'completed'
                      ? 'text-syte-gray-700'
                      : 'text-syte-gray-400'
                  }`}
                >
                  {step.title}
                </p>
                {step.description && (
                  <p className="text-xs text-syte-gray-500 mt-1 max-w-24">
                    {step.description}
                  </p>
                )}
              </div>
            </div>
            
            {/* Connector Line */}
            {stepIdx < steps.length - 1 && (
              <div
                className={`ml-4 h-0.5 w-12 md:w-16 transition-colors duration-300 ${
                  steps[stepIdx + 1].status === 'completed' || step.status === 'completed'
                    ? 'bg-blue-600'
                    : 'bg-syte-gray-300'
                }`}
              />
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default WorkflowStepper;