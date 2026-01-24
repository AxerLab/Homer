import { HugeiconsIcon } from '@hugeicons/react'
import type { ComponentProps } from 'react'

type HugeiconsProps = ComponentProps<typeof HugeiconsIcon>

export function Icon({
  size = 16,
  color = 'currentColor',
  strokeWidth = 1.5,
  className,
  ...rest
}: HugeiconsProps) {
  return (
    <HugeiconsIcon
      size={size}
      color={color}
      strokeWidth={strokeWidth}
      className={className}
      {...rest}
    />
  )
}

export { HugeiconsIcon }
