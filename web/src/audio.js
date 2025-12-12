// Web Audio API synthesis - mirrors the Python soundslike library

// Random number generators for distributions
function normalRandom(mean, std) {
  // Box-Muller transform
  const u1 = Math.random();
  const u2 = Math.random();
  const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  return mean + std * z;
}

function betaRandom(a, b) {
  // Using gamma distribution method
  const gammaA = gammaRandom(a);
  const gammaB = gammaRandom(b);
  return gammaA / (gammaA + gammaB);
}

function gammaRandom(shape) {
  // Marsaglia and Tsang's method
  if (shape < 1) {
    return gammaRandom(shape + 1) * Math.pow(Math.random(), 1 / shape);
  }
  const d = shape - 1/3;
  const c = 1 / Math.sqrt(9 * d);
  while (true) {
    let x, v;
    do {
      x = normalRandom(0, 1);
      v = 1 + c * x;
    } while (v <= 0);
    v = v * v * v;
    const u = Math.random();
    if (u < 1 - 0.0331 * (x * x) * (x * x)) return d * v;
    if (Math.log(u) < 0.5 * x * x + d * (1 - v + Math.log(v))) return d * v;
  }
}

function exponentialRandom(scale) {
  return -scale * Math.log(Math.random());
}

function poissonRandom(lambda) {
  const L = Math.exp(-lambda);
  let k = 0;
  let p = 1;
  do {
    k++;
    p *= Math.random();
  } while (p > L);
  return k - 1;
}

// Generate frequency samples from distributions
export function generateSamples(distribution, params, numSamples) {
  const samples = [];

  for (let i = 0; i < numSamples; i++) {
    let freq;
    switch (distribution) {
      case 'normal':
        freq = normalRandom(params.mean, params.std);
        break;
      case 'uniform':
        freq = params.low + Math.random() * (params.high - params.low);
        break;
      case 'beta':
        const beta = betaRandom(params.alpha, params.beta);
        freq = params.freqLow + beta * (params.freqHigh - params.freqLow);
        break;
      case 'exponential':
        freq = params.baseFreq + exponentialRandom(params.scale);
        break;
      case 'poisson':
        freq = poissonRandom(params.lambda);
        break;
      default:
        freq = 440;
    }
    // Clip to audible range
    samples.push(Math.max(20, Math.min(20000, freq)));
  }

  return samples;
}

// ADSR envelope generator
function generateEnvelope(length, sampleRate, attack, decay, sustain, sustainLevel, release) {
  const envelope = new Float32Array(length);
  const attackSamples = Math.floor(attack * sampleRate);
  const decaySamples = Math.floor(decay * sampleRate);
  const sustainSamples = Math.floor(sustain * sampleRate);
  const releaseSamples = Math.floor(release * sampleRate);

  let idx = 0;

  // Attack
  for (let i = 0; i < attackSamples && idx < length; i++, idx++) {
    envelope[idx] = i / attackSamples;
  }

  // Decay
  for (let i = 0; i < decaySamples && idx < length; i++, idx++) {
    envelope[idx] = 1 - (1 - sustainLevel) * (i / decaySamples);
  }

  // Sustain
  for (let i = 0; i < sustainSamples && idx < length; i++, idx++) {
    envelope[idx] = sustainLevel;
  }

  // Release
  for (let i = 0; i < releaseSamples && idx < length; i++, idx++) {
    envelope[idx] = sustainLevel * (1 - i / releaseSamples);
  }

  return envelope;
}

// Main synthesis function
export function synthesize(frequencies, duration = 1.0, sampleRate = 44100) {
  const numSamples = Math.floor(duration * sampleRate);
  const buffer = new Float32Array(numSamples);

  // Generate mixed sine waves
  for (const freq of frequencies) {
    for (let i = 0; i < numSamples; i++) {
      const t = i / sampleRate;
      buffer[i] += Math.sin(2 * Math.PI * freq * t);
    }
  }

  // Normalize
  if (frequencies.length > 0) {
    for (let i = 0; i < numSamples; i++) {
      buffer[i] /= frequencies.length;
    }
  }

  // Apply ADSR envelope
  const envelope = generateEnvelope(
    numSamples, sampleRate,
    0.05,  // attack
    0.1,   // decay
    duration - 0.25, // sustain
    0.7,   // sustain level
    0.1    // release
  );

  for (let i = 0; i < numSamples; i++) {
    buffer[i] *= envelope[i];
  }

  return buffer;
}

// Play audio using Web Audio API
export function playAudio(buffer, sampleRate = 44100) {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const audioBuffer = audioContext.createBuffer(1, buffer.length, sampleRate);
  audioBuffer.getChannelData(0).set(buffer);

  const source = audioContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioContext.destination);
  source.start();

  return { source, audioContext };
}

// Generate histogram data from samples
export function generateHistogram(samples, numBins = 30) {
  if (samples.length === 0) return { bins: [], counts: [] };

  const min = Math.min(...samples);
  const max = Math.max(...samples);
  const binWidth = (max - min) / numBins || 1;

  const counts = new Array(numBins).fill(0);

  for (const sample of samples) {
    const binIndex = Math.min(Math.floor((sample - min) / binWidth), numBins - 1);
    counts[binIndex]++;
  }

  const bins = [];
  for (let i = 0; i < numBins; i++) {
    bins.push(min + (i + 0.5) * binWidth);
  }

  return { bins, counts, min, max };
}
