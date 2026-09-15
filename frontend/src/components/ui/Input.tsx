import type { InputHTMLAttributes, ReactNode } from 'react'
import { cn } from '../../utils/cn'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
}

export function Input({ label, error, hint, className, id, ...rest }: InputProps) {
  const inputId = id ?? (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)
  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={cn(
          'h-11 w-full rounded-xl border border-gray-200 bg-white px-4 text-sm text-gray-900',
          'placeholder:text-gray-400 transition-all duration-200',
          'focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 focus:outline-none',
          error && 'border-red-300 focus:border-red-500 focus:ring-red-500/20',
          className,
        )}
        aria-invalid={Boolean(error)}
        {...rest}
      />
      {error ? (
        <p className="text-xs text-red-600 flex items-center gap-1" role="alert">
          <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
          {error}
        </p>
      ) : hint ? (
        <p className="text-xs text-gray-500">{hint}</p>
      ) : null}
    </div>
  )
}

export function FieldError({ children }: { children: ReactNode }) {
  return (
    <p className="text-xs text-red-600 flex items-center gap-1">
      <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
      {children}
    </p>
  )
}
