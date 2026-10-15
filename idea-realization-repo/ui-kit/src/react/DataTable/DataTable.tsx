import { useMemo, useState, type ReactNode } from 'react'
import {
  Cell,
  Checkbox,
  Column,
  Row,
  Table,
  TableBody,
  TableHeader,
  type Key,
  type Selection,
  type SortDescriptor,
} from 'react-aria-components'
import { cx } from '../cx'
import { StateView } from '../StateView/StateView'
import { Button } from '../Button/Button'

/** `num`: right-aligned tabular numerals. `id`: monospace identifier. */
export type CellKind = 'text' | 'num' | 'id'

export interface DataTableColumn<T> {
  key: string
  header: string
  kind?: CellKind
  sortable?: boolean
  /** The value sorted on; defaults to `row[key]`. */
  sortValue?: (row: T) => string | number
  /** Cell content; defaults to `String(row[key])`. */
  render?: (row: T) => ReactNode
  /** Marks the column that names the row (one per table; defaults to the first column). */
  isRowHeader?: boolean
}

export interface DataTableProps<T extends object> {
  /** Accessible name of the table. */
  label: string
  columns: readonly DataTableColumn<T>[]
  /** The rows to show, already filtered, in the server (fetched) order. */
  rows: readonly T[]
  rowKey: (row: T) => Key
  /** Size of the unfiltered set; when larger than `rows.length` the count reads "N of M". */
  total?: number
  /** Toolbar content (search, filter chips) placed before the count. */
  toolbar?: ReactNode
  selectionMode?: 'none' | 'single' | 'multiple'
  selectedKeys?: Selection
  defaultSelectedKeys?: Selection
  onSelectionChange?: (keys: Selection) => void
  /** Empty state when there are no rows at all. */
  emptyTitle?: ReactNode
  emptyBody?: ReactNode
  emptyAction?: ReactNode
  /** When filters hide every row, the "No rows match" state offers this as "Clear filters". */
  onClearFilters?: () => void
}

type SortDirection = SortDescriptor['direction']

function defaultValue<T extends object>(row: T, key: string): unknown {
  return (row as Record<string, unknown>)[key]
}

function compare(a: unknown, b: unknown): number {
  if (typeof a === 'number' && typeof b === 'number') return a - b
  return String(a ?? '').localeCompare(String(b ?? ''), undefined, { numeric: true, sensitivity: 'base' })
}

function kindClass(kind: CellKind | undefined): string | undefined {
  if (kind === 'num') return 'ui-table__num'
  if (kind === 'id') return 'ui-table__id'
  return undefined
}

/**
 * DataTable on React Aria `Table`. Header sort cycles ascending -> descending -> the original
 * (fetched) order, with aria-sort on the column header. Client sort is a view of the server order,
 * never a re-ranking of it (principle 18).
 */
export function DataTable<T extends object>({
  label,
  columns,
  rows,
  rowKey,
  total,
  toolbar,
  selectionMode = 'none',
  selectedKeys,
  defaultSelectedKeys,
  onSelectionChange,
  emptyTitle = 'Nothing here yet',
  emptyBody,
  emptyAction,
  onClearFilters,
}: DataTableProps<T>) {
  const [sort, setSort] = useState<SortDescriptor | undefined>(undefined)

  const onSortChange = (next: SortDescriptor) => {
    // React Aria proposes "ascending" after "descending" on the same column; the kit's third state
    // is the original order instead.
    if (sort && sort.column === next.column && sort.direction === 'descending') {
      setSort(undefined)
      return
    }
    setSort(next)
  }

  const sortedRows = useMemo(() => {
    if (!sort) return rows
    const column = columns.find((c) => c.key === sort.column)
    if (!column) return rows
    const value = column.sortValue ?? ((row: T) => defaultValue(row, column.key) as string | number)
    const sign: number = (sort.direction as SortDirection) === 'descending' ? -1 : 1
    return [...rows].sort((a, b) => sign * compare(value(a), value(b)))
  }, [rows, columns, sort])

  const items = useMemo(() => sortedRows.map((row) => ({ id: rowKey(row), row })), [sortedRows, rowKey])

  const filtered = total !== undefined && total > rows.length
  const countText = filtered ? `${rows.length} of ${total}` : `${rows.length} ${rows.length === 1 ? 'row' : 'rows'}`
  const rowHeaderKey = columns.find((c) => c.isRowHeader)?.key ?? columns[0]?.key
  const withCheckbox = selectionMode === 'multiple'

  return (
    <div>
      <div className="ui-table__toolbar">
        {toolbar}
        <p className="ui-table__count" role="status">
          {countText}
        </p>
      </div>
      <div className="ui-table-wrap">
        <Table
          aria-label={label}
          className="ui-table"
          sortDescriptor={sort}
          onSortChange={onSortChange}
          selectionMode={selectionMode}
          selectedKeys={selectedKeys}
          defaultSelectedKeys={defaultSelectedKeys}
          onSelectionChange={onSelectionChange}
        >
          <TableHeader>
            {withCheckbox && (
              <Column id="__select" className="ui-table__select">
                <Checkbox slot="selection" className="ui-table__checkbox" />
              </Column>
            )}
            {columns.map((column) => (
              <Column
                key={column.key}
                id={column.key}
                isRowHeader={column.key === rowHeaderKey}
                allowsSorting={column.sortable === true}
                className={kindClass(column.kind)}
              >
                {column.sortable ? <span className="ui-table__sort">{column.header}</span> : column.header}
              </Column>
            ))}
          </TableHeader>
          <TableBody
            items={items}
            dependencies={[columns, withCheckbox]}
            renderEmptyState={() =>
              filtered ? (
                <StateView
                  state="empty"
                  title="No rows match"
                  body="Change or clear the filters to see rows."
                  action={
                    onClearFilters ? (
                      <Button variant="secondary" onPress={onClearFilters}>
                        Clear filters
                      </Button>
                    ) : undefined
                  }
                />
              ) : (
                <StateView state="empty" title={emptyTitle} body={emptyBody} action={emptyAction} />
              )
            }
          >
            {(item) => (
              <Row id={item.id}>
                {withCheckbox && (
                  <Cell className="ui-table__select">
                    <Checkbox slot="selection" className="ui-table__checkbox" />
                  </Cell>
                )}
                {columns.map((column) => (
                  <Cell key={column.key} className={cx(kindClass(column.kind))}>
                    {column.render ? column.render(item.row) : String(defaultValue(item.row, column.key) ?? '')}
                  </Cell>
                ))}
              </Row>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
