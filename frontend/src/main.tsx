import React from 'react'
import ReactDOM from 'react-dom/client'
import { Toaster } from 'sonner'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Toaster
      position="bottom-right"
      theme="dark"
      richColors
      toastOptions={{
        style: {
          background: '#13131a',
          border: '1px solid #1e293b',
          color: '#f8fafc',
        },
        duration: 4000,
      }}
    />
    <App />
  </React.StrictMode>,
)
