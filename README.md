# Homework Grader - AI-Powered Presentation Grading System

An AI-assisted web application for teachers to evaluate student homework presentations (.pptx) according to a rubric, producing structured scoring reports with evidence quotes.

## Features

- **PPTX Parsing**: Extracts text content from PowerPoint presentations
- **Deterministic Checks**: Automatic validation of page numbers, ethics principles, and template compliance
- **AI Grading**: LLM-powered evaluation using OpenAI-compatible APIs
- **Detailed Reports**: Rubric scores with evidence quotes and improvement suggestions
- **Zero Hosting Cost**: Deployable on Netlify (frontend) and Render (backend) free tiers

## Project Structure

```
homework-grader/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models/         # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   │   ├── pptx_parser.py
│   │   │   ├── deterministic_checks.py
│   │   │   └── llm_grader.py
│   │   └── utils/
│   ├── tests/              # Unit tests
│   └── requirements.txt
├── frontend/               # Next.js TypeScript frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # API client
│   │   └── types/         # TypeScript types
│   └── package.json
└── README.md
```

## Rubric (100 points)

| Category | Points | Description |
|----------|--------|-------------|
| Ethics Principles | 15 | At least 5 distinct ethics principles |
| Scene Explanation | 50 | Specificity (20) + Coherence (15) + Ethical Link (15) |
| Template Compliance | 15 | Required fields + page numbers |
| Visual Design | 10 | Readability and organization |
| On-time Submission | 10 | Manual toggle (teacher sets) |

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key (or compatible API)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local if needed (defaults to localhost:8000)

# Run development server
npm run dev
```

### Running Both (Quick Start)

Open two terminal windows:

**Terminal 1 (Backend):**
```bash
cd homework-grader/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key_here" > .env
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd homework-grader/frontend
npm install
npm run dev
```

Visit http://localhost:3000 in your browser.

### Running Tests

```bash
cd backend
pytest -v
```

## Deployment

### Backend on Render (Free Tier)

1. Create a [Render](https://render.com) account
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENAI_MODEL`: `gpt-4o-mini` (or your preferred model)
   - `CORS_ORIGINS`: `https://your-frontend.netlify.app` (add after frontend deploy)
6. Deploy

### Frontend on Netlify (Free Tier)

1. Create a [Netlify](https://netlify.com) account
2. Import your GitHub repository
3. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/.next`
4. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL (e.g., `https://homework-grader-api.onrender.com`)
5. Deploy

**Important**: After deploying both, update the backend's `CORS_ORIGINS` to include your Netlify URL.

### Alternative: Vercel (Frontend)

1. Import repository to [Vercel](https://vercel.com)
2. Set root directory to `frontend`
3. Add `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

## API Endpoints

### `POST /api/analyze`

Analyze a PPTX presentation.

**Request:**
- `file`: PPTX file (multipart/form-data)
- `on_time`: boolean (form field)

**Response:**
```json
{
  "success": true,
  "result": {
    "total_score": 75.5,
    "rubric_scores": [...],
    "missing_items": [...],
    "improvements": [...],
    "deterministic_checks": [...],
    "on_time_submitted": true
  }
}
```

### `POST /api/parse`

Parse PPTX without grading (for debugging).

### `GET /health`

Health check endpoint.

## Environment Variables

### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model to use |
| `OPENAI_BASE_URL` | No | - | Custom API base URL |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated origins |
| `PORT` | No | `8000` | Server port |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000` | Backend API URL |

## Sample Parsed PPTX Output

```json
{
  "meta": {
    "slide_width": 9144000,
    "slide_height": 6858000,
    "units": "EMU",
    "total_slides": 5
  },
  "slides": [
    {
      "slide_no": 1,
      "elements": [
        {
          "id": "a1b2c3d4",
          "type": "text",
          "text": "Film Analizi: Etik Degerlendirme",
          "raw_text": "Film Analizi: Etik Degerlendirme",
          "bbox": {"x": 914400, "y": 914400, "w": 7315200, "h": 914400},
          "style": {"font_size": 24.0, "bold": true}
        }
      ]
    }
  ]
}
```

## Security Considerations

- PPTX files are processed in-memory and not stored
- API keys are stored only in environment variables
- File size limited to 15MB
- Basic rate limiting implemented
- CORS configured for specific origins

## License

MIT
