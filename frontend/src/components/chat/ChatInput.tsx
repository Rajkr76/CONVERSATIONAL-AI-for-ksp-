"use client";

import { useState, useRef, KeyboardEvent } from "react";
import { Send, Languages, Sparkles } from "lucide-react";
import { useChatStore } from "@/store/chatStore";
import { VoiceInput } from "../shared/VoiceInput";

export function ChatInput() {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { sendMessage, isStreaming, language, setLanguage, statusText } = useChatStore();

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    sendMessage(input);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceTranscript = (text: string) => {
    setInput((prev) => (prev ? `${prev} ${text}` : text));
  };

  return (
    <div className="p-3 sm:p-4 bg-slate-900/90 border-t border-slate-800 backdrop-blur-xl sticky bottom-0">
      {/* Streaming Pipeline Status Bar */}
      {isStreaming && statusText && (
        <div className="mb-2.5 px-3 py-1.5 rounded-lg bg-indigo-950/60 border border-indigo-500/20 text-xs text-indigo-300 font-mono flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-spin" />
          <span>{statusText}</span>
        </div>
      )}

      {/* Input Row */}
      <div className="flex items-end gap-2 bg-slate-950/80 border border-slate-800 focus-within:border-indigo-500/60 rounded-2xl p-2 transition-all shadow-xl">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            language === "kn"
              ? "ಕರ್ನಾಟಕ ಪೊಲೀಸ್ ಡೇಟಾಬೇಸ್ میں ತನಿಖೆ ಮಾಡಿ (Ask a question in English or Kannada)..."
              : "Ask about FIRs, accused history, financial trails, officer records..."
          }
          rows={1}
          disabled={isStreaming}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm p-2 resize-none outline-none max-h-32 min-h-[40px] leading-relaxed"
        />

        {/* Action Controls */}
        <div className="flex items-center gap-1.5 pb-0.5">
          {/* Language Toggle (English / Kannada) */}
          <button
            type="button"
            onClick={() => setLanguage(language === "en" ? "kn" : "en")}
            className={`px-2 py-1.5 rounded-xl border text-xs font-semibold font-mono transition-all flex items-center gap-1 ${
              language === "kn"
                ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                : "bg-slate-800/80 border-slate-700/80 text-slate-400 hover:text-slate-200"
            }`}
            title="Toggle Language (English / Kannada)"
          >
            <Languages className="w-3.5 h-3.5" />
            <span>{language === "kn" ? "ಕನ್ನಡ" : "EN"}</span>
          </button>

          {/* Voice Input */}
          <VoiceInput onTranscript={handleVoiceTranscript} language={language} />

          {/* Send Button */}
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white disabled:opacity-40 disabled:hover:bg-indigo-600 transition-all shadow-md shadow-indigo-600/30"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
