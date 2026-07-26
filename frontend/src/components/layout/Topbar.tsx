"use client";

import { useAuthStore } from "@/store/authStore";
import { useChatStore } from "@/store/chatStore";
import { PDFExportButton } from "../shared/PDFExportButton";
import { Menu, LogOut, ShieldCheck, Database, Server } from "lucide-react";

interface TopbarProps {
  onToggleSidebar: () => void;
}

export function Topbar({ onToggleSidebar }: TopbarProps) {
  const { user, logout } = useAuthStore();
  const { currentConversationId } = useChatStore();

  return (
    <header className="h-14 px-4 bg-slate-950/80 border-b border-slate-800 backdrop-blur-xl flex items-center justify-between sticky top-0 z-30">
      {/* Left: Sidebar Toggle & Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-300">Karnataka State Police</span>
          <span className="text-slate-600">•</span>
          <div className="flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full font-mono">
            <Server className="w-3 h-3" />
            <span>Local LLM Online</span>
          </div>
        </div>
      </div>

      {/* Right: PDF Export, User Profile & Logout */}
      <div className="flex items-center gap-3">
        {/* PDF Export */}
        <PDFExportButton conversationId={currentConversationId} />

        {/* User Info */}
        {user && (
          <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
            <div className="w-7 h-7 rounded-full bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 flex items-center justify-center font-bold text-xs">
              {user.full_name ? user.full_name[0] : "U"}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-semibold text-slate-200">{user.full_name}</div>
              <div className="text-[10px] text-slate-500 font-mono capitalize">{user.role} ({user.badge_number || "KSP"})</div>
            </div>
            <button
              onClick={logout}
              className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors ml-1"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
