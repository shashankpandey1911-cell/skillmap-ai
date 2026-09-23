import { useState } from 'react'
import { Trash2 } from 'lucide-react'

/** Two-step delete: the trash icon turns into a confirm prompt. */
export function ConfirmDelete({ onConfirm }: { onConfirm: () => void }) {
  const [confirming, setConfirming] = useState(false)
  if (!confirming) {
    return (
      <button
        type="button"
        onClick={() => setConfirming(true)}
        className="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600"
        aria-label="Delete"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    )
  }
  return (
    <span className="flex items-center gap-1.5">
      <span className="text-xs text-slate-500">Delete?</span>
      <button
        type="button"
        onClick={onConfirm}
        className="rounded-md bg-red-600 px-2 py-1 text-xs font-medium text-white hover:bg-red-700"
      >
        Yes
      </button>
      <button
        type="button"
        onClick={() => setConfirming(false)}
        className="rounded-md px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
      >
        No
      </button>
    </span>
  )
}
