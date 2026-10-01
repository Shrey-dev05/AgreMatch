# 🚀 Hackathon & Opportunity Aggregator (Agreggator)

A unified portal designed for students and developers to discover, track, and apply to hackathons across multiple platforms in a single dashboard. Includes support for campus organizers to list local college hackathons and an interactive teammate finder.

---

## 🌟 Highlights

- **Multi-Platform Real-Time Scraping**: Aggregates 50+ live hackathons directly from:
  - 🟣 **[Devfolio](https://devfolio.co/hackathons)** (`https://devfolio.co/hackathons`)
  - 🟢 **[Devnovate](https://devnovate.co/events)** (`https://devnovate.co/events`)
  - 🔵 **[Unstop](https://unstop.com/hackathons?oppstatus=open&usertype=students&domain=2&course=6&passingOutYear=2028)** (`https://unstop.com/hackathons`)
- **🏫 Local & Campus Hackathons**: College clubs and student organizers can publish their own local/in-person hackathons directly onto the portal with prize pools, registration forms, dates, and venue details.
- **🤝 Find a Partner / Matchmaker**: Post teammate requests for specific hackathons with your tech stack (Frontend, Backend, AI/ML, UI/UX) to find complementary co-builders.
- **✨ AI Resume Matcher**: Upload a PDF or DOCX resume to analyze technical skills against live hackathon challenges.
- **🔍 Smart Filtering & Bookmarking**: Filter by platform, format (In-Person, Virtual, Hybrid), prize pool, search keywords, and save favorite hackathons to your browser.

---

## 🛠️ Tech Stack & Architecture

- **Frontend**: [Next.js](https://nextjs.org/) (App Router), React 19, TypeScript, [Tailwind CSS](https://tailwindcss.com/), [Framer Motion](https://motion.dev/), [Lucide React](https://lucide.dev/).
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+), Uvicorn, HTTPX (async client), BeautifulSoup4, LXML, Pydantic.
- **Data Persistence**: JSON-backed local storage (`backend/data/local_hackathons.json`) & in-memory caching with force-refresh support.

---

## 📋 Prerequisites

Before running the project on your machine, ensure you have:

1. **Node.js** (v18.0.0 or higher) — [Download Node.js](https://nodejs.org/)
2. **Python** (v3.10 or higher) — [Download Python](https://www.python.org/)
3. **Git** — [Download Git](https://git-scm.com/)

---

## ⚡ Quick Start Guide (Run on Any PC)

Follow these steps to clone and run the project locally.

### 1. Clone or Open the Repository

```bash
cd Aggregator_New
```

---

### 2. Backend Setup (FastAPI)

1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. (Recommended) Create and activate a Python virtual environment:
   - **On Windows (PowerShell / Command Prompt)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **On macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   > 🚀 The backend will start at: `http://localhost:8000`  
   > 📖 Interactive Swagger API Docs: `http://localhost:8000/docs`

---

### 3. Frontend Setup (Next.js)

1. Open a **new terminal** and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   > 🌐 Open your browser and go to: `http://localhost:3000`  
   > 🔗 Hackathons Portal: `http://localhost:3000/hackathons`

---

## 📡 Backend API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status and root greeting |
| `GET` | `/api/hackathons/scrape/all` | Scrapes Devfolio, Devnovate, and Unstop in parallel + includes local hackathons |
| `GET` | `/api/hackathons/scrape/devfolio` | Returns live hackathons scraped from Devfolio |
| `GET` | `/api/hackathons/scrape/devnovate` | Returns live events scraped from Devnovate |
| `GET` | `/api/hackathons/scrape/unstop` | Returns live student hackathons scraped from Unstop |
| `GET` | `/api/hackathons/local` | Returns all locally listed campus hackathons |
| `POST` | `/api/hackathons/local` | Submit a new local campus hackathon |
| `DELETE` | `/api/hackathons/local/{id}` | Remove a local hackathon listing |
| `GET` | `/api/stats` | Aggregated statistics (total count, prize pool, breakdown) |
| `POST` | `/api/parse-resume` | AI Resume scoring against opportunity description |

> **Pro Tip**: Add `?refresh=true` to any scraper endpoint (e.g., `/api/hackathons/scrape/all?refresh=true`) to bypass the cache and fetch fresh data from target websites.

---

## 🏫 How to List a Local / Campus Hackathon

1. Navigate to `http://localhost:3000/hackathons`.
2. Click **"+ List Campus Hackathon"** in the top action bar.
3. Fill in the event details:
   - **Title** (e.g. *IIT Bombay CodeFest 2026*)
   - **College / Organization**
   - **Format** (In-Person / Virtual / Hybrid)
   - **Venue Location** (e.g. *Auditorium Hall, North Campus*)
   - **Prize Pool** (₹)
   - **Registration URL** (Google Form, website, or portal)
   - **Dates & Contact Info**
4. Click **Publish Hackathon** — the event will instantly appear in the feed under the **Campus / Local** filter with special spotlight styling.

---

## ❓ Troubleshooting & FAQs

### 1. PowerShell Script Execution Error (Windows)
If you get `cannot be loaded because running scripts is disabled on this system`:
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Or run commands with `cmd /c "npm run dev"` or `npm.cmd run dev`.

### 2. Port Already in Use
- If port `8000` is occupied: run `uvicorn main:app --port 8001` and update the URL in `frontend/src/app/hackathons/page.tsx`.
- If port `3000` is occupied: Next.js will automatically suggest running on `http://localhost:3001`.

### 3. Running Without Internet
The frontend includes a pre-seeded snapshot in `frontend/src/data/initialHackathons.json`. Even if offline, you can explore the portal, test local submissions, filter by platforms, and test UI components seamlessly.

---

## 👥 Contributing
Pull requests are welcome! Feel free to submit scrapers for additional hackathon platforms (MLH, Devpost, DoraHacks) or UI enhancements.
