# BudgetPro 💰
### Your Personal Finance Management Application

![Python](https://img.shields.io/badge/Python-3.x-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## Overview
**BudgetPro** is a full-stack personal finance management 
application designed to help individuals take control of 
their money — track income, manage expenses, set budgets, 
and gain clear visibility into their financial health.

Built with a Python backend and a dynamic frontend, 
BudgetPro combines simplicity with powerful financial 
tracking capabilities.

> *"You don't have to be rich to manage money well. 
> You just need the right tools."*

---

## Features

- 🔐 **Secure Authentication** — User login and 
  registration with encrypted credentials
- 📊 **Budget Tracking** — Set and monitor budgets 
  across multiple categories
- 💸 **Expense Management** — Log, view, and manage 
  daily expenses in real time
- 📈 **Financial Dashboard** — Visual overview of 
  income vs. expenditure
- 🗄️ **Persistent Storage** — All data securely stored 
  in a local SQLite database
- 🌐 **Web-Based Interface** — Accessible via any 
  modern browser

---

## Project Structure
```
📁 BudgetPro
├── 📁 frontend/          # UI templates and static assets
├── 📄 main.py            # Application entry point & routing
├── 📄 auth.py            # Authentication & session management
├── 📄 models.py          # Database models and schema
├── 📄 database.py        # Database connection and configuration
├── 📄 create_tables.py   # Database table initialization
├── 📄 security.py        # Password hashing & security utilities
├── 📄 Budget_Tracker.py  # Core budget tracking logic
├── 📄 deps.py            # Dependency injection
├── 📄 budget.db          # SQLite database
├── 📄 requirements.txt   # Project dependencies
└── 📄 start.sh           # Application startup script
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI |
| **Frontend** | HTML, CSS, JavaScript |
| **Database** | SQLite |
| **Authentication** | Session-based with password hashing |
| **Deployment** | Shell script (start.sh) |


## Getting Started

### Prerequisites
- Python 3.x installed
- pip package manager

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/AbdRaqeeb6/BudgetPro.git
cd BudgetPro
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Initialize the database**
```bash
python create_tables.py
```

**4. Run the application**
```bash
bash start.sh
```
or
```bash
python main.py
```

**5. Open your browser**
```
http://localhost:8000

## Security
- Passwords are hashed and never stored in plain text
- Session-based authentication protects all routes
- Security utilities managed via `security.py`

## Roadmap 🚀
- [ ] Mobile-responsive design
- [ ] Income tracking module
- [ ] Monthly financial reports & exports
- [ ] Budget alerts and notifications
- [ ] Multi-currency support
- [ ] Cloud deployment (Render / Railway)


## Author
**Abdul Rakib Mohammed**
Business Analyst | Full-Stack Developer |
Data Analyst

*Building solutions that solve real problems.*



## License
This project is open source and available under 
the MIT License.
