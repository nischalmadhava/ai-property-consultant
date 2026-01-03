'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Button } from './ui/Button'
import { Card } from './ui/Card'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface Property {
  id: number
  name: string
  location: string
  area: number
  price: number
  price_per_sqft: number
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Hello! 👋 I am your AI Property Consultant. I can help you find the perfect property in Bangalore. You can describe what you are looking for in plain English, for example:\n\n"I\'m looking for a plot in South Bangalore (Kanakapura area), around 30x40 feet, with a budget of 40-45 lakhs."',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [properties, setProperties] = useState<Property[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim()) return

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Send to backend
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: input,
        user_id: 'web_user',
      })

      const { response: assistantResponse, properties: foundProperties } = response.data

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: assistantResponse,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])

      // Update properties
      if (foundProperties) {
        setProperties(foundProperties)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content:
          '❌ Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-white text-gray-900 border border-gray-200 rounded-bl-none'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap break-words">
                {message.content}
              </p>
              <p
                className={`text-xs mt-1 ${
                  message.role === 'user'
                    ? 'text-blue-100'
                    : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {/* Properties Display */}
        {properties.length > 0 && (
          <div className="mt-6">
            <h3 className="font-bold text-gray-900 mb-3">Found Properties:</h3>
            <div className="space-y-2">
              {properties.map((prop) => (
                <Card key={prop.id} className="p-3">
                  <p className="font-semibold text-gray-900">{prop.name}</p>
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mt-2">
                    <div>📍 {prop.location}</div>
                    <div>📐 {prop.area} sqft</div>
                    <div>💰 ₹{(prop.price / 100000).toFixed(1)} L</div>
                    <div>📊 ₹{prop.price_per_sqft.toFixed(0)}/sqft</div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe the property you are looking for..."
            className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-600"
            rows={3}
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()}
            className="self-end"
          >
            {isLoading ? '⏳ Searching...' : '📤 Send'}
          </Button>
        </div>
      </div>
    </div>
  )
}
