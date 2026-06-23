# TownPulse — UI 개선 가이드

> 작성일: 2026년 6월 | 팀: Pulse Lab  
> 대상: 커서(Cursor) AI 개발 전달용  
> 범위: ① 랜딩페이지 신규 구현 (`app/page.tsx`) ② 대시보드 TOP5 카드 개선 (`DangerTop5.tsx`)

---

## 1. 랜딩페이지 신규 구현

### 1-1. 배경 및 목적

현재 `app/page.tsx`는 `/login`으로 즉시 redirect만 하고 있어, 처음 방문한 공무원·지자체 담당자가 서비스를 파악할 수 없는 상태.

**목표:** 로그인 없이도 서비스 목적·주요 기능·데모 체험을 바로 이해할 수 있는 랜딩페이지 구현.

---

### 1-2. 파일 경로

```
townpulse-web/
├── app/
│   └── page.tsx                  ← 여기를 수정 (redirect 제거 → 랜딩 페이지로)
├── components/
│   └── landing/
│       ├── LandingNav.tsx         ← 신규
│       ├── HeroSection.tsx        ← 신규
│       ├── StatsSection.tsx       ← 신규 (API 연동)
│       ├── FeatureSection.tsx     ← 신규
│       ├── HowToSection.tsx       ← 신규
│       └── LandingCTA.tsx         ← 신규
└── lib/
    └── api/
        └── landing.ts             ← 신규 (stats API 호출)
```

---

### 1-3. `app/page.tsx` — 기존 redirect 제거 후 랜딩 페이지로 교체

```tsx
// app/page.tsx
import LandingNav from '@/components/landing/LandingNav'
import HeroSection from '@/components/landing/HeroSection'
import StatsSection from '@/components/landing/StatsSection'
import FeatureSection from '@/components/landing/FeatureSection'
import HowToSection from '@/components/landing/HowToSection'
import LandingCTA from '@/components/landing/LandingCTA'

export default function LandingPage() {
  return (
    <main>
      <LandingNav />
      <HeroSection />
      <StatsSection />
      <FeatureSection />
      <HowToSection />
      <LandingCTA />
      <footer style={{ textAlign: 'center', padding: '1.5rem', fontSize: '12px', color: 'var(--color-text-tertiary)', borderTop: '0.5px solid var(--color-border-tertiary)' }}>
        © 2026 Pulse Lab · TownPulse · 충북 마을생존 AI 의사결정 플랫폼
      </footer>
    </main>
  )
}
```

---

### 1-4. `components/landing/LandingNav.tsx`

```tsx
'use client'
import { useRouter } from 'next/navigation'
import { getDemoToken } from '@/lib/api/auth'
import { useAuthStore } from '@/lib/store/authStore'

export default function LandingNav() {
  const router = useRouter()
  const setToken = useAuthStore(s => s.setToken)

  async function handleDemo() {
    const token = await getDemoToken()   // POST /api/townpulse/users/demo/token
    setToken(token)
    router.push('/dashboard')
  }

  return (
    <nav style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '1rem 2rem', borderBottom: '0.5px solid var(--color-border-tertiary)',
      background: 'var(--color-background-primary)'
    }}>
      <span style={{ fontSize: '16px', fontWeight: 500 }}>
        Town<span style={{ color: '#1d9e75' }}>Pulse</span>
      </span>
      <div style={{ display: 'flex', gap: '8px' }}>
        <button className="btn" onClick={handleDemo}>데모 체험</button>
        <button className="btn btn-primary" onClick={() => router.push('/login')}>로그인</button>
      </div>
    </nav>
  )
}
```

---

### 1-5. `components/landing/HeroSection.tsx`

```tsx
'use client'
import { useRouter } from 'next/navigation'
import { getDemoToken } from '@/lib/api/auth'
import { useAuthStore } from '@/lib/store/authStore'

export default function HeroSection() {
  const router = useRouter()
  const setToken = useAuthStore(s => s.setToken)

  async function handleDemo() {
    const token = await getDemoToken()
    setToken(token)
    router.push('/dashboard')
  }

  return (
    <section style={{ padding: '4rem 2rem 3rem', textAlign: 'center', maxWidth: '680px', margin: '0 auto' }}>
      {/* 상단 배지 */}
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: '6px',
        background: 'var(--color-background-secondary)',
        border: '0.5px solid var(--color-border-tertiary)',
        borderRadius: '999px', padding: '4px 14px',
        fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '1.5rem'
      }}>
        <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#1d9e75' }} />
        충청북도 공식 파일럿 운영 중
      </div>

      {/* 헤드라인 */}
      <h1 style={{ fontSize: '28px', fontWeight: 500, lineHeight: 1.4, marginBottom: '1rem', color: 'var(--color-text-primary)' }}>
        충북 228개 마을,<br />
        <span style={{ color: '#1d9e75' }}>소멸위험을 AI로 진단합니다</span>
      </h1>

      <p style={{ fontSize: '15px', color: 'var(--color-text-secondary)', lineHeight: 1.7, marginBottom: '2rem' }}>
        인구·빈집·교통 데이터를 실시간 분석해<br />
        마을별 위험 등급과 맞춤 처방을 제안합니다
      </p>

      {/* CTA 버튼 */}
      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
        <button className="btn btn-lg btn-lg-primary" onClick={handleDemo}>
          ▶ 데모로 시작하기
        </button>
        <button className="btn btn-lg" onClick={() => router.push('/login')}>
          기관 로그인
        </button>
      </div>
    </section>
  )
}
```

---

### 1-6. `components/landing/StatsSection.tsx` — 대시보드 API 연동

> `GET /api/townpulse/dashboard/summary` 응답값을 그대로 사용.  
> 로딩 중에는 skeleton 또는 `—` 표시.

```tsx
'use client'
import { useEffect, useState } from 'react'
import { getDashboardSummary } from '@/lib/api/dashboard'
import type { DashboardSummary } from '@/lib/types/dashboard'

export default function StatsSection() {
  const [data, setData] = useState<DashboardSummary | null>(null)

  useEffect(() => {
    getDashboardSummary().then(setData).catch(() => {})
  }, [])

  const stats = [
    {
      value: data?.danger_count ?? '—',
      label: '소멸위험 마을\n(danger 등급)',
      danger: true,
    },
    {
      value: data?.total_villages ?? '—',
      label: '충북 전체\n읍면동 분석',
      danger: false,
    },
    {
      value: data?.transport_gap_count ?? '—',
      label: '교통 공백\n마을 수',
      danger: false,
    },
  ]

  return (
    <div style={{
      display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px',
      padding: '0 2rem 3rem', maxWidth: '680px', margin: '0 auto'
    }}>
      {stats.map((s, i) => (
        <div key={i} style={{
          background: 'var(--color-background-secondary)',
          borderRadius: 'var(--border-radius-lg)',
          padding: '1.25rem', textAlign: 'center'
        }}>
          <div style={{
            fontSize: '28px', fontWeight: 500, marginBottom: '4px',
            color: s.danger ? 'var(--color-text-danger)' : 'var(--color-text-primary)'
          }}>
            {s.value}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', whiteSpace: 'pre-line', lineHeight: 1.5 }}>
            {s.label}
          </div>
        </div>
      ))}
    </div>
  )
}
```

> **주의:** `getDashboardSummary()`는 **인증 없이 호출** 가능해야 함.  
> 백엔드에서 `GET /api/townpulse/dashboard/summary`를 demo 토큰 없이도 공개하거나,  
> 별도 public summary 엔드포인트를 만들어야 한다면 백엔드팀에 요청.  
> 대안: 숫자를 하드코딩 상수로 고정하고 배치 이후 갱신.

---

### 1-7. `components/landing/FeatureSection.tsx`

```tsx
const features = [
  {
    icon: '📊',
    title: 'TVI 위험 지수',
    desc: '인구·빈집·교통 5개 지표를 종합한 마을생존지수로 위험 순위를 한눈에',
  },
  {
    icon: '🗺️',
    title: '소멸위험 지도',
    desc: '충북 읍면동 히트맵으로 위험 지역을 시각적으로 파악하고 필터링',
  },
  {
    icon: '✨',
    title: 'AI 처방 추천',
    desc: 'Gemini AI가 마을 데이터를 분석해 빈집 활용·DRT·귀농 정착 등 처방 제안',
  },
  {
    icon: '📄',
    title: 'PDF 리포트',
    desc: '보고서·회의 자료로 바로 쓸 수 있는 마을별 분석 리포트 자동 생성',
  },
]

export default function FeatureSection() {
  return (
    <section style={{ padding: '2.5rem 2rem', maxWidth: '680px', margin: '0 auto' }}>
      <p style={{ fontSize: '12px', fontWeight: 500, color: '#0f6e56', marginBottom: '.75rem', textTransform: 'uppercase', letterSpacing: '.05em' }}>
        주요 기능
      </p>
      <h2 style={{ fontSize: '20px', fontWeight: 500, marginBottom: '.5rem', color: 'var(--color-text-primary)' }}>
        의사결정에 필요한 모든 것
      </h2>
      <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', lineHeight: 1.7, marginBottom: '1.5rem' }}>
        공무원이 현장에서 바로 쓸 수 있도록 복잡한 데이터를 한 화면에 정리했습니다
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
        {features.map((f, i) => (
          <div key={i} style={{
            background: 'var(--color-background-primary)',
            border: '0.5px solid var(--color-border-tertiary)',
            borderRadius: 'var(--border-radius-lg)',
            padding: '1rem 1.25rem'
          }}>
            <div style={{ fontSize: '20px', marginBottom: '10px' }}>{f.icon}</div>
            <h3 style={{ fontSize: '14px', fontWeight: 500, marginBottom: '4px', color: 'var(--color-text-primary)' }}>{f.title}</h3>
            <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: 1.6, margin: 0 }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
```

---

### 1-8. `components/landing/HowToSection.tsx`

```tsx
const steps = [
  {
    title: '마을 검색 또는 지도에서 선택',
    desc: '충북 228개 읍면동을 지도에서 클릭하거나 이름으로 검색해 진입합니다',
  },
  {
    title: 'TVI 위험 지수 및 원인 확인',
    desc: '인구 감소율·고령화·빈집·교통 점수를 한 화면에서 확인하고 주요 원인을 파악합니다',
  },
  {
    title: 'AI 처방 확인 후 리포트 생성',
    desc: 'AI가 제안하는 처방과 예산 추정을 검토한 뒤 PDF 보고서로 바로 출력합니다',
  },
]

export default function HowToSection() {
  return (
    <section style={{ padding: '2.5rem 2rem', maxWidth: '680px', margin: '0 auto', borderTop: '0.5px solid var(--color-border-tertiary)' }}>
      <p style={{ fontSize: '12px', fontWeight: 500, color: '#0f6e56', marginBottom: '.75rem', textTransform: 'uppercase', letterSpacing: '.05em' }}>
        사용 방법
      </p>
      <h2 style={{ fontSize: '20px', fontWeight: 500, marginBottom: '1.5rem', color: 'var(--color-text-primary)' }}>
        3단계로 바로 시작
      </h2>
      {steps.map((s, i) => (
        <div key={i} style={{
          display: 'flex', gap: '1rem', alignItems: 'flex-start',
          padding: '1rem 0',
          borderBottom: i < steps.length - 1 ? '0.5px solid var(--color-border-tertiary)' : 'none'
        }}>
          <div style={{
            width: '28px', height: '28px', borderRadius: '50%',
            background: '#1d9e75', color: '#fff',
            fontSize: '13px', fontWeight: 500,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0, marginTop: '2px'
          }}>
            {i + 1}
          </div>
          <div>
            <h3 style={{ fontSize: '14px', fontWeight: 500, marginBottom: '3px', color: 'var(--color-text-primary)' }}>{s.title}</h3>
            <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.6, margin: 0 }}>{s.desc}</p>
          </div>
        </div>
      ))}
    </section>
  )
}
```

---

### 1-9. `components/landing/LandingCTA.tsx`

```tsx
'use client'
import { useRouter } from 'next/navigation'
import { getDemoToken } from '@/lib/api/auth'
import { useAuthStore } from '@/lib/store/authStore'

export default function LandingCTA() {
  const router = useRouter()
  const setToken = useAuthStore(s => s.setToken)

  async function handleDemo() {
    const token = await getDemoToken()
    setToken(token)
    router.push('/dashboard')
  }

  return (
    <section style={{
      background: 'var(--color-background-secondary)',
      margin: '0 2rem', borderRadius: 'var(--border-radius-lg)',
      padding: '2rem', textAlign: 'center'
    }}>
      <h2 style={{ fontSize: '18px', fontWeight: 500, marginBottom: '.5rem', color: 'var(--color-text-primary)' }}>
        지금 바로 체험해보세요
      </h2>
      <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '1.5rem', lineHeight: 1.6 }}>
        로그인 없이 데모 모드로<br />
        단양군 영춘면 등 실제 분석 사례를 확인할 수 있습니다
      </p>
      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
        <button className="btn btn-lg btn-lg-primary" onClick={handleDemo}>
          ▶ 데모로 시작하기
        </button>
        <button className="btn btn-lg">
          기관 담당자 문의
        </button>
      </div>
    </section>
  )
}
```

---

### 1-10. `lib/api/auth.ts` — getDemoToken 추가

기존 `auth.ts`에 아래 함수 추가:

```ts
// lib/api/auth.ts
import apiClient from './client'

// 기존 login 함수 유지 ...

/** 데모 모드 토큰 발급 — POST /api/townpulse/users/demo/token */
export async function getDemoToken(): Promise<string> {
  const res = await apiClient.post<{ access_token: string }>(
    '/api/townpulse/users/demo/token'
  )
  return res.data.access_token
}
```

---

### 1-11. 전역 CSS 버튼 클래스 (`app/globals.css`)

랜딩 전용 버튼 클래스를 globals.css에 추가:

```css
/* 랜딩 공통 버튼 */
.btn {
  font-size: 13px;
  padding: 7px 16px;
  border-radius: var(--border-radius-md);
  border: 0.5px solid var(--color-border-secondary);
  background: transparent;
  color: var(--color-text-primary);
  cursor: pointer;
  font-family: var(--font-sans);
}
.btn-primary {
  background: #1d9e75;
  color: #fff;
  border-color: #1d9e75;
  font-weight: 500;
}
.btn-lg {
  font-size: 14px;
  padding: 10px 24px;
  border-radius: var(--border-radius-md);
  border: 0.5px solid var(--color-border-secondary);
  background: transparent;
  color: var(--color-text-primary);
  cursor: pointer;
  font-family: var(--font-sans);
}
.btn-lg-primary {
  background: #1d9e75;
  color: #fff;
  border-color: #1d9e75;
  font-weight: 500;
}
```

---

## 2. 대시보드 TOP5 카드 개선

### 2-1. 배경 및 목적

기존 `DangerTop5.tsx`는 마을명 + TVI 숫자만 나열되어 있어 공무원이 봤을 때:
- TVI가 0~100 중 어느 위치인지 파악 불가
- 위험 등급(danger/warning/safe)이 시각적으로 표현 안 됨
- 왜 위험한지 원인이 보이지 않음

**개선 목표:**
- `/ 100` 척도 표시로 위험도 직관화
- 위험 등급 배지(신호등) 추가
- 마을별 주요 위험 원인 한 줄 자동 생성

---

### 2-2. 파일 경로

```
townpulse-web/
└── components/
    └── dashboard/
        └── DangerTop5.tsx    ← 수정
```

---

### 2-3. `components/dashboard/DangerTop5.tsx` 전면 개선

```tsx
import type { DashboardSummary } from '@/lib/types/dashboard'

// 위험 등급별 스타일
function getRiskBadge(tviScore: number) {
  if (tviScore <= 30) return { label: '위험', bg: 'var(--color-background-danger)', color: 'var(--color-text-danger)' }
  if (tviScore <= 60) return { label: '주의', bg: 'var(--color-background-warning)', color: 'var(--color-text-warning)' }
  return { label: '안전', bg: 'var(--color-background-success)', color: 'var(--color-text-success)' }
}

// 위험 원인 자동 한 줄 생성
// ※ village-detail API에서 snap 데이터를 받아오는 경우 아래 함수를 활용.
//   TOP5는 대시보드 summary API에 snap 상세가 없으므로,
//   우선 TVI 점수 기반으로 범주 메시지를 생성하고
//   향후 백엔드가 top5에 reason 필드를 추가하면 교체.
function getRiskReason(tviScore: number, rank: number): string {
  // 임시 로직: 실제 SNAP 데이터 연동 시 아래 로직으로 교체
  // if (snap.net_youth_migration < 0) reasons.push('청년 유출')
  // if (snap.bus_interval_score === 0) reasons.push('교통 공백')
  // ...
  const reasons = [
    ['인구 급감 · 청년 유출 심각 · 교통 공백', '고령화율 최상위 · 빈집 밀집', '인구밀도 하위 · 청년 순이동 마이너스', '세대 수 감소 · 빈집 증가 추세', '버스 배차 공백 · 고령 인구 집중'],
  ]
  return reasons[0][rank - 1] ?? '복합 위험 요인'
}

interface Village {
  village_code: string
  village_name: string
  sigun_name: string
  tvi_score: number
}

interface Props {
  villages: Village[]
}

export default function DangerTop5({ villages }: Props) {
  return (
    <section>
      <h2 style={{ fontSize: '16px', fontWeight: 500, marginBottom: '1rem', color: 'var(--color-text-primary)' }}>
        위험 마을 TOP 5
      </h2>

      {/* 범례 */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '1rem' }}>
        {[
          { label: '위험 (0–30)', bg: 'var(--color-background-danger)', border: 'var(--color-border-danger)' },
          { label: '주의 (31–60)', bg: 'var(--color-background-warning)', border: 'var(--color-border-warning)' },
          { label: '안전 (61–100)', bg: 'var(--color-background-success)', border: 'var(--color-border-success)' },
        ].map((item, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: item.bg, border: `1px solid ${item.border}` }} />
            {item.label}
          </div>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--color-text-tertiary)' }}>
          TVI 0~100 · 낮을수록 위험
        </span>
      </div>

      {/* 카드 리스트 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {villages.map((v, i) => {
          const badge = getRiskBadge(v.tvi_score)
          const reason = getRiskReason(v.tvi_score, i + 1)
          const barWidth = `${Math.min(v.tvi_score, 100)}%`

          return (
            <div key={v.village_code} style={{
              background: 'var(--color-background-primary)',
              border: '0.5px solid var(--color-border-tertiary)',
              borderRadius: 'var(--border-radius-lg)',
              padding: '1rem 1.25rem',
              display: 'flex', alignItems: 'center', gap: '1rem'
            }}>
              {/* 순위 */}
              <span style={{ fontSize: '13px', color: 'var(--color-text-tertiary)', fontWeight: 500, minWidth: '20px' }}>
                {i + 1}
              </span>

              {/* 마을 정보 */}
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '15px', fontWeight: 500, color: 'var(--color-text-primary)', margin: '0 0 4px' }}>
                  {v.village_name} ({v.sigun_name})
                </p>
                <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', margin: 0 }}>
                  {reason}
                </p>
              </div>

              {/* 오른쪽: 배지 + 점수 + 바 */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
                {/* 위험 등급 배지 */}
                <span style={{
                  fontSize: '11px', fontWeight: 500,
                  padding: '3px 10px', borderRadius: 'var(--border-radius-md)',
                  background: badge.bg, color: badge.color
                }}>
                  {badge.label}
                </span>

                {/* TVI 점수 */}
                <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                  <strong style={{ fontSize: '17px', color: 'var(--color-text-primary)' }}>
                    {v.tvi_score.toFixed(1)}
                  </strong>
                  {' '}
                  <span style={{ fontSize: '12px' }}>/ 100</span>
                </div>

                {/* 진행 바 */}
                <div style={{
                  height: '4px', background: 'var(--color-background-tertiary)',
                  borderRadius: '2px', width: '80px'
                }}>
                  <div style={{
                    height: '4px', borderRadius: '2px',
                    width: barWidth,
                    background: 'var(--color-text-danger)'
                  }} />
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
```

---

### 2-4. `DangerTop5` 사용처 (`app/(dashboard)/dashboard/page.tsx`) 수정

```tsx
// 기존 호출 유지, top5_danger_villages 필드를 villages prop으로 전달
<DangerTop5 villages={summary.top5_danger_villages} />
```

---

### 2-5. 향후 개선 — SNAP 기반 위험 원인 자동화

현재 `getRiskReason()`은 임시 하드코딩. 백엔드 `top5_danger_villages` 응답에 아래 필드가 추가되면 교체:

```ts
// 백엔드 담당자 요청 항목 (선택)
interface Top5Village {
  village_code: string
  village_name: string
  sigun_name: string
  tvi_score: number
  // 아래 필드 추가 요청
  risk_reasons?: string[]   // ['인구 급감', '교통 공백'] 등 — 백엔드 snap 기반 생성
}
```

또는 프론트에서 village-detail API를 추가 호출해 SNAP 데이터로 직접 생성:

```ts
function getRiskReasonFromSnap(snap: SnapData): string {
  const reasons: string[] = []
  if (snap.annual_pop_change_rate < -1) reasons.push('인구 급감')
  if (snap.net_youth_migration < 0) reasons.push('청년 유출')
  if (snap.bus_interval_score === 0) reasons.push('교통 공백')
  if (snap.vacancy_score < 40) reasons.push('빈집 밀집')
  if (snap.aging_ratio > 0.4) reasons.push('고령화율 높음')
  return reasons.slice(0, 3).join(' · ') || '복합 위험 요인'
}
```

> **주의:** TOP5마다 village-detail API를 호출하면 5회 추가 요청 발생 — 성능 고려 시 백엔드 응답에 포함 요청 권장.

---

## 3. 구현 우선순위 및 체크리스트

### 즉시 구현 (이번 스프린트)

- [ ] `app/page.tsx` — redirect 제거, 랜딩 컴포넌트 조립
- [ ] `components/landing/` — 6개 컴포넌트 신규 생성
- [ ] `lib/api/auth.ts` — `getDemoToken()` 함수 추가
- [ ] `app/globals.css` — `.btn`, `.btn-primary`, `.btn-lg`, `.btn-lg-primary` 클래스 추가
- [ ] `components/dashboard/DangerTop5.tsx` — 카드형 UI 전면 교체

### 백엔드 확인 필요

- [ ] `GET /api/townpulse/dashboard/summary` — 인증 없이 호출 가능 여부 (랜딩 stats용)
- [ ] `POST /api/townpulse/users/demo/token` — 정상 동작 확인
- [ ] TOP5 응답에 `risk_reasons` 필드 추가 여부 (선택)

### 이후 개선

- [ ] `getRiskReason()` — SNAP 데이터 기반 자동 생성으로 교체
- [ ] 랜딩 stats 숫자 실시간 API 연동 (또는 공개 엔드포인트 추가)
- [ ] 모바일 반응형 확인 (랜딩 hero, feature grid 2열 → 1열)

---

*© 2026 Pulse Lab | TownPulse UI 개선 가이드 v1.0*
