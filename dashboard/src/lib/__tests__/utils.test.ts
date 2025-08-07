import { describe, it, expect } from 'vitest'
import { cn } from '../utils'

describe('cn utility', () => {
  it('combines class names', () => {
    const result = cn('class1', 'class2')
    expect(result).toBe('class1 class2')
  })

  it('handles conditional classes', () => {
    const showClass = true
    const hideClass = false
    const result = cn('base', showClass && 'show', hideClass && 'hide')
    expect(result).toBe('base show')
  })
}) 