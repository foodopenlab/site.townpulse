"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ComponentProps } from "react";
import { ensureDemoSession } from "@/lib/api/auth";

type DemoLinkProps = Omit<ComponentProps<typeof Link>, "href"> & {
  href: string;
};

/** 데모 토큰 발급 후 앱 화면으로 이동 */
export function DemoLink({ href, onClick, children, ...rest }: DemoLinkProps) {
  const router = useRouter();

  return (
    <Link
      href={href}
      onClick={async (e) => {
        onClick?.(e);
        if (e.defaultPrevented) return;
        e.preventDefault();
        await ensureDemoSession();
        router.push(href);
      }}
      {...rest}
    >
      {children}
    </Link>
  );
}
