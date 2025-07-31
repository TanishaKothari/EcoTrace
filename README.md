# EcoTrace - AI-Powered Environmental Impact Analysis

EcoTrace is a comprehensive web application that reveals the hidden environmental impact of everyday products through AI-powered analysis. It provides users with clear EcoScores (1-100 scale) and detailed insights into a product's carbon footprint, resource usage, and sustainability.

## Features

### 🔍 Product Analysis
- **Manual Search**: Enter product names or paste product URLs
- **Barcode Scanning**: Scan barcodes using camera or upload images
- **AI-Powered Analysis**: Uses Ollama3 for intelligent environmental impact assessment

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

## Technology Stack

### Backend
- **Python FastAPI**: High-performance API framework
- **Ollama3**: Local AI model for environmental analysis
- **OpenFoodFacts API**: Product database integration
- **Computer Vision**: Barcode scanning with OpenCV and pyzbar

### Frontend
- **Next.js 15**: Modern React framework with TypeScript
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Beautiful icons
- **React Webcam**: Camera integration for barcode scanning

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- Ollama installed locally with llama3 model

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EcoTrace
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Install System Dependencies**
   ```bash
   # For barcode scanning (Ubuntu/Debian)
   sudo apt install libzbar0
   ```

### Running the Application

1. **Start Ollama** (if not already running)
   ```bash
   ollama serve
   ollama pull llama3
   ```

2. **Start Backend**
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```
   Backend will be available at `http://localhost:8000`

3. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

## API Endpoints

### Product Analysis
- `POST /analyze/product` - Analyze by product name or URL
- `POST /analyze/barcode` - Analyze by barcode number
- `POST /analyze/image` - Analyze barcode from uploaded image

### Health Check
- `GET /health` - Check API and Ollama status

## Example Usage

### Product Search
```bash
curl -X POST http://localhost:8000/analyze/product \
  -H "Content-Type: application/json" \
  -d '{"query": "organic cotton t-shirt", "query_type": "name"}'
```

### Barcode Analysis
```bash
curl -X POST http://localhost:8000/analyze/barcode \
  -H "Content-Type: application/json" \
  -d '{"barcode": "1234567890123"}'
```

## Sample Results

### Organic Cotton T-Shirt
- **EcoScore**: 84/100 (Very Good)
- **Key Factors**: Sustainable materials, lower water usage, biodegradable

### Plastic Water Bottle
- **EcoScore**: 45/100 (Poor)
- **Key Factors**: Single-use plastic, high carbon footprint, waste generation

### Tesla Model S
- **EcoScore**: 92/100 (Excellent)
- **Key Factors**: Electric powertrain, renewable energy potential, longevity

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   Ollama3       │
│   Frontend      │◄──►│   Backend       │◄──►│   AI Engine     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │                       ▼                       
         │              ┌─────────────────┐              
         │              │ OpenFoodFacts   │              
         │              │ Product DB      │              
         │              └─────────────────┘              
         │                                               
         ▼                                               
┌─────────────────┐                                     
│ Camera/Barcode  │                                     
│ Scanning        │                                     
└─────────────────┘                                     
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Ollama team for the excellent local AI framework
- OpenFoodFacts for the comprehensive product database
- The open-source community for the amazing tools and libraries
