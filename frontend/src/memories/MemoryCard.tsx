import { useState } from 'react'
import type { Memory } from './types'
import { useReportMemory } from './useMemories'

interface MemoryCardProps {
  memory: Memory
}

export function MemoryCard({ memory }: MemoryCardProps) {
  const reportMemory = useReportMemory()
  const [confirming, setConfirming] = useState(false)

  async function handleReport() {
    try {
      await reportMemory.mutateAsync(memory.id)
    } catch {
      // Swallow: reportMemory.isError already drives the inline message below.
    }
    setConfirming(false)
  }

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm">
      <p className="whitespace-pre-wrap leading-relaxed text-gray-900">{memory.text}</p>

      <div className="mt-4 flex items-center justify-between gap-2 border-t border-gray-50 pt-3">
        <p className="text-[11px] text-gray-400">این خاطره به‌صورت ناشناس نمایش داده می‌شود.</p>

        {reportMemory.isSuccess ? (
          <span className="shrink-0 text-xs font-medium text-emerald-600">گزارش شد ✓</span>
        ) : confirming ? (
          <div className="flex shrink-0 items-center gap-2">
            <button
              type="button"
              onClick={handleReport}
              disabled={reportMemory.isPending}
              className="text-xs font-medium text-red-600 disabled:opacity-50"
            >
              مطمئنی؟
            </button>
            <button
              type="button"
              onClick={() => setConfirming(false)}
              className="text-xs text-gray-400"
            >
              انصراف
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setConfirming(true)}
            className="shrink-0 text-xs font-medium text-gray-400 underline"
          >
            گزارش این خاطره
          </button>
        )}
      </div>

      {reportMemory.isError && (
        <p className="mt-1.5 text-right text-[11px] text-red-500">گزارش ثبت نشد. دوباره امتحان کن.</p>
      )}
    </div>
  )
}
