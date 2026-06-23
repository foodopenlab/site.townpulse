from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Gemini 모델 정책 (무료 티어 · 텍스트/SSE 처방 설명)
# - 기본: 3.5 Flash (Stable, 주력)
# - 폴백: 3.1 Flash-Lite → 2.5 Flash → 2.5 Flash-Lite
# - 제외: 3.1 Pro / 3.5 Pro (Billing 필요), 1.5·2.0 (API 미지원·할당량 이슈)
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"

FALLBACK_GEMINI_MODELS = (
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
)

TOWNPULSE_PRESCRIPTION_PERSONA = """
당신은 충청북도청 마을활력과 소속 주무관입니다.
상급자(팀장·과장)에게 검토 자료를 보고하듯 작성하세요.
근거 중심으로 명확하게, 그러나 이해하기 쉬운 말로 정리합니다.

[출력 형식 — 반드시 아래 마크다운 구조를 그대로 사용]

## 현황
마을의 TVI 점수와 위험 등급, 충북 내 상대적 위치를 2~3문장으로 설명.

## 이 처방을 제안하는 이유
마을의 구체적 문제(빈집·교통·인구 유출 등)와 처방이 어떻게 연결되는지 3~5문장으로 설명.
전문 용어 대신 현장 언어로 작성.

## 기대 효과
처방 시행 후 TVI 개선 수치와 실질적 변화를 3~4문장으로 서술.
수치는 [데이터]에 있는 것만 사용.

## 예산 및 기금 안내
사업비 범위와 기금 매칭 가능 여부를 2~3문장으로 안내.
기금 정보가 없으면 이 섹션 전체를 생략.

[절대 금지]
- fund_applicable / True / False 등 코드 변수명 출력
- "[데이터] 내 ~ 정보 없음" 등 시스템 문구 출력
- "본 정책", "행정적 조치를 수행", "목표로 합니다" 등 공문서 투 표현
- 섹션 제목을 ** 볼드로 대체하는 것 (반드시 ## 헤더 사용)
- 근거 없는 수치 생성

[분량]
전체 700자 이상 1000자 이내. 너무 짧으면 각 섹션을 충분히 풀어 쓸 것.
"""


def default_backend_env_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / ".env"


def models_to_try(primary: str) -> list[str]:
    candidates = [primary, *FALLBACK_GEMINI_MODELS]
    seen: set[str] = set()
    result: list[str] = []
    for m in candidates:
        m = m.removeprefix("models/")
        if m and m not in seen:
            seen.add(m)
            result.append(m)
    return result


def generate_with_fallback(client: Any, prompt: str, models: list[str]) -> Any:
    last_error: Exception | None = None
    for model in models:
        try:
            return client.models.generate_content(model=model, contents=prompt)
        except Exception as exc:
            if "429" in str(exc):
                time.sleep(1)
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("사용 가능한 Gemini 모델이 없습니다.")


class Keymaker:
    _instance: Keymaker | None = None

    def __init__(self, env_path: Path | None = None) -> None:
        self._env_path = env_path or default_backend_env_path()
        self._dotenv_loaded = False
        self._gemini_client: Any = None
        self._gemini_model_id = DEFAULT_GEMINI_MODEL

    @classmethod
    def instance(cls, env_path: Path | None = None) -> Keymaker:
        if cls._instance is None:
            cls._instance = cls(env_path=env_path)
        return cls._instance

    def load_env(self) -> None:
        if self._dotenv_loaded:
            return
        load_dotenv(self._env_path)
        self._dotenv_loaded = True
        self._bootstrap_gemini()

    def _bootstrap_gemini(self) -> None:
        from google import genai

        key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if not key:
            self._gemini_client = None
            return
        model_id = (os.getenv("GEMINI_MODEL") or self._gemini_model_id).strip().removeprefix("models/")
        self._gemini_model_id = model_id or DEFAULT_GEMINI_MODEL
        self._gemini_client = genai.Client(api_key=key)

    def get_secret(self, name: str, default: str = "") -> str:
        self.load_env()
        return (os.getenv(name) or default).strip()

    def get_gemini_model_name(self) -> str:
        self.load_env()
        return self._gemini_model_id

    def get_gemini_model(self) -> Any:
        self.load_env()
        return self._gemini_client

    def is_gemini_ready(self) -> bool:
        self.load_env()
        return self._gemini_client is not None

    def generate_content(self, prompt: str) -> Any:
        self.load_env()
        if not self.is_gemini_ready():
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")
        return generate_with_fallback(
            client=self._gemini_client,
            prompt=prompt,
            models=models_to_try(self._gemini_model_id),
        )


def get_keymaker(env_path: Path | None = None) -> Keymaker:
    return Keymaker.instance(env_path=env_path)
