import axe from 'axe-core'

/**
 * Runs axe-core on a rendered container and returns the violations. Colour contrast is off because
 * jsdom has no layout or computed colours; the token test checks contrast pairs instead.
 */
export async function axeViolations(container: Element) {
  const result = await axe.run(container, {
    rules: { 'color-contrast': { enabled: false } },
  })
  return result.violations.map((v) => ({
    id: v.id,
    help: v.help,
    nodes: v.nodes.map((n) => n.target.join(' ')),
  }))
}
