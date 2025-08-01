export enum AnalysisType {
  PRODUCT_SEARCH = "product_search",
  BARCODE_SCAN = "barcode_scan",
  URL_ANALYSIS = "url_analysis",
  COMPARISON = "comparison"
}

export interface HistoryEntry {
  id: string;
  timestamp: string;
  analysis_type: AnalysisType;
  query: string;
  analysis: ProductAnalysis;
  user_session?: string;
}

export interface ComparisonHistoryEntry {
  id: string;
  timestamp: string;
  analysis_type: AnalysisType.COMPARISON;
  products: ProductAnalysis[];
  comparison_notes?: string;
  user_session?: string;
}

export interface JourneyStats {
  total_analyses: number;
  total_comparisons: number;
  average_eco_score: number;
  best_eco_score: number;
  worst_eco_score: number;
  favorite_categories: string[];
  improvement_trend: number;
  days_active: number;
  first_analysis_date?: string;
  last_analysis_date?: string;
}

export interface CategoryStats {
  category: string;
  count: number;
  average_score: number;
  best_score: number;
  worst_score: number;
  trend: number;
}

export interface TimelineEntry {
  date: string;
  eco_score: number;
  product_name: string;
  category?: string;
  analysis_type: AnalysisType;
}

export interface EcoJourney {
  stats: JourneyStats;
  recent_analyses: HistoryEntry[];
  recent_comparisons: ComparisonHistoryEntry[];
  category_breakdown: CategoryStats[];
  timeline: TimelineEntry[];
  milestones: string[];
}

export interface HistoryFilter {
  analysis_type?: AnalysisType;
  category?: string;
  min_eco_score?: number;
  max_eco_score?: number;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}

export interface HistoryResponse {
  success: boolean;
  entries: HistoryEntry[];
  comparisons: ComparisonHistoryEntry[];
  total_count: number;
  has_more: boolean;
}

export interface JourneyResponse {
  success: boolean;
  journey: EcoJourney;
  insights: string[];
}

// Import ProductAnalysis from existing types
import { ProductAnalysis } from './index';
