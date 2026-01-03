'use client'

import { useState, useEffect } from 'react'

interface Division {
  name: string
  bounds: {
    north: number
    south: number
    east: number
    west: number
  }
  description?: string
}

const DIVISIONS: Division[] = [
  {
    name: 'North Bangalore',
    bounds: { north: 13.2, south: 13.0, east: 77.7, west: 77.5 },
    description: 'Yeshwanthpur, Whitefield, Hebbal, Yelahanka',
  },
  {
    name: 'South Bangalore',
    bounds: { north: 12.95, south: 12.7, east: 77.65, west: 77.45 },
    description: 'Kanakapura, HSR Layout, Koramangala, Jayanagar',
  },
  {
    name: 'East Bangalore',
    bounds: { north: 13.05, south: 12.8, east: 77.8, west: 77.6 },
    description: 'Marathahalli, Sarjapur, Varthur',
  },
  {
    name: 'West Bangalore',
    bounds: { north: 13.1, south: 12.85, east: 77.5, west: 77.2 },
    description: 'Tumkur Road, Nelamangala, Chikballapur',
  },
]

interface MapViewProps {
  onDivisionSelect: (division: string) => void
}

export default function MapView({ onDivisionSelect }: MapViewProps) {
  const [selectedDivision, setSelectedDivision] = useState<string | null>(null)
  const [hoveredDivision, setHoveredDivision] = useState<string | null>(null)

  const handleDivisionClick = (division: Division) => {
    setSelectedDivision(division.name)
    onDivisionSelect(division.name)
  }

  return (
    <div className="w-full h-full flex flex-col bg-white">
      {/* Map Grid */}
      <div className="flex-1 grid grid-cols-2 gap-4 p-8 bg-gradient-to-br from-blue-50 to-indigo-50">
        {DIVISIONS.map((division, index) => (
          <div
            key={index}
            className={`relative rounded-xl cursor-pointer transition-all transform hover:scale-105 ${
              selectedDivision === division.name
                ? 'ring-4 ring-blue-600 shadow-xl'
                : 'shadow-lg hover:shadow-xl'
            } ${
              hoveredDivision === division.name ? 'scale-102' : ''
            }`}
            onClick={() => handleDivisionClick(division)}
            onMouseEnter={() => setHoveredDivision(division.name)}
            onMouseLeave={() => setHoveredDivision(null)}
          >
            {/* Division Card */}
            <div
              className={`w-full h-full flex flex-col justify-center items-center p-6 rounded-xl transition-colors ${
                selectedDivision === division.name
                  ? 'bg-gradient-to-br from-blue-600 to-blue-800 text-white'
                  : 'bg-white text-gray-900'
              }`}
            >
              <div className="text-3xl mb-2">
                {index === 0 && '⬆️'}
                {index === 1 && '⬇️'}
                {index === 2 && '➡️'}
                {index === 3 && '⬅️'}
              </div>
              <h3 className="text-lg font-bold text-center">{division.name}</h3>
              <p
                className={`text-sm text-center mt-2 ${
                  selectedDivision === division.name
                    ? 'text-blue-100'
                    : 'text-gray-600'
                }`}
              >
                {division.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Info Panel */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <p className="text-sm text-gray-600">
          {selectedDivision
            ? `Selected: ${selectedDivision}`
            : 'Click on any division to view properties'}
        </p>
      </div>
    </div>
  )
}
