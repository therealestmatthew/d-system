import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../../../dist/ui.css'
import { ToastProvider } from '../index'
import { Playground } from './Playground'

const root = document.getElementById('root')
if (!root) throw new Error('index.html has no #root')

createRoot(root).render(
  <StrictMode>
    <ToastProvider>
      <Playground />
    </ToastProvider>
  </StrictMode>,
)
