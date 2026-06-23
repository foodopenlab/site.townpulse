# TownPulse — 프론트엔드 개발 정의서

> 서비스명: TownPulse | 충북 마을생존 AI 의사결정 플랫폼  
> 버전: **v2.3** | 작성일: 2026년 6월 | 팀: Pulse Lab  
> 배포: Vercel | 도메인: **townpulse.site**  
> 백엔드: `api.townpulse.site` (FastAPI · **Railway**) ★ v9.5  
> DB: NeonDB (PostgreSQL serverless)  
> 변경 이력:
> - v1.0 — Next.js 14·Leaflet·Zustand·6화면 MVP 초안
> - **v2.0 — 백엔드 v8.3·ERD v5 정합** — 오케스트레이터 API 경로 확정, SNAP_TRANSPORT(15098534) UI 반영, Gemini AI, `village_code`/`village_id` 이중 식별자
> - **v2.1 — 테마** — **기본 라이트** · `next-themes` 토글 다크 · 시맨틱 CSS 변수(`globals.css`)
> - **v2.2 — §13 데모 403 폴백** — `양호` 등급·dispatch 0건 시 `noPrescriptionReason` (백엔드 §12-1d optional 연동) ★ v9.2
> - **v2.3 — §5-4 증평 교통 배지** — `bus_route_count=null` → 「교통 데이터 제한적」 vs 확정 「교통 공백」 분리 (백엔드 §9-4·§10-9-3) ★ v9.4
> 참고 백엔드: `TownPulse_백엔드_MVP_개발정의서_v9_5.md`  
> 참고 데이터 모델: `TownPulse_ERD_MVP_v6_1.md`  
> API 필드: `TownPulse_API필드검증_v2_0.md` · `town.www/_docs/api_samples/FIELD_MAPPING_v2_0.md`

---

## 목차

0. [백엔드 v8.3·ERD v5 정합 요약](#0-백엔드-v83erd-v5-정합-요약)
1. [기술 스택 및 환경](#1-기술-스택-및-환경)
2. [프로젝트 구조](#2-프로젝트-구조)
3. [환경 변수 및 설정](#3-환경-변수-및-설정)
4. [페이지 및 라우팅](#4-페이지-및-라우팅)
5. [컴포넌트 구조](#5-컴포넌트-구조)
6. [상태 관리 (Zustand)](#6-상태-관리-zustand)
7. [API 클라이언트 레이어](#7-api-클라이언트-레이어)
8. [지도 컴포넌트 (Leaflet)](#8-지도-컴포넌트-leaflet)
9. [AI 처방 채팅 (SSE 스트리밍)](#9-ai-처방-채팅-sse-스트리밍)
10. [PDF 리포트 생성](#10-pdf-리포트-생성)
11. [인증 흐름](#11-인증-흐름)
12. [디자인 시스템](#12-디자인-시스템)
13. [백엔드 연동 시 주의사항](#13-백엔드-연동-시-주의사항)
14. [Vercel 배포 설정](#14-vercel-배포-설정)
15. [개발 체크리스트](#15-개발-체크리스트)

---

## 0. 백엔드 v8.3·ERD v5 정합 요약

프론트는 **화면용 오케스트레이터 API**를 우선 호출하고, 원본 SNAP 확인이 필요할 때만 `snap/*`·`tvi-scores`를 직접 호출한다.

### 0-1. 화면 ↔ API 매핑 (MVP)

| 화면 | 주 API (오케스트레이터) | 백엔드 도메인 |
|---|---|---|
| D-02 대시보드 | `GET /api/townpulse/dashboard/summary` | DASHBOARD_ORCHESTRATOR |
| D-03 지도 | `GET /api/townpulse/dashboard/map/villages` | DASHBOARD_ORCHESTRATOR |
| D-03 요약 카드 | `GET /api/townpulse/dashboard/map/villages/{village_code}` | DASHBOARD_ORCHESTRATOR |
| D-04 마을 상세 | `GET /api/townpulse/village-detail/{village_code}` | VILLAGE_DETAIL_ORCHESTRATOR |
| D-05 처방 | `GET .../prescription-results/by-village/{village_id}` + `POST .../prescription-results` | PRESCRIPTION_RESULT |
| D-05 AI 스트림 | `GET .../prescription-results/{id}/stream?token=` | PRESCRIPTION_RESULT (Gemini SSE) |
| D-06 리포트 | `POST /api/townpulse/report-data/{village_code}` | REPORT_ORCHESTRATOR |
| D-01 로그인 | `POST /api/townpulse/users/login` | USER |

> 모든 REST 경로 prefix: `/api/townpulse/` (백엔드 `townpulse_router` + `app.include_router(..., prefix="/api")`)

### 0-2. 식별자 규칙 ★ v2

| 필드 | 형식 | 용도 |
|---|---|---|
| `village_code` | 10자리 문자열 (`"4300025000"`) | URL `[villageCode]`, 오케스트레이터 경로, GeoJSON `emd_code` 조인 |
| `village_id` | UUID | `snap/*`, `prescription-results/by-village/{village_id}` |
| `legal_dong_code` | 10자리 법정동코드 | 백엔드 REGION 조인키 — 프론트 표시·필터용 참조 |

`village-detail` 응답에 **`village_id` + `village_code` 둘 다** 포함한다고 가정하고, 이후 API 호출에 재사용한다.

### 0-3. SNAP_TRANSPORT UI 반영 (ERD v5 / v8.3)

백엔드 ingest: vworld geocode → `ingest_for_village` (노선 2단계 + **15098534** 정류소).

| SNAP 필드 | 화면 표시 예 |
|---|---|
| `avg_bus_interval_min` | 배차 간격 (분) — 시/군 평균 |
| `nearest_stop_distance_m` | 최근접 정류장 거리 (m) |
| `bus_stops_within_1km` | 1km 내 정류장 수 |
| `bus_interval_score` | TVI 교통 부분점수 (0 = **확정 교통 공백**; `bus_route_count=null`은 §9-4 절충) ★ v2.3 |

**교통 공백 판정 (TVI·백엔드 §9-4 동일):** `bus_route_count != null` 이고 (`bus_stops_within_1km === 0` 또는 `nearest_stop_distance_m > 1000`) → **확정 교통 공백**. `snap_transport.bus_route_count == null`(증평군 등 TAGO 미제공) → **「교통 데이터 제한적」** 배지 — 공백 배지와 분리 (§5-4).

### 0-4. AI 텍스트

- 백엔드: **Google Gemini API** (`prescription_result.ai_description`)
- v1의 Claude 언급은 v2에서 제거 — UI 문구도 "AI 처방 설명 (Gemini)" 로 통일

---

## 1. 기술 스택 및 환경

### 1-1. 핵심 스택

| 분류 | 기술 | 버전 | 용도 |
|---|---|---|---|
| 프레임워크 | Next.js | 14.x (App Router) | 전체 UI, SSR/CSR 혼합 |
| 언어 | TypeScript | 5.x | 전체 코드베이스 |
| 스타일 | Tailwind CSS | 3.x | 반응형 · **`darkMode: 'class'`** |
| 테마 | next-themes | 0.4.x | **기본 라이트** · 토글 다크 |
| 지도 | Leaflet.js + react-leaflet | 최신 | 읍면동 히트맵 |
| 차트 | Recharts | 최신 | 바 차트, 라인 차트 |
| 상태관리 | Zustand | 4.x | 전역 상태 (인증, 마을 선택) |
| HTTP | Axios | 최신 | FastAPI 백엔드 통신 |
| 인증 저장 | localStorage | — | JWT access/refresh 토큰 |
| PDF | html2canvas + jspdf | 최신 | 클라이언트 PDF 생성 |
| 아이콘 | lucide-react | 최신 | UI 아이콘 |

### 1-2. 개발 도구

| 도구 | 용도 |
|---|---|
| ESLint + Prettier | 코드 품질·포맷 |
| Cursor | AI 보조 개발 |
| Vercel CLI | 로컬 프리뷰·배포 |

### 1-3. 배포 아키텍처

```
townpulse.site  (Vercel — Next.js)
      ↕ HTTPS REST / SSE
api.townpulse.site  (AWS EC2 — FastAPI + Docker)
      ↕ asyncpg
NeonDB  (PostgreSQL serverless)

DNS: townpulse.site → Vercel
     api.townpulse.site → EC2 Elastic IP
```

---

## 2. 프로젝트 구조

```
townpulse-web/
├── app/
│   ├── globals.css                   # :root(라이트) / .dark(다크) 시맨틱 토큰 ★ v2.1
│   ├── layout.tsx                    # ThemeProvider defaultTheme="light" ★ v2.1
│   ├── page.tsx                      # / → /login redirect
│   ├── (auth)/
│   │   └── login/
│   │       └── page.tsx              # D-01 로그인
│   └── (dashboard)/
│       ├── layout.tsx                # 헤더 + 사이드바 레이아웃
│       ├── dashboard/
│       │   └── page.tsx              # D-02 메인 대시보드
│       ├── map/
│       │   ├── page.tsx              # D-03 소멸위험 지도
│       │   └── [villageCode]/
│       │       └── page.tsx          # D-04 마을 상세 리포트
│       ├── prescription/
│       │   └── [villageCode]/
│       │       └── page.tsx          # D-05 AI 처방 추천
│       └── report/
│           └── [villageCode]/
│               └── page.tsx          # D-06 리포트 생성
│
├── components/
│   ├── theme/
│   │   └── theme-toggle.tsx          # Moon/Sun — Header·로그인 카드 ★ v2.1
│   ├── layout/
│   │   ├── Header.tsx                # 공통 헤더 + ThemeToggle
│   │   ├── Sidebar.tsx               # 사이드바 내비게이션
│   │   └── BottomNav.tsx             # 모바일 하단 탭
│   ├── dashboard/
│   │   ├── StatCard.tsx              # 지표 카드 (4개)
│   │   ├── DangerTop5.tsx            # 위험 마을 TOP5
│   │   └── MapPreview.tsx            # 히트맵 미리보기
│   ├── map/
│   │   ├── VillageMap.tsx            # Leaflet 지도 (동적 import)
│   │   ├── MapFilters.tsx            # 위험등급·시군·지표 필터
│   │   └── VillageSummaryCard.tsx    # 클릭 시 요약 카드
│   ├── village/
│   │   ├── VillageHeader.tsx         # 마을명 + 배지 + 기준일
│   │   ├── IndicatorCards.tsx        # 5개 지표 카드 (인구·빈집·고령·배차·정류장) ★ v2
│   │   ├── RiskBarChart.tsx          # 악순환 지수 바 차트
│   │   └── ExtinctionProbability.tsx # 5년 소멸 확률 박스
│   ├── prescription/
│   │   ├── PrescriptionCard.tsx      # 처방 카드 (1·2·3순위)
│   │   ├── ChatBubble.tsx            # AI/사용자 말풍선
│   │   ├── QuickQuestionBar.tsx      # 빠른 질문 버튼
│   │   └── ChatInput.tsx             # 입력창 + 전송
│   ├── report/
│   │   ├── ReportOptions.tsx         # 포함 항목 체크박스
│   │   └── ReportPreview.tsx         # 미리보기 영역
│   └── ui/
│       ├── Badge.tsx                 # 위험/주의/안전 배지
│       ├── RiskBar.tsx               # 위험도 바
│       ├── LoadingSpinner.tsx        # 로딩
│       └── ErrorMessage.tsx          # 오류 메시지
│
├── lib/
│   ├── api/
│   │   ├── client.ts                 # Axios 인스턴스 + 인터셉터
│   │   ├── auth.ts                   # 로그인·토큰 갱신 API
│   │   ├── dashboard.ts              # 대시보드·지도 오케스트레이터 API ★ v2
│   │   ├── village.ts                # village-detail API ★ v2
│   │   ├── prescription.ts           # prescription-results API ★ v2
│   │   └── report.ts                 # report-data API ★ v2
│   ├── store/
│   │   ├── authStore.ts              # 인증 상태 (Zustand)
│   │   ├── mapStore.ts               # 지도 필터·선택 상태
│   │   └── chatStore.ts              # 채팅 메시지 상태
│   ├── utils/
│   │   ├── tvi.ts                    # TVI 등급 판정 유틸
│   │   ├── format.ts                 # 숫자 포맷 (%, 만원 등)
│   │   └── pdf.ts                    # PDF 생성 유틸
│   └── types/
│       ├── village.ts                # Village, VillageDetail, SnapTransport ★ v2
│       ├── prescription.ts           # Prescription, ChatMessage 타입
│       ├── dashboard.ts              # DashboardSummary 타입
│       └── report.ts                 # ReportConfig, ReportData 타입
│
├── public/
│   ├── geojson/
│   │   └── chungbuk_emd.geojson     # 충북 읍면동 경계 GeoJSON
│   └── logo.svg
│
├── .env.local                        # 로컬 환경변수
├── .env.production                   # 프로덕션 환경변수
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 3. 환경 변수 및 설정

### 3-1. 환경 변수

```bash
# .env.local (개발)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# .env.production (Vercel 환경변수 설정)
NEXT_PUBLIC_API_BASE_URL=https://api.townpulse.site
NEXT_PUBLIC_SITE_URL=https://townpulse.site
```

> Vercel 대시보드 → Settings → Environment Variables에서 `NEXT_PUBLIC_API_BASE_URL` 등록

### 3-2. next.config.ts

```typescript
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Leaflet은 SSR 미지원 → 동적 import 필수
  transpilePackages: ['leaflet', 'react-leaflet'],
}

export default nextConfig
```

### 3-3. Leaflet CSS 전역 로드

```typescript
// app/layout.tsx
import 'leaflet/dist/leaflet.css'
```

### 3-4. 테마 Provider (기본 라이트) ★ v2.1

```typescript
// app/layout.tsx
import { ThemeProvider } from 'next-themes'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem={false}
          disableTransitionOnChange
          storageKey="townpulse-theme"
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

| 옵션 | 값 | 비고 |
|---|---|---|
| `defaultTheme` | **`light`** | 첫 방문·미설정 = 라이트 UI |
| `enableSystem` | `false` | MVP: OS 자동 전환 제외 |
| `storageKey` | `townpulse-theme` | 새로고침 후 선택 유지 |

---

## 4. 페이지 및 라우팅

### 4-1. 라우팅 구조

| 경로 | 파일 | 화면 ID | 인증 필요 |
|---|---|---|---|
| `/` | `app/page.tsx` | — | ❌ → `ensureDemoSession()` 후 `/dashboard` |
| `/login` | `app/(auth)/login/page.tsx` | D-01 | ❌ |
| `/dashboard` | `app/(dashboard)/dashboard/page.tsx` | D-02 | ✅ |
| `/map` | `app/(dashboard)/map/page.tsx` | D-03 | ✅ |
| `/map/[villageCode]` | `app/(dashboard)/map/[villageCode]/page.tsx` | D-04 | ✅ |
| `/prescription/[villageCode]` | `app/(dashboard)/prescription/[villageCode]/page.tsx` | D-05 | ✅ |
| `/report/[villageCode]` | `app/(dashboard)/report/[villageCode]/page.tsx` | D-06 | ✅ |

### 4-2. 레이아웃 계층

```typescript
// app/(dashboard)/layout.tsx
// 헤더 + 사이드바 공통 레이아웃
// JWT 없으면 ensureDemoSession() 시도 → 실패 시 /login

export default function DashboardLayout({ children }) {
  // useAuthStore()로 토큰 확인
  // 토큰 없으면 ensureDemoSession() → 실패 시 router.replace('/login')
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
```

### 4-3. 모바일 반응형 레이아웃

```typescript
// 데스크톱: 사이드바 + 헤더
// 모바일 (< 768px): 헤더 + 하단 탭 (사이드바 숨김)

// app/(dashboard)/layout.tsx
<>
  {/* 데스크톱 사이드바 */}
  <div className="hidden md:flex md:w-[180px]">
    <Sidebar />
  </div>

  {/* 모바일 하단 탭 */}
  <div className="md:hidden fixed bottom-0 inset-x-0 z-50">
    <BottomNav />
  </div>
</>
```

---

## 5. 컴포넌트 구조

### 5-1. 지표 카드 (StatCard)

```typescript
// components/dashboard/StatCard.tsx
interface StatCardProps {
  label: string
  value: string
  variant: 'primary' | 'danger' | 'warning' | 'safe'
  icon?: string
}

const variantStyles = {
  primary: 'bg-secondary text-secondary-foreground border-border',
  danger:  'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-900',
  warning: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300',
  safe:    'bg-green-50 text-green-700 border-green-200 dark:bg-green-950/40 dark:text-green-300',
}

export function StatCard({ label, value, variant }: StatCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${variantStyles[variant]}`}>
      <p className="text-sm font-medium opacity-80">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}
```

### 5-2. 배지 (Badge)

```typescript
// components/ui/Badge.tsx
type BadgeVariant = 'danger' | 'warning' | 'safe' | 'info' | 'urgent' | 'medium' | 'long'

const styles: Record<BadgeVariant, string> = {
  danger:  'bg-[#FCEBEB] text-[#A32D2D]',
  warning: 'bg-[#FAEEDA] text-[#854F0B]',
  safe:    'bg-[#EAF3DE] text-[#3B6D11]',
  info:    'bg-[#E6F1FB] text-[#185FA5]',
  urgent:  'bg-[#FCEBEB] text-[#A32D2D]',
  medium:  'bg-[#FAEEDA] text-[#854F0B]',
  long:    'bg-gray-100 text-gray-600',
}

export function Badge({ variant, children }: { variant: BadgeVariant; children: React.ReactNode }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[variant]}`}>
      {children}
    </span>
  )
}
```

### 5-3. TVI 등급 유틸

```typescript
// lib/utils/tvi.ts
export type TviGrade = 'danger' | 'warning' | 'safe'

export function getTviGrade(score: number): TviGrade {
  if (score <= 30) return 'danger'
  if (score <= 60) return 'warning'
  return 'safe'
}

export const tviGradeLabel: Record<TviGrade, string> = {
  danger:  '위험',
  warning: '주의',
  safe:    '안전',
}

export const tviGradeColor: Record<TviGrade, string> = {
  danger:  '#E24B4A',
  warning: '#EF9F27',
  safe:    '#639922',
}
```

### 5-4. 지표 카드 그리드 (IndicatorCards) ★ v2

D-04 마을 상세 — `village-detail` 응답 기준 **5개 카드**:

| 카드 | 데이터 소스 | 표시 |
|---|---|---|
| 인구 감소 | `population_change_rate` | % |
| 빈집 추정 | `vacant_house_rate` | % |
| 고령화 | `elderly_rate` | % |
| 버스 배차 | `bus_interval_minutes` / `avg_bus_interval_min` | 분 (시/군 평균) |
| 정류장 접근 | `nearest_stop_distance_m`, `bus_stops_within_1km` | m / 개 — **확정 교통 공백** 시 경고 배지 · `bus_route_count=null`은 「교통 데이터 제한적」 ★ v2.3 |

```typescript
// components/village/IndicatorCards.tsx (발췌) ★ v2.3
export function IndicatorCards({ detail }: { detail: VillageDetail }) {
  const isPartialTransportData = detail.snap_transport?.bus_route_count == null
  const confirmedTransportGap =
    !isPartialTransportData &&
    (detail.transport_gap ||
      detail.bus_stops_within_1km === 0 ||
      (detail.nearest_stop_distance_m != null && detail.nearest_stop_distance_m > 1000))

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {confirmedTransportGap && <Badge variant="danger">교통 공백</Badge>}
      {isPartialTransportData && (
        <Badge
          variant="muted"
          title="TAGO 버스 API가 도시코드를 제공하지 않는 지역 — 정류장 근접 데이터만 일부 반영"
        >
          교통 데이터 제한적
        </Badge>
      )}
      {/* ...인구·빈집·고령·배차 */}
      <StatCard
        label="최근접 정류장"
        value={
          detail.nearest_stop_distance_m != null
            ? `${detail.nearest_stop_distance_m}m`
            : '—'
        }
        variant={confirmedTransportGap ? 'danger' : 'safe'}
      />
    </div>
  )
}
```

### 5-5. 처방 카드 (PrescriptionCard)

```typescript
// components/prescription/PrescriptionCard.tsx
interface PrescriptionCardProps {
  rank: 1 | 2 | 3
  title: string
  description: string
  budgetMin: number   // 만원 단위
  budgetMax: number
  tviGainMin: number
  tviGainMax: number
  fundApplicable: boolean
  timeline: 'urgent' | 'medium' | 'long'
}

const rankBorderColor = {
  1: 'border-l-[#185FA5]',
  2: 'border-l-gray-200',
  3: 'border-l-gray-200',
}

const timelineLabel = {
  urgent: '즉시',
  medium: '6개월 내',
  long: '중장기',
}

export function PrescriptionCard({ rank, title, description, budgetMin, budgetMax, tviGainMin, tviGainMax, fundApplicable, timeline }: PrescriptionCardProps) {
  return (
    <div className={`border border-gray-200 border-l-4 ${rankBorderColor[rank]} rounded-lg p-4 bg-white shadow-sm`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <Badge variant={timeline}>{timelineLabel[timeline]}</Badge>
      </div>
      <p className="text-sm text-gray-600 mb-3">{description}</p>
      <div className="flex gap-2 flex-wrap">
        <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">
          예산 {formatBudget(budgetMin)}~{formatBudget(budgetMax)}
        </span>
        <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded">
          TVI +{tviGainMin}~{tviGainMax}점
        </span>
        {fundApplicable && (
          <span className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded">
            ✅ 기금 신청 가능
          </span>
        )}
      </div>
    </div>
  )
}
```

---

## 6. 상태 관리 (Zustand)

### 6-1. 인증 스토어

```typescript
// lib/store/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  accessToken: string | null
  orgName: string | null
  userName: string | null
  isAuthenticated: boolean
  login: (token: string, orgName: string, userName: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      orgName: null,
      userName: null,
      isAuthenticated: false,
      login: (accessToken, orgName, userName) =>
        set({ accessToken, orgName, userName, isAuthenticated: true }),
      logout: () =>
        set({ accessToken: null, orgName: null, userName: null, isAuthenticated: false }),
    }),
    { name: 'townpulse-auth' }
  )
)
```

### 6-2. 지도 스토어

```typescript
// lib/store/mapStore.ts
import { create } from 'zustand'

interface MapState {
  selectedGrade: 'all' | 'danger' | 'warning' | 'safe'
  selectedSigun: string | null
  selectedIndicator: 'tvi' | 'vacant' | 'elderly' | 'bus' | 'stop_access'  // bus=배차, stop_access=정류장 ★ v2
  selectedVillageCode: string | null
  setGradeFilter: (grade: MapState['selectedGrade']) => void
  setSigunFilter: (sigun: string | null) => void
  setIndicatorFilter: (indicator: MapState['selectedIndicator']) => void
  selectVillage: (code: string | null) => void
}

export const useMapStore = create<MapState>((set) => ({
  selectedGrade: 'all',
  selectedSigun: null,
  selectedIndicator: 'tvi',
  selectedVillageCode: null,
  setGradeFilter: (grade) => set({ selectedGrade: grade }),
  setSigunFilter: (sigun) => set({ selectedSigun: sigun }),
  setIndicatorFilter: (indicator) => set({ selectedIndicator: indicator }),
  selectVillage: (code) => set({ selectedVillageCode: code }),
}))
```

### 6-3. 채팅 스토어

```typescript
// lib/store/chatStore.ts
import { create } from 'zustand'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ChatState {
  messages: Record<string, ChatMessage[]>  // villageCode → messages
  sessionKey: Record<string, string>       // villageCode → sessionKey
  isStreaming: boolean
  addMessage: (villageCode: string, message: ChatMessage) => void
  setSessionKey: (villageCode: string, key: string) => void
  setStreaming: (value: boolean) => void
  appendToLastAssistant: (villageCode: string, text: string) => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: {},
  sessionKey: {},
  isStreaming: false,
  addMessage: (villageCode, message) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [villageCode]: [...(state.messages[villageCode] ?? []), message],
      },
    })),
  setSessionKey: (villageCode, key) =>
    set((state) => ({
      sessionKey: { ...state.sessionKey, [villageCode]: key },
    })),
  setStreaming: (value) => set({ isStreaming: value }),
  appendToLastAssistant: (villageCode, text) =>
    set((state) => {
      const msgs = [...(state.messages[villageCode] ?? [])]
      const last = msgs[msgs.length - 1]
      if (last?.role === 'assistant') {
        msgs[msgs.length - 1] = { ...last, content: last.content + text }
      }
      return { messages: { ...state.messages, [villageCode]: msgs } }
    }),
}))
```

---

## 7. API 클라이언트 레이어

> ★ v2: 구 `/api/townpulse/map/*`, `/prescription/chat` 경로 **사용 금지** — 백엔드 v8.3 오케스트레이터·`prescription-results` 기준.

### 7-1. Axios 인스턴스

```typescript
// lib/api/client.ts
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 요청 인터셉터 — JWT 자동 주입
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    // Zustand persist store에서 토큰 직접 읽기
    const auth = JSON.parse(localStorage.getItem('townpulse-auth') ?? '{}')
    const token = auth?.state?.accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// 응답 인터셉터 — 401 → /login 리다이렉트
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('townpulse-auth')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 7-2. 대시보드·지도 API ★ v2

```typescript
// lib/api/dashboard.ts
import apiClient from './client'
import type { DashboardSummary, VillageListItem, VillageMapSummary } from '../types/dashboard'
import type { VillageListItem as MapVillage } from '../types/village'

export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const { data } = await apiClient.get('/api/townpulse/dashboard/summary')
    return data
  },

  getMapVillages: async (params?: { grade?: string; sigun?: string }): Promise<{
    villages: MapVillage[]
    total: number
  }> => {
    const { data } = await apiClient.get('/api/townpulse/dashboard/map/villages', { params })
    return data
  },

  getMapVillageSummary: async (villageCode: string): Promise<VillageMapSummary> => {
    const { data } = await apiClient.get(
      `/api/townpulse/dashboard/map/villages/${villageCode}`,
    )
    return data
  },
}
```

### 7-3. 마을 상세 API ★ v2

```typescript
// lib/api/village.ts
import apiClient from './client'
import type { VillageDetail } from '../types/village'

export const villageApi = {
  getDetail: async (villageCode: string): Promise<VillageDetail> => {
    const { data } = await apiClient.get(`/api/townpulse/village-detail/${villageCode}`)
    return data
  },
}
```

### 7-4. 처방 API ★ v2

```typescript
// lib/api/prescription.ts
import apiClient from './client'
import type { PrescriptionList } from '../types/prescription'

export const prescriptionApi = {
  // 마을 처방 목록 (village_id = UUID, village-detail에서 획득)
  getByVillage: async (villageId: string): Promise<PrescriptionList> => {
    const { data } = await apiClient.get(
      `/api/townpulse/prescription-results/by-village/${villageId}`,
    )
    return data
  },

  // 처방 생성 (TVI 기반 dispatch — 없을 때 1회 호출)
  generate: async (villageId: string): Promise<PrescriptionList> => {
    const { data } = await apiClient.post('/api/townpulse/prescription-results', {
      village_id: villageId,
    })
    return data
  },
}

// SSE — prescription_result_id 단위 Gemini 스트리밍 (EventSource, 헤더 불가 → ?token=)
export function createPrescriptionStream(
  prescriptionResultId: string,
  onChunk: (text: string) => void,
  onDone: () => void,
): () => void {
  const token = JSON.parse(localStorage.getItem('townpulse-auth') ?? '{}')?.state?.accessToken
  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/townpulse/prescription-results/${prescriptionResultId}/stream?token=${token}`

  const es = new EventSource(url)

  es.onmessage = (e) => {
    if (e.data === '[DONE]') {
      es.close()
      onDone()
      return
    }
    onChunk(e.data)
  }

  es.onerror = () => {
    es.close()
    onDone()
  }

  return () => es.close()
}
```

### 7-5. 리포트 API ★ v2

```typescript
// lib/api/report.ts
import apiClient from './client'
import type { ReportData, ReportBuildRequest } from '../types/report'

export const reportApi = {
  buildData: async (body: ReportBuildRequest): Promise<ReportData> => {
    const { village_code, ...options } = body
    const { data } = await apiClient.post(
      `/api/townpulse/report-data/${village_code}`,
      options,
    )
    return data
  },
}
```

### 7-6. 인증 API ★ v2 → v2.1 데모 모드

```typescript
// lib/api/auth.ts
import apiClient from './client'
import { useAuthStore } from '@/lib/store/authStore'

export const authApi = {
  login: async (orgId: string, password: string) => {
    const { data } = await apiClient.post('/api/townpulse/users/login', {
      org_id: orgId,
      password,
    })
    return data as { access_token: string; org_name: string; user_name: string }
  },

  /** MVP 데모: ID/PW 없이 읽기전용 JWT (백엔드 §12-1b) */
  fetchDemoToken: async () => {
    const { data } = await apiClient.post('/api/townpulse/users/demo/token')
    return data as { access_token: string; scope: string; expires_in: number }
  },
}

/** 앱 진입 시 1회 — 토큰 없으면 데모 JWT 발급 후 authStore 저장 */
export async function ensureDemoSession(): Promise<void> {
  const { accessToken } = useAuthStore.getState()
  if (accessToken) return
  const { access_token } = await authApi.fetchDemoToken()
  useAuthStore.getState().login(access_token, '데모', '방문자')
}
```

> 로그인 폼(`app/(auth)/login/page.tsx`)은 **삭제하지 않음** — v1.0 유료 전환·QA GATE 1용.

---

## 8. 지도 컴포넌트 (Leaflet)

### 8-1. 동적 Import (SSR 비활성)

```typescript
// components/map/VillageMap.tsx — 이 파일 자체는 'use client'
// 상위에서 dynamic import

// app/(dashboard)/map/page.tsx
import dynamic from 'next/dynamic'

const VillageMap = dynamic(
  () => import('@/components/map/VillageMap'),
  { ssr: false, loading: () => <div className="h-full bg-gray-100 animate-pulse rounded-lg" /> }
)
```

### 8-2. 히트맵 구현

```typescript
// components/map/VillageMap.tsx
'use client'

import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import type { VillageListItem } from '@/lib/types/village'
import { tviGradeColor, getTviGrade } from '@/lib/utils/tvi'

interface VillageMapProps {
  villages: VillageListItem[]
  selectedIndicator: 'tvi' | 'vacant' | 'elderly' | 'bus' | 'stop_access'
  onVillageClick: (code: string) => void
}

export default function VillageMap({ villages, selectedIndicator, onVillageClick }: VillageMapProps) {
  // GeoJSON 파일은 public/geojson/chungbuk_emd.geojson
  const geoJsonStyle = (feature: GeoJSON.Feature) => {
    const village = villages.find((v) => v.village_code === feature.properties?.emd_code)
    if (!village) return { fillColor: '#e5e7eb', fillOpacity: 0.5, color: '#fff', weight: 1 }

    // 지표 필터: stop_access = bus_interval_score 0 또는 정류장 1km 밖
    const grade = getTviGrade(village.tvi_score)
    const fill =
      selectedIndicator === 'stop_access' && (village.bus_interval_score ?? 100) === 0
        ? '#7f1d1d'
        : tviGradeColor[grade]

    return { fillColor: fill, fillOpacity: 0.7, color: '#ffffff', weight: 1 }
  }

  const onEachFeature = (feature: any, layer: any) => {
    const village = villages.find(v => v.village_code === feature.properties.emd_code)
    if (village) {
      layer.bindTooltip(
        `${village.village_name}<br/>TVI ${village.tvi_score}점`,
        { sticky: true }
      )
      layer.on('click', () => onVillageClick(village.village_code))
    }
  }

  return (
    <MapContainer
      center={[36.8, 127.9]}  // 충북 중심 좌표
      zoom={9}
      className="h-full w-full"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='© OpenStreetMap'
      />
      <GeoJSON
        // @ts-ignore
        data={/* chungbuk_emd.geojson fetch */}
        style={geoJsonStyle}
        onEachFeature={onEachFeature}
      />
    </MapContainer>
  )
}
```

### 8-3. GeoJSON 로드

```typescript
// app/(dashboard)/map/page.tsx
'use client'

import { useEffect, useState } from 'react'

export default function MapPage() {
  const [geoJson, setGeoJson] = useState(null)

  useEffect(() => {
    fetch('/geojson/chungbuk_emd.geojson')
      .then(r => r.json())
      .then(setGeoJson)
  }, [])

  // ...
}
```

---

## 9. AI 처방 설명 (SSE 스트리밍) ★ v2

> v1의 자유 채팅(`/prescription/chat`)은 백엔드 v8에 없음.  
> **1순위 처방 카드**의 `prescription_result_id`에 대해 `GET .../stream`으로 Gemini 설명을 스트리밍한다.  
> `QuickQuestionBar`는 동일 스트림을 재호출하거나 `ai_description` 캐시를 표시.

### 9-1. 처방 페이지 구현

```typescript
// app/(dashboard)/prescription/[villageCode]/page.tsx
'use client'

import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '@/lib/store/chatStore'
import { prescriptionApi, createPrescriptionStream } from '@/lib/api/prescription'
import { villageApi } from '@/lib/api/village'

export default function PrescriptionPage({ params }: { params: { villageCode: string } }) {
  const { villageCode } = params
  const { messages, isStreaming, addMessage, setStreaming, appendToLastAssistant } = useChatStore()
  const [primaryResultId, setPrimaryResultId] = useState<string | null>(null)
  const [noPrescriptionReason, setNoPrescriptionReason] = useState<string | null>(null)
  const cleanupRef = useRef<(() => void) | null>(null)

  useEffect(() => {
    ;(async () => {
      setNoPrescriptionReason(null)
      const detail = await villageApi.getDetail(villageCode)
      let list = await prescriptionApi.getByVillage(detail.village_id)
      if (!list.prescriptions.length) {
        try {
          list = await prescriptionApi.generate(detail.village_id)
        } catch (e) {
          // 데모 scope(403) 또는 dispatch_rule 0건(양호 등급) — §12-1d
          const status = (e as { response?: { status?: number } })?.response?.status
          if (status === 403) {
            setNoPrescriptionReason(
              '이 마을은 위험 지표가 낮아 별도 처방이 필요하지 않습니다.',
            )
            return
          }
          throw e
        }
      }
      const top = list.prescriptions.find((p) => p.rank === 1)
      if (top) setPrimaryResultId(top.id)
    })()
  }, [villageCode])

  const startStream = (prescriptionResultId: string) => {
    if (isStreaming) return
    addMessage(villageCode, { role: 'assistant', content: '', timestamp: new Date().toISOString() })
    setStreaming(true)
    cleanupRef.current = createPrescriptionStream(
      prescriptionResultId,
      (text) => appendToLastAssistant(villageCode, text),
      () => setStreaming(false),
    )
  }

  const handleQuickQuestion = () => {
    if (primaryResultId) startStream(primaryResultId)
  }

  useEffect(() => () => { cleanupRef.current?.() }, [])

  // ...render PrescriptionCard ×3 + ChatBubble + QuickQuestionBar
  // noPrescriptionReason 있으면 처방 패널 대신 안내 문구 표시
}
```

> **§13 데모 폴백 (v2.2):** `demo_readonly`에서 `generate()` POST → 403. §12-1d 선생성 마을은 `by-village`에 row가 있어 `generate` 미호출. `양호` 등급(dispatch 0건)은 빈 목록 + 403 모두 **동일 UX**로 처리.

### 9-2. 빠른 질문 버튼

```typescript
// components/prescription/QuickQuestionBar.tsx
const QUICK_QUESTIONS = [
  '예산 상세 내역 알려줘',
  '행안부 기금 신청 방법은?',
  '타 지역 성공 사례 있어?',
  '시행 일정 어떻게 잡아야 해?',
]

export function QuickQuestionBar({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1">
      {QUICK_QUESTIONS.map((q) => (
        <button
          key={q}
          onClick={() => onSelect(q)}
          className="flex-shrink-0 text-xs bg-blue-50 text-blue-700 px-3 py-1.5 rounded-full hover:bg-blue-100 transition-colors"
        >
          {q}
        </button>
      ))}
    </div>
  )
}
```

---

## 10. PDF 리포트 생성

### 10-1. PDF 생성 유틸

```typescript
// lib/utils/pdf.ts
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

export async function generatePDF(elementId: string, filename: string): Promise<void> {
  const element = document.getElementById(elementId)
  if (!element) throw new Error('PDF 대상 요소를 찾을 수 없습니다')

  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
  })

  const imgData = canvas.toDataURL('image/png')
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  })

  const pdfWidth = pdf.internal.pageSize.getWidth()
  const pdfHeight = (canvas.height * pdfWidth) / canvas.width

  pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)
  pdf.save(filename)
}
```

### 10-2. 리포트 생성 페이지

```typescript
// app/(dashboard)/report/[villageCode]/page.tsx
'use client'

import { useState } from 'react'
import { generatePDF } from '@/lib/utils/pdf'
import { reportApi } from '@/lib/api/report'

export default function ReportPage({ params }: { params: { villageCode: string } }) {
  const [options, setOptions] = useState({
    includeRiskAnalysis: true,
    includePrescriptions: true,
    includeBudget: true,
    includeBenchmark: false,
    includeTrend: false,
  })
  const [isGenerating, setIsGenerating] = useState(false)

  const handleGeneratePDF = async () => {
    setIsGenerating(true)
    try {
      // 1. 백엔드에서 리포트 데이터 fetch
      await reportApi.buildData({
        village_code: params.villageCode,
        include_risk_analysis: options.includeRiskAnalysis,
        include_prescriptions: options.includePrescriptions,
        include_budget_simulation: options.includeBudget,
        include_benchmark: options.includeBenchmark,
        include_trend_5y: options.includeTrend,
      })

      // 2. 미리보기 영역을 PDF로 변환
      await generatePDF('report-preview', `townpulse_${params.villageCode}_${new Date().toISOString().slice(0, 10)}.pdf`)
    } finally {
      setIsGenerating(false)
    }
  }

  // ...render
}
```

---

## 11. 인증 흐름

### 11-1. 로그인

```typescript
// app/(auth)/login/page.tsx
'use client'

import { useAuthStore } from '@/lib/store/authStore'
import { authApi } from '@/lib/api/auth'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const { login } = useAuthStore()
  const router = useRouter()

  const handleLogin = async (orgId: string, password: string) => {
    try {
      const { access_token, org_name, user_name } = await authApi.login(orgId, password)
      login(access_token, org_name, user_name)
      router.replace('/dashboard')
    } catch {
      // 오류 메시지 표시
    }
  }
  // ...
}
```

### 11-2. 인증 가드 (미들웨어)

```typescript
// middleware.ts (프로젝트 루트)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Next.js middleware에서 localStorage 접근 불가 → 쿠키 또는 헤더로 처리
  // 단순 MVP에서는 클라이언트 레이아웃에서 Zustand 확인 후 redirect
  return NextResponse.next()
}
```

> **주의:** Next.js App Router에서 JWT는 클라이언트 레이아웃(`app/(dashboard)/layout.tsx`)에서 Zustand persist store를 확인해 리다이렉트한다. 미들웨어 레벨 보호는 v1.1에서 HttpOnly 쿠키 방식으로 전환 예정.

---

## 12. 디자인 시스템

> ★ v2.1 **기본 = 라이트** · **다크 = 토글** · `:root` = 라이트 SSOT · `.dark` = 다크 SSOT  
> 브랜드 컬러: TownPulse Blue (`#1F4E79` / `#185FA5`) — FOODOPENLAB 에메랄드 가이드와 동일 패턴, hue만 블루(250) 계열.

### 12-1. 테마 기본 방침

| 항목 | 값 |
|---|---|
| 기본 테마 | **`light`** (`defaultTheme="light"`) |
| 토글 | Header 우측 **Moon → 다크** / **Sun → 라이트** |
| 제어 | `next-themes` + `<html class="dark">` (`attribute="class"`) |
| Tailwind | `darkMode: 'class'` (v3) |
| 컴포넌트 색 | 시맨틱 토큰 (`bg-background`, `text-foreground` …) **우선** |

**TVI 시맨틱 색(위험/주의/안전)** 은 라이트·다크 **공통** — `#E24B4A` / `#EF9F27` / `#639922` (지도·배지·차트).

### 12-2. CSS 변수 (`app/globals.css`)

```css
/* 기본 = 라이트 (와이어프레임 v2 설계 UI) */
:root {
  --background: oklch(0.99 0.005 250);
  --foreground: oklch(0.22 0.04 250);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.22 0.04 250);
  --primary: oklch(0.42 0.08 250);           /* #1F4E79 근사 */
  --primary-foreground: oklch(0.99 0 0);
  --secondary: oklch(0.96 0.02 250);         /* #E6F1FB 근사 */
  --secondary-foreground: oklch(0.45 0.1 250); /* #185FA5 */
  --muted: oklch(0.96 0.01 250);
  --muted-foreground: oklch(0.45 0.02 250);
  --accent: oklch(0.48 0.12 250);            /* #185FA5 */
  --accent-foreground: oklch(0.99 0 0);
  --destructive: oklch(0.55 0.2 25);
  --border: oklch(0.90 0.01 250);
  --input: oklch(0.94 0.01 250);
  --ring: oklch(0.48 0.12 250);
  --header: oklch(0.42 0.08 250);            /* 헤더 전용 — 라이트에서도 #1F4E79 */
  --header-foreground: oklch(0.99 0 0);
  --chart-grid: oklch(0.92 0.01 250);
}

/* 토글 = 다크 (신규 — 다크 네이비 + 블루 primary) */
.dark {
  --background: oklch(0.13 0.02 250);
  --foreground: oklch(0.95 0 0);
  --card: oklch(0.16 0.02 250);
  --card-foreground: oklch(0.95 0 0);
  --primary: oklch(0.62 0.12 250);           /* 다크에서 밝은 블루 */
  --primary-foreground: oklch(0.13 0.02 250);
  --secondary: oklch(0.22 0.02 250);
  --secondary-foreground: oklch(0.85 0.02 250);
  --muted: oklch(0.22 0.02 250);
  --muted-foreground: oklch(0.65 0 0);
  --accent: oklch(0.62 0.12 250);
  --accent-foreground: oklch(0.13 0.02 250);
  --destructive: oklch(0.65 0.2 25);
  --border: oklch(0.28 0.02 250);
  --input: oklch(0.20 0.02 250);
  --ring: oklch(0.62 0.12 250);
  --header: oklch(0.16 0.03 250);
  --header-foreground: oklch(0.95 0 0);
  --chart-grid: oklch(0.25 0.02 250);
}

@layer base {
  body {
    @apply bg-background text-foreground;
  }
}
```

### 12-3. Tailwind 설정

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        card: { DEFAULT: 'var(--card)', foreground: 'var(--card-foreground)' },
        primary: { DEFAULT: 'var(--primary)', foreground: 'var(--primary-foreground)' },
        secondary: { DEFAULT: 'var(--secondary)', foreground: 'var(--secondary-foreground)' },
        muted: { DEFAULT: 'var(--muted)', foreground: 'var(--muted-foreground)' },
        accent: { DEFAULT: 'var(--accent)', foreground: 'var(--accent-foreground)' },
        destructive: 'var(--destructive)',
        border: 'var(--border)',
        input: 'var(--input)',
        ring: 'var(--ring)',
        header: { DEFAULT: 'var(--header)', foreground: 'var(--header-foreground)' },
        /* TVI 고정 — 테마 무관 */
        'tvi-danger': '#E24B4A',
        'tvi-warning': '#EF9F27',
        'tvi-safe': '#639922',
      },
    },
  },
}

export default config
```

### 12-4. ThemeToggle 컴포넌트

```typescript
// components/theme/theme-toggle.tsx
'use client'

import { Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])
  if (!mounted) {
    return <button type="button" className="size-10 rounded-full" aria-hidden />
  }

  const isDark = resolvedTheme === 'dark'

  return (
    <button
      type="button"
      className="inline-flex size-10 items-center justify-center rounded-full text-header-foreground hover:bg-white/10"
      aria-label={isDark ? '라이트 모드로 전환' : '다크 모드로 전환'}
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
    >
      {isDark ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </button>
  )
}
```

| 현재 | 아이콘 | 클릭 시 |
|---|---|---|
| **라이트 (기본)** | Moon | → 다크 |
| **다크** | Sun | → 라이트 |

**배치:** `components/layout/Header.tsx` 우측(로그아웃 앞) · D-01 로그인 카드 우상단(선택).

### 12-5. 시맨틱 클래스 패턴 (권장)

```typescript
// 레이아웃
'bg-background text-foreground'
'bg-header text-header-foreground'           // 헤더 — 라이트·다크 각각 --header
'border-border bg-card shadow-sm'

// 사이드바 활성
'bg-secondary text-secondary-foreground border-l-4 border-l-accent'

// 카드·버튼
'bg-card border border-border rounded-lg p-4'
'bg-primary hover:bg-accent text-primary-foreground'

// 보조 텍스트
'text-muted-foreground'
```

### 12-6. 지양 패턴

```typescript
// ❌ 하드코딩 — 라이트/다크 전환 시 깨짐
'bg-white dark:bg-[#0a0a0a]'
'bg-[#1F4E79]'   // → bg-header 또는 bg-primary

// ✅ TVI·지도 히트맵만 예외적으로 고정 hex 허용
fillColor: tviGradeColor[grade]  // lib/utils/tvi.ts
```

### 12-7. 컴포넌트별 테마 메모

| 영역 | 라이트 | 다크 |
|---|---|---|
| StatCard variant | `bg-secondary` / danger·warning 틴트 | 동일 토큰, 대비만 `.dark`에서 조정 |
| Leaflet 타일 | OSM 기본 | `dark:brightness-90 dark:contrast-110` (선택) |
| Recharts | `--chart-grid` 축·그리드 | 다크에서 grid 색 자동 전환 |
| PDF 미리보기 | `bg-card` | 인쇄 시 라이트 고정 권장 |

### 12-8. 반응형 레이아웃 패턴

```typescript
// 2열 그리드 (지표 카드)
'grid grid-cols-2 md:grid-cols-4 gap-4'

// 2열 콘텐츠 영역
'grid grid-cols-1 lg:grid-cols-2 gap-6'

// 사이드바 너비
'w-0 md:w-[180px] flex-shrink-0 transition-all'
```

---

## 13. 백엔드 연동 시 주의사항

> **AI 코딩 시 이 섹션을 반드시 확인할 것.**  
> 계약 기준: `TownPulse_백엔드_MVP_개발정의서_v9_5.md` §7·§9·§9-3-1·§9-4·§9-5·§12-1b·§12-1d, `TownPulse_ERD_MVP_v6_1.md` SNAP 컬럼.

### 13-1. API 응답 타입 계약 ★ v2

백엔드(`FastAPI + Pydantic`)와 프론트엔드(`TypeScript`)의 타입이 일치해야 한다.  
아래 타입을 기준으로 삼는다. 백엔드가 다른 필드명을 쓰면 프론트엔드 타입을 맞춰 수정한다.

```typescript
// lib/types/village.ts

// GET /api/townpulse/dashboard/map/villages 응답 항목
export interface VillageListItem {
  village_id: string              // UUID — snap·prescription API용
  village_code: string            // "4300025000" — URL·GeoJSON 조인
  village_name: string
  sigun_name: string
  tvi_score: number
  tvi_grade: 'danger' | 'warning' | 'safe'
  tvi_label: string
  color_hex: string
  lat: number
  lng: number
  bus_interval_score?: number     // 0 = 교통 공백 ★ v2
  nearest_stop_distance_m?: number
}

// GET /api/townpulse/dashboard/map/villages/{village_code} — 클릭 요약
export interface VillageMapSummary {
  village_code: string
  village_name: string
  tvi_score: number
  tvi_grade: 'danger' | 'warning' | 'safe'
  nearest_stop_distance_m: number | null
  bus_stops_within_1km: number | null
}

// GET /api/townpulse/village-detail/{village_code}
export interface SnapTransport {
  bus_route_count: number | null   // null = tago_city_code 미보유(증평군) — "0대" 아님 ★ v2.3
  avg_bus_interval_min: number | null
  nearest_stop_distance_m: number | null
  bus_stops_within_1km: number | null
  fetched_at: string
}

export interface VillageDetail {
  village_id: string
  village_code: string
  village_name: string
  sigun_name: string
  tvi_score: number
  tvi_grade: 'danger' | 'warning' | 'safe'
  bus_interval_score: number
  vacant_house_rate: number
  elderly_rate: number
  bus_interval_minutes: number | null      // avg_bus_interval_min 별칭
  nearest_stop_distance_m: number | null   // ★ SNAP_TRANSPORT
  bus_stops_within_1km: number | null      // ★ SNAP_TRANSPORT
  transport_gap: boolean                   // bus_interval_score === 0 (확정 공백만; 증평형 절충값 제외) ★ v2.3
  population_change_rate: number
  extinction_probability_5y: number
  snap_transport?: SnapTransport
  updated_at: string
  prescriptions_preview?: PrescriptionItem[]  // 상위 2건
}
```

```typescript
// lib/types/prescription.ts

export interface PrescriptionItem {
  id: string                      // prescription_result UUID — SSE용 ★ v2
  rank: 1 | 2 | 3
  code: string
  title: string
  description: string | null      // Gemini 생성 — null이면 스트림으로 채움
  budget_min: number
  budget_max: number
  tvi_gain_min: number
  tvi_gain_max: number
  fund_applicable: boolean
  timeline: 'urgent' | 'medium' | 'long'
}

export interface PrescriptionList {
  village_id: string
  prescriptions: PrescriptionItem[]
  generated_at: string
}
```

```typescript
// lib/types/dashboard.ts

// GET /api/townpulse/dashboard/summary 응답
export interface DashboardSummary {
  total_villages: number        // 228
  danger_count: number          // 114
  warning_count: number         // 68
  safe_count: number            // 46
  total_vacant_houses: number   // 41200
  transport_gap_count: number   // bus_interval_score === 0 마을 수 ★ v2 (15098534 반영)
  top5_danger_villages: {
    village_code: string
    village_name: string
    sigun_name: string
    tvi_score: number
  }[]
  grade_changed_this_month: number
  pending_prescription_count: number
}
```

### 13-2. SSE 스트리밍 프로토콜 ★ v2

백엔드 `GET /api/townpulse/prescription-results/{id}/stream`:

```
data: 빈집 매입 비용은
data:  약 2억원으로
data: [DONE]
```

- `EventSource.onmessage` — `e.data`가 순수 텍스트 청크 (JSON 래핑 없을 수 있음)
- `[DONE]` 또는 `onerror` 시 연결 종료
- JWT: `?token=` 쿼리 (Trinity mixin, 백엔드 §6)

### 13-3. CORS 허용 도메인

백엔드 FastAPI가 허용해야 할 Origin:

```python
# FastAPI CORS 설정 (백엔드 담당자 확인 필요)
allow_origins = [
  "https://townpulse.site",
  "https://www.townpulse.site",
  "http://localhost:3000",
]
```

### 13-4. 인증 토큰 전달 방식

- 프론트: `Authorization: Bearer {token}` 헤더로 전달
- SSE는 EventSource가 헤더 설정 불가 → `?token={token}` 쿼리 파라미터로 전달
- 백엔드가 SSE 엔드포인트에서 쿼리 파라미터 `token`을 파싱해야 함

### 13-5. village_code vs village_id ★ v2

| 용도 | 필드 |
|---|---|
| Next.js URL `/map/[villageCode]` | `village_code` (10자리) |
| GeoJSON `feature.properties.emd_code` 조인 | `village_code` |
| `prescription-results`, `snap/*` | `village_id` (UUID) |

`village-detail` 1회 호출로 `village_id`를 확보한 뒤 처방·SNAP API에 사용한다.

### 13-6. 날짜·시간 형식

- 모든 날짜: ISO 8601 UTC → 프론트에서 로컬 시간으로 변환

```typescript
// lib/utils/format.ts
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

export function formatBudget(manwon: number): string {
  if (manwon >= 10000) return `${(manwon / 10000).toFixed(1)}억원`
  return `${manwon.toLocaleString()}만원`
}
```

---

## 14. Vercel 배포 설정

### 14-1. vercel.json

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["icn1"],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    }
  ]
}
```

### 14-2. Vercel 환경 변수 등록

Vercel 대시보드 → Project → Settings → Environment Variables:

| 키 | 값 | 환경 |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `https://api.townpulse.site` | Production, Preview |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Development |

### 14-3. 도메인 설정

1. Vercel 대시보드 → Domains → `townpulse.site` 추가
2. 도메인 구매처 DNS 설정:
   - A 레코드: `@` → Vercel IP (76.76.21.21)
   - CNAME: `www` → `cname.vercel-dns.com`
3. SSL: Vercel 자동 발급 (Let's Encrypt)

---

## 15. 개발 체크리스트

### 환경 설정

- [ ] `npm install next-themes` ★ v2.1
- [ ] `app/globals.css` — `:root`(라이트) / `.dark`(다크) 토큰 ★ v2.1
- [ ] `app/layout.tsx` — `ThemeProvider` `defaultTheme="light"` ★ v2.1
- [ ] `tailwind.config.ts` — `darkMode: 'class'` + 시맨틱 color map ★ v2.1
- [ ] `components/theme/theme-toggle.tsx` + `Header.tsx` 배치 ★ v2.1
- [ ] 하드코딩 `bg-white`·`#1F4E79` → 시맨틱 토큰 치환 ★ v2.1
- [ ] `.env.local` 작성 (`NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`)
- [ ] Leaflet CSS 전역 import (`app/layout.tsx`)
- [ ] `next.config.ts` Leaflet transpile 설정
- [ ] Vercel CLI 설치 및 로그인 (`npm i -g vercel && vercel login`)

### 공통 인프라

- [ ] `lib/api/client.ts` — Axios 인스턴스 + JWT 인터셉터
- [ ] `lib/api/dashboard.ts` — summary + map/villages ★ v2
- [ ] `lib/api/village.ts` — village-detail ★ v2
- [ ] `lib/api/prescription.ts` — prescription-results + SSE ★ v2
- [ ] `lib/api/report.ts` — report-data ★ v2
- [ ] `lib/store/authStore.ts` — 인증 Zustand (persist)
- [ ] `lib/store/mapStore.ts` — 지도 필터 Zustand
- [ ] `lib/store/chatStore.ts` — 채팅 Zustand
- [ ] `lib/utils/tvi.ts` — TVI 등급 유틸
- [ ] `lib/utils/format.ts` — 날짜·예산 포맷
- [ ] `lib/types/` — 모든 타입 정의 (백엔드 응답과 일치 확인)
- [ ] `components/ui/Badge.tsx`, `RiskBar.tsx`, `LoadingSpinner.tsx`

### 레이아웃

- [ ] `app/layout.tsx` — 루트 레이아웃
- [ ] `app/(dashboard)/layout.tsx` — 헤더 + 사이드바 + 인증 가드
- [ ] `components/layout/Header.tsx`
- [ ] `components/layout/Sidebar.tsx` (데스크톱)
- [ ] `components/layout/BottomNav.tsx` (모바일)

### D-01 로그인

- [ ] `app/(auth)/login/page.tsx`
- [ ] `lib/api/auth.ts`
- [ ] 로그인 성공 → /dashboard redirect
- [ ] 오류 메시지 표시

### D-02 대시보드

- [ ] `app/(dashboard)/dashboard/page.tsx`
- [ ] `components/dashboard/StatCard.tsx`
- [ ] `components/dashboard/DangerTop5.tsx`
- [ ] `components/dashboard/MapPreview.tsx` (히트맵 미니)
- [ ] `lib/api/dashboard.ts`
- [ ] `GET /api/townpulse/dashboard/summary` 연동
- [ ] StatCard 4번째 — **교통 공백** (`transport_gap_count`) ★ v2

### D-03 소멸위험 지도

- [ ] `app/(dashboard)/map/page.tsx`
- [ ] `components/map/VillageMap.tsx` (dynamic import)
- [ ] `components/map/MapFilters.tsx`
- [ ] `components/map/VillageSummaryCard.tsx`
- [ ] `public/geojson/chungbuk_emd.geojson` 파일 배치
- [ ] `dashboardApi.getMapVillages` 연동 (구 mapApi 제거) ★ v2
- [ ] MapFilters — `stop_access` 지표 필터 ★ v2
- [ ] 마을 클릭 → 요약 카드 출현

### D-04 마을 상세

- [ ] `app/(dashboard)/map/[villageCode]/page.tsx`
- [ ] `villageApi.getDetail` — `/village-detail/{village_code}` ★ v2
- [ ] `components/village/IndicatorCards.tsx` (5개 지표 — 정류장 접근 포함) ★ v2
- [ ] `components/village/RiskBarChart.tsx`
- [ ] `components/village/ExtinctionProbability.tsx`
- [ ] AI 처방 미리보기 (상위 2개)
- [ ] breadcrumb 내비게이션

### D-05 AI 처방

- [ ] `app/(dashboard)/prescription/[villageCode]/page.tsx`
- [ ] `components/prescription/PrescriptionCard.tsx`
- [ ] `components/prescription/ChatBubble.tsx`
- [ ] `components/prescription/QuickQuestionBar.tsx`
- [ ] `components/prescription/ChatInput.tsx`
- [ ] `prescriptionApi.getByVillage` / `generate` ★ v2
- [ ] SSE `prescription-results/{id}/stream?token=` (Gemini) ★ v2
- [ ] 처방 3개 초기 로드

### D-06 리포트 생성

- [ ] `app/(dashboard)/report/[villageCode]/page.tsx`
- [ ] `components/report/ReportOptions.tsx`
- [ ] `components/report/ReportPreview.tsx`
- [ ] `lib/utils/pdf.ts` — html2canvas + jsPDF
- [ ] `reportApi.buildData` — `POST /report-data/{village_code}` ★ v2

### 모바일 반응형

- [ ] M-01~M-05 모든 화면 모바일 레이아웃 확인
- [ ] 하단 탭 내비게이션 (≤767px)
- [ ] 히트맵 모바일 터치 확대/축소
- [ ] 채팅 입력창 모바일 키보드 올라올 때 레이아웃 유지

### 백엔드 연동 확인

- [ ] 백엔드 v8.3 오케스트레이터 경로 일치 (`§0` 표) ★ v2
- [ ] `village_id`(UUID) vs `village_code`(10자리) 혼용 없음 ★ v2
- [ ] SNAP_TRANSPORT 필드 UI 표시 (`nearest_stop_distance_m` 등) ★ v2
- [ ] CORS 오류 없음 확인 (`api.townpulse.site`)
- [ ] SSE 스트리밍 토큰 전달 (`?token=` 쿼리) 확인
- [ ] village_code 10자리 형식 일치 확인
- [ ] JWT 401 → /login redirect 동작 확인

### Vercel 배포

- [ ] `vercel.json` 작성
- [ ] Vercel 환경 변수 등록 (`NEXT_PUBLIC_API_BASE_URL`)
- [ ] `townpulse.site` 도메인 연결
- [ ] HTTPS 인증서 발급 확인
- [ ] 첫 방문 → **라이트 UI** · 토글 → 다크 · 새로고침 후 `townpulse-theme` 유지 ★ v2.1
- [ ] D-02~D-06·모바일 주요 화면 라이트/다크 대비 점검 ★ v2.1
- [ ] 프로덕션 빌드 오류 없음 (`npm run build`)

---

*© 2026 Pulse Lab | TownPulse 프론트엔드 개발 정의서 v2.1 | Confidential*
