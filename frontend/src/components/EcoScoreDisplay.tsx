'use client';

import { Loader2, Leaf, AlertCircle, TrendingUp, TrendingDown, Minus, Zap, Droplets, Factory, Truck, Package, Recycle } from 'lucide-react';

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

interface EcoScoreResult {
  success: boolean;
  analysis?: ProductAnalysis;
  error?: string;
  processing_time_ms?: number;
}

interface EcoScoreDisplayProps {
  result: EcoScoreResult | null;
  isLoading: boolean;
}

export default function EcoScoreDisplay({ result, isLoading }: EcoScoreDisplayProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getFactorIcon = (factorName: string) => {
    const name = factorName.toLowerCase();
    if (name.includes('carbon') || name.includes('footprint') || name.includes('emission')) {
      return <Zap className="w-5 h-5 text-gray-600" />;
    }
    if (name.includes('resource') || name.includes('water') || name.includes('energy')) {
      return <Droplets className="w-5 h-5 text-blue-600" />;
    }
    if (name.includes('manufacturing') || name.includes('process')) {
      return <Factory className="w-5 h-5 text-gray-700" />;
    }
    if (name.includes('transport') || name.includes('supply') || name.includes('chain')) {
      return <Truck className="w-5 h-5 text-orange-600" />;
    }
    if (name.includes('packaging') || name.includes('waste')) {
      return <Package className="w-5 h-5 text-amber-600" />;
    }
    if (name.includes('end') || name.includes('life') || name.includes('disposal') || name.includes('recycle')) {
      return <Recycle className="w-5 h-5 text-green-600" />;
    }
    return <Leaf className="w-5 h-5 text-green-600" />;
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    if (score >= 40) return 'bg-orange-100';
    return 'bg-red-100';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 60) return <TrendingUp className="h-5 w-5" />;
    if (score >= 40) return <Minus className="h-5 w-5" />;
    return <TrendingDown className="h-5 w-5" />;
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-green-600" />
        <p className="text-gray-700">Analyzing environmental impact...</p>
        <p className="text-sm text-gray-600">This may take a few moments</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4 text-gray-600">
        <Leaf className="h-12 w-12 text-gray-400" />
        <p className="text-lg font-medium">Ready for Analysis</p>
        <p className="text-sm text-center">
          Enter a product name, URL, or scan a barcode to get started with environmental impact analysis.
        </p>
      </div>
    );
  }

  if (!result.success || !result.analysis) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <AlertCircle className="h-12 w-12 text-red-500" />
        <p className="text-lg font-medium text-red-600">Analysis Failed</p>
        <p className="text-sm text-gray-700 text-center">
          {result.error || 'Unable to analyze this product. Please try again.'}
        </p>
      </div>
    );
  }

  const { analysis } = result;

  return (
    <div className="space-y-6">
      {/* Product Info */}
      <div className="border-b border-gray-200 pb-4">
        <h3 className="text-lg font-bold text-gray-800">{analysis.product_info.name}</h3>
        {analysis.product_info.brand && (
          <p className="text-sm text-gray-700">by {analysis.product_info.brand}</p>
        )}
        {analysis.product_info.category && (
          <p className="text-sm text-gray-600">{analysis.product_info.category}</p>
        )}
      </div>

      {/* EcoScore */}
      <div className="text-center">
        <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${getScoreBgColor(analysis.eco_score)} mb-4`}>
          <div className="text-center">
            <div className={`text-2xl font-bold ${getScoreColor(analysis.eco_score)}`}>
              {analysis.eco_score}
            </div>
            <div className="text-xs text-gray-600">EcoScore</div>
          </div>
        </div>
        <div className={`flex items-center justify-center space-x-2 ${getScoreColor(analysis.eco_score)}`}>
          {getScoreIcon(analysis.eco_score)}
          <span className="font-medium">{getScoreLabel(analysis.eco_score)}</span>
        </div>
        <p className="text-sm text-gray-700 mt-2">
          Confidence: {Math.round(analysis.confidence_level * 100)}%
        </p>
      </div>

      {/* Impact Factors */}
      <div>
        <h4 className="font-bold text-lg text-gray-900 mb-4">Key Impact Factors</h4>
        <div className="space-y-3">
          {analysis.impact_factors.map((factor, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getFactorIcon(factor.name)}
                  <span className="font-medium text-sm text-gray-900">{factor.name}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${getScoreColor(factor.score)}`}>
                    {factor.score}/100
                  </span>
                  <span className="text-xs text-gray-600">
                    ({Math.round(factor.weight * 100)}% weight)
                  </span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                  className={`h-2 rounded-full ${
                    factor.score >= 80 ? 'bg-green-500' :
                    factor.score >= 60 ? 'bg-yellow-500' :
                    factor.score >= 40 ? 'bg-orange-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${factor.score}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-700">{factor.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Analysis Summary */}
      <div>
        <h4 className="font-bold text-gray-800 mb-2">Analysis Summary</h4>
        <p className="text-sm text-gray-800 bg-gray-50 rounded-lg p-3">
          {analysis.analysis_summary}
        </p>
      </div>

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div>
          <h4 className="font-bold text-gray-800 mb-2">Recommendations</h4>
          <ul className="space-y-2">
            {analysis.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start space-x-2 text-sm">
                <Leaf className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span className="text-gray-800">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Data Sources */}
      <div className="text-xs text-gray-600 border-t border-gray-200 pt-4">
        <p>Data sources: {analysis.data_sources.join(', ')}</p>
        {result.processing_time_ms && (
          <p>Analysis completed in {result.processing_time_ms}ms</p>
        )}
      </div>
    </div>
  );
}
