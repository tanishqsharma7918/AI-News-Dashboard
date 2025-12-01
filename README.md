# 🧠 AI Pulse: Intelligent News Aggregator & Dashboard

## 📋 Overview
**AI Pulse** is a production-ready, full-stack intelligence engine designed to aggregate, cluster, and rank high-impact AI news. Unlike simple RSS readers, it uses an internal **Intelligence Layer** to group similar stories into **Topic Clusters** and ranks them by importance using a weighted popularity score.

It automatically ingests data from 20+ "high-signal" sources (OpenAI, Google Research, TechCrunch, etc.) and presents it in a premium, interactive dashboard.

---

## ✨ Key Features (V2 Upgrade)
* **🔥 Topic Clustering:** Automatically groups related articles (e.g., "Google Gemini Launch") from different sources into single **Topic Cards** to reduce noise.
* **📈 Popularity Scoring:** Ranks topics based on **Coverage** (how many sources reported it) and **Velocity**.
* **🤖 Automated Ingestion:** Self-healing fetcher that pulls from 20+ RSS feeds using robust anti-bot headers.
* **📊 3-Tab Intelligence Dashboard:**
    * **All News:** Chronological feed of every update.
    * **Popular:** High-level view of trending clusters with scores.
    * **Favorites:** Personalized saved items.
* **📢 Social Broadcasting:** Users can "broadcast" topics or articles to **LinkedIn**, **WhatsApp**, or **Email** (simulated API integration).
* **🚀 Zero-Config Deployment:** Fully containerized. The entire system (DB + Backend + Frontend + Intelligence Engine) launches with one command.

---

## 🏗️ System Architecture

**Data Flow:**
`Sources` ➡️ `Fetcher` ➡️ `Clustering Engine` ➡️ `PostgreSQL` ➡️ `FastAPI` ➡️ `Next.js Dashboard`

```mermaid
graph TD
    %% External Nodes
    Sources[🌍 External Sources<br/>OpenAI, Google, Wired...]
    User([👤 User / Browser])

    %% Docker Container Context
    subgraph "Docker Container Network"
        
        subgraph "Backend Container (Python)"
            Fetcher[🤖 Ingestion Worker<br/>(fetcher.py)]
            Engine[🧠 Intelligence Engine<br/>(clustering.py)]
            API[⚙️ FastAPI Server<br/>(main.py)]
        end

        subgraph "Database Container"
            Postgres[(🗄️ PostgreSQL DB<br/>Topics, News, Favorites)]
        end

        subgraph "Frontend Container"
            NextJS[💻 Next.js Dashboard<br/>(App Router)]
        end
    end

    %% Data Flow Connections
    Sources -->|1. Pull RSS Feeds| Fetcher
    Fetcher -->|2. Save Unique Articles| Postgres
    
    Postgres -->|3. Fetch Recent News| Engine
    Engine -->|4. Cluster & Score Topics| Postgres
    
    User -->|5. Open Dashboard| NextJS
    NextJS -->|6. Request JSON Data| API
    API -->|7. Query DB| Postgres
    Postgres -->|8. Return Data| API
    API -->|9. Serve Response| NextJS

