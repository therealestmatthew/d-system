import ErrorBoundary from './stage/ErrorBoundary'
import StagePage from './stage/StagePage'

/** The stage, inside a last-resort error boundary: a render error that escapes every panel's own
 * boundary shows an error and a Retry button instead of a blank page (idea 000569). */
export default function App() {
  return (
    <ErrorBoundary label="The stage">
      <StagePage />
    </ErrorBoundary>
  )
}
