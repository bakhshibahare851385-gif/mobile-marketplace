import { describe, expect, it } from 'vitest'

import html from '../../index.html?raw'

describe('document direction', () => {
  it('declares Persian as the document language', () => {
    expect(html).toContain('lang="fa"')
  })

  it('declares right-to-left layout', () => {
    expect(html).toContain('dir="rtl"')
  })

  it('uses a Persian document title', () => {
    expect(html).not.toContain('Mobile Accessories Marketplace')
  })
})
