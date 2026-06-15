# 🌍 Travel Planner App

> An intelligent, AI-powered travel planning platform that helps you discover, organize, and plan your perfect trips.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0.6%2B-darkgreen?style=flat-square&logo=django)](https://djangoproject.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-blue?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## ✨ Features

- 🤖 **AI-Powered Agents** - Advanced CrewAI agents for intelligent travel planning and recommendations
- 🗺️ **Smart Search** - Location-based search with geospatial analysis using Haversine distance calculations
- 💬 **Real-Time Chat** - WebSocket-powered chat interface using Django Channels for instant communication
- 👥 **Group Planning** - Collaborative travel planning for groups with shared itineraries
- 🔐 **User Accounts** - Secure authentication and personalized user profiles
- 📱 **Responsive UI** - Modern, responsive HTML5 frontend
- 🚀 **Microservices Architecture** - Scalable FastAPI-based backend services
- 🌐 **Multi-Source Data** - Integration with OpenStreetMap and DuckDuckGo for comprehensive travel data

---

## 📁 Project Structure

```
travel-planner-app/
├── travel/                      # Main Django application
│   ├── accounts/               # User authentication & profiles
│   ├── chat/                   # Real-time chat functionality
│   ├── groups/                 # Group planning features
│   ├── templates/              # HTML templates
│   ├── static/                 # Static assets (CSS, JS)
│   ├── travel/                 # Core Django config
│   └── manage.py              # Django management script
│
├── microservices/              # FastAPI backend services
│   ├── main.py                # FastAPI application
│   ├── agents.py              # CrewAI agent definitions
│   ├── tasks.py               # AI task orchestration
│   ├── search.py              # Location search utilities
│   ├── models.py              # Pydantic models
│   └── requirements.txt        # Service dependencies
│
├── pyproject.toml             # Project configuration
├── requirements.txt           # Main dependencies
└── uv.lock                    # Dependency lock file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **pip** or **uv** package manager
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SwapnanilDatta/travel-planner-app.git
   cd travel-planner-app
   ```

2. **Install dependencies**
   
   Using `uv` (recommended):
   ```bash
   uv pip install -r requirements.txt
   ```
   
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   pip install -r microservices/requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run Django migrations**
   ```bash
   cd travel
   python manage.py migrate
   ```

5. **Start the development servers**

   **Django application** (Terminal 1):
   ```bash
   cd travel
   python manage.py runserver
   ```

   **FastAPI microservices** (Terminal 2):
   ```bash
   cd microservices
   python -m uvicorn main:app --reload
   ```

---

## 🔧 Tech Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Responsive styling
- **JavaScript** - Interactive features
- **WebSockets** - Real-time communication

### Backend
- **Django 6.0.6+** - Web framework & ORM
- **FastAPI** - High-performance microservices API
- **Channels** - WebSocket support for real-time chat
- **Daphne** - ASGI server

### AI & Intelligence
- **CrewAI** - Multi-agent orchestration
- **LangChain** - LLM integration
- **LLM Support** - Groq integration via LiteLLM
- **DuckDuckGo Search** - Web search capabilities

### Data & Utilities
- **Pydantic** - Data validation
- **Geopy** - Geocoding services
- **Haversine** - Distance calculations
- **NumPy & Pandas** - Data processing
- **OverPy** - OpenStreetMap data access

---

## 📚 API Documentation

Once the FastAPI server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Environment Variables

Create a `.env` file in the root directory:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///db.sqlite3

# AI/LLM Configuration
GROQ_API_KEY=your-groq-api-key
LLM_MODEL=mixtral-8x7b-32768

# CORS & Security
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

---

## 🐛 Troubleshooting

### WebSocket Connection Issues
- Ensure Daphne is running instead of the default Django development server
- Check that Channels configuration is correct in Django settings

### AI Agent Timeouts
- Verify API keys are correctly set in environment variables
- Check network connectivity to LLM provider

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use the same Python version (3.12+)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Swapnanil Datta**
- GitHub: [@SwapnanilDatta](https://github.com/SwapnanilDatta)

---

## 🙌 Acknowledgments

- [Django](https://www.djangoproject.com/) - Web framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern API framework
- [CrewAI](https://github.com/joaomdmoura/crewai) - AI agent orchestration
- [LangChain](https://langchain.com/) - LLM framework

---

<div align="center">

**[⬆ back to top](#-travel-planner-app)**

Made with ❤️ for travel enthusiasts

</div>
