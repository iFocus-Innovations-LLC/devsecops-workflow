import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import './App.css'

function App() {
  const [healthStatus, setHealthStatus] = useState(null)
  const [workflowStatus, setWorkflowStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api'

  useEffect(() => {
    checkBackendHealth()
    fetchWorkflowStatus()
  }, [])

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:5001/health')
      const data = await response.json()
      setHealthStatus(data)
    } catch (err) {
      setError('Backend is not responding. Please ensure the backend server is running.')
    } finally {
      setLoading(false)
    }
  }

  const fetchWorkflowStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/workflow/status`)
      const data = await response.json()
      setWorkflowStatus(data.status)
    } catch (err) {
      console.error('Failed to fetch workflow status:', err)
    }
  }

  const runFullWorkflow = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/workflow/run-full`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      const data = await response.json()
      if (data.success) {
        alert('Workflow completed successfully!')
        fetchWorkflowStatus()
      } else {
        alert('Workflow failed: ' + data.message)
      }
    } catch (err) {
      alert('Failed to run workflow: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading DevSecOps Workflow...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-600">Connection Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={checkBackendHealth} className="w-full">
              Retry Connection
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            DevSecOps Video Workflow
          </h1>
          <p className="text-gray-600">
            Automated content creation and publishing pipeline
          </p>
        </div>

        {/* Health Status */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Badge variant={healthStatus?.status === 'healthy' ? 'default' : 'destructive'}>
                {healthStatus?.status || 'unknown'}
              </Badge>
              Backend Status
            </CardTitle>
            <CardDescription>{healthStatus?.message}</CardDescription>
          </CardHeader>
        </Card>

        {/* Workflow Status */}
        {workflowStatus && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Content Topics</CardTitle>
                <CardDescription>Planned and approved topics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total:</span>
                    <span className="font-semibold">{workflowStatus.topics?.total || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Approved:</span>
                    <span className="font-semibold text-green-600">{workflowStatus.topics?.approved || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Video Scripts</CardTitle>
                <CardDescription>Generated and produced scripts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total:</span>
                    <span className="font-semibold">{workflowStatus.scripts?.total || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Produced:</span>
                    <span className="font-semibold text-blue-600">{workflowStatus.scripts?.produced || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Video Projects</CardTitle>
                <CardDescription>Created and published videos</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total:</span>
                    <span className="font-semibold">{workflowStatus.projects?.total || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Published:</span>
                    <span className="font-semibold text-purple-600">{workflowStatus.projects?.published || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Publishing</CardTitle>
                <CardDescription>YouTube publishing records</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total:</span>
                    <span className="font-semibold">{workflowStatus.publishing?.total || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Published:</span>
                    <span className="font-semibold text-orange-600">{workflowStatus.publishing?.published || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Workflow Actions</CardTitle>
            <CardDescription>Run automated content creation pipeline</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <Button 
                onClick={runFullWorkflow} 
                disabled={loading}
                className="flex-1"
              >
                {loading ? 'Running...' : 'Run Full Workflow'}
              </Button>
              <Button 
                onClick={fetchWorkflowStatus}
                variant="outline"
              >
                Refresh Status
              </Button>
            </div>
            <p className="text-sm text-gray-500">
              This will execute the complete pipeline: content planning → script generation → video production → YouTube publishing
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
