# RMG News AI Agent - Frontend

A modern, responsive frontend for the RMG News AI Agent built with Next.js and Tailwind CSS.

## Features

- 🎯 **Market Intelligence Dashboard** - AI-powered insights for the RMG industry
- 📊 **Trending Topics** - Real-time identification of hot topics
- 📈 **Statistics Cards** - Key metrics at a glance
- 🔄 **Real-time Updates** - Refresh data with one click
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- ⚡ **Fast Performance** - Built with Next.js for optimal speed

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Icons**: Heroicons
- **Language**: TypeScript
- **State Management**: React Hooks

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/          # Reusable components
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorMessage.tsx
│   │   ├── globals.css          # Global styles
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Main dashboard
│   └── ...
├── public/                      # Static assets
└── package.json
```

## API Integration

The frontend connects to the backend API endpoints:

- **GET** `/api/insights` - Market insights dashboard data
- **GET** `/health` - Health check
- **GET** `/` - Root endpoint

## Components

### LoadingSpinner
A reusable loading component with different sizes and custom text.

### ErrorMessage
A consistent error display component with retry functionality.

### Dashboard
The main dashboard component that displays:
- Market statistics
- Trending topics
- Last updated timestamp
- Refresh functionality

## Styling

The app uses Tailwind CSS for styling with:
- Responsive grid layouts
- Modern card designs
- Consistent color scheme
- Smooth transitions and hover effects

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Style

- TypeScript for type safety
- ESLint for code quality
- Prettier for code formatting
- Component-based architecture

## Deployment

The app can be deployed to:
- Vercel (recommended for Next.js)
- Netlify
- Any static hosting service

### Build for Production

```bash
npm run build
npm run start
```

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test on different screen sizes
4. Update documentation as needed

## License

This project is part of the RMG News AI Agent platform.
