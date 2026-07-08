"""Alert detection and notification system for vegetation health anomalies."""
import asyncio
import logging
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

import aiosmtplib
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Alert, FieldZone, HealthIndex

logger = logging.getLogger(__name__)


class AlertDetector:
    """Detects vegetation health anomalies and generates alerts."""

    # Alert thresholds
    NDVI_DROP_THRESHOLD = -0.15  # 15% drop in NDVI
    DROUGHT_STRESS_THRESHOLD = -0.2  # NDMI below -0.2
    WATERLOG_THRESHOLD = 0.5  # NDMI above 0.5
    HEALTH_SCORE_CRITICAL = 40  # Health score below 40
    HEALTH_SCORE_WARNING = 60  # Health score below 60

    def __init__(self, db: Session):
        """
        Initialize alert detector.

        Args:
            db: Database session
        """
        self.db = db

    def get_previous_health_index(
        self,
        zone_id: int,
        current_date: datetime,
        days_back: int = 30
    ) -> Optional[HealthIndex]:
        """
        Get the most recent health index before a given date.

        Args:
            zone_id: Field zone ID
            current_date: Current date
            days_back: How many days to look back

        Returns:
            Previous HealthIndex record, or None if not found
        """
        cutoff_date = current_date - timedelta(days=days_back)

        return (
            self.db.query(HealthIndex)
            .filter(
                HealthIndex.zone_id == zone_id,
                HealthIndex.acquisition_date < current_date,
                HealthIndex.acquisition_date >= cutoff_date
            )
            .order_by(HealthIndex.acquisition_date.desc())
            .first()
        )

    def detect_ndvi_drop(
        self,
        zone_id: int,
        current_health: HealthIndex
    ) -> Optional[Alert]:
        """
        Detect sudden drop in NDVI (vegetation loss).

        Args:
            zone_id: Field zone ID
            current_health: Current health index

        Returns:
            Alert if NDVI drop detected, None otherwise
        """
        # Get previous measurement
        previous = self.get_previous_health_index(
            zone_id,
            current_health.acquisition_date,
            days_back=30
        )

        if previous is None:
            logger.debug(f"Zone {zone_id}: No baseline for NDVI drop detection")
            return None

        # Calculate NDVI change
        ndvi_change = current_health.ndvi_mean - previous.ndvi_mean

        if ndvi_change <= self.NDVI_DROP_THRESHOLD:
            severity = 'critical' if ndvi_change <= -0.25 else 'warning'

            alert = Alert(
                zone_id=zone_id,
                alert_type='ndvi_drop',
                severity=severity,
                title=f"Vegetation Loss Detected in {self._get_zone_name(zone_id)}",
                description=(
                    f"NDVI dropped by {abs(ndvi_change):.3f} "
                    f"(from {previous.ndvi_mean:.3f} to {current_health.ndvi_mean:.3f}). "
                    f"This may indicate vegetation stress, disease, or physical damage."
                ),
                metric='ndvi',
                metric_value=current_health.ndvi_mean,
                threshold_value=previous.ndvi_mean + self.NDVI_DROP_THRESHOLD,
                status='active'
            )

            logger.warning(
                f"Zone {zone_id}: NDVI drop alert ({severity}) - "
                f"change: {ndvi_change:.3f}"
            )

            return alert

        return None

    def detect_drought_stress(
        self,
        zone_id: int,
        current_health: HealthIndex
    ) -> Optional[Alert]:
        """
        Detect drought stress based on NDMI.

        Args:
            zone_id: Field zone ID
            current_health: Current health index

        Returns:
            Alert if drought stress detected, None otherwise
        """
        if current_health.ndmi_mean <= self.DROUGHT_STRESS_THRESHOLD:
            # Determine severity based on how low NDMI is
            if current_health.ndmi_mean <= -0.4:
                severity = 'critical'
                description = (
                    f"Severe drought stress detected (NDMI: {current_health.ndmi_mean:.3f}). "
                    f"Immediate irrigation recommended to prevent permanent damage."
                )
            elif current_health.ndmi_mean <= -0.3:
                severity = 'critical'
                description = (
                    f"Critical drought stress (NDMI: {current_health.ndmi_mean:.3f}). "
                    f"Trees are experiencing severe water deficit. Irrigation needed."
                )
            else:
                severity = 'warning'
                description = (
                    f"Moderate drought stress (NDMI: {current_health.ndmi_mean:.3f}). "
                    f"Monitor closely and consider irrigation if conditions persist."
                )

            alert = Alert(
                zone_id=zone_id,
                alert_type='drought_stress',
                severity=severity,
                title=f"Drought Stress in {self._get_zone_name(zone_id)}",
                description=description,
                metric='ndmi',
                metric_value=current_health.ndmi_mean,
                threshold_value=self.DROUGHT_STRESS_THRESHOLD,
                status='active'
            )

            logger.warning(
                f"Zone {zone_id}: Drought stress alert ({severity}) - "
                f"NDMI: {current_health.ndmi_mean:.3f}"
            )

            return alert

        return None

    def detect_waterlogging(
        self,
        zone_id: int,
        current_health: HealthIndex
    ) -> Optional[Alert]:
        """
        Detect waterlogging based on NDMI.

        Args:
            zone_id: Field zone ID
            current_health: Current health index

        Returns:
            Alert if waterlogging detected, None otherwise
        """
        if current_health.ndmi_mean >= self.WATERLOG_THRESHOLD:
            severity = 'warning' if current_health.ndmi_mean < 0.6 else 'critical'

            alert = Alert(
                zone_id=zone_id,
                alert_type='waterlogging',
                severity=severity,
                title=f"Waterlogging Risk in {self._get_zone_name(zone_id)}",
                description=(
                    f"High moisture content detected (NDMI: {current_health.ndmi_mean:.3f}). "
                    f"Olive trees are susceptible to root rot in waterlogged conditions. "
                    f"Check drainage and reduce irrigation if applicable."
                ),
                metric='ndmi',
                metric_value=current_health.ndmi_mean,
                threshold_value=self.WATERLOG_THRESHOLD,
                status='active'
            )

            logger.warning(
                f"Zone {zone_id}: Waterlogging alert ({severity}) - "
                f"NDMI: {current_health.ndmi_mean:.3f}"
            )

            return alert

        return None

    def detect_health_score_alert(
        self,
        zone_id: int,
        current_health: HealthIndex
    ) -> Optional[Alert]:
        """
        Detect low overall health score.

        Args:
            zone_id: Field zone ID
            current_health: Current health index

        Returns:
            Alert if health score is concerning, None otherwise
        """
        score = current_health.vegetation_health_score

        if score < self.HEALTH_SCORE_CRITICAL:
            severity = 'critical'
            title = f"Critical Health Score in {self._get_zone_name(zone_id)}"
            description = (
                f"Overall health score is critically low ({score}/100). "
                f"NDVI: {current_health.ndvi_mean:.3f}, NDMI: {current_health.ndmi_mean:.3f}. "
                f"Immediate investigation and intervention recommended."
            )
        elif score < self.HEALTH_SCORE_WARNING:
            severity = 'warning'
            title = f"Low Health Score in {self._get_zone_name(zone_id)}"
            description = (
                f"Health score below normal ({score}/100). "
                f"NDVI: {current_health.ndvi_mean:.3f}, NDMI: {current_health.ndmi_mean:.3f}. "
                f"Monitor closely and address any visible issues."
            )
        else:
            return None

        alert = Alert(
            zone_id=zone_id,
            alert_type='health_score',
            severity=severity,
            title=title,
            description=description,
            metric='health_score',
            metric_value=score,
            threshold_value=self.HEALTH_SCORE_WARNING,
            status='active'
        )

        logger.warning(
            f"Zone {zone_id}: Health score alert ({severity}) - "
            f"score: {score}/100"
        )

        return alert

    def check_all_alerts(
        self,
        zone_id: int,
        health_index: HealthIndex
    ) -> List[Alert]:
        """
        Run all alert detections for a health index.

        Args:
            zone_id: Field zone ID
            health_index: Current health index

        Returns:
            List of detected alerts
        """
        alerts = []

        # Check for NDVI drop
        alert = self.detect_ndvi_drop(zone_id, health_index)
        if alert:
            alerts.append(alert)

        # Check for drought stress
        alert = self.detect_drought_stress(zone_id, health_index)
        if alert:
            alerts.append(alert)

        # Check for waterlogging
        alert = self.detect_waterlogging(zone_id, health_index)
        if alert:
            alerts.append(alert)

        # Check overall health score
        alert = self.detect_health_score_alert(zone_id, health_index)
        if alert:
            alerts.append(alert)

        # Save alerts to database
        for alert in alerts:
            self.db.add(alert)

        if alerts:
            self.db.commit()
            logger.info(f"Zone {zone_id}: Generated {len(alerts)} alerts")

        return alerts

    def _get_zone_name(self, zone_id: int) -> str:
        """Get zone name for alert messages."""
        zone = self.db.query(FieldZone).filter(FieldZone.id == zone_id).first()
        return zone.name if zone else f"Zone {zone_id}"


class AlertNotifier:
    """Handles email notifications for alerts."""

    def __init__(self):
        """Initialize email notifier with settings."""
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.alert_email = settings.alert_email

    async def send_email(
        self,
        subject: str,
        body_html: str,
        recipient: Optional[str] = None
    ) -> bool:
        """
        Send email notification.

        Args:
            subject: Email subject
            body_html: HTML body content
            recipient: Recipient email (defaults to settings.alert_email)

        Returns:
            True if email sent successfully, False otherwise
        """
        if not all([self.smtp_username, self.smtp_password, self.alert_email]):
            logger.warning("Email credentials not configured, skipping notification")
            return False

        recipient = recipient or self.alert_email

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.smtp_username
            message['To'] = recipient

            # Attach HTML body
            html_part = MIMEText(body_html, 'html')
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=True
            )

            logger.info(f"Email sent to {recipient}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False

    async def notify_alerts(self, alerts: List[Alert], db: Session) -> int:
        """
        Send email notification for a list of alerts.

        Args:
            alerts: List of Alert objects
            db: Database session for querying zone info

        Returns:
            Number of emails sent successfully
        """
        if not alerts:
            return 0

        # Group alerts by severity
        critical = [a for a in alerts if a.severity == 'critical']
        warnings = [a for a in alerts if a.severity == 'warning']

        # Build email subject
        if critical:
            subject = f"🚨 Critical Alert: Olive Grove Health Issues ({len(alerts)} total)"
        else:
            subject = f"⚠️ Warning: Olive Grove Health Monitoring ({len(alerts)} alerts)"

        # Build HTML body
        body_html = self._build_alert_email(critical, warnings, db)

        # Send email
        success = await self.send_email(subject, body_html)
        return 1 if success else 0

    def _build_alert_email(
        self,
        critical: List[Alert],
        warnings: List[Alert],
        db: Session
    ) -> str:
        """Build HTML email body for alerts."""
        html_parts = [
            '<html><body>',
            '<h2>Olive Grove Health Monitoring - Alert Summary</h2>',
            f'<p><strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>',
            '<p>Automated analysis of Sentinel-2 satellite imagery has detected the following issues:</p>'
        ]

        # Critical alerts
        if critical:
            html_parts.append('<h3 style="color: #d32f2f;">🚨 Critical Alerts</h3>')
            html_parts.append('<ul>')
            for alert in critical:
                html_parts.append(
                    f'<li><strong>{alert.title}</strong><br>'
                    f'{alert.description}<br>'
                    f'<small>Zone ID: {alert.zone_id} | Detected: {alert.detected_at.strftime("%Y-%m-%d %H:%M")}</small></li>'
                )
            html_parts.append('</ul>')

        # Warnings
        if warnings:
            html_parts.append('<h3 style="color: #f57c00;">⚠️ Warnings</h3>')
            html_parts.append('<ul>')
            for alert in warnings:
                html_parts.append(
                    f'<li><strong>{alert.title}</strong><br>'
                    f'{alert.description}<br>'
                    f'<small>Zone ID: {alert.zone_id} | Detected: {alert.detected_at.strftime("%Y-%m-%d %H:%M")}</small></li>'
                )
            html_parts.append('</ul>')

        html_parts.extend([
            '<hr>',
            '<p><small>This is an automated alert from the Tatasciore Olive Farm Monitoring System. '
            'For more details, please check the monitoring dashboard.</small></p>',
            '</body></html>'
        ])

        return ''.join(html_parts)


def detect_and_notify_alerts(
    db: Session,
    zone_id: int,
    health_index: HealthIndex,
    send_notifications: bool = True
) -> List[Alert]:
    """
    Convenience function to detect alerts and optionally send notifications.

    Args:
        db: Database session
        zone_id: Field zone ID
        health_index: Health index to analyze
        send_notifications: Whether to send email notifications

    Returns:
        List of detected alerts
    """
    # Detect alerts
    detector = AlertDetector(db)
    alerts = detector.check_all_alerts(zone_id, health_index)

    # Send notifications if enabled
    if send_notifications and alerts:
        notifier = AlertNotifier()
        asyncio.run(notifier.notify_alerts(alerts, db))

    return alerts
