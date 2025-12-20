"""
Database-based history service for EcoTrace application
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional
from collections import defaultdict, Counter
import statistics
from sqlalchemy import desc

from database import get_db_session, User, HistoryEntry, ComparisonEntry
from models.history import (
    HistoryFilter, HistoryResponse, JourneyResponse, EcoJourney,
    JourneyStats, CategoryStats, TimelineEntry, AnalysisType
)
from models.eco_score import ProductAnalysis
from utils.security import validate_token, hash_token_for_storage
from services.auth_service import auth_service

logger = logging.getLogger(__name__)

class DatabaseHistoryService:
    """Database-based service for managing analysis history and eco journey tracking"""
    
    def __init__(self):
        pass
    
    def get_or_create_user(self, user_token: str) -> User:
        """Get existing user or create new anonymous user with secure token validation"""
        # Validate token format and signature
        if not validate_token(user_token):
            raise ValueError("Invalid token format or signature")

        db = get_db_session()
        try:
            # Hash token for database lookup
            token_hash = hash_token_for_storage(user_token)

            # Look up user by token hash
            user = db.query(User).filter(User.token_hash == token_hash).first()
            if not user:
                # Create new user with hashed token
                user_id = f"user_{uuid.uuid4().hex[:12]}"
                user = User(
                    id=user_id,
                    token_hash=token_hash,
                    is_anonymous=True
                )
                db.add(user)
                db.commit()
                # Don't refresh here, just return the user object
            else:
                # Update last active
                user.last_active = datetime.utcnow()
                db.commit()
            return user
        finally:
            db.close()
    
    def save_analysis(self, user_token: str, query: str, analysis: ProductAnalysis,
                     analysis_type: AnalysisType, is_comparison_analysis: bool = False) -> Optional[str]:
        """Save a new analysis to history (only for authenticated users)"""
        # Only save history for authenticated users
        if not auth_service.is_authenticated_user(user_token):
            return None  # No history tracking for anonymous users

        user = auth_service.get_user_by_token(user_token)
        if not user:
            return None

        db = get_db_session()
        try:
            # Update last active
            user.last_active = datetime.utcnow()
            db.merge(user)

            # Create history entry
            entry_id = str(uuid.uuid4())
            entry = HistoryEntry(
                id=entry_id,
                user_id=user.id,
                timestamp=datetime.utcnow(),
                analysis_type=analysis_type.value,
                query=query,
                analysis=analysis.model_dump(),
                is_comparison_analysis=is_comparison_analysis
            )

            db.add(entry)
            db.commit()
            return entry_id
        finally:
            db.close()
    
    def save_comparison(self, user_token: str, products: List[ProductAnalysis],
                       notes: Optional[str] = None) -> Optional[str]:
        """Save a product comparison to history (only for authenticated users)"""
        # Only save history for authenticated users
        if not auth_service.is_authenticated_user(user_token):
            return None  # No history tracking for anonymous users

        user = auth_service.get_user_by_token(user_token)
        if not user:
            return None

        db = get_db_session()
        try:
            # Update last active
            user.last_active = datetime.utcnow()
            db.merge(user)

            # Create comparison entry
            entry_id = str(uuid.uuid4())
            entry = ComparisonEntry(
                id=entry_id,
                user_id=user.id,
                timestamp=datetime.utcnow(),
                products=[product.model_dump() for product in products],
                comparison_notes=notes
            )

            db.add(entry)
            db.commit()
            return entry_id
        finally:
            db.close()
    
    def get_history(self, user_token: str, filters: Optional[HistoryFilter] = None) -> HistoryResponse:
        """Get user's analysis history with optional filters (only for authenticated users)"""
        # Only return history for authenticated users
        if not auth_service.is_authenticated_user(user_token):
            return HistoryResponse(entries=[], comparisons=[], total_count=0, has_more=False)

        user = auth_service.get_user_by_token(user_token)
        if not user:
            return HistoryResponse(entries=[], comparisons=[], total_count=0, has_more=False)

        db = get_db_session()
        try:
            
            # Build query for history entries
            query = db.query(HistoryEntry).filter(HistoryEntry.user_id == user.id)
            
            # Apply filters if provided
            if filters:
                if filters.analysis_type:
                    query = query.filter(HistoryEntry.analysis_type == filters.analysis_type.value)
                if filters.date_from:
                    query = query.filter(HistoryEntry.timestamp >= filters.date_from)
                if filters.date_to:
                    query = query.filter(HistoryEntry.timestamp <= filters.date_to)
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            limit = filters.limit if filters and filters.limit else 20
            offset = filters.offset if filters and filters.offset else 0
            
            entries = query.order_by(desc(HistoryEntry.timestamp)).offset(offset).limit(limit).all()
            
            # Get comparisons
            comparison_query = db.query(ComparisonEntry).filter(ComparisonEntry.user_id == user.id)
            if filters and filters.date_from:
                comparison_query = comparison_query.filter(ComparisonEntry.timestamp >= filters.date_from)
            if filters and filters.date_to:
                comparison_query = comparison_query.filter(ComparisonEntry.timestamp <= filters.date_to)
            
            comparisons = comparison_query.order_by(desc(ComparisonEntry.timestamp)).limit(10).all()
            
            # Convert to response format
            from models.history import HistoryEntry as HistoryEntryModel, ComparisonHistoryEntry
            
            history_entries = []
            for entry in entries:
                history_entries.append(HistoryEntryModel(
                    id=entry.id,
                    timestamp=entry.timestamp,
                    analysis_type=AnalysisType(entry.analysis_type),
                    query=entry.query,
                    analysis=ProductAnalysis(**entry.analysis),
                    user_session=entry.user_id,
                    is_comparison_analysis=entry.is_comparison_analysis
                ))
            
            comparison_entries = []
            for comp in comparisons:
                comparison_entries.append(ComparisonHistoryEntry(
                    id=comp.id,
                    timestamp=comp.timestamp,
                    products=[ProductAnalysis(**product) for product in comp.products],
                    comparison_notes=comp.comparison_notes,
                    user_session=comp.user_id
                ))
            
            has_more = (offset + len(entries)) < total_count
            
            return HistoryResponse(
                entries=history_entries,
                comparisons=comparison_entries,
                total_count=total_count,
                has_more=has_more
            )
        finally:
            db.close()
    
    def get_journey(self, user_token: str) -> JourneyResponse:
        """Get comprehensive eco journey data for user (only for authenticated users)"""
        # Only return journey for authenticated users
        if not auth_service.is_authenticated_user(user_token):
            return JourneyResponse(journey=EcoJourney())

        user = auth_service.get_user_by_token(user_token)
        if not user:
            return JourneyResponse(journey=EcoJourney())

        db = get_db_session()
        try:
            
            # Get all entries for this user
            entries = db.query(HistoryEntry).filter(HistoryEntry.user_id == user.id).all()
            comparisons = db.query(ComparisonEntry).filter(ComparisonEntry.user_id == user.id).all()
            
            if not entries:
                return JourneyResponse(journey=EcoJourney())
            
            # Convert to model format for processing
            from models.history import HistoryEntry as HistoryEntryModel, ComparisonHistoryEntry
            
            history_entries = []
            for entry in entries:
                history_entries.append(HistoryEntryModel(
                    id=entry.id,
                    timestamp=entry.timestamp,
                    analysis_type=AnalysisType(entry.analysis_type),
                    query=entry.query,
                    analysis=ProductAnalysis(**entry.analysis),
                    user_session=entry.user_id,
                    is_comparison_analysis=entry.is_comparison_analysis
                ))
            
            comparison_entries = []
            for comp in comparisons:
                comparison_entries.append(ComparisonHistoryEntry(
                    id=comp.id,
                    timestamp=comp.timestamp,
                    products=[ProductAnalysis(**product) for product in comp.products],
                    comparison_notes=comp.comparison_notes,
                    user_session=comp.user_id
                ))
            
            # Calculate journey statistics
            stats = self._calculate_journey_stats(history_entries, comparison_entries)
            category_breakdown = self._calculate_category_stats(history_entries)
            timeline = self._generate_timeline(history_entries, comparison_entries)
            
            journey = EcoJourney(
                stats=stats,
                category_breakdown=category_breakdown,
                timeline=timeline
            )
            
            return JourneyResponse(journey=journey)
        finally:
            db.close()
    
    def _calculate_journey_stats(self, entries: List, comparisons: List) -> JourneyStats:
        """Calculate journey statistics (same logic as before)"""
        if not entries:
            return JourneyStats()
        
        # Filter out comparison analyses for statistics
        regular_entries = [entry for entry in entries if not entry.is_comparison_analysis]
        
        if not regular_entries:
            return JourneyStats()
        
        eco_scores = [entry.analysis.eco_score for entry in regular_entries]
        
        # Calculate improvement trend (last 5 vs first 5)
        improvement_trend = 0.0
        if len(eco_scores) >= 2:
            recent_scores = eco_scores[:min(5, len(eco_scores)//2)]
            early_scores = eco_scores[-min(5, len(eco_scores)//2):]
            if recent_scores and early_scores:
                improvement_trend = statistics.mean(recent_scores) - statistics.mean(early_scores)
        
        # Calculate favorite categories
        categories = [entry.analysis.product_info.category for entry in regular_entries 
                     if entry.analysis.product_info.category]
        category_counts = Counter(categories)
        favorite_categories = [cat for cat, count in category_counts.most_common(5)]
        
        # Calculate days active
        timestamps = [entry.timestamp for entry in entries]
        first_date = min(timestamps)
        last_date = max(timestamps)
        days_active = (last_date - first_date).days + 1
        
        return JourneyStats(
            total_analyses=len(regular_entries),
            total_comparisons=len(comparisons),
            average_eco_score=statistics.mean(eco_scores),
            best_eco_score=max(eco_scores),
            worst_eco_score=min(eco_scores),
            improvement_trend=improvement_trend,
            favorite_categories=favorite_categories,
            days_active=days_active,
            first_analysis_date=min([entry.timestamp for entry in regular_entries]) if regular_entries else None,
            last_analysis_date=max([entry.timestamp for entry in regular_entries]) if regular_entries else None
        )
    
    def _calculate_category_stats(self, entries: List) -> List[CategoryStats]:
        """Calculate statistics by category (same logic as before)"""
        category_data = defaultdict(list)
        
        # Only use regular analyses for category stats
        regular_entries = [entry for entry in entries if not entry.is_comparison_analysis]
        
        for entry in regular_entries:
            if entry.analysis.product_info.category:
                category_data[entry.analysis.product_info.category].append(entry)
        
        category_stats = []
        for category, category_entries in category_data.items():
            scores = [entry.analysis.eco_score for entry in category_entries]
            
            # Calculate trend (recent vs older)
            trend = 0.0
            if len(scores) >= 2:
                mid_point = len(scores) // 2
                recent_avg = statistics.mean(scores[:mid_point])
                older_avg = statistics.mean(scores[mid_point:])
                trend = recent_avg - older_avg
            
            category_stats.append(CategoryStats(
                category=category,
                count=len(category_entries),
                average_score=statistics.mean(scores),
                best_score=max(scores),
                worst_score=min(scores),
                trend=trend
            ))
        
        return sorted(category_stats, key=lambda x: x.average_score, reverse=True)
    
    def _generate_timeline(self, entries: List, comparisons: List) -> List[TimelineEntry]:
        """Generate timeline entries for visualization (same logic as before)"""
        timeline = []
        # Only include regular analyses in timeline
        regular_entries = [entry for entry in entries if not entry.is_comparison_analysis]

        for entry in regular_entries:
            timeline.append(TimelineEntry(
                date=entry.timestamp,
                eco_score=entry.analysis.eco_score,
                product_name=entry.analysis.product_info.name,
                category=entry.analysis.product_info.category,
                analysis_type=entry.analysis_type
            ))
        
        # Add comparison entries to timeline
        for comparison in comparisons:
            product_names = [product.product_info.name for product in comparison.products]
            avg_score = sum(product.eco_score for product in comparison.products) / len(comparison.products)
            timeline.append(TimelineEntry(
                date=comparison.timestamp,
                eco_score=int(avg_score),
                product_name=f"Compared {', '.join(product_names[:2])}{'...' if len(product_names) > 2 else ''}",
                category=None,
                analysis_type=AnalysisType.COMPARISON
            ))
        
        # Sort by date
        timeline.sort(key=lambda x: x.date)
        return timeline

# Create global instance
database_history_service = DatabaseHistoryService()
