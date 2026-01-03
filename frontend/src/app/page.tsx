'use client'

import { useState } from 'react'
import MapView from '@/components/MapView'
import ChatInterface from '@/components/ChatInterface'
import { Card } from '@/components/ui/Card'

export default function Home() {
  const [selectedDivision, setSelectedDivision] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'map' | 'chat'>('map')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🏠 AI Property Consultant
              </h1>
              <p className="text-gray-600 mt-1">
                Find your perfect property in Bangalore using AI
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('map')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  viewMode === 'map'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                🗺️ Map View
              </button>
              <button
                onClick={() => setViewMode('chat')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  viewMode === 'chat'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                💬 Chat
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {viewMode === 'map' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <Card className="h-[600px]">
                <MapView onDivisionSelect={setSelectedDivision} />
              </Card>
            </div>
            <div className="lg:col-span-1">
              <Card className="h-[600px] overflow-y-auto">
                <div className="p-6">
                  <h2 className="text-xl font-bold mb-4">Selected Area</h2>
                  {selectedDivision ? (
                    <div>
                      <p className="text-lg font-semibold text-blue-600 mb-4">
                        {selectedDivision}
                      </p>
                      <div className="bg-blue-50 p-4 rounded-lg mb-4">
                        <p className="text-sm text-gray-700">
                          Loading properties for this area...
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-500">
                      Select a division on the map to see available properties
                    </p>
                  )}
                </div>
              </Card>
            </div>
          </div>
        ) : (
          <div className="max-w-2xl mx-auto">
            <Card className="min-h-[600px]">
              <ChatInterface />
            </Card>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">About</h3>
              <p className="text-gray-600 text-sm">
                AI-powered property search for Bangalore
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Divisions</h3>
              <ul className="text-gray-600 text-sm space-y-1">
                <li>North Bangalore</li>
                <li>South Bangalore</li>
                <li>East Bangalore</li>
                <li>West Bangalore</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Contact</h3>
              <p className="text-gray-600 text-sm">
                Email: info@aipropertyconsultant.com
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
