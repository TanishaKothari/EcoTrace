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
- **Optional Account System**: Choose between anonymous usage or account-based history tracking
- **Complete History Tracking**: Automatic saving of all analyses and comparisons for authenticated users
- **Journey Analytics**: Track your environmental awareness progress over time with interactive charts
- **Smart Timeline**: Chronological view of analyses and comparisons with visual indicators
- **Intent-Based Statistics**: Separate tracking for regular analyses vs. comparison analyses
- **Visual Indicators**: Clear "For Comparison" tags and purple styling for comparison entries
- **Category Performance**: Detailed breakdown of performance across different product categories
- **Milestone Achievements**: Gamified progress tracking with eco-friendly goals
- **User Data Isolation**: Each user only sees their own data with cryptographic token validation
- **Persistent Data**: SQLite database ensures data survives server restarts and scaling

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
- **react-webcam** for camera integration and barcode scanning
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

## Usage Guide

### Anonymous Mode (No Account Required)
1. **Visit the application** at `http://localhost:3000`
2. **Start analyzing** products immediately - no registration required
3. **Use all features** including product search, barcode scanning, and comparisons
4. **Note**: Analysis history will not be saved

### Account Mode (Full Experience)
1. **Click "Sign In"** in the top navigation
2. **Create an account** with email and password
3. **Enjoy persistent history** and journey analytics
4. **Access from any device** with your account credentials

### Benefits of Creating an Account
- **📊 Complete History**: All your analyses and comparisons are saved
- **📈 Journey Analytics**: Track your environmental awareness progress over time
- **🎯 Goal Tracking**: Set and monitor eco-friendly milestones
- **🔄 Cross-Device Sync**: Access your data from any device
- **📱 Persistent Data**: Never lose your analysis history

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Main Endpoints

#### Analysis Endpoints
- `POST /analyze/product` - Analyze product by name or URL
- `POST /analyze/barcode` - Analyze product by barcode
- `POST /analyze/image` - Extract and analyze barcode from uploaded image

#### History & Journey Endpoints
- `GET /history` - Get analysis history with optional filters and pagination (user-specific)
- `GET /journey` - Get comprehensive eco journey data with analytics and insights (user-specific)
- `POST /history/comparison` - Save product comparison to history (auto-called by frontend)

#### Authentication Endpoints
- `POST /auth/token` - Generate secure anonymous user token
- `POST /auth/register` - Register new user account
- `POST /auth/login` - Login user and return auth token
- `GET /auth/validate` - Validate user token and return user info

## 🎯 Usage

### Main Features
1. **Product Search**: Enter a product name (e.g., "Tesla Model Y", "iPhone 15") or paste product URLs
2. **Barcode Scanning**: Use camera, upload barcode images, or enter manually for instant analysis
3. **Product Comparison**: Add multiple products to compare their environmental impact side-by-side
4. **Detailed Analysis**: View comprehensive eco-scores, impact factors, and actionable recommendations

### History & Journey Tracking (Account Required)
5. **Account-Based History**: Create an account to automatically save all analyses and comparisons
6. **Eco Journey Dashboard**: Navigate to History page to view your complete environmental awareness journey
7. **Progress Analytics**: Track improvement over time with interactive charts and timeline visualization
8. **Category Performance**: Monitor your choices across different product categories

### Navigation
- **Analyze Tab**: Main product analysis and comparison interface (available to all users)
- **History Tab**: Complete journey dashboard with Recent Analyses, Category Breakdown, Timeline, and Analytics (requires account)
- **Authentication**: Sign in/register button in navigation, user info display when logged in
- **Mobile Responsive**: Optimized experience across all devices with adaptive navigation

### User Account System
- **Optional Registration**: Create account with email and password for history tracking
- **Anonymous Mode**: Use immediately without registration (no history saved)
- **Secure Authentication**: HMAC-signed tokens with password hashing
- **Privacy Choice**: Users decide whether to create accounts or remain anonymous
- **Cross-Device Sync**: Account-based history accessible from any device

## 🔄 Data Persistence & Security

### Database Architecture
- **SQLite database** automatically created at `backend/data/ecotrace.db` on first startup
- **Proper schema** with Users, HistoryEntries, and ComparisonEntries tables
- **Foreign key relationships** ensuring data integrity

### Authentication Security
- **Dual token system**: Separate tokens for anonymous users and authenticated accounts
- **HMAC-SHA256 signatures** prevent token forgery for both user types
- **Password hashing** with salt for secure credential storage
- **Token validation** on every request to prevent unauthorized access
- **Hashed token storage** in database for security
- **User data isolation** - each user only sees their own data

### 🔄 User Mode Comparison

| Feature | Anonymous Mode | Account Mode |
|---------|---------------|--------------|
| **Product Analysis** | ✅ Full access | ✅ Full access |
| **Product Comparison** | ✅ Full access | ✅ Full access |
| **History Tracking** | ❌ No history saved | ✅ Complete history |
| **Journey Analytics** | ❌ Not available | ✅ Full analytics |
| **Cross-Device Access** | ❌ Browser-only | ✅ Any device |
| **Data Persistence** | ❌ No persistence | ✅ Permanent |
| **Registration Required** | ❌ None | ✅ Email & password |

### Intent-Based Analytics
- **Regular analyses** count toward user statistics and appear in timeline
- **Comparison analyses** are saved for reference but don't inflate analysis counts
- **Smart categorization** distinguishes between research intent vs. comparison intent
- **Visual indicators** clearly show "For Comparison" tags in history

### Auto-Save Features (Account Users Only)
- **Analyses**: Automatically saved when performed (search, barcode, URL)
- **Comparisons**: Automatically saved when 2+ products are compared
- **No manual saving required** - seamless user experience
- **Consistent behavior** across all analysis types
