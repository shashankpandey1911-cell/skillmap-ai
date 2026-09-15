import { useState, useCallback } from 'react'

type ValidationRules<T> = {
  [K in keyof T]?: {
    required?: boolean
    minLength?: number
    maxLength?: number
    pattern?: RegExp
    patternMessage?: string
    custom?: (value: T[K]) => string | null
  }
}

type Errors<T> = Partial<Record<keyof T, string>>

export function useFormValidation<T extends Record<string, unknown>>(
  initialValues: T,
  rules: ValidationRules<T>
) {
  const [values, setValues] = useState<T>(initialValues)
  const [errors, setErrors] = useState<Errors<T>>({})
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({})

  const validate = useCallback(
    (vals: T): Errors<T> => {
      const newErrors: Errors<T> = {}
      for (const key in rules) {
        const rule = rules[key]
        if (!rule) continue
        const value = vals[key]

        if (rule.required && (!value || (typeof value === 'string' && !value.trim()))) {
          newErrors[key] = 'This field is required'
          continue
        }

        if (rule.minLength && typeof value === 'string' && value.length < rule.minLength) {
          newErrors[key] = `Must be at least ${rule.minLength} characters`
          continue
        }

        if (rule.maxLength && typeof value === 'string' && value.length > rule.maxLength) {
          newErrors[key] = `Must be no more than ${rule.maxLength} characters`
          continue
        }

        if (rule.pattern && typeof value === 'string' && !rule.pattern.test(value)) {
          newErrors[key] = rule.patternMessage ?? 'Invalid format'
          continue
        }

        if (rule.custom) {
          const msg = rule.custom(value)
          if (msg) newErrors[key] = msg
        }
      }
      return newErrors
    },
    [rules]
  )

  const handleChange = useCallback(
    (field: keyof T, value: T[keyof T]) => {
      setValues((prev) => {
        const next = { ...prev, [field]: value }
        if (touched[field]) {
          setErrors(validate(next))
        }
        return next
      })
    },
    [touched, validate]
  )

  const handleBlur = useCallback(
    (field: keyof T) => {
      setTouched((prev) => ({ ...prev, [field]: true }))
      setErrors(validate(values))
    },
    [values, validate]
  )

  const validateAll = useCallback(() => {
    const allTouched: Partial<Record<keyof T, boolean>> = {}
    for (const key in rules) allTouched[key] = true
    setTouched(allTouched)
    const newErrors = validate(values)
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }, [values, rules, validate])

  const reset = useCallback(() => {
    setValues(initialValues)
    setErrors({})
    setTouched({})
  }, [initialValues])

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validateAll,
    reset,
    setValues,
  }
}
