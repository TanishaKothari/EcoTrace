'use client';

import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp, Award, Calendar, Filter, Search, BarChart3 } from 'lucide-react';
import { HistoryResponse, JourneyResponse, HistoryFilter, AnalysisType } from '@/types/history';
import { EcoScoreDisplay } from '@/components/EcoScoreDisplay';
import JourneyAnalytics from '@/components/JourneyAnalytics';

export default function HistoryPage() {
  const [historyData, setHistoryData] = useState<HistoryResponse | null>(null);
  const [journeyData, setJourneyData] = useState<JourneyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'recent' | 'journey' | 'timeline' | 'analytics'>('recent');
  const [filters, setFilters] = useState<HistoryFilter>({
    limit: 20,
    offset: 0
  });

  useEffect(() => {
    fetchHistoryData();
    fetchJourneyData();
  }, [filters]);

  const fetchHistoryData = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.analysis_type) params.append('analysis_type', filters.analysis_type);
      if (filters.category) params.append('category', filters.category);
      if (filters.min_eco_score) params.append('min_eco_score', filters.min_eco_score.toString());
      if (filters.max_eco_score) params.append('max_eco_score', filters.max_eco_score.toString());
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.offset) params.append('offset', filters.offset.toString());

      const response = await fetch(`http://localhost:8000/history?${params}`);
      const data = await response.json();
      setHistoryData(data);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const fetchJourneyData = async () => {
    try {
      const response = await fetch('http://localhost:8000/journey');
      const data = await response.json();
      setJourneyData(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching journey data:', error);
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getAnalysisTypeIcon = (type: AnalysisType) => {
    switch (type) {
      case AnalysisType.PRODUCT_SEARCH:
        return <Search className="w-4 h-4" />;
      case AnalysisType.BARCODE_SCAN:
        return <div className="w-4 h-4 border border-gray-400 rounded"></div>;
      case AnalysisType.URL_ANALYSIS:
        return <div className="w-4 h-4 text-blue-500">🔗</div>;
      case AnalysisType.COMPARISON:
        return <BarChart3 className="w-4 h-4 text-purple-500" />;
      default:
        return <Search className="w-4 h-4" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your eco journey...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Eco Journey</h1>
          <p className="text-gray-600">Track your environmental impact analysis history and progress</p>
        </div>

        {/* Journey Stats Cards */}
        {journeyData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <Search className="w-8 h-8 text-blue-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Analyses</p>
                  <p className="text-2xl font-bold text-gray-900">{journeyData.journey.stats.total_analyses}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <TrendingUp className="w-8 h-8 text-green-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Average EcoScore</p>
                  <p className={`text-2xl font-bold ${getScoreColor(journeyData.journey.stats.average_eco_score)}`}>
                    {journeyData.journey.stats.average_eco_score.toFixed(1)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <Award className="w-8 h-8 text-yellow-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Best Score</p>
                  <p className={`text-2xl font-bold ${getScoreColor(journeyData.journey.stats.best_eco_score)}`}>
                    {journeyData.journey.stats.best_eco_score}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <Calendar className="w-8 h-8 text-purple-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Days Active</p>
                  <p className="text-2xl font-bold text-gray-900">{journeyData.journey.stats.days_active}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Insights */}
        {journeyData && journeyData.insights.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 Your Eco Insights</h3>
            <ul className="space-y-2">
              {journeyData.insights.map((insight, index) => (
                <li key={index} className="text-blue-800">{insight}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Milestones */}
        {journeyData && journeyData.journey.milestones.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-yellow-900 mb-3">🏆 Achievements</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {journeyData.journey.milestones.map((milestone, index) => (
                <div key={index} className="text-yellow-800 bg-yellow-100 rounded px-3 py-2">
                  {milestone}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {[
                { id: 'recent', label: 'Recent Analyses', icon: Clock },
                { id: 'journey', label: 'Category Breakdown', icon: TrendingUp },
                { id: 'timeline', label: 'Timeline', icon: Calendar },
                { id: 'analytics', label: 'Analytics', icon: BarChart3 }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === id
                      ? 'border-green-500 text-green-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{label}</span>
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'recent' && historyData && (
              <div className="space-y-4">
                {historyData.entries.length === 0 ? (
                  <div className="text-center py-12">
                    <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No analyses yet</h3>
                    <p className="text-gray-600">Start analyzing products to see your history here!</p>
                  </div>
                ) : (
                  historyData.entries.map((entry) => (
                    <div key={entry.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            {getAnalysisTypeIcon(entry.analysis_type)}
                            <span className="text-sm text-gray-500 capitalize">
                              {entry.analysis_type.replace('_', ' ')}
                            </span>
                            {entry.is_comparison_analysis && (
                              <>
                                <span className="text-sm text-gray-400">•</span>
                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  <BarChart3 className="w-3 h-3 mr-1" />
                                  For Comparison
                                </span>
                              </>
                            )}
                            <span className="text-sm text-gray-400">•</span>
                            <span className="text-sm text-gray-500">{formatDate(entry.timestamp)}</span>
                          </div>
                          <h4 className="font-medium text-gray-900 mb-1">{entry.analysis.product_info.name}</h4>
                          <p className="text-sm text-gray-600 mb-2">Query: "{entry.query}"</p>
                          {entry.analysis.product_info.category && (
                            <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                              {entry.analysis.product_info.category}
                            </span>
                          )}
                        </div>
                        <div className="ml-4 text-right">
                          <div className={`text-2xl font-bold ${getScoreColor(entry.analysis.eco_score)}`}>
                            {entry.analysis.eco_score}
                          </div>
                          <div className="text-sm text-gray-500">EcoScore</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'journey' && journeyData && (
              <div className="space-y-6">
                {journeyData.journey.category_breakdown.length === 0 ? (
                  <div className="text-center py-12">
                    <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No category data yet</h3>
                    <p className="text-gray-600">Analyze more products to see category breakdowns!</p>
                  </div>
                ) : (
                  journeyData.journey.category_breakdown.map((category) => (
                    <div key={category.category} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium text-gray-900">{category.category}</h4>
                        <span className="text-sm text-gray-500">{category.count} analyses</span>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">Average</p>
                          <p className={`font-semibold ${getScoreColor(category.average_score)}`}>
                            {category.average_score.toFixed(1)}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600">Best</p>
                          <p className={`font-semibold ${getScoreColor(category.best_score)}`}>
                            {category.best_score}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600">Trend</p>
                          <p className={`font-semibold ${category.trend > 0 ? 'text-green-600' : category.trend < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                            {category.trend > 0 ? '+' : ''}{category.trend.toFixed(1)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'timeline' && journeyData && (
              <div className="space-y-4">
                {journeyData.journey.timeline.length === 0 ? (
                  <div className="text-center py-12">
                    <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No timeline data yet</h3>
                    <p className="text-gray-600">Your analysis timeline will appear here as you use EcoTrace!</p>
                  </div>
                ) : (
                  <div className="relative">
                    <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                    {journeyData.journey.timeline.map((entry, index) => (
                      <div key={index} className="relative flex items-center space-x-4 pb-6">
                        <div className={`relative z-10 w-8 h-8 bg-white border-2 rounded-full flex items-center justify-center ${
                          entry.analysis_type === 'comparison' ? 'border-purple-300 bg-purple-50' : 'border-gray-300'
                        }`}>
                          {getAnalysisTypeIcon(entry.analysis_type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium text-gray-900">{entry.product_name}</p>
                              <p className="text-sm text-gray-500">{formatDate(entry.date)}</p>
                              {entry.analysis_type === 'comparison' && (
                                <span className="inline-block bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded mt-1">
                                  Product Comparison
                                </span>
                              )}
                              {entry.category && entry.analysis_type !== 'comparison' && (
                                <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded mt-1">
                                  {entry.category}
                                </span>
                              )}
                            </div>
                            <div className={`text-lg font-bold ${getScoreColor(entry.eco_score)}`}>
                              {entry.analysis_type === 'comparison' ? `${entry.eco_score} avg` : entry.eco_score}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'analytics' && journeyData && (
              <JourneyAnalytics journey={journeyData.journey} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
