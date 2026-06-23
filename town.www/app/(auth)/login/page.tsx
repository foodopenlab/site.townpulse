"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ensureDemoSession, login } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/store/authStore";
import { DEMO_LOGIN } from "@/lib/config/demo";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

export default function LoginPage() {
  const router = useRouter();
  const [orgId, setOrgId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await login(orgId, password);
      useAuthStore.getState().setAuth(data.access_token);
      router.push("/dashboard");
    } catch {
      setError("로그인에 실패했습니다.");
    }
  };

  const onDemoToken = async () => {
    setError("");
    try {
      await ensureDemoSession();
      router.push("/dashboard");
    } catch {
      setError("데모 토큰 발급에 실패했습니다. 백엔드(8000)가 실행 중인지 확인하세요.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted p-4">
      <div className="w-full max-w-md rounded-xl border border-border bg-card p-8 shadow-sm">
        <div className="mb-6 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-primary">
            TownPulse
          </Link>
          <ThemeToggle />
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          <input
            className="w-full rounded-lg border border-border px-3 py-2"
            placeholder="아이디"
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
          />
          <input
            type="password"
            className="w-full rounded-lg border border-border px-3 py-2"
            placeholder="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <ErrorMessage message={error} />}
          <button type="submit" className="w-full rounded-lg bg-primary py-2 text-white">
            로그인
          </button>
          <button
            type="button"
            onClick={onDemoToken}
            className="w-full rounded-lg border border-border py-2 text-sm"
          >
            데모 토큰으로 시작
          </button>
        </form>
        <p className="mt-4 rounded-lg bg-muted p-3 text-xs text-muted-foreground">
          로컬 QA 계정: 아이디 <code className="text-foreground">{DEMO_LOGIN.orgId}</code>
          <br />
          비밀번호 <code className="text-foreground">{DEMO_LOGIN.password}</code>
        </p>
      </div>
    </div>
  );
}
