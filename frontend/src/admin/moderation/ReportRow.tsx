import { useState } from 'react'
import type { AdminReport } from './types'
import { useDismissReport, useHideMemory, useResolveReport, useRestoreMemory } from './useAdminModeration'

const reportStatusLabel: Record<AdminReport['status'], string> = {
  OPEN: 'در انتظار بررسی',
  RESOLVED: 'حل‌شده',
  DISMISSED: 'رد‌شده',
}

const reportStatusClass: Record<AdminReport['status'], string> = {
  OPEN: 'bg-amber-100 text-amber-700',
  RESOLVED: 'bg-green-100 text-green-700',
  DISMISSED: 'bg-gray-100 text-gray-500',
}

const memoryStatusLabel: Record<AdminReport['memory']['status'], string> = {
  VISIBLE: 'قابل مشاهده',
  REPORTED: 'گزارش‌شده',
  HIDDEN: 'پنهان',
}

interface ReportRowProps {
  report: AdminReport
}

export function ReportRow({ report }: ReportRowProps) {
  const resolveReport = useResolveReport()
  const dismissReport = useDismissReport()
  const hideMemory = useHideMemory()
  const restoreMemory = useRestoreMemory()

  const [error, setError] = useState<string | null>(null)
  const busy =
    resolveReport.isPending || dismissReport.isPending || hideMemory.isPending || restoreMemory.isPending

  async function run(action: () => Promise<unknown>) {
    setError(null)
    try {
      await action()
    } catch {
      setError('عملیات انجام نشد.')
    }
  }

  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${reportStatusClass[report.status]}`}>
            {reportStatusLabel[report.status]}
          </span>
          <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600">
            خاطره: {memoryStatusLabel[report.memory.status]}
          </span>
        </div>
        <p className="text-xs text-gray-400">{new Date(report.created_at).toLocaleString('fa-IR')}</p>
      </div>

      <p className="mt-3 whitespace-pre-wrap text-sm text-gray-900">{report.memory.text}</p>

      {report.reason && <p className="mt-2 text-xs text-gray-500">دلیل گزارش: {report.reason}</p>}

      <div className="mt-3 flex flex-wrap gap-2 border-t border-gray-50 pt-3">
        {report.memory.status !== 'HIDDEN' ? (
          <button
            type="button"
            disabled={busy}
            onClick={() => run(() => hideMemory.mutateAsync(report.memory.id))}
            className="rounded-full bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 disabled:opacity-50"
          >
            پنهان کردن خاطره
          </button>
        ) : (
          <button
            type="button"
            disabled={busy}
            onClick={() => run(() => restoreMemory.mutateAsync(report.memory.id))}
            className="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 disabled:opacity-50"
          >
            بازگردانی خاطره
          </button>
        )}

        {report.status === 'OPEN' && (
          <>
            <button
              type="button"
              disabled={busy}
              onClick={() => run(() => resolveReport.mutateAsync(report.id))}
              className="rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 disabled:opacity-50"
            >
              حل شد
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => run(() => dismissReport.mutateAsync(report.id))}
              className="rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 disabled:opacity-50"
            >
              رد کردن گزارش
            </button>
          </>
        )}
      </div>

      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
    </div>
  )
}
