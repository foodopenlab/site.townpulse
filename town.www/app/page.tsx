import { FeatureSection } from "@/components/landing/FeatureSection";
import { HeroSection } from "@/components/landing/HeroSection";
import { HowToSection } from "@/components/landing/HowToSection";
import { LandingCTA } from "@/components/landing/LandingCTA";
import { LandingNav } from "@/components/landing/LandingNav";
import { StatsSection } from "@/components/landing/StatsSection";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <LandingNav />
      <HeroSection />
      <StatsSection />
      <FeatureSection />
      <HowToSection />
      <LandingCTA />
      <footer className="border-t border-border py-6 text-center text-xs text-muted-foreground">
        © 2026 Pulse Lab · TownPulse · 충북 마을생존 AI 의사결정 플랫폼
      </footer>
    </div>
  );
}
