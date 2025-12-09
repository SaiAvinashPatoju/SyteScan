'use client';

import { useCallback } from 'react';
import { toast } from 'react-hot-toast';

export interface ApiError {
  error: string;
  message: string;
  status_code: number;
  details?: Record<string, any>;
  request_id?: string;
}

export const useErrorHandler = () => {
  const handleError = useCallback((error: any) => {
    console.error('Error occurred:', error);

    // Handle API errors with structured format
    if (error?.response?.data) {
      const apiError: ApiError = error.response.data;
      
      // Show user-friendly error message
      toast.error(apiError.message || 'An error occurred');
      
      // Log detailed error for debugging
      console.error('API Error:', {
        error: apiError.error,
        message: apiError.message,
        status_code: apiError.status_code,
        details: apiError.details,
        request_id: apiError.request_id
      });
      
      return apiError;
    }
    
    // Handle network errors
    if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error')) {
      toast.error('Network error. Please check your connection and try again.');
      return { error: 'NetworkError', message: 'Network connection failed', status_code: 0 };
    }
    
    // Handle timeout errors
    if (error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
      toast.error('Request timed out. Please try again.');
      return { error: 'TimeoutError', message: 'Request timed out', status_code: 0 };
    }
    
    // Handle generic errors
    const message = error?.message || 'An unexpected error occurred';
    toast.error(message);
    
    return { error: 'UnknownError', message, status_code: 500 };
  }, []);

  const handleSuccess = useCallback((message: string) => {
    toast.success(message);
  }, []);

  return { handleError, handleSuccess };
};

export default useErrorHandler;