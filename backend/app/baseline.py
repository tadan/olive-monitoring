"""Baseline statistics calculation for seasonal patterns and anomaly detection."""
import logging
from datetime import date, datetime
from typing import Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import BaselineStatistic, FieldZone, HealthIndex

logger = logging.getLogger(__name__)


class BaselineManager:
    """Manages seasonal baseline statistics for vegetation indices."""

    # Season definitions (Northern Hemisphere)
    SEASONS = {
        'winter': [12, 1, 2],
        'spring': [3, 4, 5],
        'summer': [6, 7, 8],
        'fall': [9, 10, 11]
    }

    # Minimum samples needed for reliable baseline
    MIN_SAMPLES = 3

    def __init__(self, db: Session):
        """
        Initialize baseline manager.

        Args:
            db: Database session
        """
        self.db = db

    @staticmethod
    def get_season(date_obj: date) -> str:
        """
        Determine season from date.

        Args:
            date_obj: Date to check

        Returns:
            Season name ('spring', 'summer', 'fall', 'winter')
        """
        month = date_obj.month

        for season, months in BaselineManager.SEASONS.items():
            if month in months:
                return season

        # Should never reach here, but default to season by month
        return 'spring'

    def calculate_baseline(
        self,
        zone_id: int,
        metric: str,
        season: Optional[str] = None,
        years_back: int = 3
    ) -> Optional[BaselineStatistic]:
        """
        Calculate baseline statistics for a zone and metric.

        Args:
            zone_id: Field zone ID
            metric: Metric name ('ndvi' or 'ndmi')
            season: Specific season ('spring', 'summer', 'fall', 'winter'), or None for all
            years_back: How many years of data to include

        Returns:
            BaselineStatistic object, or None if insufficient data
        """
        # Validate metric
        if metric not in ['ndvi', 'ndmi']:
            logger.error(f"Invalid metric: {metric}")
            return None

        # Query health indices for this zone
        query = self.db.query(HealthIndex).filter(HealthIndex.zone_id == zone_id)

        # Filter by season if specified
        if season:
            # Get months for this season
            months = self.SEASONS.get(season, [])
            if not months:
                logger.error(f"Invalid season: {season}")
                return None

            # Filter by month
            query = query.filter(
                func.extract('month', HealthIndex.acquisition_date).in_(months)
            )

        # Get only recent data (last N years)
        cutoff_date = datetime.now().date().replace(year=datetime.now().year - years_back)
        query = query.filter(HealthIndex.acquisition_date >= cutoff_date)

        # Execute query
        health_indices = query.all()

        if len(health_indices) < self.MIN_SAMPLES:
            logger.warning(
                f"Zone {zone_id}, {metric}, {season or 'all seasons'}: "
                f"Insufficient data ({len(health_indices)} samples, need {self.MIN_SAMPLES})"
            )
            return None

        # Extract metric values
        metric_field = f"{metric}_mean"
        values = [getattr(hi, metric_field) for hi in health_indices if getattr(hi, metric_field) is not None]

        if len(values) < self.MIN_SAMPLES:
            logger.warning(
                f"Zone {zone_id}, {metric}, {season or 'all seasons'}: "
                f"Insufficient valid values ({len(values)} values)"
            )
            return None

        # Calculate statistics
        import numpy as np
        mean_value = float(np.mean(values))
        std_dev = float(np.std(values))
        min_value = float(np.min(values))
        max_value = float(np.max(values))

        logger.info(
            f"Zone {zone_id}, {metric}, {season or 'all seasons'}: "
            f"Baseline calculated from {len(values)} samples - "
            f"mean: {mean_value:.3f}, std: {std_dev:.3f}"
        )

        # Check if baseline already exists
        existing = (
            self.db.query(BaselineStatistic)
            .filter(
                BaselineStatistic.zone_id == zone_id,
                BaselineStatistic.metric == metric,
                BaselineStatistic.season == season
            )
            .first()
        )

        if existing:
            # Update existing baseline
            existing.mean_value = mean_value
            existing.std_dev = std_dev
            existing.min_value = min_value
            existing.max_value = max_value
            existing.sample_count = len(values)
            existing.last_updated = datetime.now()
            baseline = existing
        else:
            # Create new baseline
            baseline = BaselineStatistic(
                zone_id=zone_id,
                metric=metric,
                season=season,
                mean_value=mean_value,
                std_dev=std_dev,
                min_value=min_value,
                max_value=max_value,
                sample_count=len(values)
            )
            self.db.add(baseline)

        self.db.commit()
        self.db.refresh(baseline)

        return baseline

    def update_all_baselines(self, zone_id: int) -> int:
        """
        Update all baselines (both metrics, all seasons + overall) for a zone.

        Args:
            zone_id: Field zone ID

        Returns:
            Number of baselines successfully calculated
        """
        count = 0
        metrics = ['ndvi', 'ndmi']

        for metric in metrics:
            # Overall baseline (all seasons)
            baseline = self.calculate_baseline(zone_id, metric, season=None)
            if baseline:
                count += 1

            # Seasonal baselines
            for season in self.SEASONS.keys():
                baseline = self.calculate_baseline(zone_id, metric, season=season)
                if baseline:
                    count += 1

        logger.info(f"Zone {zone_id}: Updated {count} baselines")
        return count

    def get_baseline(
        self,
        zone_id: int,
        metric: str,
        date_obj: date
    ) -> Optional[BaselineStatistic]:
        """
        Get the appropriate baseline for a zone, metric, and date.

        Prefers seasonal baseline, falls back to overall baseline if not available.

        Args:
            zone_id: Field zone ID
            metric: Metric name ('ndvi' or 'ndmi')
            date_obj: Date to determine season

        Returns:
            BaselineStatistic object, or None if not found
        """
        season = self.get_season(date_obj)

        # Try seasonal baseline first
        baseline = (
            self.db.query(BaselineStatistic)
            .filter(
                BaselineStatistic.zone_id == zone_id,
                BaselineStatistic.metric == metric,
                BaselineStatistic.season == season
            )
            .first()
        )

        if baseline:
            return baseline

        # Fall back to overall baseline
        baseline = (
            self.db.query(BaselineStatistic)
            .filter(
                BaselineStatistic.zone_id == zone_id,
                BaselineStatistic.metric == metric,
                BaselineStatistic.season.is_(None)
            )
            .first()
        )

        return baseline

    def is_anomaly(
        self,
        zone_id: int,
        metric: str,
        value: float,
        date_obj: date,
        std_dev_threshold: float = 2.0
    ) -> Tuple[bool, Optional[BaselineStatistic]]:
        """
        Check if a value is anomalous compared to baseline.

        Args:
            zone_id: Field zone ID
            metric: Metric name ('ndvi' or 'ndmi')
            value: Value to check
            date_obj: Date for seasonal baseline selection
            std_dev_threshold: Number of standard deviations for anomaly (default: 2.0)

        Returns:
            Tuple of (is_anomaly, baseline_used)
        """
        baseline = self.get_baseline(zone_id, metric, date_obj)

        if baseline is None:
            logger.debug(
                f"Zone {zone_id}, {metric}: No baseline available for anomaly detection"
            )
            return False, None

        # Calculate deviation from baseline
        deviation = abs(value - baseline.mean_value)
        threshold = std_dev_threshold * baseline.std_dev

        is_anomalous = deviation > threshold

        if is_anomalous:
            logger.warning(
                f"Zone {zone_id}, {metric}: Anomaly detected - "
                f"value: {value:.3f}, baseline: {baseline.mean_value:.3f}, "
                f"deviation: {deviation:.3f} (threshold: {threshold:.3f})"
            )

        return is_anomalous, baseline

    def get_zone_baseline_summary(self, zone_id: int) -> dict:
        """
        Get a summary of all baselines for a zone.

        Args:
            zone_id: Field zone ID

        Returns:
            Dictionary with baseline summary
        """
        zone = self.db.query(FieldZone).filter(FieldZone.id == zone_id).first()
        if not zone:
            return {'error': 'Zone not found'}

        baselines = (
            self.db.query(BaselineStatistic)
            .filter(BaselineStatistic.zone_id == zone_id)
            .all()
        )

        summary = {
            'zone_id': zone_id,
            'zone_name': zone.name,
            'baselines': []
        }

        for baseline in baselines:
            summary['baselines'].append({
                'metric': baseline.metric,
                'season': baseline.season or 'all',
                'mean': float(baseline.mean_value),
                'std_dev': float(baseline.std_dev),
                'min': float(baseline.min_value),
                'max': float(baseline.max_value),
                'sample_count': baseline.sample_count,
                'last_updated': baseline.last_updated.isoformat() if baseline.last_updated else None
            })

        return summary


def update_baselines_for_all_zones(db: Session) -> int:
    """
    Convenience function to update baselines for all zones.

    Args:
        db: Database session

    Returns:
        Total number of baselines calculated
    """
    manager = BaselineManager(db)
    zones = db.query(FieldZone).all()

    total_count = 0
    for zone in zones:
        count = manager.update_all_baselines(zone.id)
        total_count += count

    logger.info(f"Updated {total_count} baselines across {len(zones)} zones")
    return total_count


def check_anomaly(
    db: Session,
    zone_id: int,
    metric: str,
    value: float,
    date_obj: date
) -> bool:
    """
    Convenience function to check if a value is anomalous.

    Args:
        db: Database session
        zone_id: Field zone ID
        metric: Metric name ('ndvi' or 'ndmi')
        value: Value to check
        date_obj: Date for seasonal baseline

    Returns:
        True if anomalous, False otherwise
    """
    manager = BaselineManager(db)
    is_anomalous, _ = manager.is_anomaly(zone_id, metric, value, date_obj)
    return is_anomalous
