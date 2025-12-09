'use client';

import React from 'react';
import LoadingSpinner from './LoadingSpinner';

export type StatusType = 'idle' | 'loading' | 'success' | 'error';

interface StatusIndicatorProps {
  status: StatusType;
  message?: string;
  className?: string;
  showIcon?: boolean;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  message,
  className = '',
  showIcon = true
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'loading':
        return {
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          icon: <LoadingSpinner size="sm" color="blue" />
        };
      case 'success':
        return {
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          icon: (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )
        };
      case 'error':
        return {
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          icon: (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )
        };
      default:
        return {
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          icon: null
        };
    }
  };

  const config = getStatusConfig();

  if (status === 'idle' && !message) {
    return null;
  }

  return (
    <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg border ${config.bgColor} ${config.borderColor} ${className}`}>
      {showIcon && config.icon && (
        <div className={config.color}>
          {config.icon}
        </div>
      )}
      {message && (
        <span className={`text-sm font-medium ${config.color}`}>
          {message}
        </span>
      )}
    </div>
  );
};

export default StatusIndicator;