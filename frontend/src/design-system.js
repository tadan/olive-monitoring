/**
 * Design System JavaScript Constants
 * Maps CSS custom properties to JavaScript for use in components
 */

/**
 * Get a CSS custom property value from the root element
 * @param {string} propertyName - CSS custom property name (with or without --)
 * @returns {string} The computed value
 */
export function getCSSVar(propertyName) {
  const name = propertyName.startsWith('--') ? propertyName : `--${propertyName}`;
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

/**
 * Health status color mapping
 * Maps health scores to semantic color tokens
 */
export const HealthColors = {
  excellent: 'var(--color-health-excellent)',  // >= 70
  good: 'var(--color-health-good)',            // >= 50
  warning: 'var(--color-health-warning)',      // >= 30
  poor: 'var(--color-health-poor)',            // >= 15
  critical: 'var(--color-health-critical)',    // < 15
  noData: 'var(--color-health-nodata)',        // No data available
};

/**
 * Get health color based on score
 * @param {number} score - Health score (0-100)
 * @returns {string} CSS color value or CSS variable
 */
export function getHealthColor(score) {
  if (!score || score === 0) return HealthColors.noData;
  if (score >= 70) return HealthColors.excellent;
  if (score >= 50) return HealthColors.good;
  if (score >= 30) return HealthColors.warning;
  if (score >= 15) return HealthColors.poor;
  return HealthColors.critical;
}

/**
 * Get health border color (darker version for map zones)
 * @param {number} score - Health score (0-100)
 * @returns {string} CSS color value
 */
export function getHealthBorderColor(score) {
  // Use olive tones for borders
  if (!score || score === 0) return 'var(--color-stone-500)';
  if (score >= 70) return 'var(--color-olive-800)';
  if (score >= 50) return 'var(--color-olive-700)';
  if (score >= 30) return 'oklch(0.58 0.13 50)'; // Darker terracotta
  if (score >= 15) return 'oklch(0.50 0.15 40)'; // Darker clay
  return 'oklch(0.40 0.16 25)'; // Darker rust
}

/**
 * Alert severity color mapping
 */
export const AlertColors = {
  critical: 'var(--color-error)',
  high: 'var(--color-health-poor)',
  medium: 'var(--color-warning)',
  warning: 'var(--color-warning)',
  low: 'var(--color-info)',
  info: 'var(--color-info)',
};

/**
 * Get alert severity color
 * @param {string} severity - Alert severity level
 * @returns {string} CSS color value
 */
export function getAlertColor(severity) {
  const normalized = severity.toLowerCase();
  return AlertColors[normalized] || AlertColors.info;
}

/**
 * Data visualization colors for charts
 */
export const ChartColors = {
  // Vegetation indices
  ndvi: 'var(--color-data-ndvi)',
  ndmi: 'var(--color-data-ndmi)',
  arvi: 'var(--color-data-arvi)',
  osavi: 'var(--color-data-osavi)',
  health: 'var(--color-data-health)',

  // Trend colors
  improving: 'var(--color-health-excellent)',
  stable: 'var(--color-warning)',
  declining: 'var(--color-error)',
  baseline: 'var(--color-info)',
};

/**
 * Get resolved color value from CSS variable
 * Useful when you need the actual hex/rgb value (e.g., for Chart.js)
 * @param {string} cssVar - CSS variable (e.g., 'var(--color-olive-600)')
 * @returns {string} Resolved color value
 */
export function resolveColor(cssVar) {
  if (!cssVar.startsWith('var(')) {
    return cssVar; // Already a color value
  }

  // Extract variable name from var() function
  const varName = cssVar.match(/var\((--[^)]+)\)/)?.[1];
  if (!varName) return cssVar;

  // Create temporary element to get computed color
  const tempEl = document.createElement('div');
  tempEl.style.color = cssVar;
  document.body.appendChild(tempEl);
  const color = getComputedStyle(tempEl).color;
  document.body.removeChild(tempEl);

  return color;
}

/**
 * Convert color to rgba with opacity
 * @param {string} color - Color value (CSS variable or color)
 * @param {number} opacity - Opacity (0-1)
 * @returns {string} rgba color string
 */
export function colorWithOpacity(color, opacity) {
  const resolved = resolveColor(color);

  // If already in OKLCH format, add alpha
  if (resolved.startsWith('oklch(')) {
    return resolved.replace(')', ` / ${opacity})`);
  }

  // For rgb/rgba, extract values and set alpha
  if (resolved.startsWith('rgb')) {
    const values = resolved.match(/\d+\.?\d*/g);
    if (values && values.length >= 3) {
      return `rgba(${values[0]}, ${values[1]}, ${values[2]}, ${opacity})`;
    }
  }

  return resolved; // Return as-is if can't parse
}
