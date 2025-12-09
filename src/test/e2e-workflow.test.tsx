import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import ProjectForm from '@/components/ProjectForm'
import ImageUpload from '@/components/ImageUpload'
import Dashboard from '@/app/projects/[id]/dashboard/page'

// Mock the API module
vi.mock('@/lib/api', () => ({
  createProject: vi.fn(),
  uploadImages: vi.fn(),
  getProjectProgress: vi.fn(),
  getProject: vi.fn()
}))

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn()
  }),
  useParams: () => ({ id: 'test-project-id' })
}))

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn()
  }
}))

import { createProject, uploadImages, getProjectProgress, getProject } from '@/lib/api'

const mockCreateProject = createProject as any
const mockUploadImages = uploadImages as any
const mockGetProjectProgress = getProjectProgress as any
const mockGetProject = getProject as any

describe('End-to-End Workflow Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Project Creation Workflow', () => {
    it('should create a project with requirements', async () => {
      const mockProject = {
        id: 'test-project-id',
        name: 'Test Project',
        requirements: ['chair', 'table', 'window'],
        created_at: new Date().toISOString()
      }

      mockCreateProject.mockResolvedValue(mockProject)

      render(<ProjectForm />)

      // Fill in project name
      const nameInput = screen.getByLabelText(/project name/i)
      fireEvent.change(nameInput, { target: { value: 'Test Project' } })

      // Add requirements
      const requirementInput = screen.getByLabelText(/add requirement/i)
      const addButton = screen.getByRole('button', { name: /add requirement/i })

      fireEvent.change(requirementInput, { target: { value: 'chair' } })
      fireEvent.click(addButton)

      fireEvent.change(requirementInput, { target: { value: 'table' } })
      fireEvent.click(addButton)

      fireEvent.change(requirementInput, { target: { value: 'window' } })
      fireEvent.click(addButton)

      // Submit form
      const submitButton = screen.getByRole('button', { name: /create project/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockCreateProject).toHaveBeenCalledWith({
          name: 'Test Project',
          requirements: ['chair', 'table', 'window']
        })
      })
    })

    it('should handle project creation errors', async () => {
      mockCreateProject.mockRejectedValue(new Error('Project creation failed'))

      render(<ProjectForm />)

      const nameInput = screen.getByLabelText(/project name/i)
      fireEvent.change(nameInput, { target: { value: 'Test Project' } })

      const submitButton = screen.getByRole('button', { name: /create project/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockCreateProject).toHaveBeenCalled()
      })

      // Should show error message
      expect(screen.getByText(/failed to create project/i)).toBeInTheDocument()
    })
  })

  describe('Image Upload Workflow', () => {
    it('should upload images and process them', async () => {
      const mockUploadResult = {
        uploaded_files: ['image1.jpg', 'image2.jpg'],
        detection_results: [
          {
            image_path: 'image1.jpg',
            detected_objects: [
              { name: 'chair', confidence: 0.85, bbox: [10, 10, 50, 50] }
            ]
          },
          {
            image_path: 'image2.jpg',
            detected_objects: [
              { name: 'table', confidence: 0.92, bbox: [20, 20, 60, 60] }
            ]
          }
        ]
      }

      mockUploadImages.mockResolvedValue(mockUploadResult)

      render(<ImageUpload projectId="test-project-id" />)

      // Create mock files
      const file1 = new File(['test'], 'test1.jpg', { type: 'image/jpeg' })
      const file2 = new File(['test'], 'test2.jpg', { type: 'image/jpeg' })

      const fileInput = screen.getByLabelText(/upload images/i)
      
      // Simulate file selection
      Object.defineProperty(fileInput, 'files', {
        value: [file1, file2],
        writable: false,
      })

      fireEvent.change(fileInput)

      // Click upload button
      const uploadButton = screen.getByRole('button', { name: /upload images/i })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(mockUploadImages).toHaveBeenCalledWith('test-project-id', [file1, file2])
      })

      // Should show success message
      await waitFor(() => {
        expect(screen.getByText(/images uploaded successfully/i)).toBeInTheDocument()
      })
    })

    it('should handle upload errors', async () => {
      mockUploadImages.mockRejectedValue(new Error('Upload failed'))

      render(<ImageUpload projectId="test-project-id" />)

      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const fileInput = screen.getByLabelText(/upload images/i)
      
      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      const uploadButton = screen.getByRole('button', { name: /upload images/i })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(screen.getByText(/upload failed/i)).toBeInTheDocument()
      })
    })

    it('should validate file types', async () => {
      render(<ImageUpload projectId="test-project-id" />)

      // Try to upload invalid file type
      const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' })
      const fileInput = screen.getByLabelText(/upload images/i)
      
      Object.defineProperty(fileInput, 'files', {
        value: [invalidFile],
        writable: false,
      })

      fireEvent.change(fileInput)

      // Should show validation error
      await waitFor(() => {
        expect(screen.getByText(/only jpeg and png files are allowed/i)).toBeInTheDocument()
      })
    })
  })

  describe('Dashboard Workflow', () => {
    it('should display project progress', async () => {
      const mockProject = {
        id: 'test-project-id',
        name: 'Test Project',
        requirements: ['chair', 'table', 'window'],
        created_at: new Date().toISOString()
      }

      const mockProgress = {
        project_id: 'test-project-id',
        completion_percentage: 75.5,
        requirement_matches: [
          {
            requirement: 'chair',
            detected: true,
            confidence: 0.85,
            count: 2
          },
          {
            requirement: 'table',
            detected: true,
            confidence: 0.92,
            count: 1
          },
          {
            requirement: 'window',
            detected: false,
            confidence: 0,
            count: 0
          }
        ],
        detection_summary: {
          total_objects: 15,
          unique_objects: 8,
          avg_confidence: 0.78
        }
      }

      mockGetProject.mockResolvedValue(mockProject)
      mockGetProjectProgress.mockResolvedValue(mockProgress)

      render(<Dashboard params={{ id: 'test-project-id' }} />)

      await waitFor(() => {
        expect(mockGetProject).toHaveBeenCalledWith('test-project-id')
        expect(mockGetProjectProgress).toHaveBeenCalledWith('test-project-id')
      })

      // Should display project name
      expect(screen.getByText('Test Project')).toBeInTheDocument()

      // Should display completion percentage
      expect(screen.getByText('75.5%')).toBeInTheDocument()

      // Should display requirement matches
      expect(screen.getByText('chair')).toBeInTheDocument()
      expect(screen.getByText('table')).toBeInTheDocument()
      expect(screen.getByText('window')).toBeInTheDocument()

      // Should show detected status
      expect(screen.getAllByText(/detected/i)).toHaveLength(2)
      expect(screen.getByText(/not detected/i)).toBeInTheDocument()
    })

    it('should handle dashboard loading errors', async () => {
      mockGetProject.mockRejectedValue(new Error('Project not found'))
      mockGetProjectProgress.mockRejectedValue(new Error('Progress not found'))

      render(<Dashboard params={{ id: 'test-project-id' }} />)

      await waitFor(() => {
        expect(screen.getByText(/failed to load project data/i)).toBeInTheDocument()
      })
    })

    it('should display empty state when no data', async () => {
      const mockProject = {
        id: 'test-project-id',
        name: 'Empty Project',
        requirements: [],
        created_at: new Date().toISOString()
      }

      const mockProgress = {
        project_id: 'test-project-id',
        completion_percentage: 0,
        requirement_matches: [],
        detection_summary: {
          total_objects: 0,
          unique_objects: 0,
          avg_confidence: 0
        }
      }

      mockGetProject.mockResolvedValue(mockProject)
      mockGetProjectProgress.mockResolvedValue(mockProgress)

      render(<Dashboard params={{ id: 'test-project-id' }} />)

      await waitFor(() => {
        expect(screen.getByText(/no requirements defined/i)).toBeInTheDocument()
      })
    })
  })

  describe('Complete User Journey', () => {
    it('should complete full workflow from project creation to dashboard', async () => {
      // This test simulates the complete user journey
      // In a real e2e test, this would navigate between actual pages
      
      const mockProject = {
        id: 'test-project-id',
        name: 'Complete Test Project',
        requirements: ['chair', 'table'],
        created_at: new Date().toISOString()
      }

      const mockUploadResult = {
        uploaded_files: ['image1.jpg'],
        detection_results: [
          {
            image_path: 'image1.jpg',
            detected_objects: [
              { name: 'chair', confidence: 0.85, bbox: [10, 10, 50, 50] }
            ]
          }
        ]
      }

      const mockProgress = {
        project_id: 'test-project-id',
        completion_percentage: 50,
        requirement_matches: [
          {
            requirement: 'chair',
            detected: true,
            confidence: 0.85,
            count: 1
          },
          {
            requirement: 'table',
            detected: false,
            confidence: 0,
            count: 0
          }
        ],
        detection_summary: {
          total_objects: 1,
          unique_objects: 1,
          avg_confidence: 0.85
        }
      }

      mockCreateProject.mockResolvedValue(mockProject)
      mockUploadImages.mockResolvedValue(mockUploadResult)
      mockGetProject.mockResolvedValue(mockProject)
      mockGetProjectProgress.mockResolvedValue(mockProgress)

      // Step 1: Create project
      const { rerender } = render(<ProjectForm />)
      
      const nameInput = screen.getByLabelText(/project name/i)
      fireEvent.change(nameInput, { target: { value: 'Complete Test Project' } })

      const requirementInput = screen.getByLabelText(/add requirement/i)
      const addButton = screen.getByRole('button', { name: /add requirement/i })

      fireEvent.change(requirementInput, { target: { value: 'chair' } })
      fireEvent.click(addButton)

      fireEvent.change(requirementInput, { target: { value: 'table' } })
      fireEvent.click(addButton)

      const submitButton = screen.getByRole('button', { name: /create project/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockCreateProject).toHaveBeenCalled()
      })

      // Step 2: Upload images
      rerender(<ImageUpload projectId="test-project-id" />)

      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const fileInput = screen.getByLabelText(/upload images/i)
      
      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(fileInput)

      const uploadButton = screen.getByRole('button', { name: /upload images/i })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(mockUploadImages).toHaveBeenCalled()
      })

      // Step 3: View dashboard
      rerender(<Dashboard params={{ id: 'test-project-id' }} />)

      await waitFor(() => {
        expect(mockGetProject).toHaveBeenCalled()
        expect(mockGetProjectProgress).toHaveBeenCalled()
      })

      // Verify final state
      expect(screen.getByText('Complete Test Project')).toBeInTheDocument()
      expect(screen.getByText('50%')).toBeInTheDocument()
    })
  })
})