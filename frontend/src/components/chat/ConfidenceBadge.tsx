"use client";

import { ShieldCheck, ShieldAlert } from "lucide-react";

interface ConfidenceBadgeProps {
  confidence?: number;
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  if (confidence === undefined || confidence === null) return null;

  const score = Math.round(confidence * 100);

  let badgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
  let Icon = ShieldCheck;
  let label = "High Confidence";

  if (score < 50) {
    badgeColor = "bg-rose-500/10 text-rose-400 border-rose-500/30";
    Icon = ShieldAlert;
    label = "Low Confidence";
  } else if (score < 75) {
    badgeColor = "bg-amber-500/10 text-amber-400 border-amber-500/30";
    Icon = ShieldAlert;
    label = "Moderate Confidence";
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium backdrop-blur-sm ${badgeColor}`}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{label} ({score}%)</span>
    </div>
  );
}
