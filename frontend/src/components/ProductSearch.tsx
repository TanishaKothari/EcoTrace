'use client';

import { useState } from 'react';
import { Search, Link, Loader2 } from 'lucide-react';
import { getAuthHeaders } from '@/utils/userToken';

interface ProductSearchProps {
  onAnalysis: (result: any) => void;
  onLoading: (loading: boolean) => void;
}

export default function ProductSearch({ onAnalysis, onLoading }: ProductSearchProps) {
  const [query, setQuery] = useState('');
  const [queryType, setQueryType] = useState<'name' | 'url'>('name');

  const validateInput = (input: string): { isValid: boolean; error?: string } => {
    const trimmedInput = input.trim();

    // Check minimum length
    if (trimmedInput.length < 2) {
      return { isValid: false, error: 'Please enter at least 2 characters' };
    }

    // Check for URL - more thorough validation
    const urlPattern = /^https?:\/\/[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\/.*/i;
    if (trimmedInput.startsWith('http://') || trimmedInput.startsWith('https://')) {
      if (urlPattern.test(trimmedInput)) {
        return { isValid: true };
      } else {
        return { isValid: false, error: 'Please enter a valid URL' };
      }
    }

    // Check for obviously invalid patterns
    const hasRepeatingChars = /(.)\1{5,}/.test(trimmedInput); // 6+ repeating chars
    const isAllSameChar = /^(.)\1+$/.test(trimmedInput);
    const isKeyboardMashing = /^[qwertyuiop]+$|^[asdfghjkl]+$|^[zxcvbnm]+$/i.test(trimmedInput.replace(/\s/g, ''));

    if (hasRepeatingChars || isAllSameChar || isKeyboardMashing) {
      return { isValid: false, error: 'Please enter a valid product name or URL' };
    }

    // Check for excessive consonants (more lenient)
    const consonantPattern = /[bcdfghjklmnpqrstvwxyz]{7,}/i;
    if (consonantPattern.test(trimmedInput)) {
      return { isValid: false, error: 'Please enter a valid product name' };
    }

    // Very basic check for completely random strings
    const words = trimmedInput.split(/\s+/);
    if (words.length === 1 && words[0].length < 3 && !/\d/.test(words[0])) {
      // Allow common short brand/product names
      const commonShortNames = ['tv', 'pc', 'mac', 'ps5', 'xbox', 'cpu', 'gpu', 'ssd', 'ram', 'bmw', 'vw'];
      if (!commonShortNames.includes(words[0].toLowerCase())) {
        return { isValid: false, error: 'Please enter a more specific product name' };
      }
    }

    return { isValid: true };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Validate input before sending to API
    const validation = validateInput(query);
    if (!validation.isValid) {
      onAnalysis({
        success: false,
        error: validation.error || 'Invalid input',
      });
      return;
    }

    onLoading(true);
    try {
      const response = await fetch('http://localhost:8000/analyze/product', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          query: query.trim(),
          query_type: queryType,
        }),
      });

      if (!response.ok) {
        try {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        } catch (parseError) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      const result = await response.json();
      onAnalysis(result);
    } catch (error) {
      console.error('Analysis failed:', error);
      onAnalysis({
        success: false,
        error: error instanceof Error ? error.message : 'Analysis failed',
      });
    } finally {
      onLoading(false);
    }
  };

  const detectQueryType = (value: string) => {
    const urlPattern = /^https?:\/\/.+/i;
    return urlPattern.test(value) ? 'url' : 'name';
  };

  const handleQueryChange = (value: string) => {
    setQuery(value);
    setQueryType(detectQueryType(value));
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-4">Product Analysis</h3>
        <p className="text-gray-700 mb-6">
          Enter a product name or paste a product URL to get an environmental impact analysis.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="product-query" className="block text-sm font-medium text-gray-800 mb-2">
            Product Name or URL
          </label>
          <div className="relative">
            <input
              id="product-query"
              type="text"
              value={query}
              onChange={(e) => handleQueryChange(e.target.value)}
              placeholder="e.g., iPhone 15 Pro or https://example.com/product"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-600 text-gray-900"
            />
            <div className="absolute right-3 top-3">
              {queryType === 'url' ? (
                <Link className="h-5 w-5 text-blue-500" />
              ) : (
                <Search className="h-5 w-5 text-gray-600" />
              )}
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-700">
            {queryType === 'url'
              ? 'URL detected - we\'ll extract product information from the page'
              : 'Product name - we\'ll search for environmental data'
            }
          </p>
        </div>

        <button
          type="submit"
          disabled={!query.trim()}
          className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
        >
          <Search className="h-5 w-5" />
          <span>Analyze Environmental Impact</span>
        </button>
      </form>

      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-bold text-gray-800 mb-2">Examples:</h4>
        <div className="space-y-2 text-sm text-gray-700">
          <div className="flex items-center space-x-2">
            <Search className="h-4 w-4" />
            <span>Product names: "Organic cotton t-shirt", "Tesla Model 3", "iPhone 15"</span>
          </div>
          <div className="flex items-center space-x-2">
            <Link className="h-4 w-4" />
            <span>Product URLs: Amazon, eBay, manufacturer websites</span>
          </div>
        </div>
      </div>
    </div>
  );
}
