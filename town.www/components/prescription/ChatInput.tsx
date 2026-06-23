"use client";

import { useState } from "react";

export function ChatInput({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  const [text, setText] = useState("");

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  return (
    <div className="flex gap-2">
      <input
        className="flex-1 rounded-lg border border-border px-3 py-2 text-sm"
        placeholder="추가 질문을 입력하세요"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        disabled={disabled}
      />
      <button
        type="button"
        onClick={submit}
        disabled={disabled || !text.trim()}
        className="rounded-lg bg-primary px-4 py-2 text-sm text-white disabled:opacity-60"
      >
        전송
      </button>
    </div>
  );
}
