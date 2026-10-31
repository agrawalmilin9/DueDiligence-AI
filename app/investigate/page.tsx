import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { InvestigationProgress } from "@/components/investigation/investigation-progress";
import { DEFAULT_REQUEST } from "@/lib/investigations";

export const metadata: Metadata = {
  title: "Investigating… — DueDiligence AI",
};

export default async function InvestigatePage({
  searchParams,
}: {
  searchParams: Promise<{ id?: string; company?: string; request?: string }>;
}) {
  const { id, company, request } = await searchParams;
  const companyName = company?.trim();
  if (!companyName || !id) redirect("/");

  return (
    <main className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-2xl flex-col justify-center px-4 py-12 sm:px-6">
      <InvestigationProgress
        companyName={companyName}
        investigationId={id}
        request={request?.trim() || DEFAULT_REQUEST}
      />
    </main>
  );
}
