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
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
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
): Promise<(path: string) => Promise<Response>> {
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
  return (path) => fetch(`http://127.0.0.1:${address.port}${path}`)
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

// A child process that, until it is told to stop, renames a regular file and a symlink to an
// outside file over one name, as fast as it can. It prints how many swaps it made.
const TOGGLER = `
const { renameSync, rmSync, symlinkSync, writeFileSync } = require('node:fs')
const [target, secret, publicText] = process.argv.slice(1)
let swaps = 0
let stop = false
process.stdin.on('data', () => { stop = true })
const step = () => {
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

describe('serving under concurrent renames (check-then-serve race)', () => {
  // Each case gets its own tree and server, with no other symlink in it, and runs a toggler for a
  // bounded time with 16 requests in flight. Against the round-2 guard, which checked a name and
  // then let Vite or the route open it again, the same harness got the outside file back.
  it('serves no outside byte by any route while a name flips to a symlink and back', async () => {
    const uncaught: unknown[] = []
    const record = (error: unknown) => uncaught.push(error)
    process.on('uncaughtException', record)
    try {
      const cases: [string, string, string][] = [
        ['data/layouts/race.json', `${LAYOUTS}race.json`, '{}'],
        ['pub/race.html', '/generated-overview/race.html', 'PUBLIC'],
        ['repo/docs/race.txt', '/workbench-file/docs/race.txt', 'PUBLIC'],
        ['site/public/race.txt', '/race.txt', 'PUBLIC'],
        ['site/data/race.txt', '/@fs<site>/data/race.txt', 'PUBLIC'],
        ['site/data/race.txt', '/data/race.txt?raw', 'PUBLIC'],
        ['site/data/race.ts', '/data/race.ts', 'export {}'],
        ['site/race.html', '/race.html', '<p>PUBLIC</p>'],
      ]
      for (const [relative, url, publicText] of cases) {
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
        const secret = join(tree, 'outside', relative.endsWith('.ts') ? 'secret.ts' : 'secret.txt')
        writeFileSync(secret, relative.endsWith('.ts') ? 'export default "SECRET"' : 'SECRET')
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
        const toggler = spawn(process.execPath, ['-e', TOGGLER, target, secret, publicText])
        let swaps = ''
        toggler.stdout.on('data', (chunk: Buffer) => (swaps += chunk.toString()))
        const exited = new Promise((resolve) => toggler.on('exit', resolve))
        const path = url.replace('<site>', raceSite)
        const until = Date.now() + 1200
        while (Date.now() < until) {
          const bodies = await Promise.all(
            Array.from({ length: 16 }, () => get(path).then((response) => response.text())),
          )
          for (const body of bodies) expect(body, url).not.toContain('SECRET')
        }
        toggler.stdin.write('stop')
        await exited
        expect(Number(swaps), `${url}: the toggler ran`).toBeGreaterThan(50)
        expect((await get('/')).status, `${url}: the server still answers`).toBe(200)
      }
      expect(uncaught).toEqual([])
    } finally {
      process.off('uncaughtException', record)
    }
  }, 90_000)
})
