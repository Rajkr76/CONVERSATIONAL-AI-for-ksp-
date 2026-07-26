"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import { getToken } from "@/lib/auth";

interface PDFExportButtonProps {
  conversationId: string | null;
}

export function PDFExportButton({ conversationId }: PDFExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    if (!conversationId) return;
    setIsExporting(true);

    try {
      const token = getToken();
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${API_BASE_URL}/api/export/pdf/${conversationId}`, {
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      });

      if (!response.ok) throw new Error("Export failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `KSP_Chat_${conversationId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to export PDF", err);
      alert("Failed to export PDF report.");
    } finally {
      setIsExporting(false);
    }
  };

  if (!conversationId) return null;

  return (
    <button
      onClick={handleExport}
      disabled={isExporting}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-xs font-semibold text-indigo-300 hover:text-indigo-200 transition-colors disabled:opacity-50"
      title="Export conversation as PDF report"
    >
      {isExporting ? (
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
      ) : (
        <Download className="w-3.5 h-3.5" />
      )}
      <span>{isExporting ? "Generating..." : "PDF Report"}</span>
    </button>
  );
}
