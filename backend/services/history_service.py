import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from collections import defaultdict, Counter
import statistics

from models.history import (
    HistoryEntry, ComparisonHistoryEntry, JourneyStats, CategoryStats,
    TimelineEntry, EcoJourney, HistoryFilter, AnalysisType
)
from models.eco_score import ProductAnalysis

class HistoryService:
    """Service for managing analysis history and eco journey tracking"""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self.history_entries: List[HistoryEntry] = []
        self.comparison_entries: List[ComparisonHistoryEntry] = []
        
    def save_analysis(self, query: str, analysis: ProductAnalysis, 
                     analysis_type: AnalysisType, user_session: Optional[str] = None) -> str:
        """Save a new analysis to history"""
        entry_id = str(uuid.uuid4())
        entry = HistoryEntry(
            id=entry_id,
            timestamp=datetime.now(),
            analysis_type=analysis_type,
            query=query,
            analysis=analysis,
            user_session=user_session
        )
        self.history_entries.append(entry)
        return entry_id
    
    def save_comparison(self, products: List[ProductAnalysis], 
                       user_session: Optional[str] = None, 
                       notes: Optional[str] = None) -> str:
        """Save a product comparison to history"""
        entry_id = str(uuid.uuid4())
        entry = ComparisonHistoryEntry(
            id=entry_id,
            timestamp=datetime.now(),
            products=products,
            comparison_notes=notes,
            user_session=user_session
        )
        self.comparison_entries.append(entry)
        return entry_id
    
    def get_history(self, filter_options: HistoryFilter, 
                   user_session: Optional[str] = None) -> tuple[List[HistoryEntry], int]:
        """Get filtered history entries"""
        # Filter entries
        filtered_entries = self._filter_entries(self.history_entries, filter_options, user_session)
        
        # Apply pagination
        total_count = len(filtered_entries)
        start_idx = filter_options.offset
        end_idx = start_idx + filter_options.limit
        paginated_entries = filtered_entries[start_idx:end_idx]
        
        return paginated_entries, total_count
    
    def get_comparisons(self, limit: int = 10, offset: int = 0, 
                       user_session: Optional[str] = None) -> tuple[List[ComparisonHistoryEntry], int]:
        """Get comparison history"""
        filtered_comparisons = [
            comp for comp in self.comparison_entries
            if user_session is None or comp.user_session == user_session
        ]
        
        # Sort by timestamp (newest first)
        filtered_comparisons.sort(key=lambda x: x.timestamp, reverse=True)
        
        total_count = len(filtered_comparisons)
        paginated_comparisons = filtered_comparisons[offset:offset + limit]
        
        return paginated_comparisons, total_count
    
    def get_eco_journey(self, user_session: Optional[str] = None) -> EcoJourney:
        """Generate comprehensive eco journey data"""
        # Get user's entries
        user_entries = [
            entry for entry in self.history_entries
            if user_session is None or entry.user_session == user_session
        ]
        user_comparisons = [
            comp for comp in self.comparison_entries
            if user_session is None or comp.user_session == user_session
        ]
        
        # Calculate journey stats
        stats = self._calculate_journey_stats(user_entries, user_comparisons)
        
        # Get recent analyses (last 10)
        recent_analyses = sorted(user_entries, key=lambda x: x.timestamp, reverse=True)[:10]
        
        # Get recent comparisons (last 5)
        recent_comparisons = sorted(user_comparisons, key=lambda x: x.timestamp, reverse=True)[:5]
        
        # Calculate category breakdown
        category_breakdown = self._calculate_category_stats(user_entries)
        
        # Generate timeline
        timeline = self._generate_timeline(user_entries)
        
        # Generate milestones
        milestones = self._generate_milestones(stats, user_entries)
        
        return EcoJourney(
            stats=stats,
            recent_analyses=recent_analyses,
            recent_comparisons=recent_comparisons,
            category_breakdown=category_breakdown,
            timeline=timeline,
            milestones=milestones
        )
    
    def _filter_entries(self, entries: List[HistoryEntry], 
                       filter_options: HistoryFilter, 
                       user_session: Optional[str]) -> List[HistoryEntry]:
        """Apply filters to history entries"""
        filtered = entries
        
        # User session filter
        if user_session:
            filtered = [e for e in filtered if e.user_session == user_session]
        
        # Analysis type filter
        if filter_options.analysis_type:
            filtered = [e for e in filtered if e.analysis_type == filter_options.analysis_type]
        
        # Category filter
        if filter_options.category:
            filtered = [e for e in filtered if e.analysis.product_info.category == filter_options.category]
        
        # Eco score range filter
        if filter_options.min_eco_score:
            filtered = [e for e in filtered if e.analysis.eco_score >= filter_options.min_eco_score]
        if filter_options.max_eco_score:
            filtered = [e for e in filtered if e.analysis.eco_score <= filter_options.max_eco_score]
        
        # Date range filter
        if filter_options.date_from:
            filtered = [e for e in filtered if e.timestamp >= filter_options.date_from]
        if filter_options.date_to:
            filtered = [e for e in filtered if e.timestamp <= filter_options.date_to]
        
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered
    
    def _calculate_journey_stats(self, entries: List[HistoryEntry], 
                                comparisons: List[ComparisonHistoryEntry]) -> JourneyStats:
        """Calculate journey statistics"""
        if not entries:
            return JourneyStats()
        
        eco_scores = [entry.analysis.eco_score for entry in entries]
        
        # Calculate improvement trend (compare first half vs second half)
        improvement_trend = 0.0
        if len(eco_scores) >= 4:
            mid_point = len(eco_scores) // 2
            first_half_avg = statistics.mean(eco_scores[:mid_point])
            second_half_avg = statistics.mean(eco_scores[mid_point:])
            improvement_trend = second_half_avg - first_half_avg
        
        # Calculate favorite categories
        categories = [entry.analysis.product_info.category for entry in entries 
                     if entry.analysis.product_info.category]
        category_counts = Counter(categories)
        favorite_categories = [cat for cat, count in category_counts.most_common(5)]
        
        # Calculate days active
        timestamps = [entry.timestamp for entry in entries]
        first_date = min(timestamps)
        last_date = max(timestamps)
        days_active = (last_date - first_date).days + 1
        
        return JourneyStats(
            total_analyses=len(entries),
            total_comparisons=len(comparisons),
            average_eco_score=statistics.mean(eco_scores),
            best_eco_score=max(eco_scores),
            worst_eco_score=min(eco_scores),
            favorite_categories=favorite_categories,
            improvement_trend=improvement_trend,
            days_active=days_active,
            first_analysis_date=first_date,
            last_analysis_date=last_date
        )
    
    def _calculate_category_stats(self, entries: List[HistoryEntry]) -> List[CategoryStats]:
        """Calculate statistics by category"""
        category_data = defaultdict(list)
        
        for entry in entries:
            category = entry.analysis.product_info.category or "Unknown"
            category_data[category].append({
                'score': entry.analysis.eco_score,
                'timestamp': entry.timestamp
            })
        
        category_stats = []
        for category, data in category_data.items():
            scores = [item['score'] for item in data]
            
            # Calculate trend (improvement over time)
            trend = 0.0
            if len(data) >= 2:
                # Sort by timestamp and compare first vs last half
                sorted_data = sorted(data, key=lambda x: x['timestamp'])
                mid_point = len(sorted_data) // 2
                first_half = [item['score'] for item in sorted_data[:mid_point]]
                second_half = [item['score'] for item in sorted_data[mid_point:]]
                if first_half and second_half:
                    trend = statistics.mean(second_half) - statistics.mean(first_half)
            
            category_stats.append(CategoryStats(
                category=category,
                count=len(scores),
                average_score=statistics.mean(scores),
                best_score=max(scores),
                worst_score=min(scores),
                trend=trend
            ))
        
        # Sort by count (most analyzed categories first)
        category_stats.sort(key=lambda x: x.count, reverse=True)
        return category_stats
    
    def _generate_timeline(self, entries: List[HistoryEntry]) -> List[TimelineEntry]:
        """Generate timeline entries for visualization"""
        timeline = []
        for entry in entries:
            timeline.append(TimelineEntry(
                date=entry.timestamp,
                eco_score=entry.analysis.eco_score,
                product_name=entry.analysis.product_info.name,
                category=entry.analysis.product_info.category,
                analysis_type=entry.analysis_type
            ))
        
        # Sort by date
        timeline.sort(key=lambda x: x.date)
        return timeline
    
    def _generate_milestones(self, stats: JourneyStats, entries: List[HistoryEntry]) -> List[str]:
        """Generate achievement-like milestones"""
        milestones = []
        
        # Analysis count milestones
        if stats.total_analyses >= 1:
            milestones.append("🎯 First Analysis Complete!")
        if stats.total_analyses >= 10:
            milestones.append("🔥 10 Products Analyzed!")
        if stats.total_analyses >= 50:
            milestones.append("🌟 Eco Explorer - 50 Analyses!")
        if stats.total_analyses >= 100:
            milestones.append("🏆 Eco Champion - 100 Analyses!")
        
        # Score milestones
        if stats.best_eco_score >= 90:
            milestones.append("💚 Found an Eco Superstar (90+ score)!")
        if stats.average_eco_score >= 70:
            milestones.append("🌱 Eco-Conscious Choices (70+ avg score)!")
        
        # Improvement milestones
        if stats.improvement_trend > 10:
            milestones.append("📈 Great Progress - Improving choices!")
        
        # Category diversity
        if len(stats.favorite_categories) >= 5:
            milestones.append("🎨 Category Explorer - 5+ categories!")
        
        # Consistency milestones
        if stats.days_active >= 7:
            milestones.append("⭐ Week-long Journey!")
        if stats.days_active >= 30:
            milestones.append("🗓️ Month-long Commitment!")
        
        return milestones

# Global instance
history_service = HistoryService()
