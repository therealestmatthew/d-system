// @vitest-environment node
//
// The dev server's symlink guard (`refuseSymlinkEscapes` in vite.config.ts, security review of
// `phase-arch-07`, 2026-10-09). Each case builds a throwaway tree with a symlink that points out of
// the allowed directory and runs a real Vite dev server over it: first without the guard, to show
// Vite itself serves the outside file (so the test reproduces the hole rather than assuming it),
// then with the guard, which must refuse it while still serving an ordinary allowed file. The
// config's own file-serving routes (`/workbench-layouts/`, `/generated-overview/`,
// `/workbench-file/`) are run over the same kind of tree, since each serves files by its own route
// rather than through Vite's.
import { execFileSync, spawn } from 'node:child_process'
import {
  linkSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { extname, join } from 'node:path'
import { createServer, type Connect, type Plugin, type ViteDevServer } from 'vite'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import {
  refuseSymlinkEscapes,
  serveGeneratedOverview,
  serveRepositoryFiles,
  serveWorkbenchLayouts,
} from './vite.config'

let base: string
let site: string
let data: string
const servers: ViteDevServer[] = []

beforeEach(() => {
  base = realpathSync(mkdtempSync(join(tmpdir(), 'vite-fs-guard-')))
  site = join(base, 'site')
  data = join(site, 'data')
  mkdirSync(data, { recursive: true })
  mkdirSync(join(base, 'outside'))
  writeFileSync(join(base, 'outside', 'secret.txt'), 'SECRET')
  writeFileSync(join(data, 'ok.txt'), 'OK')
  writeFileSync(join(site, 'index.html'), '<!doctype html><title>t</title>')
  symlinkSync(join(base, 'outside'), join(data, 'evil'))
  symlinkSync(join(base, 'outside'), join(site, 'evil-root'))
  mkdirSync(join(data, 'layouts'))
  writeFileSync(join(data, 'layouts', 'layout-1.json'), '{"ok": true}')
  symlinkSync(join(base, 'outside', 'secret.txt'), join(data, 'layouts', 'evil-layout.json'))
})

const LAYOUTS = '/workbench-layouts/'

// A route that serves a directory with only a textual containment check, as
// `serveWorkbenchLayouts` did before the security review: it shows the guard's own mapping of the
// route's prefix is what refuses the symlink, independent of the route's own check.
function naiveRoute(prefix: string, directory: string): Plugin {
  return {
    name: 'naive-route',
    configureServer(server) {
      server.middlewares.use(prefix, ((req, res) => {
        try {
          res.end(readFileSync(join(directory, (req.url ?? '').split('?')[0] ?? '')))
        } catch {
          res.statusCode = 404
          res.end()
        }
      }) as Connect.NextHandleFunction)
    },
  }
}

afterEach(async () => {
  await Promise.all(servers.splice(0).map((server) => server.close()))
  rmSync(base, { recursive: true, force: true })
})

async function serve(
  plugins: Plugin[],
  root: string = site,
): Promise<(path: string, headers?: Record<string, string>) => Promise<Response>> {
  const server = await createServer({
    configFile: false,
    root,
    logLevel: 'silent',
    plugins,
    optimizeDeps: { noDiscovery: true },
    server: { port: 0, hmr: false, fs: { allow: [root] } },
  })
  servers.push(server)
  await server.listen()
  const address = server.httpServer?.address()
  if (address === null || typeof address !== 'object') throw new Error('no listening address')
  return (path, headers) => fetch(`http://127.0.0.1:${address.port}${path}`, { headers })
}

describe('refuseSymlinkEscapes', () => {
  it('reproduces the hole: without the guard, Vite serves a file outside the list', async () => {
    const get = await serve([])
    const viaFs = await get(`/@fs${data}/evil/secret.txt`)
    expect(viaFs.status).toBe(200)
    expect(await viaFs.text()).toBe('SECRET')
    const viaRoot = await get('/evil-root/secret.txt')
    expect(viaRoot.status).toBe(200)
    expect(await viaRoot.text()).toBe('SECRET')
  })

  it('refuses a symlink escape through /@fs/ and through a root-relative URL', async () => {
    const get = await serve([refuseSymlinkEscapes(site, [site])])
    for (const path of [
      `/@fs${data}/evil/secret.txt`,
      '/evil-root/secret.txt',
      '/data/evil/secret.txt',
      '/data/%2E%2E/evil-root/secret.txt',
    ]) {
      const response = await get(path)
      expect(response.status, path).toBe(403)
      expect(await response.text(), path).not.toContain('SECRET')
    }
  })

  it('still serves an allowed file, and leaves a missing one to Vite', async () => {
    const get = await serve([refuseSymlinkEscapes(site, [site])])
    const viaFs = await get(`/@fs${data}/ok.txt`)
    expect(viaFs.status).toBe(200)
    expect(await viaFs.text()).toBe('OK')
    const viaRoot = await get('/data/ok.txt')
    expect(viaRoot.status).toBe(200)
    expect(await viaRoot.text()).toBe('OK')
    expect((await get('/data/absent.txt')).status).not.toBe(403)
  })

  it('covers a route of this config through its prefix mapping', async () => {
    const layouts = join(data, 'layouts')
    const naive = await serve([naiveRoute(LAYOUTS, layouts)])
    expect(await (await naive(`${LAYOUTS}evil-layout.json`)).text()).toBe('SECRET')
    const get = await serve([
      refuseSymlinkEscapes(site, [site], { [LAYOUTS]: layouts }),
      naiveRoute(LAYOUTS, layouts),
    ])
    expect((await get(`${LAYOUTS}evil-layout.json`)).status).toBe(403)
    expect(await (await get(`${LAYOUTS}layout-1.json`)).text()).toBe('{"ok": true}')
  })
})

describe("the config's own file routes check the real path", () => {
  it('/workbench-layouts/ refuses a symlink that leads out of its directory', async () => {
    const get = await serve([serveWorkbenchLayouts(join(data, 'layouts'))])
    const evil = await get(`${LAYOUTS}evil-layout.json`)
    expect(evil.status).toBe(403)
    expect(await evil.text()).not.toContain('SECRET')
    const ok = await get(`${LAYOUTS}layout-1.json`)
    expect(ok.status).toBe(200)
    expect(await ok.text()).toBe('{"ok": true}')
  })

  it('/generated-overview/ refuses a symlink that leads out of its directory', async () => {
    const pub = join(base, 'public-dir')
    mkdirSync(pub)
    writeFileSync(join(pub, 'overview.html'), '<p>overview</p>')
    symlinkSync(join(base, 'outside', 'secret.txt'), join(pub, 'evil.html'))
    const get = await serve([serveGeneratedOverview(pub)])
    const evil = await get('/generated-overview/evil.html')
    expect(evil.status).toBe(403)
    expect(await evil.text()).not.toContain('SECRET')
    expect(await (await get('/generated-overview/overview.html')).text()).toBe('<p>overview</p>')
  })

  it('/workbench-file/ judges ignore rules and .git on the resolved path', async () => {
    const repo = join(base, 'repo')
    mkdirSync(join(repo, 'docs'), { recursive: true })
    mkdirSync(join(repo, 'secret'))
    execFileSync('git', ['init', '--quiet'], { cwd: repo })
    writeFileSync(join(repo, '.gitignore'), 'secret/\n')
    writeFileSync(join(repo, 'secret', 'private.txt'), 'PRIVATE')
    writeFileSync(join(repo, 'docs', 'ok.txt'), 'OK')
    symlinkSync(join(repo, 'secret', 'private.txt'), join(repo, 'docs', 'to-ignored.txt'))
    symlinkSync(join(repo, '.git', 'config'), join(repo, 'docs', 'to-git.txt'))
    const get = await serve([serveRepositoryFiles(repo)])
    const ignored = await get('/workbench-file/docs/to-ignored.txt')
    expect(ignored.status).toBe(404)
    expect(await ignored.text()).not.toContain('PRIVATE')
    expect((await get('/workbench-file/docs/to-git.txt')).status).toBe(403)
    expect(await (await get('/workbench-file/docs/ok.txt?raw=1')).text()).toBe('OK')
  })
})

// A child process that renames a regular file and a symlink to an outside file over one name, as
// fast as it can, until it is told to stop, then prints how many swaps it made. It also exits on
// its own at its deadline, and as soon as its parent is gone (its stdin pipe ends, or its parent
// process id changes), so a test run that is killed or crashes cannot leave it spinning.
const TOGGLER = `
const { renameSync, rmSync, symlinkSync, writeFileSync } = require('node:fs')
const [target, secret, publicText, deadlineMs] = process.argv.slice(1)
const deadline = Date.now() + Number(deadlineMs)
const parent = process.ppid
let swaps = 0
let stop = false
process.stdin.on('data', () => { stop = true })
process.stdin.on('end', () => process.exit(0))
process.stdin.on('error', () => process.exit(0))
const step = () => {
  if (process.ppid !== parent || Date.now() > deadline) process.exit(0)
  for (let i = 0; i < 200 && !stop; i += 1) {
    const temporary = target + '.swap' + (swaps % 2)
    rmSync(temporary, { force: true })
    if (swaps % 2) symlinkSync(secret, temporary)
    else writeFileSync(temporary, publicText)
    renameSync(temporary, target)
    swaps += 1
  }
  if (stop) {
    writeFileSync(target, publicText)
    process.stdout.write(String(swaps))
    process.exit(0)
  }
  setImmediate(step)
}
step()
`

const TOGGLER_DEADLINE_MS = 10_000

// Runs `body` while a toggler flips `target`; `stop` ends the toggler and returns its swap count.
// Whatever `body` does, the toggler is killed and waited for before this returns or throws, and
// `onSpawn` sees its process id, so a test can check that none survives.
async function withToggler<T>(
  args: { target: string; secret: string; publicText: string; deadlineMs?: number },
  body: (stop: () => Promise<number>) => Promise<T>,
  onSpawn: (pid: number) => void = () => {},
): Promise<T> {
  const deadline = String(args.deadlineMs ?? TOGGLER_DEADLINE_MS)
  const toggler = spawn(process.execPath, [
    '-e',
    TOGGLER,
    args.target,
    args.secret,
    args.publicText,
    deadline,
  ])
  if (toggler.pid !== undefined) onSpawn(toggler.pid)
  let output = ''
  toggler.stdout.on('data', (chunk: Buffer) => (output += chunk.toString()))
  const exited = new Promise<void>((resolve) => toggler.on('exit', () => resolve()))
  const stop = async () => {
    toggler.stdin.write('stop')
    await exited
    return Number(output)
  }
  try {
    return await body(stop)
  } finally {
    if (toggler.exitCode === null && toggler.signalCode === null) toggler.kill('SIGKILL')
    await exited
  }
}

function isAlive(pid: number): boolean {
  try {
    process.kill(pid, 0)
    return true
  } catch {
    return false
  }
}

async function waitUntilDead(pid: number, withinMs: number): Promise<boolean> {
  const until = Date.now() + withinMs
  while (Date.now() < until) {
    if (!isAlive(pid)) return true
    await new Promise((resolve) => setTimeout(resolve, 50))
  }
  return !isAlive(pid)
}

describe('the race test cleans up after itself', () => {
  it('leaves no toggler running when a case fails', async () => {
    const target = join(data, 'flip.txt')
    writeFileSync(target, 'PUBLIC')
    let pid = 0
    await expect(
      withToggler(
        { target, secret: join(base, 'outside', 'secret.txt'), publicText: 'PUBLIC' },
        async () => {
          throw new Error('a failing case')
        },
        (spawned) => (pid = spawned),
      ),
    ).rejects.toThrow('a failing case')
    expect(pid).toBeGreaterThan(0)
    expect(isAlive(pid)).toBe(false)
  })

  it('stops on its own at its deadline', async () => {
    const target = join(data, 'flip.txt')
    writeFileSync(target, 'PUBLIC')
    // Never told to stop, and its stdin kept open: only the deadline can end it.
    const toggler = spawn(process.execPath, [
      '-e',
      TOGGLER,
      target,
      join(base, 'outside', 'secret.txt'),
      'PUBLIC',
      '300',
    ])
    try {
      const started = Date.now()
      const pid = toggler.pid ?? 0
      expect(await waitUntilDead(pid, 5_000)).toBe(true)
      expect(Date.now() - started).toBeLessThan(5_000)
    } finally {
      toggler.kill('SIGKILL')
    }
  })

  it('exits when the process that started it is killed', async () => {
    const target = join(data, 'flip.txt')
    writeFileSync(target, 'PUBLIC')
    // A stand-in for a test worker: it starts a toggler with a long deadline, reports its pid,
    // and waits. Killing it must take the toggler with it.
    const worker = spawn(process.execPath, [
      '-e',
      `const { spawn } = require('node:child_process')
       const t = spawn(process.execPath, ['-e', process.argv[1], ...process.argv.slice(2)],
         { stdio: ['pipe', 'ignore', 'ignore'] })
       process.stdout.write(String(t.pid) + '\\n')
       setInterval(() => {}, 1000)`,
      TOGGLER,
      target,
      join(base, 'outside', 'secret.txt'),
      'PUBLIC',
      '60000',
    ])
    const togglerPid = await new Promise<number>((resolve) =>
      worker.stdout.once('data', (chunk: Buffer) => resolve(Number(chunk.toString().trim()))),
    )
    try {
      expect(isAlive(togglerPid)).toBe(true)
      worker.kill('SIGKILL')
      expect(await waitUntilDead(togglerPid, 5_000)).toBe(true)
    } finally {
      worker.kill('SIGKILL')
      if (isAlive(togglerPid)) process.kill(togglerPid, 'SIGKILL')
    }
  })
})

describe('hard links (security review, 2026-10-09)', () => {
  // A hard link is a second name for the same file: one inside a served directory can name a file
  // that lives outside it, and neither the path nor the inode shows that. Every route refuses a
  // file with more than one link, except under `node_modules`, where package managers make them.
  it('refuses a hard link to an outside file on every route', async () => {
    const secret = join(base, 'outside', 'secret.txt')
    const pub = join(base, 'public-dir')
    const repo = join(base, 'repo')
    mkdirSync(join(site, 'public'))
    mkdirSync(pub)
    mkdirSync(join(repo, 'docs'), { recursive: true })
    execFileSync('git', ['init', '--quiet'], { cwd: repo })
    linkSync(secret, join(site, 'public', 'hard.txt'))
    linkSync(secret, join(data, 'hard.txt'))
    linkSync(secret, join(data, 'layouts', 'hard.json'))
    linkSync(secret, join(pub, 'hard.html'))
    linkSync(secret, join(repo, 'docs', 'hard.txt'))
    // Directories merely named `node_modules` get no exemption; only the root's own one does.
    for (const fake of [
      join(data, 'node_modules', 'evil'),
      join(site, 'src', 'node_modules', 'evil'),
      join(repo, 'node_modules', 'evil'),
    ]) {
      mkdirSync(fake, { recursive: true })
      linkSync(secret, join(fake, 'hard.txt'))
    }
    const get = await serve([
      refuseSymlinkEscapes(site, [site], { [LAYOUTS]: join(data, 'layouts') }),
      serveWorkbenchLayouts(join(data, 'layouts')),
      serveGeneratedOverview(pub),
      serveRepositoryFiles(repo),
    ])
    for (const path of [
      '/hard.txt',
      `/@fs${data}/hard.txt`,
      '/data/hard.txt',
      '/data/hard.txt?raw',
      `${LAYOUTS}hard.json`,
      '/generated-overview/hard.html',
      '/workbench-file/docs/hard.txt',
      `/@fs${data}/node_modules/evil/hard.txt`,
      '/data/node_modules/evil/hard.txt',
      `/@fs${site}/src/node_modules/evil/hard.txt`,
      '/src/node_modules/evil/hard.txt',
      '/workbench-file/node_modules/evil/hard.txt',
    ]) {
      const response = await get(path)
      expect(response.status, path).toBe(403)
      expect(await response.text(), path).not.toContain('SECRET')
    }
  })

  it("still serves a hard-linked file under the root's own node_modules", async () => {
    const pkg = join(site, 'node_modules', 'pkg')
    mkdirSync(pkg, { recursive: true })
    writeFileSync(join(pkg, 'asset.txt'), 'PACKAGE')
    linkSync(join(pkg, 'asset.txt'), join(pkg, 'asset-copy.txt'))
    const get = await serve([refuseSymlinkEscapes(site, [site])])
    for (const path of ['/node_modules/pkg/asset.txt', `/@fs${pkg}/asset.txt`]) {
      const response = await get(path)
      expect(response.status, path).toBe(200)
      expect(await response.text(), path).toBe('PACKAGE')
    }
  })
})

describe('serving under concurrent renames (check-then-serve race)', () => {
  // Each case gets its own tree and server, with no other symlink in it, and runs a toggler for a
  // bounded time with 16 requests in flight. Against the round-2 guard, which checked a name and
  // then let Vite or the route open it again, the same harness got the outside file back.
  it('serves no outside byte by any route while a name flips to a symlink and back', async () => {
    const uncaught: unknown[] = []
    const record = (error: unknown) => uncaught.push(error)
    process.on('uncaughtException', record)
    try {
      // The browser's headers for a module import, and for a worker's own script.
      const fromModule = { accept: '*/*', 'sec-fetch-dest': 'script' }
      const fromWorker = { 'sec-fetch-dest': 'worker' }
      const svg = ['<svg>PUBLIC</svg>', '<svg>SECRET</svg>']
      const css = ['body{} /* PUBLIC */', 'body{} /* SECRET */']
      const js = ['self.onmessage = () => {} // PUBLIC', 'self.onmessage = () => {} // SECRET']
      type RaceCase = [string, string, string[], Record<string, string>?]
      const cases: RaceCase[] = [
        ['data/layouts/race.json', `${LAYOUTS}race.json`, ['{}', 'SECRET']],
        ['pub/race.html', '/generated-overview/race.html', ['PUBLIC', 'SECRET']],
        ['repo/docs/race.txt', '/workbench-file/docs/race.txt', ['PUBLIC', 'SECRET']],
        ['site/public/race.txt', '/race.txt', ['PUBLIC', 'SECRET']],
        ['site/data/race.txt', '/@fs<site>/data/race.txt', ['PUBLIC', 'SECRET']],
        ['site/data/race.txt', '/data/race.txt?raw', ['PUBLIC', 'SECRET']],
        ['site/data/race.ts', '/data/race.ts', ['export {}', 'export default "SECRET"']],
        ['site/race.html', '/race.html', ['<p>PUBLIC</p>', 'SECRET']],
        // Import queries Vite's asset and worker plugins would answer by reading the name: the
        // security review's case (`?import&url` fetched directly) first, then each from a module.
        ['site/data/race.svg', '/data/race.svg?import&url', svg],
        ['site/data/race.svg', '/data/race.svg?import&url', svg, fromModule],
        ['site/data/race.svg', '/data/race.svg?import&inline', svg, fromModule],
        ['site/data/race.svg', '/data/race.svg?import&raw', svg, fromModule],
        ['site/data/race.svg', '/data/race.svg?import', svg, fromModule],
        ['site/data/race.css', '/data/race.css?inline', css, fromModule],
        ['site/data/race.css', '/data/race.css?inline', css],
        ['site/data/race.css', '/data/race.css?url', css, fromModule],
        ['site/data/race.css', '/data/race.css?raw', css],
        ['site/data/race.js', '/data/race.js?worker', js, fromModule],
        ['site/data/race.js', '/data/race.js?worker&inline', js, fromModule],
        ['site/data/race.js', '/data/race.js?worker_file&type=module', js, fromWorker],
      ]
      for (const [relative, url, [publicText, secretText], headers] of cases) {
        const tree = realpathSync(mkdtempSync(join(base, 'race-')))
        const raceSite = join(tree, 'site')
        const layouts = join(raceSite, 'data', 'layouts')
        mkdirSync(layouts, { recursive: true })
        mkdirSync(join(raceSite, 'public'))
        mkdirSync(join(tree, 'pub'))
        mkdirSync(join(tree, 'repo', 'docs'), { recursive: true })
        mkdirSync(join(tree, 'outside'))
        execFileSync('git', ['init', '--quiet'], { cwd: join(tree, 'repo') })
        writeFileSync(join(raceSite, 'index.html'), '<!doctype html><title>t</title>')
        const secret = join(tree, 'outside', `secret${extname(relative)}`)
        writeFileSync(secret, secretText)
        // The secret as served raw, or inside a data URL.
        const encoded = Buffer.from(secretText).toString('base64')
        const target = join(tree, relative.replace(/^data\//, 'site/data/'))
        writeFileSync(target, publicText)
        const get = await serve(
          [
            refuseSymlinkEscapes(raceSite, [raceSite], { [LAYOUTS]: layouts }),
            serveWorkbenchLayouts(layouts),
            serveGeneratedOverview(join(tree, 'pub')),
            serveRepositoryFiles(join(tree, 'repo')),
          ],
          raceSite,
        )
        const path = url.replace('<site>', raceSite)
        try {
          const swaps = await withToggler({ target, secret, publicText }, async (stop) => {
            const until = Date.now() + 1200
            while (Date.now() < until) {
              const bodies = await Promise.all(
                Array.from({ length: 16 }, () =>
                  get(path, headers).then((response) => response.text()),
                ),
              )
              for (const body of bodies) {
                expect(body, url).not.toContain('SECRET')
                expect(body, url).not.toContain(encoded)
              }
            }
            return stop()
          })
          expect(swaps, `${url}: the toggler ran`).toBeGreaterThan(50)
          expect((await get('/')).status, `${url}: the server still answers`).toBe(200)
        } finally {
          rmSync(tree, { recursive: true, force: true })
        }
      }
      expect(uncaught).toEqual([])
    } finally {
      process.off('uncaughtException', record)
    }
  }, 90_000)
})
