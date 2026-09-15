import type { ReactNode } from 'react'
import { cn } from '../../utils/cn'

interface CardProps {
  title?: ReactNode
  subtitle?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
  /** Remove default padding for custom layouts */
  noPadding?: boolean
}

export function Card({ title, subtitle, actions, children, className, noPadding }: CardProps) {
  return (
    <section
      className={cn(
        'rounded-2xl border border-gray-100 bg-white shadow-card',
        'transition-shadow duration-200 hover:shadow-card-hover',
        className,
      )}
    >
      {(title || actions) && (
        <header className="flex items-start justify-between gap-3 border-b border-gray-100 px-6 py-4">
          <div>
            {title && <h3 className="text-sm font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-gray-500">{subtitle}</p>}
          </div>
          {actions}
        </header>
      )}
      <div className={noPadding ? '' : 'px-6 py-5'}>{children}</div>
    </section>
  )
}
