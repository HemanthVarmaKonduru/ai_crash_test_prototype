"use client"

import type React from "react"

import { useState, useRef, useEffect, useCallback } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, Send, Loader2, Bot, User, AlertCircle } from "lucide-react"
import { chatWithFirewall } from "@/lib/firewall-api"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  status?: "sending" | "success" | "error" | "blocked"
  blockedReason?: string
  threatType?: string
  latency?: number
}

// Local storage key for session ID
const CHAT_SESSION_ID_KEY = "firewall_chat_session_id"

export function ChatContent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your AI Assistant. I can help you with questions, information, and conversations. How can I assist you today?",
      timestamp: new Date(),
      status: "success",
    },
  ])
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [sessionId, setSessionId] = useState<string>("")
  
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Initialize session ID
  useEffect(() => {
    let storedSessionId = localStorage.getItem(CHAT_SESSION_ID_KEY)
    if (!storedSessionId) {
      storedSessionId = `chat_session_${Date.now()}`
      localStorage.setItem(CHAT_SESSION_ID_KEY, storedSessionId)
    }
    setSessionId(storedSessionId)
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages, isTyping])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px"
    }
  }, [input])

  const handleSend = useCallback(async () => {
    if (!input.trim() || isTyping) return

    const userInput = input.trim()
    setInput("")
    setIsTyping(true)

    try {
      // Build conversation history for API
      const conversationHistory = messages
        .filter((m) => m.status === "success")
        .map((m) => ({
          role: m.role,
          content: m.content,
        }))

      // Add user message immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: userInput,
        timestamp: new Date(),
        status: "success",
      }
      setMessages((prev) => [...prev, userMessage])

      // Call chat API (raw, no firewall evaluation)
      const chatResponse = await chatWithFirewall({
        message: userInput,
        conversation_history: conversationHistory,
        user_id: `chat_user_${Date.now()}`,
        session_id: sessionId,
      })

      // Add assistant response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: chatResponse.response,
        timestamp: new Date(),
        status: "success",
        latency: chatResponse.latency_ms,
      }

      setMessages((prev) => [...prev, assistantMessage])
      setIsTyping(false)

    } catch (error: any) {
      console.error("Error in chat:", error)
      setIsTyping(false)

      // Show error message
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `Error: ${error.message || "An error occurred while processing your message"}`,
        timestamp: new Date(),
        status: "error",
      }
      setMessages((prev) => [...prev, errorMessage])
    }
  }, [input, messages, isTyping, sessionId])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight">AI Assistant</h1>
                <p className="text-muted-foreground">
                  Ask questions and have conversations. Direct, unfiltered AI interaction.
                </p>
              </div>
            </div>
            <Badge className="bg-green-500 text-white flex items-center space-x-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
              </span>
              <span>Online</span>
            </Badge>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full" ref={scrollAreaRef}>
          <div className="max-w-4xl mx-auto p-6 space-y-6">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`flex ${message.role === "user" ? "flex-row-reverse" : "flex-row"} items-start space-x-3 max-w-[80%]`}
                >
                  {/* Avatar */}
                  <div
                    className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${
                      message.role === "user"
                        ? "bg-gradient-to-br from-blue-500 to-blue-600 ml-3"
                        : "bg-gradient-to-br from-purple-500 to-purple-600 mr-3"
                    }`}
                  >
                    {message.role === "user" ? (
                      <User className="w-5 h-5 text-white" />
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>

                  {/* Message Content */}
                  <div className="flex-1">
                    <div
                      className={`rounded-lg p-4 ${
                        message.role === "user"
                          ? "bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20"
                          : "bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20"
                      }`}
                    >
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    </div>
                    <div className="flex items-center space-x-2 mt-2 px-1">
                      <span className="text-xs text-muted-foreground">
                        {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                      {message.latency && (
                        <span className="text-xs text-muted-foreground">
                          • {message.latency.toFixed(0)}ms
                        </span>
                      )}
                      {message.status === "error" && <AlertCircle className="w-3 h-3 text-red-500" />}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="flex items-start space-x-3 max-w-[80%]">
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="rounded-lg p-4 bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20">
                      <div className="flex space-x-2">
                        <div
                          className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        />
                        <div
                          className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
                          style={{ animationDelay: "150ms" }}
                        />
                        <div
                          className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
                          style={{ animationDelay: "300ms" }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-card">
        <div className="max-w-4xl mx-auto p-4">
          <Card className="bg-gradient-to-br from-muted/50 to-transparent">
            <CardContent className="p-4">
              <div className="flex items-end space-x-3">
                <Textarea
                  ref={textareaRef}
                  placeholder="Ask me anything..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="min-h-[60px] max-h-[200px] resize-none border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0"
                  disabled={isTyping}
                />
                <Button
                  onClick={handleSend}
                  disabled={!input.trim() || isTyping}
                  className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white h-12 px-6"
                >
                  {isTyping ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">Press Enter to send, Shift+Enter for new line</p>
            </CardContent>
          </Card>
        </div>
      </div>

    </div>
  )
}
