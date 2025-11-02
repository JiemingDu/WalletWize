import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Questionnaire from './pages/Questionnaire'
import App from './App' // (keep as a test page if you want)

const router = createBrowserRouter([
  { path: '/', element: <Questionnaire /> },
  { path: '/test', element: <App /> }, // optional test route
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)