import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { DataTable, type DataTableColumn } from './DataTable'

interface R {
  id: string
  name: string
  n: number
}
// Fetched (server) order is deliberately neither ascending nor descending on any column.
const ROWS: R[] = [
  { id: 'b-2', name: 'Bravo', n: 20 },
  { id: 'a-1', name: 'Alpha', n: 5 },
  { id: 'c-3', name: 'Charlie', n: 100 },
]
const COLUMNS: DataTableColumn<R>[] = [
  { key: 'id', header: 'Id', kind: 'id' },
  { key: 'name', header: 'Name', sortable: true, isRowHeader: true },
  { key: 'n', header: 'Count', kind: 'num', sortable: true },
]

function names() {
  return screen
    .getAllByRole('row')
    .slice(1)
    .map((row) => within(row).getByRole('rowheader').textContent)
}

describe('DataTable', () => {
  it('renders contract classes and cell kinds', () => {
    const { container } = render(<DataTable label="Things" columns={COLUMNS} rows={ROWS} rowKey={(r) => r.id} />)
    expect(container.querySelector('.ui-table-wrap table.ui-table')).not.toBeNull()
    expect(container.querySelector('.ui-table__toolbar .ui-table__count')).toHaveTextContent('3 rows')
    const header = screen.getByRole('columnheader', { name: 'Count' })
    expect(header.querySelector('.ui-table__sort')).not.toBeNull()
    expect(container.querySelectorAll('td.ui-table__num')).toHaveLength(3)
    expect(container.querySelectorAll('td.ui-table__id')).toHaveLength(3)
    expect(screen.getByRole('grid', { name: 'Things' })).toBeInTheDocument()
  })

  it('header activation cycles ascending -> descending -> original order with aria-sort', async () => {
    const user = userEvent.setup()
    render(<DataTable label="Things" columns={COLUMNS} rows={ROWS} rowKey={(r) => r.id} />)
    const header = screen.getByRole('columnheader', { name: 'Count' })
    expect(names()).toEqual(['Bravo', 'Alpha', 'Charlie'])
    expect(header.getAttribute('aria-sort') ?? 'none').toBe('none')

    await user.click(header)
    expect(header).toHaveAttribute('aria-sort', 'ascending')
    expect(names()).toEqual(['Alpha', 'Bravo', 'Charlie'])

    await user.click(header)
    expect(header).toHaveAttribute('aria-sort', 'descending')
    expect(names()).toEqual(['Charlie', 'Bravo', 'Alpha'])

    await user.click(header)
    expect(header.getAttribute('aria-sort') ?? 'none').toBe('none')
    expect(names()).toEqual(['Bravo', 'Alpha', 'Charlie'])
  })

  it('sorts from the keyboard with Enter on a focused header', async () => {
    const user = userEvent.setup()
    render(<DataTable label="Things" columns={COLUMNS} rows={ROWS} rowKey={(r) => r.id} />)
    const header = screen.getByRole('columnheader', { name: 'Name' })
    await user.tab()
    // Move focus from the first cell up to the header row, then to the Name column.
    await user.keyboard('{ArrowUp}')
    while (document.activeElement !== header) {
      const before = document.activeElement
      await user.keyboard('{ArrowRight}')
      if (document.activeElement === before) break
    }
    expect(header).toHaveFocus()
    await user.keyboard('{Enter}')
    expect(header).toHaveAttribute('aria-sort', 'ascending')
    await user.keyboard('{Enter}')
    expect(header).toHaveAttribute('aria-sort', 'descending')
    await user.keyboard('{Enter}')
    expect(names()).toEqual(['Bravo', 'Alpha', 'Charlie'])
  })

  it('shows "N of M" when filtered, and "No rows match" with Clear filters when nothing matches', async () => {
    const user = userEvent.setup()
    const onClear = vi.fn()
    const { container, rerender } = render(
      <DataTable label="Things" columns={COLUMNS} rows={ROWS.slice(0, 1)} total={310} rowKey={(r) => r.id} />,
    )
    expect(container.querySelector('.ui-table__count')).toHaveTextContent('1 of 310')
    rerender(<DataTable label="Things" columns={COLUMNS} rows={[]} total={310} rowKey={(r) => r.id} onClearFilters={onClear} />)
    expect(container.querySelector('.ui-state[data-state="empty"]')).toHaveTextContent('No rows match')
    await user.click(screen.getByRole('button', { name: 'Clear filters' }))
    expect(onClear).toHaveBeenCalledOnce()
  })

  it('shows the empty state when there are no rows at all', () => {
    const { container } = render(
      <DataTable label="Things" columns={COLUMNS} rows={[]} rowKey={(r) => r.id} emptyTitle="No runs yet" />,
    )
    expect(container.querySelector('.ui-state[data-state="empty"]')).toHaveTextContent('No runs yet')
  })

  it('multiple selection marks rows aria-selected', async () => {
    const user = userEvent.setup()
    const onSelectionChange = vi.fn()
    render(
      <DataTable
        label="Things"
        columns={COLUMNS}
        rows={ROWS}
        rowKey={(r) => r.id}
        selectionMode="multiple"
        onSelectionChange={onSelectionChange}
      />,
    )
    const rows = screen.getAllByRole('row').slice(1)
    await user.click(within(rows[0]!).getByRole('checkbox'))
    expect(rows[0]).toHaveAttribute('aria-selected', 'true')
    expect(rows[0]).toHaveAttribute('data-selected', 'true')
    expect(rows[1]).toHaveAttribute('aria-selected', 'false')
    expect(onSelectionChange).toHaveBeenCalled()
  })
})
