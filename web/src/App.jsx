import { useState, useEffect, useCallback, useRef } from 'react'
import { synthesize, playAudio, generateHistogram } from './audio'
import './App.css'

// Generate samples for CLT demonstration
function generateCLTSamples(nDice, numSamples = 80) {
  const samples = []
  for (let i = 0; i < numSamples; i++) {
    let sum = 0
    for (let j = 0; j < nDice; j++) {
      sum += Math.random()
    }
    // Map mean to frequency range 220-880 Hz
    const mean = sum / nDice
    samples.push(mean * 660 + 220)
  }
  return samples
}

const SLIDES = [
  {
    id: 'intro',
    title: 'Sound Reasoning',
    subtitle: 'What does probability sound like?',
    description: 'A journey through the Central Limit Theorem',
    nDice: null,
    duration: 0,
  },
  {
    id: 'uniform',
    title: 'Pure Randomness',
    subtitle: 'n = 1',
    description: 'Each frequency is independently random. Listen to the chaos — sound scattered across the spectrum.',
    nDice: 1,
    duration: 4,
  },
  {
    id: 'n2',
    title: 'Adding Structure',
    subtitle: 'n = 2',
    description: 'Average two random values. Already less extreme — the edges fade.',
    nDice: 2,
    duration: 3.5,
  },
  {
    id: 'n5',
    title: 'Emerging Pattern',
    subtitle: 'n = 5',
    description: 'The middle grows stronger. Extremes become rare.',
    nDice: 5,
    duration: 3.5,
  },
  {
    id: 'n10',
    title: 'Convergence',
    subtitle: 'n = 10',
    description: 'A clear center emerges. The sound focuses.',
    nDice: 10,
    duration: 3.5,
  },
  {
    id: 'n30',
    title: 'The Bell Curve',
    subtitle: 'n = 30',
    description: 'Nearly Gaussian. From chaos to harmony — this is the Central Limit Theorem.',
    nDice: 30,
    duration: 4,
  },
  {
    id: 'outro',
    title: 'The Central Limit Theorem',
    subtitle: 'Order from randomness',
    description: 'No matter the starting distribution, averages converge to normal. You just heard it happen.',
    nDice: null,
    duration: 0,
  },
]

function Histogram({ data, width = 500, height = 200 }) {
  if (!data || data.bins.length === 0) {
    return (
      <svg width={width} height={height} className="histogram">
        <text x={width/2} y={height/2} textAnchor="middle" fill="#666" fontSize="16">
          Press play to begin
        </text>
      </svg>
    )
  }

  const { bins, counts, min, max } = data
  const maxCount = Math.max(...counts)
  const barWidth = width / bins.length - 2

  return (
    <svg width={width} height={height} className="histogram">
      {counts.map((count, i) => {
        const barHeight = (count / maxCount) * (height - 40)
        return (
          <rect
            key={i}
            x={i * (width / bins.length) + 1}
            y={height - barHeight - 30}
            width={barWidth}
            height={barHeight}
            fill="rgba(99, 179, 237, 0.85)"
            rx={2}
          />
        )
      })}
      <text x={10} y={height - 8} fontSize="12" fill="#888">
        {Math.round(min)} Hz
      </text>
      <text x={width - 70} y={height - 8} fontSize="12" fill="#888">
        {Math.round(max)} Hz
      </text>
    </svg>
  )
}

function ProgressDots({ current, total }) {
  return (
    <div className="progress-dots">
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          className={`dot ${i === current ? 'active' : ''} ${i < current ? 'completed' : ''}`}
        />
      ))}
    </div>
  )
}

export default function App() {
  const [slideIndex, setSlideIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [samples, setSamples] = useState([])
  const [histogram, setHistogram] = useState(null)
  const [isAutoPlaying, setIsAutoPlaying] = useState(false)
  const audioContextRef = useRef(null)

  const slide = SLIDES[slideIndex]

  // Generate samples when slide changes
  useEffect(() => {
    if (slide.nDice) {
      const newSamples = generateCLTSamples(slide.nDice)
      setSamples(newSamples)
      setHistogram(generateHistogram(newSamples))
    } else {
      setSamples([])
      setHistogram(null)
    }
  }, [slideIndex, slide.nDice])

  const playCurrentSlide = useCallback(() => {
    if (samples.length === 0 || slide.duration === 0) return

    setIsPlaying(true)
    const buffer = synthesize(samples, slide.duration)
    const { audioContext } = playAudio(buffer)
    audioContextRef.current = audioContext

    return new Promise(resolve => {
      setTimeout(() => {
        setIsPlaying(false)
        audioContext.close()
        resolve()
      }, slide.duration * 1000 + 200)
    })
  }, [samples, slide.duration])

  const nextSlide = useCallback(() => {
    if (slideIndex < SLIDES.length - 1) {
      setSlideIndex(prev => prev + 1)
    }
  }, [slideIndex])

  const prevSlide = useCallback(() => {
    if (slideIndex > 0) {
      setSlideIndex(prev => prev - 1)
    }
  }, [slideIndex])

  // Auto-play through all slides
  const startDemo = useCallback(async () => {
    setIsAutoPlaying(true)
    setSlideIndex(0)

    for (let i = 0; i < SLIDES.length; i++) {
      setSlideIndex(i)
      const currentSlide = SLIDES[i]

      if (currentSlide.nDice) {
        // Wait for samples to generate
        await new Promise(r => setTimeout(r, 300))

        // Generate and play
        const newSamples = generateCLTSamples(currentSlide.nDice)
        setSamples(newSamples)
        setHistogram(generateHistogram(newSamples))

        setIsPlaying(true)
        const buffer = synthesize(newSamples, currentSlide.duration)
        const { audioContext } = playAudio(buffer)

        await new Promise(r => setTimeout(r, currentSlide.duration * 1000 + 500))
        audioContext.close()
        setIsPlaying(false)

        // Pause between slides
        await new Promise(r => setTimeout(r, 800))
      } else {
        // Intro/outro slides - just pause
        await new Promise(r => setTimeout(r, i === 0 ? 2500 : 3000))
      }
    }

    setIsAutoPlaying(false)
  }, [])

  const stopDemo = useCallback(() => {
    setIsAutoPlaying(false)
    setIsPlaying(false)
    if (audioContextRef.current) {
      audioContextRef.current.close()
    }
  }, [])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (isAutoPlaying) return
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault()
        nextSlide()
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        prevSlide()
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (slide.duration > 0) {
          playCurrentSlide()
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [nextSlide, prevSlide, playCurrentSlide, isAutoPlaying, slide.duration])

  const isFirstSlide = slideIndex === 0
  const isLastSlide = slideIndex === SLIDES.length - 1

  return (
    <div className="app demo-mode">
      <div className="slide">
        <div className="slide-content">
          <h1 className="slide-title">{slide.title}</h1>
          {slide.subtitle && (
            <h2 className="slide-subtitle">{slide.subtitle}</h2>
          )}

          {slide.nDice && (
            <div className="histogram-container">
              <Histogram data={histogram} width={500} height={200} />
            </div>
          )}

          <p className="slide-description">{slide.description}</p>

          {isPlaying && (
            <div className="playing-indicator">
              <span className="pulse"></span>
              <span>Playing...</span>
            </div>
          )}
        </div>

        <div className="slide-controls">
          {isFirstSlide && !isAutoPlaying ? (
            <button className="demo-button" onClick={startDemo}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
              Start Demo
            </button>
          ) : isAutoPlaying ? (
            <button className="demo-button stop" onClick={stopDemo}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="6" width="12" height="12"/>
              </svg>
              Stop
            </button>
          ) : (
            <div className="nav-buttons">
              <button
                className="nav-button"
                onClick={prevSlide}
                disabled={isFirstSlide}
              >
                ← Back
              </button>
              {slide.duration > 0 && (
                <button
                  className="nav-button play"
                  onClick={playCurrentSlide}
                  disabled={isPlaying}
                >
                  {isPlaying ? 'Playing...' : '▶ Play'}
                </button>
              )}
              <button
                className="nav-button"
                onClick={nextSlide}
                disabled={isLastSlide}
              >
                Next →
              </button>
            </div>
          )}
        </div>

        <ProgressDots current={slideIndex} total={SLIDES.length} />
      </div>

      <footer className="footer">
        <p>
          <a href="https://github.com/michael-swift/sound-reasoning" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
          {!isAutoPlaying && <span className="hint"> · Arrow keys to navigate · Enter to play</span>}
        </p>
      </footer>
    </div>
  )
}
