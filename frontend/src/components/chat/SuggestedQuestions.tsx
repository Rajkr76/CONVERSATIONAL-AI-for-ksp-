"use client";

import { motion } from "framer-motion";
import { Sparkles, ArrowRight } from "lucide-react";
import { useChatStore } from "@/store/chatStore";

interface SuggestedQuestionsProps {
  questions?: string[];
}

export function SuggestedQuestions({ questions }: SuggestedQuestionsProps) {
  const { sendMessage } = useChatStore();

  if (!questions || questions.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-slate-800/80">
      <div className="flex items-center gap-1.5 text-xs text-indigo-400 font-semibold mb-2">
        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
        <span>Suggested Follow-up Questions</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, idx) => (
          <motion.button
            key={idx}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: idx * 0.05 }}
            onClick={() => sendMessage(q)}
            className="group flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-950/40 hover:bg-indigo-900/60 border border-indigo-800/40 text-xs text-slate-300 hover:text-white transition-all text-left"
          >
            <span>{q}</span>
            <ArrowRight className="w-3 h-3 text-indigo-400 group-hover:translate-x-0.5 transition-transform" />
          </motion.button>
        ))}
      </div>
    </div>
  );
}
