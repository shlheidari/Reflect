import { ReportRow } from '../../admin/moderation/ReportRow'
import { useAdminReports } from '../../admin/moderation/useAdminModeration'

export function AdminModerationPage() {
  const { data: reports, isLoading, isError, refetch } = useAdminReports()

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-xl font-bold text-gray-900">مدیریت محتوا</h1>
      <p className="mt-1 text-sm text-gray-500">خاطره‌های گزارش‌شده توسط شرکت‌کننده‌ها</p>

      <div className="mt-6 space-y-3">
        {isLoading &&
          [0, 1, 2].map((key) => <div key={key} className="h-32 animate-pulse rounded-2xl bg-white/70" />)}

        {isError && (
          <div className="rounded-2xl bg-white p-6 text-center text-gray-500">
            <p>یه مشکلی پیش اومد.</p>
            <button
              type="button"
              onClick={() => refetch()}
              className="mt-3 text-sm font-medium text-gray-900 underline"
            >
              دوباره امتحان کن
            </button>
          </div>
        )}

        {reports && reports.length === 0 && (
          <div className="rounded-2xl bg-white p-8 text-center text-gray-500">
            <p className="text-3xl">✨</p>
            <p className="mt-3 font-medium text-gray-900">هیچ گزارشی وجود ندارد</p>
          </div>
        )}

        {reports?.map((report) => (
          <ReportRow key={report.id} report={report} />
        ))}
      </div>
    </div>
  )
}
