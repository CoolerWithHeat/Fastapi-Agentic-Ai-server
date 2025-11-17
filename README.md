# FastAPI Agentic AI Server
A production-style backend for agentic AI workflows using FastAPI, LangGraph, LLM tool-calling, JWT authentication, async SQLAlchemy, and concurrency-optimized processing.

---

## 🚀 Overview

This project implements a fully agentic AI backend designed for customer-support workflows.  
It uses **FastAPI**, **LangGraph**, and **async SQLAlchemy** to orchestrate multi-step LLM reasoning, tool-calling, message persistence, and user-specific operations — all while maintaining high throughput (400–500 req/sec in testing).

The server exposes a `/support` endpoint that interacts with an LLM agent capable of:

- 🔧 Tool calling  
- 🧠 Multi-step reasoning via LangGraph  
- 📦 Fetching user purchases  
- 🚚 Checking order status  
- 🗂 Saving structured message history  
- 💬 Generating agent-friendly JSON responses  

---

## 🛠 Tech Stack

- **FastAPI** (Async REST API)
- **LangGraph & LangChain** (Agentic workflow orchestration)
- **SQLAlchemy (Async ORM)**
- **PostgreSQL**
- **JWT Authentication**
- **Uvicorn** (server)
- **Alembic** (migrations)

---

# 📦 Installation & Setup

You MUST use Python v3.12.x

## 1. Clone the repository:
``` bash
    git clone https://github.com/CoolerWithHeat/Fastapi-Agentic-Ai-server.git
    cd Fastapi-Agentic-Ai-server
```
## 2. Create a virtual environment:
``` bash
    python3.12 -m venv env
    source env/bin/activate        # Linux/macOS

    env\Scripts\activate           # Windows

```

## 3. Install dependencies:
Once virtual environment activated, from the root folder run:
``` bash
    pip install -r requirements.txt
```

## 4. Configure your LLM API key:
Create a `.env` file in the `project/graph/` folder and add your API key as follows:
``` bash
    OPENAI_API_KEY = "_your_openai_key_"
    ANTHROPIC_API_KEY = "_your_anthropic_key_"
    GOOGLE_API_KEY = "_your_google_key_"
```
> [!WARNING]
> /support endpoint will not respond if you DO NOT provide API key as described and you will recieve a message on the terminal.

## 5. Configure Database:
Install PostgreSQL, then create a database named projectdb and a user myuser with password advanced04. Or replace with your own (make sure with asyncpg for async support)
> [!WARNING]
> Make sure both the /project/database.py and alembic.ini point to the same database, otherwise migrations and runtime connections will fail.

## 6. Migrate Database
Migrate db tables:
``` bash
    # Run from the project root folder !
    alembic revision --autogenerate -m "First migration"

    alembic upgrade head
```

## 7. Finally Run server:
``` bash
    uvicorn project.main:app --workers 2
```
> [!TIP]
> Set 1 worker per vCPU (otherwise it can even reduce performance). Increase workers to 4 or more if your VM has more vCPUs

## 8. Test all endpoints:
Open another window/terminal (within virtual env) and run:
``` bash
    cd project
    python3 test.py
```