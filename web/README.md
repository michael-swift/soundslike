# SoundsLike Web Demo

Interactive web demo for the SoundsLike probability sonification library.

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Deployment

The demo is deployed to GitHub Pages. To deploy:

1. Build the production version: `npm run build`
2. The built files are in `dist/`
3. GitHub Actions can automatically deploy on push to main

## Tech Stack

- React 18
- Vite
- Web Audio API for sound synthesis
- No external audio libraries - pure Web Audio API
