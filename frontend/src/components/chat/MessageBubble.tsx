"use client";

import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "@/types";
import { SQLAccordion } from "./SQLAccordion";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { SuggestedQuestions } from "./SuggestedQuestions";
import { ChartRenderer } from "../charts/ChartRenderer";
import { RelationshipGraph } from "../graph/RelationshipGraph";
import { Shield, User, Bot, Sparkles, FileSearch } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`flex gap-3 my-4 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {/* AI Avatar */}
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shadow-md">
          <Bot className="w-4 h-4" />
        </div>
      )}

      {/* Bubble Container */}
      <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 shadow-lg ${
        isUser
          ? "bg-indigo-600 text-white rounded-tr-xs"
          : "bg-slate-900/90 border border-slate-800 text-slate-200 rounded-tl-xs backdrop-blur-md"
      }`}>
        {/* User Message */}
        {isUser ? (
          <div className="text-sm leading-relaxed font-medium whitespace-pre-wrap">
            {message.content}
          </div>
        ) : (
          /* Assistant Message */
          <div className="space-y-3">
            {/* Header: Confidence & Timestamp */}
            <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
              <div className="flex items-center gap-2">
                <Shield className="w-3.5 h-3.5 text-indigo-400" />
                <span className="text-xs font-semibold text-indigo-300">KSP Intelligence Assistant</span>
              </div>
              <div className="flex items-center gap-2">
                <ConfidenceBadge confidence={message.confidence} />
                <span className="text-[10px] text-slate-500 font-mono">
                  {formatDate(message.created_at)}
                </span>
              </div>
            </div>

            {/* Generated SQL Section */}
            {message.sql_result && <SQLAccordion sql={message.sql_result} />}

            {/* Streaming Pulse Indicator */}
            {message.isStreaming && !message.content && (
              <div className="flex items-center gap-2 text-indigo-400 text-xs py-2 font-mono">
                <Sparkles className="w-4 h-4 animate-spin" />
                <span>Thinking & querying database...</span>
              </div>
            )}

            {/* Natural Language Markdown Content */}
            {message.content && (
              <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed font-sans">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
            )}

            {/* Auto-detected Charts */}
            {message.chart_data && <ChartRenderer chart={message.chart_data} />}

            {/* Relationship Graph */}
            {message.graph_data && <RelationshipGraph graph={message.graph_data} />}

            {/* Evidence References */}
            {message.evidence_refs && message.evidence_refs.length > 0 && (
              <div className="mt-3 p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
                <div className="flex items-center gap-1.5 text-indigo-400 font-semibold mb-1">
                  <FileSearch className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Evidence References</span>
                </div>
                <ul className="space-y-1 font-mono text-[11px] text-slate-400">
                  {message.evidence_refs.map((ref, i) => (
                    <li key={i} className="truncate">• {ref}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggested Follow-up Questions */}
            <SuggestedQuestions questions={message.suggested_questions} />
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shadow-md">
          <User className="w-4 h-4" />
        </div>
      )}
    </motion.div>
  );
}
