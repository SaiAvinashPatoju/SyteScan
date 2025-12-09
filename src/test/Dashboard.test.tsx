import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { vi } from 'vitest';
import DashboardPage from '@/app/projects/[id]/dashboard/page';
import { apiClient } from '@/lib/api';
import { ProgressResponse, ProjectResponse } from '@/types/project';
import { beforeEach } from 'node:test';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}));

// Mock API client
vi.mock('@/lib/api', () => ({
  apiClient: {
    getProject: vi.fn(),
    getProjectProgress: vi.fn(),
  },
}));

// Mock Recharts components
vi.mock('recharts', () => ({
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
}));

const mockRouter = {
  push: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  refresh: vi.fn(),
  replace: vi.fn(),
};

const mockProjectData: ProjectResponse = {
  id: 'test-project-id',
  name: 'Test Project',
  requirements: ['chair', 'table', 'lamp'],
  created_at: '2024-01-01T00:00:00Z',
};

const mockProgressData: ProgressResponse = {
  project_id: 'test-project-id',
  completion_percentage: 66.67,
  requirement_matches: [
    {
      requirement: 'chair',
      detected: true,
      confidence: 0.92,
      count: 2,
    },
    {
      requirement: 'table',
      detected: true,
      confidence: 0.78,
      count: 1,
    },
    {
      requirement: 'lamp',
      detected: false,
      confidence: null,
      count: 0,
    },
  ],
  detection_summary: {
    total_objects_detected: 3,
    unique_objects: ['chair', 'table'],
    average_confidence: 0.85,
  },
};

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue(mockRouter);
  });

  it('renders loading state initially', () => {
    (apiClient.getProject as any).mockImplementation(() => new Promise(() => {}));
    (apiClient.getProjectProgress as any).mockImplementation(() => new Promise(() => {}));

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('renders dashboard with progress data successfully', async () => {
    (apiClient.getProject as any).mockResolvedValue(mockProjectData);
    (apiClient.getProjectProgress as any).mockResolvedValue(mockProgressData);

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    await waitFor(() => {
      expect(screen.getByText('Progress Dashboard')).toBeInTheDocument();
    });

    // Check project name
    expect(screen.getByText('Test Project')).toBeInTheDocument();

    // Check completion rate
    expect(screen.getByText('66.7%')).toBeInTheDocument();
    expect(screen.getByText('2 of 3 requirements met')).toBeInTheDocument();

    // Check objects detected
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('2 unique types')).toBeInTheDocument();

    // Check average confidence
    expect(screen.getByText('85.0%')).toBeInTheDocument();

    // Check requirements table
    expect(screen.getByText('Requirements Analysis')).toBeInTheDocument();
    expect(screen.getAllByText('✓ Detected')).toHaveLength(2);
    expect(screen.getByText('✗ Not Found')).toBeInTheDocument();
  });

  it('renders error state when API calls fail', async () => {
    const errorMessage = 'Failed to fetch data';
    (apiClient.getProject as any).mockRejectedValue(new Error(errorMessage));
    (apiClient.getProjectProgress as any).mockRejectedValue(new Error(errorMessage));

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    await waitFor(() => {
      expect(screen.getByText('Error Loading Dashboard')).toBeInTheDocument();
    });

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.getByText('Back to Upload')).toBeInTheDocument();
  });

  it('renders empty state when no progress data is available', async () => {
    (apiClient.getProject as any).mockResolvedValue(mockProjectData);
    (apiClient.getProjectProgress as any).mockResolvedValue(null);

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    await waitFor(() => {
      expect(screen.getByText('No Data Available')).toBeInTheDocument();
    });

    expect(screen.getByText('No progress data found for this project. Please upload images first to generate progress analysis.')).toBeInTheDocument();
    expect(screen.getByText('Upload Images')).toBeInTheDocument();
  });

  it('handles navigation correctly', async () => {
    (apiClient.getProject as any).mockResolvedValue(mockProjectData);
    (apiClient.getProjectProgress as any).mockResolvedValue(mockProgressData);

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    await waitFor(() => {
      expect(screen.getByText('Progress Dashboard')).toBeInTheDocument();
    });

    // Test back to upload navigation
    const backToUploadButton = screen.getByText('← Back to Upload');
    fireEvent.click(backToUploadButton);
    expect(mockRouter.push).toHaveBeenCalledWith('/projects/test-project-id/upload');

    // Test back to home navigation
    const backToHomeButton = screen.getByText('Back to Home');
    fireEvent.click(backToHomeButton);
    expect(mockRouter.push).toHaveBeenCalledWith('/');
  });

  it('displays correct requirement statuses', async () => {
    (apiClient.getProject as any).mockResolvedValue(mockProjectData);
    (apiClient.getProjectProgress as any).mockResolvedValue(mockProgressData);

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    await waitFor(() => {
      expect(screen.getByText('Progress Dashboard')).toBeInTheDocument();
    });

    // Check detected requirements
    const detectedBadges = screen.getAllByText('✓ Detected');
    expect(detectedBadges).toHaveLength(2); // chair and table

    // Check not found requirements
    const notFoundBadges = screen.getAllByText('✗ Not Found');
    expect(notFoundBadges).toHaveLength(1); // lamp

    // Check confidence values
    expect(screen.getByText('92.0%')).toBeInTheDocument(); // chair confidence
    expect(screen.getByText('78.0%')).toBeInTheDocument(); // table confidence
  });

  it('displays detection summary correctly', async () => {
    (apiClient.getProject as any).mockResolvedValue(mockProjectData);
    (apiClient.getProjectProgress as any).mockResolvedValue(mockProgressData);

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    await waitFor(() => {
      expect(screen.getByText('Detection Summary')).toBeInTheDocument();
    });

    // Check detected objects tags in the detection summary section
    const detectionSummary = screen.getByText('Detection Summary').closest('div');
    expect(detectionSummary).toBeInTheDocument();

    // Check statistics
    expect(screen.getByText('Total objects detected: 3')).toBeInTheDocument();
    expect(screen.getByText('Unique object types: 2')).toBeInTheDocument();
    expect(screen.getByText('Average confidence: 85.0%')).toBeInTheDocument();
  });

  it('handles zero completion percentage correctly', async () => {
    const zeroProgressData: ProgressResponse = {
      ...mockProgressData,
      completion_percentage: 0,
      requirement_matches: mockProgressData.requirement_matches.map(match => ({
        ...match,
        detected: false,
        confidence: null,
        count: 0,
      })),
      detection_summary: {
        total_objects_detected: 0,
        unique_objects: [],
        average_confidence: 0,
      },
    };

    (apiClient.getProject as any).mockResolvedValue(mockProjectData);
    (apiClient.getProjectProgress as any).mockResolvedValue(zeroProgressData);

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    await waitFor(() => {
      expect(screen.getByText('Progress Dashboard')).toBeInTheDocument();
    });

    expect(screen.getByText('0 of 3 requirements met')).toBeInTheDocument();
    expect(screen.getByText('0 unique types')).toBeInTheDocument();
    
    // All requirements should show as not found
    const notFoundBadges = screen.getAllByText('✗ Not Found');
    expect(notFoundBadges).toHaveLength(3);
  });

  it('handles full completion percentage correctly', async () => {
    const fullProgressData: ProgressResponse = {
      ...mockProgressData,
      completion_percentage: 100,
      requirement_matches: mockProgressData.requirement_matches.map(match => ({
        ...match,
        detected: true,
        confidence: 0.9,
        count: 1,
      })),
    };

    (apiClient.getProject as any).mockResolvedValue(mockProjectData);
    (apiClient.getProjectProgress as any).mockResolvedValue(fullProgressData);

    render(<DashboardPage params={{ id: 'test-project-id' }} />);

    await waitFor(() => {
      expect(screen.getByText('Progress Dashboard')).toBeInTheDocument();
    });

    expect(screen.getByText('3 of 3 requirements met')).toBeInTheDocument();
    
    // All requirements should show as detected
    const detectedBadges = screen.getAllByText('✓ Detected');
    expect(detectedBadges).toHaveLength(3);
  });
});