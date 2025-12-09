'use client';

import React, { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { ProjectCreateRequest } from '@/types/project';
import { apiClient } from '@/lib/api';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import StatusIndicator from '@/components/ui/StatusIndicator';
import PageTransition from '@/components/ui/PageTransition';

interface ProjectFormProps {
  onSuccess: (projectId: string) => void;
  onError?: (error: string) => void;
}

interface FormData {
  name: string;
  requirements: { value: string }[];
}

export default function ProjectForm({ onSuccess, onError }: ProjectFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { handleError, handleSuccess } = useErrorHandler();

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    defaultValues: {
      name: '',
      requirements: [{ value: '' }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'requirements',
  });

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);

    try {
      // Filter out empty requirements and trim whitespace
      const requirements = data.requirements
        .map(req => req.value.trim())
        .filter(req => req.length > 0);

      if (requirements.length === 0) {
        throw new Error('At least one requirement is needed');
      }

      const projectData: ProjectCreateRequest = {
        name: data.name.trim(),
        requirements,
      };

      const response = await apiClient.createProject(projectData);
      
      // Reset form on success
      reset();
      
      // Show success message
      handleSuccess('Project created successfully!');
      
      // Call success callback
      onSuccess(response.id);
      
    } catch (error) {
      const apiError = handleError(error);
      onError?.(apiError.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addRequirement = () => {
    append({ value: '' });
  };

  const removeRequirement = (index: number) => {
    if (fields.length > 1) {
      remove(index);
    }
  };

  return (
    <PageTransition>
      <div className="card max-w-2xl mx-auto p-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-syte-black mb-2">Create New Project</h2>
          <p className="text-syte-gray-600">Set up your construction project with requirements for AI analysis</p>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Project Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-syte-black mb-2">
            Project Name *
          </label>
          <input
            type="text"
            id="name"
            {...register('name', {
              required: 'Project name is required',
              minLength: {
                value: 1,
                message: 'Project name cannot be empty',
              },
              maxLength: {
                value: 255,
                message: 'Project name cannot exceed 255 characters',
              },
            })}
            className={`input-field ${
              errors.name ? 'border-red-500 focus:ring-red-500' : ''
            }`}
            placeholder="Enter project name"
            disabled={isSubmitting}
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        {/* Requirements */}
        <div>
          <label className="block text-sm font-medium text-syte-black mb-2">
            Requirements *
          </label>
          <p className="text-sm text-syte-gray-600 mb-4">
            Add objects that should be detected in room images (e.g., chair, table, lamp, sofa, window)
          </p>
          
          <div className="space-y-3">
            {fields.map((field, index) => (
              <div key={field.id} className="flex items-center space-x-2">
                <input
                  type="text"
                  {...register(`requirements.${index}.value`, {
                    required: index === 0 ? 'At least one requirement is needed' : false,
                  })}
                  className={`input-field flex-1 ${
                    errors.requirements?.[index]?.value ? 'border-red-500 focus:ring-red-500' : ''
                  }`}
                  placeholder="Enter object name (e.g., chair, table)"
                  disabled={isSubmitting}
                />
                
                {fields.length > 1 && index > 0 && (
                  <button
                    type="button"
                    onClick={() => removeRequirement(index)}
                    className="px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                    disabled={isSubmitting}
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
              </div>
            ))}
            
            {fields.map((field, index) => (
              errors.requirements?.[index]?.value && (
                <p key={`error-${field.id}`} className="text-sm text-red-600">
                  {errors.requirements[index]?.value?.message}
                </p>
              )
            ))}
          </div>

          <button
            type="button"
            onClick={addRequirement}
            className="mt-4 flex items-center px-4 py-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isSubmitting}
          >
            <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add Another Requirement
          </button>
        </div>

        {/* Status Indicator */}
        {isSubmitting && (
          <StatusIndicator 
            status="loading" 
            message="Creating your project..." 
            className="animate-fade-in"
          />
        )}

        {/* Submit Button */}
        <div className="flex justify-end space-x-4 pt-6 border-t border-syte-gray-200">
          <button
            type="button"
            onClick={() => reset()}
            className="btn-outline"
            disabled={isSubmitting}
          >
            Reset Form
          </button>
          
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary flex items-center space-x-2"
          >
            {isSubmitting && <LoadingSpinner size="sm" color="white" />}
            <span>{isSubmitting ? 'Creating Project...' : 'Create Project'}</span>
          </button>
        </div>
      </form>
      </div>
    </PageTransition>
  );
}