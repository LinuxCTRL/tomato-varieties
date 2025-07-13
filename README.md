# 🍅 Tomato Varieties Database

A comprehensive web application that scrapes, stores, and serves tomato variety information from the Rutgers NJAES database. Built with Python (Flask) backend and Express.js frontend.

## 🌟 Features

- **Web Scraping**: Automatically scrapes tomato variety data from [Rutgers NJAES](https://njaes.rutgers.edu/tomato-varieties/)
- **REST API**: Python Flask backend serving JSON data
- **Web Interface**: Express.js frontend with responsive design
- **Search Functionality**: Search varieties by name, characteristics, or growing information
- **Dynamic Routing**: Individual pages for each tomato variety (`/tomato/:name`)
- **Statistics Dashboard**: Overview of database contents and data quality
- **Real-time Updates**: Refresh data without restarting the application

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn

### Easy Setup (Recommended)

```bash
# Make the startup script executable and run it
chmod +x start.sh
./start.sh
```

This will:
1. Install all dependencies
2. Run the scraper to get initial data
3. Start both servers
4. Open the application at http://localhost:3000

### Manual Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Node.js dependencies:**
```bash
npm install
```

3. **Run the scraper to get data:**
```bash
python scraper.py
```

4. **Start the API server:**
```bash
python api.py
```

5. **Start the frontend server (in another terminal):**
```bash
npm start
```

6. **Access the application:**
- Frontend: http://localhost:3000
- API: http://localhost:5000

## 📁 Project Structure

```
tomato-varieties-database/
├── scraper.py              # Web scraper for tomato data
├── api.py                  # Flask REST API server
├── server.js               # Express.js frontend server
├── start.sh                # Startup script
├── package.json            # Node.js dependencies
├── requirements.txt        # Python dependencies
├── tomato_varieties.json   # Scraped data (generated)
├── views/                  # EJS templates
│   ├── layout.ejs         # Base layout
│   ├── index.ejs          # Home page
│   ├── variety-detail.ejs # Individual variety page
│   ├── search.ejs         # Search page
│   ├── stats.ejs          # Statistics page
│   └── error.ejs          # Error page
└── public/                 # Static assets
    ├── css/style.css      # Custom styles
    └── js/app.js          # Frontend JavaScript
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