"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { useChatStore } from "@/store/chatStore";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { Shield, Sparkles, Database, Network, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, initialize } = useAuthStore();
  const { messages, sendMessage } = useChatStore();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    initialize();
  }, [initialize]);

  useEffect(() => {
    if (isMounted && !isAuthenticated) {
      router.push("/login");
    }
  }, [isMounted, isAuthenticated, router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const quickPrompts = [
    "How many FIRs were registered in 2024?",
    "Show accused persons with prior criminal records in Bengaluru",
    "List suspicious financial transactions over ₹5,00,000",
    "Which police station has the highest crime rate?",
  ];

  if (!isMounted || !isAuthenticated) return null;

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Topbar */}
        <Topbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

        {/* Messages / Welcome View */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.length === 0 ? (
            /* Empty State / Welcome Dashboard */
            <div className="max-w-3xl mx-auto py-12 px-4 text-center">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="space-y-6"
              >
                {/* Brand Badge */}
                <div className="inline-flex p-4 rounded-3xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 shadow-2xl shadow-indigo-500/20">
                  <Shield className="w-12 h-12" />
                </div>

                <div className="space-y-2">
                  <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-100">
                    Karnataka State Police — Crime Intelligence
                  </h2>
                  <p className="text-slate-400 text-sm max-w-xl mx-auto leading-relaxed">
                    AI-powered investigation assistant converting natural language to SQL queries against our local PostgreSQL crime database.
                  </p>
                </div>

                {/* Feature Cards Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left pt-4">
                  <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
                    <Database className="w-5 h-5 text-indigo-400 mb-2" />
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">Natural Language → SQL</h3>
                    <p className="text-xs text-slate-400 mt-1">Queries 11 normalized database tables with built-in read-only safety validation.</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
                    <Sparkles className="w-5 h-5 text-amber-400 mb-2" />
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">Auto Visualizations</h3>
                    <p className="text-xs text-slate-400 mt-1">Automatically renders Bar, Line, Pie, and Area charts from query result sets.</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
                    <Network className="w-5 h-5 text-rose-400 mb-2" />
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">Relationship Graphs</h3>
                    <p className="text-xs text-slate-400 mt-1">Extracts entity links between FIRs, accused, victims, officers, and transactions.</p>
                  </div>
                </div>

                {/* Quick Starter Chips */}
                <div className="pt-6 border-t border-slate-800/80">
                  <div className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-wider mb-3">
                    Sample Investigation Queries
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                    {quickPrompts.map((prompt, i) => (
                      <button
                        key={i}
                        onClick={() => sendMessage(prompt)}
                        className="group flex items-center justify-between p-3 rounded-xl bg-slate-900/80 hover:bg-indigo-950/40 border border-slate-800 hover:border-indigo-500/40 text-xs text-slate-300 hover:text-indigo-200 transition-all"
                      >
                        <span>{prompt}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
                      </button>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>
          ) : (
            /* Active Message List */
            <div className="max-w-4xl mx-auto space-y-4">
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Fixed Chat Input */}
        <ChatInput />
      </div>
    </div>
  );
}
