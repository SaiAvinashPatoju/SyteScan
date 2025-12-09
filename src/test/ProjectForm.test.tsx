import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import ProjectForm from '@/components/ProjectForm';
import { apiClient } from '@/lib/api';
import { beforeEach } from 'node:test';

// Mock the API client
vi.mock('@/lib/api', () => ({
  apiClient: {
    createProject: vi.fn(),
  },
}));

const mockApiClient = apiClient as any;

describe('ProjectForm', () => {
  const mockOnSuccess = vi.fn();
  const mockOnError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form elements correctly', () => {
    render(<ProjectForm onSuccess={mockOnSuccess} onError={mockOnError} />);

    expect(screen.getByText('Create New Project')).toBeInTheDocument();
    expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
    expect(screen.getByText(/requirements/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create project/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    render(<ProjectForm onSuccess={mockOnSuccess} onError={mockOnError} />);

    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Project name is required')).toBeInTheDocument();
    });
  });

  it('allows adding and removing requirements', () => {
    render(<ProjectForm onSuccess={mockOnSuccess} onError={mockOnError} />);

    // Initially should have one requirement field
    expect(screen.getAllByPlaceholderText(/enter object name/i)).toHaveLength(1);

    // Add another requirement
    const addButton = screen.getByRole('button', { name: /add another requirement/i });
    fireEvent.click(addButton);

    expect(screen.getAllByPlaceholderText(/enter object name/i)).toHaveLength(2);

    // Remove button should appear only for the second field
    const removeButtons = screen.getAllByText('Remove');
    expect(removeButtons).toHaveLength(1);

    // Remove a requirement
    fireEvent.click(removeButtons[0]);
    expect(screen.getAllByPlaceholderText(/enter object name/i)).toHaveLength(1);
    
    // After removing, no remove buttons should be visible (only 1 field left)
    expect(screen.queryByText('Remove')).not.toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    const mockResponse = {
      id: 'test-project-id',
      name: 'Test Project',
      requirements: ['chair', 'table'],
      created_at: '2023-01-01T00:00:00Z',
    };

    mockApiClient.createProject.mockResolvedValue(mockResponse);

    render(<ProjectForm onSuccess={mockOnSuccess} onError={mockOnError} />);

    // Fill in the form
    const nameInput = screen.getByLabelText(/project name/i);
    const requirementInput = screen.getAllByPlaceholderText(/enter object name/i)[0];

    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    fireEvent.change(requirementInput, { target: { value: 'chair' } });

    // Add another requirement
    const addButton = screen.getByRole('button', { name: /add another requirement/i });
    fireEvent.click(addButton);

    const secondRequirementInput = screen.getAllByPlaceholderText(/enter object name/i)[1];
    fireEvent.change(secondRequirementInput, { target: { value: 'table' } });

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApiClient.createProject).toHaveBeenCalledWith({
        name: 'Test Project',
        requirements: ['chair', 'table'],
      });
      expect(mockOnSuccess).toHaveBeenCalledWith('test-project-id');
    });
  });

  it('handles API errors gracefully', async () => {
    const errorMessage = 'Failed to create project';
    mockApiClient.createProject.mockRejectedValue(new Error(errorMessage));

    render(<ProjectForm onSuccess={mockOnSuccess} onError={mockOnError} />);

    // Fill in the form
    const nameInput = screen.getByLabelText(/project name/i);
    const requirementInput = screen.getAllByPlaceholderText(/enter object name/i)[0];

    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    fireEvent.change(requirementInput, { target: { value: 'chair' } });

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
      expect(mockOnError).toHaveBeenCalledWith(errorMessage);
    });
  });

  it('filters out empty requirements', async () => {
    const mockResponse = {
      id: 'test-project-id',
      name: 'Test Project',
      requirements: ['chair'],
      created_at: '2023-01-01T00:00:00Z',
    };

    mockApiClient.createProject.mockResolvedValue(mockResponse);

    render(<ProjectForm onSuccess={mockOnSuccess} onError={mockOnError} />);

    // Fill in the form with some empty requirements
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });

    // Add multiple requirements, some empty
    const addButton = screen.getByRole('button', { name: /add another requirement/i });
    fireEvent.click(addButton);
    fireEvent.click(addButton);

    const requirementInputs = screen.getAllByPlaceholderText(/enter object name/i);
    fireEvent.change(requirementInputs[0], { target: { value: 'chair' } });
    fireEvent.change(requirementInputs[1], { target: { value: '   ' } }); // Whitespace only
    fireEvent.change(requirementInputs[2], { target: { value: '' } }); // Empty

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApiClient.createProject).toHaveBeenCalledWith({
        name: 'Test Project',
        requirements: ['chair'], // Only non-empty requirement
      });
    });
  });

  it('shows error when no valid requirements provided', async () => {
    render(<ProjectForm onSuccess={mockOnSuccess} onError={mockOnError} />);

    // Fill in name but leave requirements empty
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });

    const requirementInput = screen.getAllByPlaceholderText(/enter object name/i)[0];
    fireEvent.change(requirementInput, { target: { value: '   ' } }); // Whitespace only

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('At least one requirement is needed')).toBeInTheDocument();
    });
  });

  it('disables form during submission', async () => {
    // Mock a slow API response
    mockApiClient.createProject.mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 1000))
    );

    render(<ProjectForm onSuccess={mockOnSuccess} onError={mockOnError} />);

    // Fill in the form
    const nameInput = screen.getByLabelText(/project name/i);
    const requirementInput = screen.getAllByPlaceholderText(/enter object name/i)[0];

    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    fireEvent.change(requirementInput, { target: { value: 'chair' } });

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);

    // Form should be disabled during submission
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /creating.../i })).toBeInTheDocument();
      expect(nameInput).toBeDisabled();
      expect(requirementInput).toBeDisabled();
    });
  });
});