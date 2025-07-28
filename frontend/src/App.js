import { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [sessionId, setSessionId] = useState(() => {
    const saved = localStorage.getItem("chatSessionId");
    return saved || `session_${Date.now()}`;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [notes, setNotes] = useState([]);
  const [showNotesPanel, setShowNotesPanel] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    localStorage.setItem("chatSessionId", sessionId);
  }, [sessionId]);

  // Load conversation history
  useEffect(() => {
    loadConversationHistory();
    loadNotes();
  }, [sessionId]);

  const loadConversationHistory = async () => {
    try {
      const response = await axios.get(`${API}/conversations/${sessionId}`);
      const conversations = response.data.conversations;
      
      // Flatten all messages from conversations
      const allMessages = [];
      conversations.forEach(conv => {
        if (conv.messages) {
          allMessages.push(...conv.messages);
        }
      });
      
      // Sort by timestamp
      allMessages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      setMessages(allMessages);
    } catch (error) {
      console.error("Error loading conversation history:", error);
    }
  };

  const loadNotes = async () => {
    try {
      const response = await axios.get(`${API}/notes`);
      setNotes(response.data.notes);
    } catch (error) {
      console.error("Error loading notes:", error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: `msg_${Date.now()}`,
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: inputMessage,
        session_id: sessionId
      });

      const assistantMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: "assistant",
        content: response.data.message,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        id: `msg_${Date.now()}_error`,
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearConversation = async () => {
    try {
      await axios.delete(`${API}/conversations/clear/${sessionId}`);
      setMessages([]);
    } catch (error) {
      console.error("Error clearing conversation:", error);
    }
  };

  const startNewSession = () => {
    const newSessionId = `session_${Date.now()}`;
    setSessionId(newSessionId);
    setMessages([]);
  };

  const uploadFiles = async (files) => {
    if (!files.length) return;

    const formData = new FormData();
    Array.from(files).forEach(file => {
      if (file.name.endsWith('.md')) {
        formData.append('files', file);
      }
    });

    try {
      setUploadStatus("Uploading...");
      const response = await axios.post(`${API}/notes/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadStatus(`Uploaded ${response.data.uploaded_notes} notes successfully!`);
      loadNotes();
      setTimeout(() => setUploadStatus(""), 3000);
    } catch (error) {
      console.error("Error uploading files:", error);
      setUploadStatus("Error uploading files");
      setTimeout(() => setUploadStatus(""), 3000);
    }
  };

  const handleFileSelect = (e) => {
    uploadFiles(e.target.files);
    e.target.value = "";
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900 mb-4">
            Continuous Memory ChatGPT
          </h1>
          
          <div className="space-y-2">
            <button
              onClick={startNewSession}
              className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              New Session
            </button>
            
            <button
              onClick={clearConversation}
              className="w-full px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
            >
              Clear Current Session
            </button>
            
            <button
              onClick={() => setShowNotesPanel(!showNotesPanel)}
              className="w-full px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
            >
              {showNotesPanel ? 'Hide' : 'Show'} Notes ({notes.length})
            </button>
          </div>
        </div>

        {/* Obsidian Notes Upload */}
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-2">Obsidian Notes</h3>
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm mb-2"
          >
            Upload .md Files
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".md"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {uploadStatus && (
            <p className="text-xs text-purple-600 mt-1">{uploadStatus}</p>
          )}
        </div>

        {/* Notes Panel */}
        {showNotesPanel && (
          <div className="flex-1 overflow-y-auto p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Your Notes</h3>
            {notes.length === 0 ? (
              <p className="text-gray-500 text-sm">No notes uploaded yet</p>
            ) : (
              <div className="space-y-2">
                {notes.map(note => (
                  <div key={note.id} className="bg-gray-50 p-2 rounded-lg">
                    <h4 className="font-medium text-sm text-gray-900">{note.title}</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {note.content.substring(0, 100)}...
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Session Info */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-600">Session: {sessionId.split('_')[1]}</p>
          <p className="text-xs text-gray-600">{messages.length} messages</p>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="bg-white rounded-xl p-8 shadow-sm max-w-2xl mx-auto">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Welcome to Continuous Memory ChatGPT! 🧠
                </h2>
                <p className="text-gray-600 mb-6">
                  I remember all our conversations and can access your Obsidian notes. 
                  Start chatting and I'll maintain context across all our interactions!
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-blue-800 mb-2">🧠 Continuous Memory</h3>
                    <p>I remember everything from our previous conversations in this session</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-purple-800 mb-2">📝 Obsidian Integration</h3>
                    <p>Upload your .md files and I'll reference them when relevant</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-900 shadow-sm border border-gray-200'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div
                  className={`text-xs mt-2 ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}
                >
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 shadow-sm border border-gray-200 rounded-2xl px-4 py-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="flex space-x-4 max-w-4xl mx-auto">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
              className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
              rows="1"
              style={{
                minHeight: '48px',
                maxHeight: '120px'
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;