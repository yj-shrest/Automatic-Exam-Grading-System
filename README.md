# Automated Exam Grading System

Automated Exam Grading System is a web-based grading platform designed to reduce the manual work involved in checking exam papers. It supports two major grading workflows:

- MCQ grading, where a scanned answer PDF is compared with a question sheet and answer key to calculate scores.
- Subjective answer grading, where handwritten or scanned answer PDFs are converted to text, compared with reference material, and scored with AI support.

The project combines a React frontend with Python-based backend services for OCR, computer vision, retrieval, and AI-assisted evaluation. Teachers can upload reference PDFs, choose or create a subject database, submit student answer sheets, and receive marks with comments.

## Main Features

- Upload and grade MCQ answer sheets from PDF files.
- Preview converted PDF pages in the browser before grading.
- Enter an MCQ answer key and export scores as an Excel file.
- Add reference material as a searchable database for subjective grading.
- Grade subjective answers using OCR, reference retrieval, and LLM-based scoring.
- Detect diagrams in answer sheets and grade diagram-based content separately.
- Use a React interface with routes for home, MCQ grading, database selection, subjective grading, login, and signup screens.

## Project Structure

```text
.
|-- Frontend/                React + Vite frontend
|   |-- src/
|   |   |-- App.jsx          Application routes
|   |   |-- Home.jsx         Main dashboard
|   |   |-- Mcq.jsx          MCQ grading screen
|   |   |-- AddDB.jsx        Reference database selection/upload
|   |   |-- SubjectiveGrading.jsx
|   |   |-- Login.jsx
|   |   `-- SignUp.jsx
|   `-- package.json
|-- OCR/
|   |-- Backend/             Subjective grading backend
|   |   |-- backend.py       Flask API on port 5000
|   |   |-- ocr.py           Florence OCR pipeline
|   |   |-- RAGG.py          PDF embedding and FAISS retrieval
|   |   |-- LLM.py           LLM/Gemini grading helpers
|   |   |-- DiagramDetecter.py
|   |   `-- Database/        Stored reference databases
|   |-- train.py             YOLO training script for diagram detection
|   `-- runs/                Trained YOLO runs and weights
|-- OpenCv/
|   |-- backend.py           MCQ grading Flask API on port 5001
|   |-- DetectTick.py        Tick detection and scoring logic
|   |-- assets/              Sample images
|   `-- static/              Generated PDF preview images
|-- Object Detection/        Earlier YOLO diagram/object detection experiments
`-- .gitignore
```

## How The System Works

### MCQ Grading Flow

1. The teacher uploads a question sheet image.
2. The teacher uploads a student answer sheet PDF.
3. The frontend sends the PDF to the MCQ backend, which converts the PDF pages into preview images.
4. The teacher enters the answer key, for example `ABCDABCD`.
5. The MCQ backend aligns the question image with each answer page, detects tick marks using OpenCV, reads nearby question/option text using PaddleOCR, and compares detected answers with the answer key.
6. The frontend displays student/page scores and can export them to `MCQ_Scores.xlsx`.

### Subjective Grading Flow

1. The teacher chooses an existing reference database or uploads a new reference PDF.
2. When a new database is uploaded, the backend extracts text from the PDF, creates embeddings with `BAAI/bge-base-en-v1.5`, and stores a FAISS index.
3. The teacher enters the question, optional ideal answer, full marks, and uploads the student's answer PDF.
4. The backend detects diagrams using a YOLO model.
5. The backend runs OCR on the answer PDF using `microsoft/Florence-2-large-ft`.
6. Relevant reference pages are retrieved from the FAISS database.
7. The answer is scored using the configured LLM workflow. If diagrams are detected, part of the marks are assigned to diagram grading and the rest to text grading.
8. The frontend displays the final grade and grading comment.

## Frontend

The frontend is built with:

- React 18
- Vite
- React Router
- Tailwind CSS
- Lucide React icons
- `xlsx` and `file-saver` for Excel export

Important routes:

| Route | Purpose |
| --- | --- |
| `/` | Home/dashboard |
| `/mcq` | MCQ grading |
| `/addDB` | Select or upload a reference database |
| `/subjective` | Subjective answer grading |
| `/login` | Login screen |
| `/signup` | Signup screen |

## Backend Services

This project uses two Flask backends.

### Subjective Backend

Location:

```text
OCR/Backend/backend.py
```

Default port:

```text
5000
```

Main endpoints:

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | GET | Health/welcome response |
| `/count` | POST | Counts pages in an uploaded PDF |
| `/add_database` | POST | Saves a reference PDF and builds embeddings/index files |
| `/all_databases` | GET | Lists available reference databases |
| `/subjective` | POST | Grades a subjective answer PDF |

### MCQ Backend

Location:

```text
OpenCv/backend.py
```

Default port:

```text
5001
```

Main endpoints:

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | GET | Health/welcome response |
| `/convert_pdf` | POST | Converts uploaded PDF pages to preview images |
| `/mcq` | POST | Detects answers and returns MCQ scores |

## Requirements

### System Requirements

- Node.js and npm
- Python 3.10 or newer recommended
- Poppler installed and available in PATH for `pdf2image`
- Ollama installed locally if using the Ollama grading path
- Sufficient memory for OCR and transformer models
- CUDA-capable GPU recommended, but the code can fall back to CPU

### Python Packages

The Python code uses packages including:

- Flask
- flask-cors
- torch
- transformers
- sentence-transformers
- faiss
- numpy
- opencv-python
- Pillow
- pdf2image
- PyPDF2
- pypdf
- ultralytics
- paddleocr
- ollama
- google-genai / google-generativeai
- pydantic
- nltk

Some experimental code under `OCR/ai-grader` includes its own `requirements.txt`, but the active Flask backends do not currently have a single shared requirements file.

## Setup And Run

### 1. Install Frontend Dependencies

```bash
cd Frontend
npm install
```

### 2. Start The Subjective Backend

Run this from the subjective backend folder so relative paths such as `Database/` resolve correctly.

```bash
cd OCR/Backend
python backend.py
```

The service starts at:

```text
http://localhost:5000
```

### 3. Start The MCQ Backend

Run this from the OpenCV backend folder.

```bash
cd OpenCv
python backend.py
```

The service starts at:

```text
http://localhost:5001
```

### 4. Start The Frontend

```bash
cd Frontend
npm run dev
```

Vite will print the local frontend URL, usually:

```text
http://localhost:5173
```

## Model And Database Files

The repository contains trained/model-related artifacts such as:

- YOLO weights under `OCR/runs/detect/.../weights/`
- YOLO weights under `Object Detection/runs/detect/.../weights/`
- Reference FAISS databases under `OCR/Backend/Database/`
- Sample assets under `OpenCv/assets/` and `OCR/Backend/assets/`

The subjective backend loads:

```text
microsoft/Florence-2-large-ft
BAAI/bge-base-en-v1.5
../runs/detect/train11/weights/best.pt
```

The first run may download model files from their providers, depending on the local environment.

## Configuration Notes

- The frontend expects the subjective backend at `http://localhost:5000`.
- The frontend expects the MCQ backend at `http://localhost:5001`.
- `pdf2image` requires Poppler. If PDF conversion fails, check that Poppler is installed and available in PATH.
- The subjective grading code currently contains LLM provider setup inside backend helper files. For production use, API keys should be moved to environment variables such as `GEMINI_API_KEY`.
- The Ollama grading path expects the model `koesn/mistral-7b-instruct:latest` to be available locally.
- `OpenCv/backend.py` saves uploaded MCQ PDFs under `OpenCv/uploads/new.pdf`; make sure the `uploads` folder exists before running MCQ grading.

## Development Notes

- The project has prototype and experimental folders in addition to the active app code.
- `Object Detection/` appears to contain earlier YOLO training experiments.
- `OCR/ai-grader/` appears to contain an alternate or earlier Chroma/Gemini-based RAG grading experiment.
- The main active UI is in `Frontend/src`.
- The main active subjective backend is `OCR/Backend/backend.py`.
- The main active MCQ backend is `OpenCv/backend.py`.

## Build

To create a production frontend build:

```bash
cd Frontend
npm run build
```

To preview the build:

```bash
npm run preview
```

## Future Improvements

- Add a shared Python `requirements.txt` for the active backends.
- Move API keys and model names into environment variables.
- Add authentication logic behind the login and signup screens.
- Add validation and better error messages for PDF/model failures.
- Store uploaded files in unique per-request paths instead of shared temporary filenames.
- Add automated tests for scoring logic, API endpoints, and frontend flows.
