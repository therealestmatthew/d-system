# ui-kit

The team's UX component kit (design guide: `docs/architecture/ARCH-001-ux-design-guide.md`;
decision: `docs/decisions/ADR-001-ux-kit-on-react-aria.md`).

## React package

React 19 components on React Aria Components, in `src/react/` and exported from
`src/react/index.ts`. They render the class contract; the styles come from `dist/ui.css`.

From this folder:

```
npm install         # exact versions pinned in package.json / package-lock.json
npm run dev         # playground at http://localhost:5199 (every component, theme/accent/density controls)
npm run typecheck   # tsc --noEmit
npm test            # vitest + jsdom + Testing Library + axe-core
npm run build       # typecheck, then build the playground into playground-dist/
```
