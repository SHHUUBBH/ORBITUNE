"use client"

import { useEffect, useRef } from 'react'

export default function AnimatedBackground({ isDarkMode = true }) {
    const svgRef = useRef(null)

    useEffect(() => {
        const svg = svgRef.current
        if (!svg) return

        const circles = svg.querySelectorAll('.floating-circle')
        const lines = svg.querySelectorAll('.floating-line')

        circles.forEach((circle, i) => {
            const duration = 15 + i * 3
            const delay = i * 2
            circle.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`
        })

        lines.forEach((line, i) => {
            const duration = 12 + i * 2
            const delay = i * 1.5
            line.style.animation = `drift ${duration}s linear ${delay}s infinite`
        })
    }, [])

    const darkColors = {
        circles: ['rgba(139, 92, 246, 0.8)', 'rgba(59, 130, 246, 0.75)', 'rgba(236, 72, 153, 0.7)'],
        lines: 'rgba(139, 92, 246, 0.6)',
    }

    const lightColors = {
        circles: ['rgba(15, 23, 42, 0.4)', 'rgba(30, 41, 59, 0.35)', 'rgba(51, 65, 85, 0.3)'],
        lines: 'rgba(15, 23, 42, 0.25)',
    }

    const colors = isDarkMode ? darkColors : lightColors

    return (
        <>
            <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translate(0, 0) scale(1);
            opacity: 0.3;
          }
          25% {
            transform: translate(30px, -40px) scale(1.1);
            opacity: 0.5;
          }
          50% {
            transform: translate(-20px, -80px) scale(0.9);
            opacity: 0.4;
          }
          75% {
            transform: translate(-40px, -40px) scale(1.05);
            opacity: 0.45;
          }
        }

        @keyframes drift {
          0% {
            transform: translateX(0) translateY(0);
            opacity: 0.2;
          }
          50% {
            opacity: 0.4;
          }
          100% {
            transform: translateX(100px) translateY(-50px);
            opacity: 0.2;
          }
        }
      `}</style>
            <svg
                ref={svgRef}
                className="absolute inset-0 w-full h-full pointer-events-none"
                xmlns="http://www.w3.org/2000/svg"
            >
                {/* Floating Circles */}
                <circle className="floating-circle" cx="10%" cy="20%" r="60" fill={colors.circles[0]} />
                <circle className="floating-circle" cx="85%" cy="30%" r="80" fill={colors.circles[1]} />
                <circle className="floating-circle" cx="50%" cy="70%" r="50" fill={colors.circles[2]} />
                <circle className="floating-circle" cx="20%" cy="80%" r="70" fill={colors.circles[0]} />
                <circle className="floating-circle" cx="90%" cy="85%" r="55" fill={colors.circles[1]} />

                {/* Floating Lines */}
                <line className="floating-line" x1="5%" y1="15%" x2="25%" y2="25%" stroke={colors.lines} strokeWidth="2" />
                <line className="floating-line" x1="70%" y1="10%" x2="95%" y2="20%" stroke={colors.lines} strokeWidth="2" />
                <line className="floating-line" x1="15%" y1="60%" x2="40%" y2="75%" stroke={colors.lines} strokeWidth="2" />
                <line className="floating-line" x1="60%" y1="65%" x2="85%" y2="80%" stroke={colors.lines} strokeWidth="2" />
                <line className="floating-line" x1="30%" y1="40%" x2="50%" y2="50%" stroke={colors.lines} strokeWidth="2" />
            </svg>
        </>
    )
}
