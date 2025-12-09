import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Home from '@/app/page'

// Mock Next.js router
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('Home Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the main heading', () => {
    render(<Home />)
    expect(screen.getByText('SyteScan')).toBeInTheDocument()
    expect(screen.getByText('AI-powered construction progress tracking platform')).toBeInTheDocument()
  })

  it('renders module cards', () => {
    render(<Home />)
    expect(screen.getByText('Progress Analyzer')).toBeInTheDocument()
    expect(screen.getByText('Floor Plan Generation')).toBeInTheDocument()
    expect(screen.getByText('Interior Designer')).toBeInTheDocument()
  })
})