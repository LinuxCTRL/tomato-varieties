# 🍅 Tomato Varieties Database

A comprehensive, modern web application that scrapes, stores, and serves detailed tomato variety information from the Rutgers NJAES database. Built with Python (Flask) backend and Express.js frontend, featuring a beautiful UI with dark mode, loading animations, and one-click data scraping.

## ✨ Features

### 🎨 **Modern UI & UX**

- **Beautiful Design**: Custom OperatorMono font with glassmorphism effects
- **Dark Mode**: Smooth toggle between light and dark themes with persistent preferences
- **Loading Animations**: Growing plant animations (🌱→🌿→🍃→🍅) throughout the app
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Smooth Transitions**: CSS animations with GPU acceleration for buttery performance

### 🚀 **Advanced Scraping**

- **Multithreaded Scraper**: 4-8x faster scraping with configurable thread count
- **Progress Bars**: Beautiful tqdm progress indicators with real-time stats
- **Rich Data Extraction**: Comprehensive variety information including:
  - Tomato Type (Heirloom, Garden, Cherry, etc.)
  - Breed (Open Pollinated, Hybrid)
  - Origin (Country/Region)
  - Season (Early, Mid, Late)
  - Plant Details (Height, Type, Leaf Type)
  - Fruit Characteristics (Size, Shape, Colors)
  - Growing Information (Days to maturity, Disease resistance)
- **One-Click Scraping**: Start scraper directly from the web interface

### 🔧 **Powerful Backend**

- **REST API**: Python Flask backend with comprehensive endpoints
- **Smart Caching**: Efficient data loading and caching mechanisms
- **Background Processing**: Non-blocking scraper execution
- **Status Monitoring**: Real-time scraper status checking
- **Error Handling**: Graceful error recovery and user feedback

### 🌐 **Rich Frontend**

- **Express.js Server**: Fast, reliable web server
- **Search Functionality**: Advanced search across all variety data
- **Dynamic Routing**: Individual pages for each tomato variety
- **Statistics Dashboard**: Comprehensive database analytics
- **Real-time Updates**: Refresh data without restarting

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Node.js 14+
- npm, yarn, or bun (recommended)
- pip (Python package installer)

### 🎯 **One-Command Setup (Recommended)**

```bash
# Clone and start everything automatically
git clone https://github.com/LinuxCTRL/tomato-varieties
cd tomato-varieties
chmod +x start.sh
./start.sh
```

**That's it!** The script will:

- ✅ Install all Python and Node.js dependencies
- ✅ Run the scraper to fetch initial data (if needed)
- ✅ Start both backend and frontend servers
- ✅ Display helpful information and URLs

### 🔧 **Manual Setup (Alternative)**

1. **Set up Python virtual environment:**

**Linux/macOS:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (Command Prompt):**

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Windows (PowerShell):**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Install frontend dependencies:**

```bash
cd ../frontend
npm install  # or bun install (recommended)
```

3. **Start the backend API:**

**Linux/macOS:**

```bash
cd ../backend
source .venv/bin/activate
python api.py
```

**Windows:**

```cmd
cd ..\backend
.venv\Scripts\activate
python api.py
```

4. **Start the frontend server (in another terminal):**

```bash
cd frontend
npm start  # or bun start
```

5. **Access the application:**

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **API**: http://localhost:5000

### 🎉 **First Time Usage**

1. **Click "Scrape Fresh Data"** button to fetch tomato varieties
2. **Toggle dark mode** 🌙 with the switch in the top-right corner
3. **Search varieties** using the search bar or dedicated search page
4. **Explore variety details** by clicking on any tomato card
5. **Watch the beautiful growing plant animations** 🌱→🌿→🍃→🍅

## 📁 Project Structure

```
tomato-varieties-database/
├── 🚀 start.sh                    # Main startup script
├── 📁 backend/                    # Python backend
│   ├── 🐍 api.py                 # Flask REST API server
│   ├── 🍅 scraper.py             # Multithreaded web scraper
│   ├── 📄 tomato_varieties.json  # Scraped data (generated)
│   ├── 📋 requirements.txt       # Python dependencies
│   └── 🔧 start.sh              # Backend-only startup script
├── 📁 frontend/                   # Node.js frontend
│   ├── 🌐 server.js              # Express.js web server
│   ├── 📋 package.json           # Node.js dependencies
│   ├── 📁 views/                 # EJS templates
│   │   ├── layout.ejs           # Base layout with dark mode
│   │   ├── index.ejs            # Home page with scrape button
│   │   ├── variety-detail.ejs   # Individual variety page
│   │   ├── search.ejs           # Advanced search page
│   │   ├── stats.ejs            # Statistics dashboard
│   │   ├── loading-demo.ejs     # Animation showcase
│   │   └── error.ejs            # Error page
│   └── 📁 public/                # Static assets
│       ├── 📁 css/
│       │   └── style.css        # Modern UI with glassmorphism
│       ├── 📁 js/
│       │   └── app.js           # Frontend logic & animations
│       └── 📁 fonts/
│           └── OperatorMonoLig-Book.otf  # Premium font
└── 📚 README.md                   # This file
```

## 🔧 API Endpoints

### Backend API (Port 5000)

- `GET /` - API documentation
- `GET /varieties` - List all varieties
- `GET /varieties/<name>` - Get specific variety details
- `GET /search?q=<query>` - Search varieties
- `GET /stats` - Database statistics
- `GET /refresh` - Refresh data from JSON file

### Frontend Routes (Port 3000)

- `GET /` - Home page with all varieties
- `GET /search?q=<query>` - Search page
- `GET /tomato/<name>` - Individual variety details
- `GET /stats` - Statistics dashboard
- `GET /api/*` - Proxy to backend API

## 🎯 Usage Examples

### Scraping Data

```bash
# Scrape fresh data from Rutgers website
python scraper.py
```

### API Usage

```bash
# Get all varieties
curl http://localhost:5000/varieties

# Search for specific variety
curl http://localhost:5000/search?q=Cherokee

# Get variety details
curl http://localhost:5000/varieties/cherokee-purple
```

### Frontend Features

1. **Browse All Varieties**: Visit the home page to see all tomato varieties
2. **Search**: Use the search bar to find specific varieties
3. **Variety Details**: Click on any variety name to see detailed information
4. **Statistics**: View database statistics and data quality metrics

## 🔄 Data Updates

The system is designed to stay current with the source website:

1. **Manual Update**: Run `python scraper.py` to fetch fresh data
2. **API Refresh**: Use the `/refresh` endpoint to reload data without restarting
3. **Frontend Refresh**: Use the "Refresh Data" button in the web interface

## 🛠️ Development

### Adding New Features

1. **Backend**: Modify `api.py` to add new endpoints
2. **Frontend**: Add new routes in `server.js` and create corresponding EJS templates
3. **Scraper**: Update `scraper.py` to extract additional data fields

### Customization

- **Styling**: Modify `public/css/style.css`
- **Frontend Logic**: Update `public/js/app.js`
- **Templates**: Edit EJS files in `views/`

## 📊 Data Structure

Each tomato variety contains:

```json
{
  "name": "Variety Name",
  "slug": "variety-name",
  "url": "https://source-url",
  "description": "Variety description",
  "characteristics": {
    "key": "value"
  },
  "growing_info": {
    "days_to_maturity": "80",
    "plant_type": "determinate"
  },
  "images": [
    {
      "url": "image-url",
      "alt": "description"
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Data source: [Rutgers NJAES Tomato Varieties](https://njaes.rutgers.edu/tomato-varieties/)
- Built with Flask, Express.js, Bootstrap, and Font Awesome

## 🔧 Development Notes

### Virtual Environment

- The project uses Python virtual environment (`venv`) for dependency isolation
- Virtual environment is automatically created and activated by `start.sh`
- For manual development, always activate the venv: `source backend/venv/bin/activate`

### Adding New Dependencies

```bash
# Backend (Python)
cd backend
source venv/bin/activate
pip install -qqq new-package
pip freeze > requirements.txt

# Frontend (Node.js)
cd frontend
npm install new-package  # or bun add new-package
```

## 🪟 Windows Support

### Windows Users

- Use `start.bat` instead of `start.sh` for one-command setup
- Virtual environment activation: `venv\Scripts\activate`
- Path separators: Use backslashes `\` instead of forward slashes `/`

### Cross-Platform Commands

| Task                  | Linux/macOS                | Windows                 |
| --------------------- | -------------------------- | ----------------------- |
| Start everything      | `./start.sh`               | `start.bat`             |
| Activate venv         | `source venv/bin/activate` | `venv\Scripts\activate` |
| Navigate to backend   | `cd backend`               | `cd backend`            |
| Navigate up one level | `cd ..`                    | `cd ..`                 |

### PowerShell Users

If using PowerShell, you may need to enable script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
