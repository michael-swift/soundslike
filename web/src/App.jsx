import { useState, useEffect, useCallback } from 'react'
import { generateSamples, synthesize, playAudio, generateHistogram } from './audio'
import './App.css'

const DISTRIBUTIONS = {
  normal: {
    name: 'Normal (Gaussian)',
    description: 'Bell curve centered on mean frequency',
    params: {
      mean: { label: 'Mean (Hz)', min: 100, max: 1000, default: 440, step: 10 },
      std: { label: 'Std Dev (Hz)', min: 5, max: 200, default: 50, step: 5 }
    }
  },
  uniform: {
    name: 'Uniform',
    description: 'Equal probability across frequency range',
    params: {
      low: { label: 'Min Freq (Hz)', min: 100, max: 800, default: 300, step: 10 },
      high: { label: 'Max Freq (Hz)', min: 200, max: 1200, default: 600, step: 10 }
    }
  },
  beta: {
    name: 'Beta',
    description: 'Flexible shape controlled by α and β',
    params: {
      alpha: { label: 'Alpha (α)', min: 0.5, max: 10, default: 2, step: 0.5 },
      beta: { label: 'Beta (β)', min: 0.5, max: 10, default: 5, step: 0.5 },
      freqLow: { label: 'Min Freq (Hz)', min: 100, max: 500, default: 220, step: 10 },
      freqHigh: { label: 'Max Freq (Hz)', min: 400, max: 1200, default: 880, step: 10 }
    }
  },
  exponential: {
    name: 'Exponential',
    description: 'Concentrated at base with long tail',
    params: {
      baseFreq: { label: 'Base Freq (Hz)', min: 100, max: 500, default: 200, step: 10 },
      scale: { label: 'Scale', min: 20, max: 300, default: 100, step: 10 }
    }
  }
}

function Histogram({ data, width = 400, height = 150 }) {
  if (!data || data.bins.length === 0) return null

  const { bins, counts, min, max } = data
  const maxCount = Math.max(...counts)
  const barWidth = width / bins.length - 2

  return (
    <svg width={width} height={height} className="histogram">
      {/* Bars */}
      {counts.map((count, i) => {
        const barHeight = (count / maxCount) * (height - 30)
        return (
          <rect
            key={i}
            x={i * (width / bins.length) + 1}
            y={height - barHeight - 20}
            width={barWidth}
            height={barHeight}
            fill="rgba(99, 179, 237, 0.8)"
            rx={2}
          />
        )
      })}
      {/* X-axis labels */}
      <text x={5} y={height - 5} fontSize="11" fill="#888">
        {Math.round(min)} Hz
      </text>
      <text x={width - 60} y={height - 5} fontSize="11" fill="#888">
        {Math.round(max)} Hz
      </text>
    </svg>
  )
}

function Slider({ label, value, onChange, min, max, step }) {
  return (
    <div className="slider-container">
      <div className="slider-header">
        <label>{label}</label>
        <span className="slider-value">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
    </div>
  )
}

export default function App() {
  const [distribution, setDistribution] = useState('normal')
  const [params, setParams] = useState({})
  const [numSamples, setNumSamples] = useState(50)
  const [duration, setDuration] = useState(1.0)
  const [samples, setSamples] = useState([])
  const [histogram, setHistogram] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)

  // Initialize params when distribution changes
  useEffect(() => {
    const dist = DISTRIBUTIONS[distribution]
    const newParams = {}
    for (const [key, config] of Object.entries(dist.params)) {
      newParams[key] = config.default
    }
    setParams(newParams)
  }, [distribution])

  // Generate samples when params change
  useEffect(() => {
    if (Object.keys(params).length === 0) return
    const newSamples = generateSamples(distribution, params, numSamples)
    setSamples(newSamples)
    setHistogram(generateHistogram(newSamples))
  }, [distribution, params, numSamples])

  const handlePlay = useCallback(() => {
    if (samples.length === 0) return
    setIsPlaying(true)

    const buffer = synthesize(samples, duration)
    const { audioContext } = playAudio(buffer)

    setTimeout(() => {
      setIsPlaying(false)
      audioContext.close()
    }, duration * 1000 + 100)
  }, [samples, duration])

  const handleParamChange = (key, value) => {
    setParams(prev => ({ ...prev, [key]: value }))
  }

  const distConfig = DISTRIBUTIONS[distribution]

  return (
    <div className="app">
      <header className="header">
        <h1>SoundsLike</h1>
        <p className="tagline">Hear what probability distributions sound like</p>
      </header>

      <main className="main">
        <section className="controls">
          <div className="distribution-select">
            <label>Distribution</label>
            <div className="button-group">
              {Object.entries(DISTRIBUTIONS).map(([key, dist]) => (
                <button
                  key={key}
                  className={`dist-button ${distribution === key ? 'active' : ''}`}
                  onClick={() => setDistribution(key)}
                >
                  {dist.name}
                </button>
              ))}
            </div>
            <p className="distribution-description">{distConfig.description}</p>
          </div>

          <div className="params">
            {Object.entries(distConfig.params).map(([key, config]) => (
              <Slider
                key={key}
                label={config.label}
                value={params[key] ?? config.default}
                onChange={(v) => handleParamChange(key, v)}
                min={config.min}
                max={config.max}
                step={config.step}
              />
            ))}

            <Slider
              label="Samples"
              value={numSamples}
              onChange={setNumSamples}
              min={10}
              max={200}
              step={10}
            />

            <Slider
              label="Duration (s)"
              value={duration}
              onChange={setDuration}
              min={0.5}
              max={3}
              step={0.25}
            />
          </div>

          <button
            className={`play-button ${isPlaying ? 'playing' : ''}`}
            onClick={handlePlay}
            disabled={isPlaying}
          >
            {isPlaying ? (
              <>
                <span className="pulse"></span>
                Playing...
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                Play Sound
              </>
            )}
          </button>
        </section>

        <section className="visualization">
          <h2>Frequency Distribution</h2>
          <div className="histogram-container">
            <Histogram data={histogram} width={400} height={180} />
          </div>
          <p className="sample-info">
            {samples.length} frequencies ranging from{' '}
            {Math.round(Math.min(...samples))} Hz to{' '}
            {Math.round(Math.max(...samples))} Hz
          </p>
        </section>
      </main>

      <footer className="footer">
        <p>
          Built with React + Web Audio API |{' '}
          <a href="https://github.com/michael-swift/soundslike" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </footer>
    </div>
  )
}
