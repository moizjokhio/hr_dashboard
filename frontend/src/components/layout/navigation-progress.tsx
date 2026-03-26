"use client";

import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";

export function NavigationProgress() {
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimers = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (hideTimerRef.current) {
      clearTimeout(hideTimerRef.current);
      hideTimerRef.current = null;
    }
  };

  const start = () => {
    clearTimers();
    setIsLoading(true);
    setProgress(8);

    timerRef.current = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev;
        // Eases naturally as it approaches completion.
        const step = Math.max((100 - prev) * 0.08, 0.6);
        return Math.min(prev + step, 90);
      });
    }, 100);
  };

  const done = () => {
    clearTimers();
    setProgress(100);

    hideTimerRef.current = setTimeout(() => {
      setIsLoading(false);
      setProgress(0);
    }, 220);
  };

  useEffect(() => {
    const onDocumentClick = (event: MouseEvent) => {
      if (event.defaultPrevented) return;
      if (event.button !== 0) return;
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

      const target = event.target as HTMLElement | null;
      const anchor = target?.closest("a[href]") as HTMLAnchorElement | null;
      if (!anchor) return;

      const href = anchor.getAttribute("href");
      if (!href || href.startsWith("#")) return;
      if (anchor.target === "_blank") return;
      if (anchor.hasAttribute("download")) return;

      const nextUrl = new URL(anchor.href, window.location.origin);
      if (nextUrl.origin !== window.location.origin) return;
      if (nextUrl.pathname === pathname) return;

      start();
    };

    const onPopState = () => {
      start();
    };

    document.addEventListener("click", onDocumentClick, true);
    window.addEventListener("popstate", onPopState);

    return () => {
      document.removeEventListener("click", onDocumentClick, true);
      window.removeEventListener("popstate", onPopState);
      clearTimers();
    };
  }, [pathname]);

  useEffect(() => {
    if (isLoading) {
      done();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed left-0 top-0 z-[100] h-[2px] w-full"
    >
      <div
        className="h-full bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-600 transition-[width,opacity] duration-200 ease-out"
        style={{
          width: `${progress}%`,
          opacity: isLoading ? 1 : 0,
          boxShadow: "0 0 8px rgba(14, 165, 233, 0.55)",
        }}
      />
    </div>
  );
}
