import { Link } from 'react-router-dom'
import type { ParticipantSummary } from './types'

function initials(name: string): string {
  return name.trim().charAt(0) || '؟'
}

interface ParticipantCardProps {
  participant: ParticipantSummary
}

export function ParticipantCard({ participant }: ParticipantCardProps) {
  return (
    <div className="flex items-center gap-4 rounded-2xl bg-white p-4 shadow-sm">
      <div className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gray-200 text-lg font-bold text-gray-600">
        {participant.avatar ? (
          <img src={participant.avatar} alt="" className="h-full w-full object-cover" />
        ) : (
          <span>{initials(participant.display_name)}</span>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate font-bold text-gray-900">{participant.display_name}</p>
        <p className="mt-1 text-sm text-gray-500">{participant.rating_count} نظر ثبت شده</p>
      </div>

      {participant.rated_by_me ? (
        <span className="shrink-0 rounded-full bg-green-100 px-3 py-1.5 text-sm font-medium text-green-700">
          ✓ نظر ثبت شده
        </span>
      ) : (
        <Link
          to={`/rate/${participant.id}`}
          className="shrink-0 rounded-full bg-gray-900 px-4 py-1.5 text-sm font-medium text-white"
        >
          نظر بده
        </Link>
      )}
    </div>
  )
}
