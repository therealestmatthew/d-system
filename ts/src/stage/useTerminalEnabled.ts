const TERMINAL_ENABLED_URL = '/api/v1/demo/stage/terminal-enabled'

/**
 * The backend mounts the workbench routes (`/api/v1/workbench/*`, ADR-015) only under
 * `D_SYSTEM_DEMO_TERMINAL=1`, the same flag the read-only `terminal-enabled` route reports
 * (`src/api/__init__.py`). With the flag unset every workbench fetch 404s, and each 404 is a
 * console error on load (REQ-012 R23).
 *
 * One probe per page load, shared by every caller: the flag is fixed when the backend starts. A
 * failed probe is not kept, so the next caller asks again.
 */
let terminalEnabledProbe: Promise<boolean> | null = null

export function terminalEnabled(): Promise<boolean> {
  if (terminalEnabledProbe === null) {
    terminalEnabledProbe = fetch(TERMINAL_ENABLED_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`status ${response.status}`)
        return response.json() as Promise<{ terminal_enabled: boolean }>
      })
      .then((body) => body.terminal_enabled === true)
      .catch(() => {
        terminalEnabledProbe = null
        return false
      })
  }
  return terminalEnabledProbe
}

/**
 * `fetch` for a workbench route. When the routes are not mounted it resolves to the 404 the
 * backend would have returned, without sending the request, so every caller's existing handling
 * of the flag-off case (a `missing` or `error` state, a bash default) is unchanged and only the
 * console entry disappears.
 */
export async function fetchWorkbench(input: string, init?: RequestInit): Promise<Response> {
  if (!(await terminalEnabled())) return new Response(null, { status: 404 })
  return fetch(input, init)
}
