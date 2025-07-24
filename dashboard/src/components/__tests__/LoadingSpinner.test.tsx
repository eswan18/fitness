import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { LoadingSpinner } from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders loading spinner', () => {
    render(<LoadingSpinner />)
    
    // Check for the loader icon (lucide-react icon)
    const spinner = screen.getByText((_, element) => {
      return element?.tagName.toLowerCase() === 'svg'
    })
    expect(spinner).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<LoadingSpinner className="custom-class" />)
    
    expect(container.firstChild).toHaveClass('custom-class')
  })
}) 