'use client';

import { useState } from 'react';
import { Search, Camera, Leaf, BarChart3, Globe, Recycle } from 'lucide-react';
import ProductSearch from '@/components/ProductSearch';
import BarcodeScanner from '@/components/BarcodeScanner';
import EcoScoreDisplay from '@/components/EcoScoreDisplay';
import ProductComparison from '@/components/ProductComparison';

interface ImpactFactor {
  name: string;
  score: number;
  description: string;
  weight: number;
}

interface ProductInfo {
  name: string;
  brand?: string;
  category?: string;
  description?: string;
}

interface ProductAnalysis {
  product_info: ProductInfo;
  impact_factors: ImpactFactor[];
  eco_score: number;
  confidence_level: number;
  analysis_summary: string;
  recommendations: string[];
  data_sources: string[];
}

interface ComparisonProduct {
  id: string;
  query: string;
  analysis: ProductAnalysis;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<'search' | 'scan' | 'compare'>('search');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [comparisonProducts, setComparisonProducts] = useState<ComparisonProduct[]>([]);
  const removeFromComparison = (productId: string) => {
    setComparisonProducts(prev => prev.filter(p => p.id !== productId));
  };

  const addProductToComparison = async (query: string, queryType: 'name' | 'url') => {
    if (comparisonProducts.length >= 3) {
      throw new Error('Maximum of 3 products can be compared');
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/analyze/product', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          query_type: queryType,
        }),
      });

      if (!response.ok) {
        let errorMessage = `Failed to analyze product: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch (parseError) {
          // If we can't parse JSON, try to get text response
          try {
            const errorText = await response.text();
            if (errorText) {
              errorMessage = errorText;
            }
          } catch (textError) {
            // Keep the default error message
          }
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();

      if (result.success && result.analysis) {
        // Validate that we got real product data, not fake analysis
        if (!result.analysis.product_info?.name ||
            result.analysis.product_info.name.toLowerCase().includes('unknown') ||
            result.analysis.product_info.name.toLowerCase().includes('generic') ||
            result.analysis.confidence_level < 0.3) {
          throw new Error(`Could not find reliable product information for "${query}". Please try a more specific product name or a valid product URL.`);
        }

        const newProduct: ComparisonProduct = {
          id: Date.now().toString(),
          query,
          analysis: result.analysis
        };

        setComparisonProducts(prev => [...prev, newProduct]);
      } else {
        throw new Error(result.error || `Could not analyze "${query}". Please check the product name or URL and try again.`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-green-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-green-600 p-2 rounded-lg">
                <Leaf className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">EcoTrace</h1>
                <p className="text-sm text-gray-700">Environmental Impact Analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-700">
              <div className="flex items-center space-x-1">
                <Globe className="h-4 w-4" />
                <span>AI-Powered</span>
              </div>
              <div className="flex items-center space-x-1">
                <BarChart3 className="h-4 w-4" />
                <span>Real-time Analysis</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4 bg-gradient-to-r from-green-700 to-blue-700 bg-clip-text text-transparent">
            Discover the Hidden Environmental Impact
          </h2>
          <p className="text-xl text-gray-700 mb-8 max-w-3xl mx-auto">
            Get instant AI-powered analysis of any product's carbon footprint, resource usage,
            and sustainability score. Make informed choices for a better planet.
          </p>

          {/* Tab Navigation */}
          <div className="flex justify-center mb-8">
            <div className="bg-white rounded-lg p-1 shadow-lg border border-gray-200 flex flex-wrap justify-center">
              <button
                onClick={() => setActiveTab('search')}
                className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-md transition-all w-40 ${
                  activeTab === 'search'
                    ? 'bg-green-600 text-white shadow-md'
                    : 'text-gray-700 hover:text-gray-900'
                }`}
              >
                <Search className="h-5 w-5" />
                <span>Search Product</span>
              </button>
              <button
                onClick={() => setActiveTab('scan')}
                className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-md transition-all w-40 ${
                  activeTab === 'scan'
                    ? 'bg-green-600 text-white shadow-md'
                    : 'text-gray-700 hover:text-gray-900'
                }`}
              >
                <Camera className="h-5 w-5" />
                <span>Scan Barcode</span>
              </button>
              <button
                onClick={() => setActiveTab('compare')}
                className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-md transition-all w-40 relative ${
                  activeTab === 'compare'
                    ? 'bg-green-600 text-white shadow-md'
                    : 'text-gray-700 hover:text-gray-900'
                }`}
              >
                <BarChart3 className="h-5 w-5" />
                <span>Compare</span>
                {comparisonProducts.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {comparisonProducts.length}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Analysis Interface */}
        {activeTab === 'compare' ? (
          <div className="w-full">
            <ProductComparison
              products={comparisonProducts}
              onRemoveProduct={removeFromComparison}
              onClose={() => setActiveTab('search')}
              onAddProduct={addProductToComparison}
              isLoading={isLoading}
            />
          </div>
        ) : (
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Input Section */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              {activeTab === 'search' ? (
                <ProductSearch
                  onAnalysis={setAnalysisResult}
                  onLoading={setIsLoading}
                />
              ) : (
                <BarcodeScanner
                  onAnalysis={setAnalysisResult}
                  onLoading={setIsLoading}
                />
              )}
            </div>

            {/* Results Section */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <EcoScoreDisplay
                result={analysisResult}
                isLoading={isLoading}
              />
            </div>
          </div>
        )}

        {/* Features Section */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">EcoScore Rating</h3>
            <p className="text-gray-700">
              Get a clear 1-100 sustainability score based on comprehensive environmental impact analysis.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Globe className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Supply Chain Analysis</h3>
            <p className="text-gray-700">
              Understand the full lifecycle impact from raw materials to disposal and recycling.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Recycle className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Smart Recommendations</h3>
            <p className="text-gray-700">
              Receive actionable suggestions for more sustainable alternatives and practices.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-20">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Leaf className="h-6 w-6 text-green-400" />
              <span className="text-xl font-bold">EcoTrace</span>
            </div>
            <p className="text-gray-400">
              Making environmental impact visible, one product at a time.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}