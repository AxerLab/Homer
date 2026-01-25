import React, { useEffect, useRef } from 'react'
import { useMotionValue } from 'framer-motion'

interface ParticleBackgroundProps {
  className?: string
  particleCount?: number
  mouseInfluenceRadius?: number
}

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  baseX: number
  baseY: number
}

export const ParticleBackground: React.FC<ParticleBackgroundProps> = ({
  className,
  particleCount = 45,
  mouseInfluenceRadius = 150,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  const particles = useRef<Particle[]>([])
  const animationFrameId = useRef<number | null>(null)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvasRef.current?.getBoundingClientRect()
      if (rect) {
        mouseX.set(e.clientX - rect.left)
        mouseY.set(e.clientY - rect.top)
      }
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [mouseX, mouseY])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches

    const resizeCanvas = () => {
      if (canvas.parentElement) {
        canvas.width = canvas.parentElement.clientWidth
        canvas.height = canvas.parentElement.clientHeight
        initParticles()
      }
    }

    const initParticles = () => {
      particles.current = []
      for (let i = 0; i < particleCount; i++) {
        const size = Math.random() * 2 + 2
        const x = Math.random() * canvas.width
        const y = Math.random() * canvas.height
        particles.current.push({
          x,
          y,
          vx: (Math.random() - 0.5) * 0.2,
          vy: (Math.random() - 0.5) * 0.2,
          size,
          baseX: x,
          baseY: y,
        })
      }
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'

      const currentMouseX = mouseX.get()
      const currentMouseY = mouseY.get()

      particles.current.forEach((particle) => {
        if (!prefersReducedMotion) {
          particle.x += particle.vx
          particle.y += particle.vy

          if (particle.x < 0) particle.x = canvas.width
          if (particle.x > canvas.width) particle.x = 0
          if (particle.y < 0) particle.y = canvas.height
          if (particle.y > canvas.height) particle.y = 0

          const dx = currentMouseX - particle.x
          const dy = currentMouseY - particle.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < mouseInfluenceRadius) {
            const forceDirectionX = dx / distance
            const forceDirectionY = dy / distance
            const force = (mouseInfluenceRadius - distance) / mouseInfluenceRadius
            const directionX = forceDirectionX * force * 0.5
            const directionY = forceDirectionY * force * 0.5

            particle.x += directionX
            particle.y += directionY
          }
        }

        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fill()
      })

      animationFrameId.current = requestAnimationFrame(animate)
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current)
      }
    }
  }, [particleCount, mouseInfluenceRadius, mouseX, mouseY])

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        display: 'block',
      }}
    />
  )
}
