"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { navigationItems } from "@/lib/navigation";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            RA
          </span>
          <p className="brand-title">ResumeAgent</p>
          <p>Private workspace for job discovery, resume review, and application control.</p>
        </div>

        <nav className="nav">
          {navigationItems.map((item) => {
            const active = pathname === item.href;

            return (
              <Link
                aria-current={active ? "page" : undefined}
                className="nav-link"
                href={item.href}
                key={item.href}
              >
                <span className="nav-label">{item.label}</span>
                <span className="nav-note">{item.note}</span>
              </Link>
            );
          })}
        </nav>

        <div className="privacy-note">
          Local-first shell. Personal resumes, trackers, imports, and config stay out of git.
        </div>
      </aside>

      <main className="content">{children}</main>
    </div>
  );
}
