from __future__ import annotations

import asyncio
import threading
from typing import Any, AsyncGenerator

from core.matrix.grid_keymaker_secret_manager import get_keymaker, models_to_try

_STREAM_DONE = object()


class Smith:
    async def stream_text(self, prompt: str) -> AsyncGenerator[str, None]:
        km = get_keymaker()
        if not km.is_gemini_ready():
            yield "AI 설명을 생성할 수 없습니다. (GEMINI_API_KEY 미설정)"
            return
        client = km.get_gemini_model()
        models = models_to_try(km.get_gemini_model_name())
        last_error: Exception | None = None
        for model in models:
            try:
                async for chunk in self._stream_model(client, model, prompt):
                    yield chunk
                return
            except Exception as exc:
                last_error = exc
                if "429" in str(exc) or "quota" in str(exc).lower():
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.5)
        if last_error:
            msg = str(last_error)
            if "429" in msg or "quota" in msg.lower():
                yield "AI 생성 오류: Gemini API 할당량이 초과되었습니다. 잠시 후 다시 시도해 주세요."
            elif "404" in msg and "not found" in msg.lower():
                yield "AI 생성 오류: 사용 가능한 Gemini 모델을 찾을 수 없습니다. GEMINI_MODEL 설정을 확인해 주세요."
            else:
                yield f"AI 생성 오류: {last_error}"
        else:
            yield "AI 설명 생성에 실패했습니다."

    async def _stream_model(self, client: Any, model: str, prompt: str) -> AsyncGenerator[str, None]:
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[Any] = asyncio.Queue()

        def producer() -> None:
            try:
                stream = client.models.generate_content_stream(model=model, contents=prompt)
                for chunk in stream:
                    text = getattr(chunk, "text", None) or ""
                    if text:
                        loop.call_soon_threadsafe(queue.put_nowait, text)
            except Exception as exc:
                loop.call_soon_threadsafe(queue.put_nowait, exc)
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, _STREAM_DONE)

        threading.Thread(target=producer, daemon=True).start()

        while True:
            item = await queue.get()
            if item is _STREAM_DONE:
                break
            if isinstance(item, Exception):
                raise item
            yield item


_smith: Smith | None = None


def get_smith() -> Smith:
    global _smith
    if _smith is None:
        _smith = Smith()
    return _smith
