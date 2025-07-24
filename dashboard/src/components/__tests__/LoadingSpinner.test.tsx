import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { LoadingSpinner } from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders loading spinner', () => {
    render(<LoadingSpinner />)
    
    const container = screen.getByTestId('loading-spinner')
    expect(container).toBeInTheDocument()
    expect(container).toHaveClass('flex', 'items-center', 'justify-center')
  })

  it('applies custom className', () => {
    render(<LoadingSpinner className="custom-class" />)
    
    const container = screen.getByTestId('loading-spinner')
    expect(container).toHaveClass('custom-class')
  })
}) 