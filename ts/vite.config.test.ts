// @vitest-environment node
//
// The dev server's symlink guard (`refuseSymlinkEscapes` in vite.config.ts, security review of
// `phase-arch-07`, 2026-10-09). Each case builds a throwaway tree with a symlink that points out of
// the allowed directory and runs a real Vite dev server over it: first without the guard, to show
// Vite itself serves the outside file (so the test reproduces the hole rather than assuming it),
// then with the guard, which must refuse it while still serving an ordinary allowed file.
import { mkdirSync, mkdtempSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createServer, type Plugin, type ViteDevServer } from 'vite'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { refuseSymlinkEscapes } from './vite.config'

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
})

afterEach(async () => {
  await Promise.all(servers.splice(0).map((server) => server.close()))
  rmSync(base, { recursive: true, force: true })
})

async function serve(plugins: Plugin[]): Promise<(path: string) => Promise<Response>> {
  const server = await createServer({
    configFile: false,
    root: site,
    logLevel: 'silent',
    plugins,
    optimizeDeps: { noDiscovery: true },
    server: { port: 0, hmr: false, fs: { allow: [site] } },
  })
  servers.push(server)
  await server.listen()
  const address = server.httpServer?.address()
  if (address === null || typeof address !== 'object') throw new Error('no listening address')
  return (path) => fetch(`http://127.0.0.1:${address.port}${path}`)
}

describe('refuseSymlinkEscapes', () => {
  it('reproduces the hole: without the guard Vite serves a file outside the allow-list', async () => {
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
})
