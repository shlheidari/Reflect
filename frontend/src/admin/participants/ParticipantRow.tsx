import { useState } from 'react'
import { ApiError } from '../../lib/apiClient'
import type { AdminParticipant } from './types'
import { useResetAdminParticipantPassword, useUpdateAdminParticipant } from './useAdminParticipants'

interface ParticipantRowProps {
  participant: AdminParticipant
}

export function ParticipantRow({ participant }: ParticipantRowProps) {
  const updateParticipant = useUpdateAdminParticipant()
  const resetPassword = useResetAdminParticipantPassword()

  const [displayName, setDisplayName] = useState(participant.display_name)
  const [resetting, setResetting] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [generatedPassword, setGeneratedPassword] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const dirty = displayName !== participant.display_name

  async function handleSaveName() {
    setError(null)
    try {
      await updateParticipant.mutateAsync({ id: participant.id, payload: { display_name: displayName } })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  async function toggleActive() {
    setError(null)
    try {
      await updateParticipant.mutateAsync({
        id: participant.id,
        payload: { is_active: !participant.is_active },
      })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'ذخیره نشد.')
    }
  }

  async function handleResetPassword() {
    setError(null)
    setGeneratedPassword(null)
    try {
      const result = await resetPassword.mutateAsync({
        id: participant.id,
        payload: newPassword ? { new_password: newPassword } : undefined,
      })
      setGeneratedPassword(result.generated_password ?? newPassword)
      setNewPassword('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'بازنشانی نشد.')
    }
  }

  return (
    <tr className="border-b border-gray-100 align-top">
      <td className="py-3 pl-3">
        <input
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          onBlur={() => dirty && handleSaveName()}
          className="w-32 rounded-lg border border-gray-200 p-1.5 text-sm"
        />
        <p className="mt-1 font-mono text-[11px] text-gray-400">{participant.username}</p>
      </td>

      <td className="py-3 pl-3 text-center">
        <button
          type="button"
          onClick={toggleActive}
          className={`rounded-full px-2.5 py-1 text-xs font-medium ${
            participant.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
          }`}
        >
          {participant.is_active ? 'فعال' : 'غیرفعال'}
        </button>
      </td>

      <td className="py-3 pl-3 text-center text-xs text-gray-500">
        {participant.last_login ? new Date(participant.last_login).toLocaleDateString('fa-IR') : 'هرگز'}
      </td>

      <td className="py-3 pl-3 text-center text-sm text-gray-700">{participant.ratings_given_count}</td>
      <td className="py-3 pl-3 text-center text-sm text-gray-700">{participant.ratings_received_count}</td>

      <td className="py-3">
        {!resetting ? (
          <button
            type="button"
            onClick={() => setResetting(true)}
            className="text-xs font-medium text-gray-500 underline"
          >
            بازنشانی رمز
          </button>
        ) : (
          <div className="w-48 space-y-1.5">
            <input
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="رمز جدید (اختیاری)"
              className="w-full rounded-lg border border-gray-200 p-1.5 text-xs"
            />
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleResetPassword}
                disabled={resetPassword.isPending}
                className="rounded-full bg-gray-900 px-3 py-1 text-xs font-medium text-white disabled:opacity-50"
              >
                ثبت
              </button>
              <button
                type="button"
                onClick={() => {
                  setResetting(false)
                  setGeneratedPassword(null)
                }}
                className="text-xs text-gray-400"
              >
                بستن
              </button>
            </div>
            {generatedPassword && (
              <p className="rounded-lg bg-amber-50 p-1.5 font-mono text-xs text-amber-800">
                {generatedPassword}
              </p>
            )}
          </div>
        )}
        {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
      </td>
    </tr>
  )
}
