import { useState, type ReactNode } from 'react'
import ideLayout from '../../../layouts/ide.json'
import {
  AppShell,
  Badge,
  Button,
  Card,
  CardGrid,
  Chip,
  ConfirmDialog,
  DataTable,
  Dialog,
  Panel,
  Pill,
  StatCard,
  StateView,
  Tabs,
  ToggleButton,
  useToast,
  type DataTableColumn,
} from '../index'

const ACCENTS = ['indigo', 'blue', 'teal', 'green', 'violet', 'magenta', 'orange', 'slate'] as const

function setRootAttribute(name: string, value: string) {
  if (value === '') document.documentElement.removeAttribute(name)
  else document.documentElement.setAttribute(name, value)
}

function ThemeControls() {
  return (
    <div>
      <label>
        Theme{' '}
        <select defaultValue="" onChange={(e) => setRootAttribute('data-theme', e.target.value)}>
          <option value="">System</option>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </label>{' '}
      <label>
        Accent{' '}
        <select defaultValue="" onChange={(e) => setRootAttribute('data-accent', e.target.value)}>
          <option value="">Default</option>
          {ACCENTS.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </label>{' '}
      <label>
        Density{' '}
        <select defaultValue="" onChange={(e) => setRootAttribute('data-density', e.target.value)}>
          <option value="">Default</option>
          <option value="compact">Compact</option>
          <option value="comfortable">Comfortable</option>
        </select>
      </label>
    </div>
  )
}

interface Run {
  id: string
  name: string
  status: 'ok' | 'warn' | 'err'
  tokens: number
}

const RUNS: Run[] = [
  { id: 'run-0042', name: 'Quarterly summary', status: 'ok', tokens: 18234 },
  { id: 'run-0043', name: 'Contract review', status: 'warn', tokens: 9120 },
  { id: 'run-0044', name: 'Invoice extraction', status: 'err', tokens: 402 },
  { id: 'run-0045', name: 'Board pack draft', status: 'ok', tokens: 31877 },
]

const STATUS_WORD: Record<Run['status'], string> = { ok: 'Done', warn: 'Needs review', err: 'Failed' }

const RUN_COLUMNS: DataTableColumn<Run>[] = [
  { key: 'id', header: 'Run', kind: 'id', sortable: true },
  { key: 'name', header: 'Name', sortable: true, isRowHeader: true },
  { key: 'status', header: 'Status', render: (r) => <Pill status={r.status}>{STATUS_WORD[r.status]}</Pill> },
  { key: 'tokens', header: 'Tokens', kind: 'num', sortable: true, render: (r) => r.tokens.toLocaleString('en-US') },
]

function RunsTable() {
  const [onlyOk, setOnlyOk] = useState(false)
  const rows = onlyOk ? RUNS.filter((r) => r.status === 'ok') : RUNS
  return (
    <DataTable
      label="Recent runs"
      columns={RUN_COLUMNS}
      rows={rows}
      rowKey={(r) => r.id}
      total={RUNS.length}
      selectionMode="multiple"
      toolbar={
        onlyOk ? (
          <Chip label="status: done" onRemove={() => setOnlyOk(false)} />
        ) : (
          <Button size="sm" onPress={() => setOnlyOk(true)}>
            Show done only
          </Button>
        )
      }
      onClearFilters={() => setOnlyOk(false)}
    />
  )
}

function Counter() {
  const [count, setCount] = useState(0)
  return (
    <p>
      Live state that survives maximize and collapse: {count}{' '}
      <Button size="sm" onPress={() => setCount((c) => c + 1)}>
        Add one
      </Button>
    </p>
  )
}

function Crashable() {
  const [crash, setCrash] = useState(false)
  if (crash) throw new Error('the inspector data could not be read')
  return (
    <Button size="sm" variant="danger" onPress={() => setCrash(true)}>
      Break this panel
    </Button>
  )
}

function ToastButtons() {
  const toast = useToast()
  return (
    <>
      <Button size="sm" onPress={() => toast.show({ status: 'ok', title: 'Report generated', body: 'Saved to runs/0045.' })}>
        Show success toast
      </Button>{' '}
      <Button size="sm" onPress={() => toast.show({ status: 'info', title: 'Sync started' })}>
        Show info toast
      </Button>{' '}
      <Button
        size="sm"
        onPress={() =>
          toast.show({
            status: 'err',
            title: 'Upload failed',
            body: 'The connection closed before the file was sent.',
            action: { label: 'Retry', onAction: () => undefined },
          })
        }
      >
        Show error toast
      </Button>
    </>
  )
}

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <section id={id} aria-labelledby={`${id}-h`}>
      <h3 id={`${id}-h`}>{title}</h3>
      {children}
    </section>
  )
}

const SECTIONS = [
  ['pg-buttons', 'Buttons'],
  ['pg-cards', 'Cards'],
  ['pg-pills', 'Pills, badges and chips'],
  ['pg-states', 'States'],
  ['pg-table', 'Data table'],
  ['pg-dialogs', 'Dialogs'],
  ['pg-tabs', 'Tabs'],
  ['pg-toasts', 'Toasts'],
] as const

function MainContent() {
  const [loading, setLoading] = useState(false)
  const [pinned, setPinned] = useState(false)
  return (
    <>
      <Section id="pg-buttons" title="Buttons">
        <p>
          <Button variant="primary">Generate report</Button> <Button>Export</Button>{' '}
          <Button variant="ghost">Details</Button> <Button variant="danger">Delete draft</Button>
        </p>
        <p>
          <Button size="sm">Small</Button> <Button>Medium</Button> <Button size="lg">Large</Button>{' '}
          <Button iconOnly icon="⟳" aria-label="Refresh" />{' '}
          <Button icon="+" variant="secondary">
            New run
          </Button>
        </p>
        <p>
          <Button variant="primary" isLoading={loading} onPress={() => setLoading(true)}>
            {loading ? 'Generating…' : 'Start loading'}
          </Button>{' '}
          <Button onPress={() => setLoading(false)}>Stop loading</Button> <Button isDisabled>Disabled</Button>{' '}
          <ToggleButton isSelected={pinned} onChange={setPinned}>
            Pin
          </ToggleButton>
        </p>
      </Section>
      <Section id="pg-cards" title="Cards">
        <CardGrid>
          <Card kicker="Run" title="Quarterly summary" meta="Source: runs table, 14 Oct 2026 09:12" actions={<Button size="sm">Open</Button>}>
            Three findings need review.
          </Card>
          <Card variant="accent" title="Needs attention">
            Two approvals are pending.
          </Card>
          <Card variant="ai" kicker="Generated by Claude" title="Draft summary">
            Revenue grew in all three regions.
          </Card>
          <StatCard label="Open findings" value={12} delta="+3 since Monday" meta="Source: findings, 14 Oct 2026" />
          <StatCard label="Cost this month" value={null} meta="Source: billing export" />
        </CardGrid>
      </Section>
      <Section id="pg-pills" title="Pills, badges and chips">
        <p>
          <Pill status="ok">Done</Pill> <Pill status="warn">Needs review</Pill> <Pill status="info">Queued</Pill>{' '}
          <Pill status="err">Failed</Pill> <Pill status="neutral">Draft</Pill> <Pill status="ai">AI generated</Pill>
        </p>
        <p>
          Inbox <Badge count={3} label="3 unread" /> <Chip label="owner: me" onRemove={() => undefined} />{' '}
          <Chip label="read-only chip" />
        </p>
      </Section>
      <Section id="pg-states" title="States">
        <CardGrid>
          <StateView state="empty" title="No findings yet" body="Upload a file to start." action={<Button variant="primary">Upload file</Button>} />
          <StateView state="loading" title="Searching…" />
          <StateView state="error" title="Search failed" body="The index did not answer in 10 seconds." action={<Button>Retry</Button>} />
          <StateView state="missing" title="Agent service not configured in this environment" />
          <StateView state="not-recorded" title="Not recorded" body="No cost data for this run." />
        </CardGrid>
      </Section>
      <Section id="pg-table" title="Data table">
        <RunsTable />
      </Section>
      <Section id="pg-dialogs" title="Dialogs">
        <p>
          <Dialog
            trigger={<Button>Open info dialog</Button>}
            title="About runs"
            footer={(close) => (
              <Button variant="primary" onPress={close}>
                Got it
              </Button>
            )}
          >
            <p>A run is one agent execution with its inputs, steps and outputs.</p>
          </Dialog>{' '}
          <Dialog
            trigger={<Button>Open form dialog</Button>}
            title="Rename run"
            variant="form"
            footer={(close) => (
              <>
                <Button onPress={close}>Cancel</Button>
                <Button variant="primary" onPress={close}>
                  Save name
                </Button>
              </>
            )}
          >
            <label>
              Name <input type="text" defaultValue="Quarterly summary" />
            </label>
          </Dialog>{' '}
          <ConfirmDialog
            trigger={<Button variant="danger">Close session</Button>}
            object='session "build-42"'
            actionLabel="Close"
            consequence="This ends the shell and stops its running command."
            onConfirm={() => undefined}
          />
        </p>
      </Section>
      <Section id="pg-tabs" title="Tabs">
        <Tabs
          label="Run detail"
          items={[
            { id: 'summary', label: 'Summary', content: <p>Three steps, 41 seconds.</p> },
            { id: 'inputs', label: 'Inputs', content: <p>One PDF, 12 pages.</p> },
            { id: 'outputs', label: 'Outputs', content: <p>One report.</p> },
          ]}
        />
      </Section>
      <Section id="pg-toasts" title="Toasts">
        <ToastButtons />
      </Section>
    </>
  )
}

export function Playground() {
  return (
    <AppShell
      layout={ideLayout}
      regions={{
        header: (
          <>
            <h1>UI kit playground</h1>
            <ThemeControls />
          </>
        ),
        nav: (
          <Panel title="Sections" body="tree" maximizable={false}>
            <ul>
              {SECTIONS.map(([id, label]) => (
                <li key={id}>
                  <a href={`#${id}`}>{label}</a>
                </li>
              ))}
            </ul>
          </Panel>
        ),
        main: (
          <Panel
            title="Components"
            body="document"
            help={<span>Every component in its states.</span>}
            controls={
              <>
                <Button size="sm" variant="primary">
                  Generate report
                </Button>
                <Button size="sm">Export</Button>
              </>
            }
          >
            <MainContent />
          </Panel>
        ),
        inspector: (
          <Panel title="Inspector" body="form">
            <Counter />
            <Crashable />
          </Panel>
        ),
        dock: (
          <Panel title="Dock" body="stream" variant="compact">
            <Tabs
              label="Dock views"
              items={[
                { id: 'console', label: 'Console', content: <StateView state="empty" title="No output yet" /> },
                { id: 'logs', label: 'Logs', content: <StateView state="not-recorded" title="Not recorded" /> },
                { id: 'runs', label: 'Runs', content: <StateView state="missing" title="Run history is not configured" /> },
              ]}
            />
          </Panel>
        ),
        strip: (
          <p>
            <Pill status="ok">Connected</Pill> Environment: demo · Model: Claude via Amazon Bedrock · Last sync 09:12
          </p>
        ),
      }}
    />
  )
}
