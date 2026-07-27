"use client";

import { useEffect } from "react";
import { Plus, MessageSquare, Trash2, Shield, ChevronLeft, ChevronRight } from "lucide-react";
import { useChatStore } from "@/store/chatStore";
import { motion, AnimatePresence } from "framer-motion";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const {
    conversations,
    currentConversationId,
    loadConversations,
    selectConversation,
    newChat,
    deleteConversation,
  } = useChatStore();

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return (
    <aside
      className={`fixed sm:static inset-y-0 left-0 z-40 flex flex-col bg-slate-950/95 border-r border-slate-800 transition-all duration-300 backdrop-blur-xl ${
        isOpen ? "w-72" : "w-0 sm:w-16"
      } overflow-hidden`}
    >
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between min-w-70">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-linear-to-br from-indigo-500 to-indigo-700 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 font-bold">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-sm text-slate-100 tracking-tight">KSP Intelligence</h1>
            <p className="text-[10px] text-indigo-400 font-mono">Karnataka State Police</p>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={newChat}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all active:scale-95"
        >
          <Plus className="w-4 h-4" />
          <span>New Investigation</span>
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
        <div className="px-3 py-1 text-[11px] font-semibold text-slate-500 uppercase tracking-wider font-mono">
          History ({conversations.length})
        </div>

        {conversations.length === 0 ? (
          <div className="p-4 text-center text-slate-600 text-xs italic">
            No previous investigations
          </div>
        ) : (
          conversations.map((conv) => {
            const isSelected = conv.conversation_id === currentConversationId;
            return (
              <div
                key={conv.conversation_id}
                onClick={() => selectConversation(conv.conversation_id)}
                className={`group flex items-center justify-between p-2.5 rounded-xl cursor-pointer text-xs transition-all ${
                  isSelected
                    ? "bg-indigo-600/20 border border-indigo-500/40 text-indigo-200 font-medium"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isSelected ? "text-indigo-400" : "text-slate-500"}`} />
                  <span className="truncate">{conv.title}</span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConversation(conv.conversation_id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-rose-400 transition-opacity"
                  title="Delete conversation"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer / Toggle Button */}
      <div className="p-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500 font-mono">
        <span>v1.0.0 (On-Premise)</span>
        <button
          onClick={onToggle}
          className="p-1 rounded hover:bg-slate-900 text-slate-400"
        >
          {isOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}
