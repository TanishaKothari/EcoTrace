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
- **Python FastAPI**: High-performance API framework
- **Pydantic** for data validation
- **httpx** for HTTP requests
- **BeautifulSoup4** for web scraping
- **OpenCV** & **pyzbar** for barcode scanning
- **Ollama3**: Local AI model for environmental analysis

### Frontend
- **React 19** with **Next.js 15**
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Chart.js** for data visualization
- **Lucide React** for icons


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

2. **Start the frontend development server**
```bash
cd frontend
npm run dev
```
The application will be available at `http://localhost:3000`

## 📖 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Main Endpoints
- `POST /analyze/product` - Analyze product by name or URL
- `POST /analyze/barcode` - Analyze product by barcode
- `POST /analyze/barcode/image` - Extract and analyze barcode from image

## 🎯 Usage

1. **Product Search**: Enter a product name (e.g., "Tesla Model Y", "iPhone 15")
2. **Barcode Scanning**: Use camera, upload barcode images, or enter manually
3. **Comparison**: Add multiple products to compare their environmental impact
4. **Analysis**: View detailed eco-scores and recommendations
