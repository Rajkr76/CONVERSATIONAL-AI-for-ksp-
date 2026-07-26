"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Database, Code, Clock, Table, CopyCheck, Copy } from "lucide-react";
import { SQLResult } from "@/types";

interface SQLAccordionProps {
  sql: SQLResult;
}

export function SQLAccordion({ sql }: SQLAccordionProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"sql" | "table">("sql");
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sql.query);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-3 border border-indigo-500/20 rounded-lg overflow-hidden bg-slate-900/60 backdrop-blur-sm text-xs font-mono">
      {/* Header Bar */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 flex items-center justify-between bg-slate-800/80 hover:bg-slate-800 transition-colors text-slate-300"
      >
        <div className="flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-indigo-400" />
          <span className="font-semibold text-indigo-300">Generated SQL Query</span>
          <span className="text-slate-500">•</span>
          <span className="text-emerald-400 font-sans font-medium">
            {sql.row_count} {sql.row_count === 1 ? "row" : "rows"} returned
          </span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-400 flex items-center gap-1 font-sans">
            <Clock className="w-3 h-3 text-slate-500" />
            {sql.execution_time_ms} ms
          </span>
        </div>
        <div className="flex items-center gap-1 text-slate-400">
          <span className="text-[10px] uppercase font-sans font-semibold tracking-wider text-indigo-400/80">
            {isOpen ? "Hide Query" : "Show Query"}
          </span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Accordion Content */}
      {isOpen && (
        <div className="p-3 border-t border-indigo-500/10 space-y-3">
          {/* Tab Selector & Copy */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab("sql")}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs transition-colors ${
                  activeTab === "sql"
                    ? "bg-indigo-600 text-white font-medium"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                <Code className="w-3 h-3" /> SQL
              </button>
              <button
                onClick={() => setActiveTab("table")}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs transition-colors ${
                  activeTab === "table"
                    ? "bg-indigo-600 text-white font-medium"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                <Table className="w-3 h-3" /> Result Table
              </button>
            </div>

            {activeTab === "sql" && (
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-slate-400 hover:text-indigo-300 transition-colors text-[11px]"
              >
                {copied ? <CopyCheck className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                {copied ? "Copied!" : "Copy SQL"}
              </button>
            )}
          </div>

          {/* SQL Code View */}
          {activeTab === "sql" && (
            <pre className="p-3 bg-slate-950 rounded border border-slate-800/80 overflow-x-auto text-indigo-200 leading-relaxed font-mono selection:bg-indigo-900 selection:text-indigo-100">
              <code>{sql.query}</code>
            </pre>
          )}

          {/* Result Table View */}
          {activeTab === "table" && (
            <div className="overflow-x-auto max-h-60 rounded border border-slate-800">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-800/90 text-indigo-300 sticky top-0 font-sans font-semibold">
                    {sql.columns.map((col) => (
                      <th key={col} className="p-2 border-b border-slate-700 whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sql.rows.slice(0, 15).map((row, idx) => (
                    <tr key={idx} className="border-b border-slate-800/50 hover:bg-slate-800/40 text-slate-300">
                      {sql.columns.map((col) => (
                        <td key={col} className="p-2 max-w-xs truncate whitespace-nowrap">
                          {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-slate-600">null</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {sql.rows.length > 15 && (
                <div className="p-2 text-center text-slate-500 font-sans italic bg-slate-900">
                  Showing 15 of {sql.row_count} rows
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
