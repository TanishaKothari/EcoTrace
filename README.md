# EcoTrace - AI-Powered Environmental Impact Analysis

EcoTrace is a comprehensive web application that reveals the hidden environmental impact of everyday products through AI-powered analysis. It provides users with clear EcoScores (1-100 scale) and detailed insights into a product's carbon footprint, resource usage, and other sustainability factors.

## Features

### 🔍 Product Analysis
- **Manual Search**: Enter product names or paste product URLs
- **Barcode Scanning**: Scan barcodes using camera, upload images, or enter manually
- **AI-Powered Analysis**: Uses Ollama3 for intelligent environmental impact assessment

### 📊 Comparison Tool
- **Multi-Product Comparison**: Compare EcoScores and impact factors across different products
- **Interactive Charts**: Visual comparison of impact factors

### 📈 Analysis History & Eco Journey
- **Complete History Tracking**: Automatic saving of all product analyses and comparisons with secure database storage
- **Journey Analytics**: Track your environmental awareness progress over time with interactive charts
- **Smart Timeline**: Chronological view of analyses and comparisons with visual indicators
- **Intent-Based Statistics**: Separate tracking for regular analyses vs. comparison analyses
- **Visual Indicators**: Clear "For Comparison" tags and purple styling for comparison entries
- **Category Performance**: Detailed breakdown of performance across different product categories
- **Milestone Achievements**: Gamified progress tracking with eco-friendly goals
- **Anonymous User Sessions**: Secure, persistent sessions without requiring account creation
- **User Data Isolation**: Each user only sees their own data with cryptographic token validation
- **Persistent Data**: SQLite database ensures data survives server restarts and scaling
- **Browser-based Storage**: History persists in browser localStorage (lost if browser data is cleared)

### 📊 EcoScore System
- **1-100 Scale**: Clear sustainability rating system
- **Impact Factors**: Detailed breakdown of environmental factors
- **Confidence Levels**: Transparency in analysis reliability
- **Smart Recommendations**: Actionable suggestions for improvement

### 🌱 Environmental Factors Analyzed
- Carbon footprint and greenhouse gas emissions
- Resource usage (water, energy, raw materials)
- Manufacturing process sustainability
- Transportation and supply chain impact
- Packaging and waste generation
- End-of-life disposal and recyclability

## 🛠️ Tech Stack

### Backend
- **Python FastAPI**: High-performance API framework with CORS support
- **SQLAlchemy**: Modern ORM with SQLite database for data persistence
- **Pydantic** for data validation and type safety
- **httpx** for HTTP requests and web scraping
- **BeautifulSoup4** for web scraping and content extraction
- **OpenCV** & **pyzbar** for barcode scanning and image processing
- **Ollama3**: Local AI model for intelligent environmental analysis

### Frontend
- **React 19** with **Next.js 15** and App Router
- **TypeScript** for complete type safety across the application
- **Tailwind CSS** for responsive styling and mobile optimization
- **Chart.js** with **react-chartjs-2** for interactive analytics dashboards
- **Lucide React** for icons
- **Responsive design** with mobile-first approach and adaptive layouts


## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+
- **Ollama installed locally with llama3 model**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/TanishaKothari/EcoTrace.git
cd EcoTrace
```

2. **Set up the backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up the frontend**
```bash
cd ../frontend
npm install
```

### Running the Application

1. **Start the backend server**
```bash
cd backend
source venv/bin/activate
python main.py
```
The API will be available at `http://localhost:8000`
- Database and tables are created automatically on first startup
- No manual database setup required

2. **Start the frontend development server**
```bash
cd frontend
npm run dev
```
The application will be available at `http://localhost:3000`

## 📖 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Main Endpoints

#### Analysis Endpoints
- `POST /analyze/product` - Analyze product by name or URL
- `POST /analyze/barcode` - Analyze product by barcode
- `POST /analyze/barcode/image` - Extract and analyze barcode from image

#### History & Journey Endpoints
- `GET /history` - Get analysis history with optional filters and pagination (user-specific)
- `GET /journey` - Get comprehensive eco journey data with analytics and insights (user-specific)
- `POST /history/comparison` - Save product comparison to history (auto-called by frontend)

#### Authentication Endpoints
- `POST /auth/token` - Generate secure anonymous user token

## 🎯 Usage

### Main Features
1. **Product Search**: Enter a product name (e.g., "Tesla Model Y", "iPhone 15") or paste product URLs
2. **Barcode Scanning**: Use camera, upload barcode images, or enter manually for instant analysis
3. **Product Comparison**: Add multiple products to compare their environmental impact side-by-side
4. **Detailed Analysis**: View comprehensive eco-scores, impact factors, and actionable recommendations

### History & Journey Tracking
5. **Automatic History**: All analyses and comparisons are automatically saved with persistent storage
6. **Eco Journey Dashboard**: Navigate to History page to view your complete environmental awareness journey
7. **Progress Analytics**: Track improvement over time with interactive charts and timeline visualization
8. **Category Performance**: Monitor your choices across different product categories

### Navigation
- **Analyze Tab**: Main product analysis and comparison interface
- **History Tab**: Complete journey dashboard with Recent Analyses, Category Breakdown, Timeline, and Analytics
- **Mobile Responsive**: Optimized experience across all devices with adaptive navigation

### 📱 Session Management
- **Automatic token generation**: First visit creates a secure anonymous session
- **Persistent across browser sessions**: History survives browser restarts
- **⚠️ Important**: Clearing browser data or switching devices will start a new session and lose access to previous history
- **Privacy-focused**: No personal information required or stored

## 🔄 Data Persistence & Security

### Database Architecture
- **SQLite database** automatically created at `backend/data/ecotrace.db` on first startup
- **Proper schema** with Users, HistoryEntries, and ComparisonEntries tables
- **Foreign key relationships** ensuring data integrity

### Anonymous User Security
- **Cryptographically secure tokens** with HMAC-SHA256 signatures
- **Token validation** on every request to prevent forgery
- **Hashed token storage** in database for security
- **User data isolation** - each user only sees their own data
- **No expiration** for persistent anonymous history

### ⚠️ Anonymous Session Limitations
- **Browser dependency**: History is tied to browser's localStorage token
- **Data loss scenarios**: Clearing browser data, switching devices, or incognito mode will result in loss of access to previous history
- **No cross-device sync**: Each device/browser maintains separate anonymous sessions
- **Privacy by design**: This limitation is intentional to maintain user anonymity without requiring accounts

### Intent-Based Analytics
- **Regular analyses** count toward user statistics and appear in timeline
- **Comparison analyses** are saved for reference but don't inflate analysis counts
- **Smart categorization** distinguishes between research intent vs. comparison intent
- **Visual indicators** clearly show "For Comparison" tags in history

### Auto-Save Features
- **Analyses**: Automatically saved when performed (search, barcode, URL)
- **Comparisons**: Automatically saved when 2+ products are compared
- **No manual saving required** - seamless user experience
- **Consistent behavior** across all analysis types
