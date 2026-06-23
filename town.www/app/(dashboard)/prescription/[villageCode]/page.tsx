"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { villageApi } from "@/lib/api/village";
import { prescriptionApi } from "@/lib/api/prescription";
import { setLastVillageCode } from "@/lib/village/lastVillage";
import { useChatStore } from "@/lib/store/chatStore";
import { useAuthStore } from "@/lib/store/authStore";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { PrescriptionCard } from "@/components/prescription/PrescriptionCard";
import { ChatBubble } from "@/components/prescription/ChatBubble";
import { QuickQuestionBar } from "@/components/prescription/QuickQuestionBar";
import { ChatInput } from "@/components/prescription/ChatInput";
import { dedupePrescriptionsByRank } from "@/lib/utils/prescription";
import type { PrescriptionItem, VillageDetail } from "@/lib/types";

export default function PrescriptionPage({ params }: { params: { villageCode: string } }) {
  const [detail, setDetail] = useState<VillageDetail | null>(null);
  const [items, setItems] = useState<PrescriptionItem[]>([]);
  const [noPrescriptionReason, setNoPrescriptionReason] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [activeItem, setActiveItem] = useState<PrescriptionItem | null>(null);
  const { messages, streaming, appendUser, startAssistant, appendToLastAssistant, finishAssistant, reset } =
    useChatStore();
  const token = useAuthStore((s) => s.token);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLastVillageCode(params.villageCode);
    reset();
    (async () => {
      setNoPrescriptionReason(null);
      setLoadError(null);
      setItems([]);
      try {
        const d = await villageApi.getDetail(params.villageCode);
        if (cancelled) return;
        setDetail(d);

        const list = await prescriptionApi.getByVillage(d.village_id);
        if (cancelled) return;

        const prescriptions = dedupePrescriptionsByRank(list.prescriptions);
        if (!prescriptions.length) {
          setNoPrescriptionReason(
            d.tvi_grade === "safe"
              ? "이 마을은 위험 지표가 낮아 별도 처방이 필요하지 않습니다."
              : "추천할 처방이 없습니다.",
          );
          return;
        }
        setItems(prescriptions);
      } catch {
        if (!cancelled) {
          setLoadError("처방 데이터를 불러오지 못했습니다. 백엔드(8000)가 실행 중인지 확인해 주세요.");
        }
      }
    })();
    return () => {
      cancelled = true;
      esRef.current?.close();
    };
  }, [params.villageCode, reset]);

  const startStream = (item: PrescriptionItem, userQuestion?: string) => {
    const authToken = token ?? (typeof window !== "undefined" ? localStorage.getItem("townpulse_token") : null);
    if (!authToken) return;
    esRef.current?.close();
    setActiveItem(item);
    if (userQuestion) {
      appendUser(userQuestion);
    } else {
      reset();
      appendUser(`${item.rank}순위 ${item.title} — AI 설명을 요청합니다.`);
    }
    startAssistant();
    const es = new EventSource(prescriptionApi.streamUrl(item.id, authToken));
    esRef.current = es;
    es.onmessage = (ev) => {
      if (ev.data === "[DONE]") {
        es.close();
        finishAssistant();
        return;
      }
      appendToLastAssistant(ev.data);
    };
    es.onerror = () => {
      es.close();
      finishAssistant();
    };
  };

  if (!detail && !loadError) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      {detail && (
        <nav className="text-sm">
          <Link href={`/map/${detail.village_code}`}>← {detail.village_name}</Link>
        </nav>
      )}
      <h1 className="text-2xl font-bold">AI 처방 추천</h1>
      {loadError && <ErrorMessage message={loadError} />}
      {noPrescriptionReason && (
        <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
          {noPrescriptionReason}
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-3">
        {items.map((item) => (
          <PrescriptionCard
            key={`${item.rank}-${item.id}`}
            item={item}
            disabled={streaming}
            onExplain={() => startStream(item)}
          />
        ))}
      </div>
      {activeItem && (
        <div className="space-y-4 rounded-xl border border-border bg-card p-4">
          <h2 className="font-semibold">AI 상담 — {activeItem.title}</h2>
          <QuickQuestionBar
            disabled={streaming}
            onSelect={(q) => startStream(activeItem, q)}
          />
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {messages.map((m) => (
              <ChatBubble key={m.id} role={m.role} content={m.content} />
            ))}
          </div>
          <ChatInput
            disabled={streaming}
            onSend={(text) => startStream(activeItem, text)}
          />
        </div>
      )}
    </div>
  );
}
