"use client"

import { useState, useEffect, useRef } from "react"
import { MessageCircle, X, Send, Bot, User, RefreshCw } from "lucide-react"

type Message = {
    id: string
    role: "user" | "agent"
    text: string
}

export function AgentChatWidget() {
    const [isOpen, setIsOpen] = useState(false)
    const [input, setInput] = useState("")
    const [messages, setMessages] = useState<Message[]>([
        { id: "init", role: "agent", text: "Hello! I'm your Resume Assistant. How can I help you today?" }
    ])
    const [isConnected, setIsConnected] = useState(false)
    const [isTyping, setIsTyping] = useState(false)

    const ws = useRef<WebSocket | null>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, isOpen])

    // Connection Logic
    useEffect(() => {
        if (isOpen && !ws.current) {
            const sessionId = "session-" + Math.random().toString(36).substring(7)
            // Connect to port 8005 (based on our verification)
            const socket = new WebSocket(`ws://localhost:8005/ws/chat/${sessionId}`)

            socket.onopen = () => {
                setIsConnected(true)
                console.log("Connected to Agent")
            }

            socket.onclose = () => {
                setIsConnected(false)
                console.log("Disconnected from Agent")
                ws.current = null
            }

            socket.onerror = (error) => {
                console.error("WebSocket Error:", error)
                setIsConnected(false)
            }

            socket.onmessage = (event) => {
                try {
                    const payload = JSON.parse(event.data)
                    // Handle specific ADK event types if needed
                    // For now we assume payload.text is the chunk or message
                    if (payload.text) {
                        setMessages((prev: Message[]) => {
                            // If the last message was from agent, maybe append? 
                            // For simplicity, just add new bubble for now
                            // Or better, ADK streams... 
                            // Let's just append as new message for each "event" with text
                            return [...prev, { id: Date.now().toString(), role: "agent", text: payload.text }]
                        })
                        setIsTyping(false)
                    }
                } catch (e) {
                    // Plain text fallback
                    if (event.data) {
                        setMessages((prev: Message[]) => [...prev, { id: Date.now().toString(), role: "agent", text: event.data }])
                    }
                }
            }

            ws.current = socket
        }

        // Cleanup on unmount (or close? maybe keep open if just minimized)
        // For now, keep open only if component mounted
        return () => {
            // ws.current?.close() 
        }
    }, [isOpen])


    const sendMessage = () => {
        if (!input.trim() || !ws.current || !isConnected) return

        const userMsg: Message = { id: Date.now().toString(), role: "user", text: input }
        setMessages((prev: Message[]) => [...prev, userMsg])
        setInput("")
        setIsTyping(true)

        // Send to backend
        ws.current.send(JSON.stringify({ text: userMsg.text }))
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            {/* Chat Window */}
            {isOpen && (
                <div className="bg-white border rounded-lg shadow-xl w-80 md:w-96 h-[500px] flex flex-col mb-4 overflow-hidden transition-all animate-in slide-in-from-bottom-5 fade-in duration-300">
                    {/* Header */}
                    <div className="bg-slate-900 text-white p-4 flex justify-between items-center">
                        <div className="flex items-center gap-2">
                            <Bot className="w-5 h-5" />
                            <span className="font-semibold">Rescue Agent</span>
                            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
                        </div>
                        <button onClick={() => setIsOpen(false)} className="hover:bg-slate-700 p-1 rounded">
                            <X className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 bg-slate-50 space-y-4">
                        {messages.map((msg: Message) => (
                            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] p-3 rounded-lg text-sm ${msg.role === 'user'
                                    ? 'bg-blue-600 text-white rounded-br-none'
                                    : 'bg-white border text-slate-800 rounded-bl-none shadow-sm'
                                    }`}>
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div className="bg-white border p-3 rounded-lg rounded-bl-none text-slate-400 text-xs flex items-center gap-1 shadow-sm">
                                    <Bot className="w-3 h-3" /> typing...
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-3 bg-white border-t flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Type a message..."
                            className="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={!isConnected}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!isConnected || !input.trim()}
                            className="bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}

            {/* Toggle Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-transform hover:scale-110 flex items-center justify-center"
                >
                    <MessageCircle className="w-6 h-6" />
                </button>
            )}
        </div>
    )
}
