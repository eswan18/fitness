import { describe, it, expect } from 'vitest'
import { cn } from '../utils'

describe('cn utility', () => {
  it('combines class names', () => {
    const result = cn('class1', 'class2')
    expect(result).toBe('class1 class2')
  })

  it('handles conditional classes', () => {
    const result = cn('base', true && 'show', false && 'hide')
    expect(result).toBe('base show')
  })
}) 