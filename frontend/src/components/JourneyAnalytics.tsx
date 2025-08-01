'use client';

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { EcoJourney } from '@/types/history';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface JourneyAnalyticsProps {
  journey: EcoJourney;
}

export default function JourneyAnalytics({ journey }: JourneyAnalyticsProps) {
  const { stats, timeline, category_breakdown } = journey;

  // Timeline Chart Data
  const timelineData = {
    labels: timeline.map(entry => 
      new Date(entry.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'EcoScore Over Time',
        data: timeline.map(entry => entry.eco_score),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const timelineOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'EcoScore Progress Over Time',
        font: {
          size: 16,
          weight: 'bold' as const,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'EcoScore',
        },
      },
    },
  };

  // Category Breakdown Chart Data
  const categoryData = {
    labels: category_breakdown.map(cat => cat.category),
    datasets: [
      {
        label: 'Average Score',
        data: category_breakdown.map(cat => cat.average_score),
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
          'rgb(168, 85, 247)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const categoryOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: true,
        text: 'Average EcoScore by Category',
        font: {
          size: 16,
          weight: 'bold' as const,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Average EcoScore',
        },
      },
    },
  };

  // Analysis Type Distribution
  const analysisTypes = timeline.reduce((acc, entry) => {
    acc[entry.analysis_type] = (acc[entry.analysis_type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const analysisTypeData = {
    labels: Object.keys(analysisTypes).map(type => 
      type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    ),
    datasets: [
      {
        data: Object.values(analysisTypes),
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(245, 158, 11, 0.8)',
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
          'rgb(168, 85, 247)',
          'rgb(245, 158, 11)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const analysisTypeOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: true,
        text: 'Analysis Methods Used',
        font: {
          size: 16,
          weight: 'bold' as const,
        },
      },
    },
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 2) return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (trend < -2) return <TrendingDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-600" />;
  };

  const getTrendColor = (trend: number) => {
    if (trend > 2) return 'text-green-600';
    if (trend < -2) return 'text-red-600';
    return 'text-gray-600';
  };

  if (timeline.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <TrendingUp className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Analytics Data Yet</h3>
        <p className="text-gray-600">Analyze more products to see detailed analytics and trends!</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Trend</h3>
          <div className="flex items-center space-x-3">
            {getTrendIcon(stats.improvement_trend)}
            <div>
              <p className={`text-2xl font-bold ${getTrendColor(stats.improvement_trend)}`}>
                {stats.improvement_trend > 0 ? '+' : ''}{stats.improvement_trend.toFixed(1)}
              </p>
              <p className="text-sm text-gray-600">Score improvement</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            {stats.improvement_trend > 5 
              ? "Great progress! Your choices are getting more eco-friendly."
              : stats.improvement_trend < -5
              ? "Consider focusing on higher-scoring products."
              : "Keep analyzing to see your trend develop."}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Score Range</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Best:</span>
              <span className="font-semibold text-green-600">{stats.best_eco_score}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Average:</span>
              <span className="font-semibold text-blue-600">{stats.average_eco_score.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Lowest:</span>
              <span className="font-semibold text-orange-600">{stats.worst_eco_score}</span>
            </div>
          </div>
          <div className="mt-3 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 h-2 rounded-full"
              style={{ width: `${stats.average_eco_score}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Analyses:</span>
              <span className="font-bold text-gray-900 text-lg">{stats.total_analyses}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Comparisons:</span>
              <span className="font-bold text-gray-900 text-lg">{stats.total_comparisons}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Days Active:</span>
              <span className="font-bold text-gray-900 text-lg">{stats.days_active}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Timeline Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <Line data={timelineData} options={timelineOptions} />
        </div>

        {/* Analysis Type Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <Doughnut data={analysisTypeData} options={analysisTypeOptions} />
        </div>
      </div>

      {/* Category Breakdown Chart */}
      {category_breakdown.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <Bar data={categoryData} options={categoryOptions} />
        </div>
      )}

      {/* Category Trends Table */}
      {category_breakdown.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Category Performance</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Count
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Average Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Best Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trend
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {category_breakdown.map((category) => (
                  <tr key={category.category}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {category.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {category.count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`font-semibold ${
                        category.average_score >= 80 ? 'text-green-600' :
                        category.average_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {category.average_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`font-semibold ${
                        category.best_score >= 80 ? 'text-green-600' :
                        category.best_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {category.best_score}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        {getTrendIcon(category.trend)}
                        <span className={getTrendColor(category.trend)}>
                          {category.trend > 0 ? '+' : ''}{category.trend.toFixed(1)}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
