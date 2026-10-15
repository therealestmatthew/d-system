import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import ide from '../../../layouts/ide.json'
import focus from '../../../layouts/focus.json'
import { AppShell } from './AppShell'

describe('AppShell', () => {
  it('renders the shell with data-layout and one landmark per region', () => {
    const { container } = render(
      <AppShell
        layout={ide}
        regions={{ header: 'H', nav: 'N', main: 'M', inspector: 'I', dock: 'D', strip: 'S' }}
      />,
    )
    const shell = container.querySelector('.ui-shell')!
    expect(shell).toHaveAttribute('data-layout', 'ide')
    const regions = Array.from(shell.querySelectorAll('.ui-shell__region'))
    expect(regions.map((r) => [r.tagName.toLowerCase(), r.getAttribute('data-region')])).toEqual([
      ['header', 'header'],
      ['nav', 'nav'],
      ['main', 'main'],
      ['aside', 'inspector'],
      ['aside', 'dock'],
      ['footer', 'strip'],
    ])
    expect(screen.getByRole('banner')).toHaveTextContent('H')
    expect(screen.getByRole('navigation', { name: 'Navigation' })).toBeInTheDocument()
    expect(screen.getByRole('complementary', { name: 'Inspector' })).toBeInTheDocument()
  })

  it('renders only the regions the layout names', () => {
    const { container } = render(<AppShell layout={focus} regions={{ header: 'H', main: 'M', nav: 'ignored' }} />)
    expect(container.querySelectorAll('.ui-shell__region')).toHaveLength(2)
    expect(container.querySelector('[data-region="nav"]')).toBeNull()
  })

  it('has a skip link that targets main', () => {
    const { container } = render(<AppShell layout={focus} regions={{ main: 'M' }} />)
    const link = container.querySelector<HTMLAnchorElement>('a.ui-skip-link')!
    const main = container.querySelector('main')!
    expect(link.getAttribute('href')).toBe(`#${main.id}`)
    expect(container.querySelector('.ui-shell')!.firstElementChild).toBe(link)
  })

  it('F6 and Shift+F6 cycle focus between regions', async () => {
    const user = userEvent.setup()
    const { container } = render(<AppShell layout={ide} regions={{ main: <button>in main</button> }} />)
    await user.click(screen.getByRole('button', { name: 'in main' }))
    await user.keyboard('{F6}')
    expect(document.activeElement).toBe(container.querySelector('[data-region="inspector"]'))
    await user.keyboard('{Shift>}{F6}{/Shift}')
    expect(document.activeElement).toBe(container.querySelector('[data-region="main"]'))
  })

  it('rejects a layout naming an unknown region', () => {
    const bad = { ...focus, regions: ['main', 'sidebar'] }
    expect(() => render(<AppShell layout={bad} regions={{}} />)).toThrow(/unknown region/)
  })
})
