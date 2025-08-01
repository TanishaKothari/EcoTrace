'use client';

import { useState } from 'react';
import { X, TrendingUp, TrendingDown, Minus, Zap, Droplets, Factory, Truck, Package, Recycle, Leaf, Plus, Search, Camera, BarChart3, Clock } from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

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

interface ProductComparisonProps {
  products: ComparisonProduct[];
  onRemoveProduct: (productId: string) => void;
  onClose: () => void;
  onAddProduct: (query: string, queryType: 'name' | 'url') => Promise<void>;
  isLoading: boolean;
}

export default function ProductComparison({ products, onRemoveProduct, onClose, onAddProduct, isLoading }: ProductComparisonProps) {
  const [newProductQuery, setNewProductQuery] = useState('');
  const [queryType, setQueryType] = useState<'name' | 'url'>('name');
  const [errorMessage, setErrorMessage] = useState('');


  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100 border-green-300';
    if (score >= 60) return 'bg-yellow-100 border-yellow-300';
    if (score >= 40) return 'bg-orange-100 border-orange-300';
    return 'bg-red-100 border-red-300';
  };

  const getFactorIcon = (factorName: string) => {
    const name = factorName.toLowerCase();
    if (name.includes('carbon') || name.includes('footprint') || name.includes('emission')) {
      return <Zap className="w-4 h-4 text-gray-600" />;
    }
    if (name.includes('resource') || name.includes('water') || name.includes('energy')) {
      return <Droplets className="w-4 h-4 text-blue-600" />;
    }
    if (name.includes('manufacturing') || name.includes('process')) {
      return <Factory className="w-4 h-4 text-gray-700" />;
    }
    if (name.includes('transport') || name.includes('supply') || name.includes('chain')) {
      return <Truck className="w-4 h-4 text-orange-600" />;
    }
    if (name.includes('packaging') || name.includes('waste')) {
      return <Package className="w-4 h-4 text-amber-600" />;
    }
    if (name.includes('end') || name.includes('life') || name.includes('disposal') || name.includes('recycle')) {
      return <Recycle className="w-4 h-4 text-green-600" />;
    }
    return <Leaf className="w-4 h-4 text-green-600" />;
  };



  const getBestScore = (factorName: string) => {
    return Math.max(...products.map(p => 
      p.analysis.impact_factors.find(f => f.name === factorName)?.score || 0
    ));
  };

  const getWorstScore = (factorName: string) => {
    return Math.min(...products.map(p => 
      p.analysis.impact_factors.find(f => f.name === factorName)?.score || 100
    ));
  };

  const detectQueryType = (value: string) => {
    const urlPattern = /^https?:\/\/.+/i;
    return urlPattern.test(value) ? 'url' : 'name';
  };

  const handleQueryChange = (value: string) => {
    setNewProductQuery(value);
    setQueryType(detectQueryType(value));
  };

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProductQuery.trim()) return;

    if (products.length >= 3) {
      setErrorMessage('You can compare up to 3 products at a time');
      return;
    }

    setErrorMessage(''); // Clear previous errors
    try {
      await onAddProduct(newProductQuery.trim(), queryType);
      setNewProductQuery('');
    } catch (error) {
      console.error('Failed to add product:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to add product. Please try again.');
    }
  };

  // Get all unique impact factors across products
  const allFactors = Array.from(new Set(
    products.flatMap(p => p.analysis.impact_factors.map(f => f.name))
  ));

  // Don't show empty state anymore - always show the interface

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Product Comparison</h2>
        <div className="flex items-center space-x-2">
          {products.length >= 2 && (
            <div className="flex items-center space-x-2 text-sm text-green-600">
              <Clock className="w-4 h-4" />
              <span>Auto-saved to history</span>
            </div>
          )}
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Add Product Form */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Add Product to Compare</h3>
        <form onSubmit={handleAddProduct} className="flex gap-3">
          <div className="flex-1">
            <input
              type="text"
              value={newProductQuery}
              onChange={(e) => handleQueryChange(e.target.value)}
              placeholder="Enter product name or paste product URL..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-600 text-gray-900"
              disabled={isLoading || products.length >= 3}
            />
          </div>
          <button
            type="submit"
            disabled={!newProductQuery.trim() || isLoading || products.length >= 3}
            className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
              !newProductQuery.trim() || isLoading || products.length >= 3
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Adding...</span>
              </>
            ) : (
              <>
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </>
            )}
          </button>
        </form>
        {products.length >= 3 && (
          <p className="text-sm text-amber-600 mt-2">
            Maximum of 3 products can be compared. Remove a product to add another.
          </p>
        )}
        {errorMessage && (
          <p className="text-sm text-red-600 mt-2">
            {errorMessage}
          </p>
        )}
        <div className="flex items-center space-x-4 mt-3 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            {queryType === 'url' ? <Camera className="w-4 h-4" /> : <Search className="w-4 h-4" />}
            <span>{queryType === 'url' ? 'Product URL detected' : 'Product name search'}</span>
          </div>
        </div>
      </div>

      {/* Comparison Grid */}
      {products.length > 0 ? (
        <div className={`grid gap-6 ${products.length === 2 ? 'grid-cols-2' : 'grid-cols-3'}`}>
        {products.map((product) => (
          <div key={product.id} className="border border-gray-200 rounded-lg p-4">
            {/* Product Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="font-bold text-lg text-gray-900 mb-1">
                  {product.analysis.product_info.name}
                </h3>
                {product.analysis.product_info.brand && (
                  <p className="text-sm text-gray-600 mb-1">
                    {product.analysis.product_info.brand}
                  </p>
                )}
                <p className="text-xs text-gray-500">
                  Query: "{product.query}"
                </p>
              </div>
              <button
                onClick={() => onRemoveProduct(product.id)}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors ml-2"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>

            {/* EcoScore */}
            <div className={`rounded-lg p-4 mb-4 border-2 ${getScoreBgColor(product.analysis.eco_score)}`}>
              <div className="text-center">
                <div className={`text-3xl font-bold ${getScoreColor(product.analysis.eco_score)}`}>
                  {product.analysis.eco_score}
                </div>
                <div className="text-sm text-gray-600">EcoScore</div>
              </div>
            </div>

            {/* Impact Factors */}
            <div className="space-y-3">
              <h4 className="font-semibold text-gray-800 text-sm">Impact Factors</h4>
              {allFactors.map((factorName) => {
                const factor = product.analysis.impact_factors.find(f => f.name === factorName);
                const bestScore = getBestScore(factorName);
                const worstScore = getWorstScore(factorName);
                
                if (!factor) {
                  return (
                    <div key={factorName} className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div className="flex items-center space-x-2">
                        {getFactorIcon(factorName)}
                        <span className="text-sm text-gray-400">{factorName}</span>
                      </div>
                      <span className="text-sm text-gray-400">N/A</span>
                    </div>
                  );
                }

                const isBest = factor.score === bestScore && products.length > 1;
                const isWorst = factor.score === worstScore && products.length > 1 && bestScore !== worstScore;

                return (
                  <div key={factorName} className="flex items-center justify-between py-2 border-b border-gray-100">
                    <div className="flex items-center space-x-2">
                      {getFactorIcon(factorName)}
                      <span className="text-sm font-medium text-gray-700">{factorName}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span className={`text-sm font-medium ${getScoreColor(factor.score)}`}>
                        {factor.score}
                      </span>
                      {isBest && <TrendingUp className="w-4 h-4 text-green-600" />}
                      {isWorst && <TrendingDown className="w-4 h-4 text-red-600" />}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Products to Compare</h3>
            <p className="text-gray-600 mb-4">
              Add products using the form above to start comparing their environmental impact.
            </p>
            <div className="text-sm text-gray-500">
              You can compare up to 3 products side by side.
            </div>
          </div>
        </div>
      )}

      {/* Summary */}
      {products.length > 1 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">Comparison Summary</h4>
          <div className="text-sm text-gray-600">
            <p className="mb-1">
              <strong>Best Overall:</strong> {products.reduce((best, current) => 
                current.analysis.eco_score > best.analysis.eco_score ? current : best
              ).analysis.product_info.name} (EcoScore: {Math.max(...products.map(p => p.analysis.eco_score))})
            </p>
            <p>
              <strong>Most Sustainable Choice:</strong> Consider the product with the highest EcoScore and best performance in factors most important to you.
            </p>
          </div>
        </div>
      )}

      {/* Impact Factors Chart */}
      {products.length > 1 && (
        <div className="mt-6 p-6 bg-white rounded-lg border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <BarChart3 className="w-5 h-5 text-gray-700" />
            <h4 className="font-semibold text-gray-800">Impact Factors Comparison</h4>
          </div>
          <div className="h-80">
            <Bar
              data={{
                labels: allFactors.map(factorName =>
                  factorName.length > 15 ? factorName.substring(0, 15) + '...' : factorName
                ),
                datasets: products.map((product, index) => {
                  const colors = ['#8884d8', '#82ca9d', '#ffc658'];
                  const color = colors[index % colors.length];
                  const productName = product.analysis.product_info.name.length > 15
                    ? product.analysis.product_info.name.substring(0, 15) + '...'
                    : product.analysis.product_info.name;

                  return {
                    label: productName,
                    data: allFactors.map(factorName => {
                      const factor = product.analysis.impact_factors.find(f => f.name === factorName);
                      return factor?.score || 0;
                    }),
                    backgroundColor: color,
                    borderColor: color,
                    borderWidth: 1,
                  };
                })
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100,
                  },
                },
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
