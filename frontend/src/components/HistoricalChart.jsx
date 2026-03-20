/**
 * Historical comparison chart showing year-over-year health trends
 */
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './HistoricalChart.css';

// Design System Colors (Chart.js needs hex values, not CSS vars)
const CHART_COLORS = {
  success: '#2da44e',
  successBorder: '#2da44e',
  warning: 'rgba(191, 135, 0, 0.7)',
  warningBorder: '#bf8700',
  danger: 'rgba(207, 34, 46, 0.7)',
  dangerBorder: '#cf222e',
  info: 'rgba(9, 105, 218, 0.7)',
  infoBorder: '#0969da',
  neutral: 'rgba(173, 181, 189, 0.3)',
  neutralBorder: 'rgba(173, 181, 189, 0.5)',
};

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const HistoricalChart = ({ historyData }) => {
  if (!historyData || !historyData.history || historyData.history.length === 0) {
    return (
      <div className='historical-chart-placeholder'>
        <p>No historical data available</p>
        <p className='placeholder-detail'>
          Historical data for mid-September will appear here once satellite
          imagery is processed
        </p>
      </div>
    );
  }

  const { history, zone_name, period, year_range } = historyData;

  // Filter out entries without data
  const dataWithValues = history.filter((h) => h.has_data);

  if (dataWithValues.length === 0) {
    return (
      <div className='historical-chart-placeholder'>
        <p>No historical data available for {zone_name}</p>
        <p className='placeholder-detail'>
          Target period: {period} ({year_range})
        </p>
      </div>
    );
  }

  const chartData = {
    labels: history.map((h) => h.year.toString()),
    datasets: [
      {
        label: 'Health Score',
        data: history.map((h) => (h.has_data ? h.health_score : null)),
        backgroundColor: history.map((h) => {
          if (!h.has_data) return CHART_COLORS.neutral;
          if (h.trend === 'improving') return CHART_COLORS.success;
          if (h.trend === 'declining') return CHART_COLORS.danger;
          if (h.trend === 'stable') return CHART_COLORS.warning;
          return CHART_COLORS.info; // baseline
        }),
        borderColor: history.map((h) => {
          if (!h.has_data) return CHART_COLORS.neutralBorder;
          if (h.trend === 'improving') return CHART_COLORS.successBorder;
          if (h.trend === 'declining') return CHART_COLORS.dangerBorder;
          if (h.trend === 'stable') return CHART_COLORS.warningBorder;
          return CHART_COLORS.infoBorder;
        }),
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: `Historical Trends for ${zone_name}`,
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      subtitle: {
        display: true,
        text: `Mid-September Analysis (${period})`,
        font: {
          size: 12,
        },
        padding: {
          bottom: 10,
        },
      },
      tooltip: {
        callbacks: {
          title: function (context) {
            const dataPoint = history[context[0].dataIndex];
            return `${dataPoint.year} ${dataPoint.trend_icon}`;
          },
          label: function (context) {
            const dataPoint = history[context.dataIndex];
            if (!dataPoint.has_data) {
              return 'No data available';
            }
            return [
              `Health Score: ${dataPoint.health_score}/100`,
              `NDVI: ${dataPoint.ndvi_mean.toFixed(3)}`,
              `NDMI: ${dataPoint.ndmi_mean.toFixed(3)}`,
              `Date: ${new Date(dataPoint.date).toLocaleDateString()}`,
              `Trend: ${dataPoint.trend}`,
            ];
          },
        },
      },
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'Health Score',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Year',
        },
      },
    },
  };

  return (
    <div className='historical-chart-container' role="img" aria-label={`Year-over-year health analysis for ${zone_name} from ${year_range}`}>
      <Bar data={chartData} options={options} />
      <div className='historical-legend' role="list" aria-label="Trend indicators">
        <div className='legend-item'>
          <span className='legend-icon improving'>↗️</span>
          <span>Improving (+5 or more)</span>
        </div>
        <div className='legend-item'>
          <span className='legend-icon stable'>➡️</span>
          <span>Stable (-5 to +5)</span>
        </div>
        <div className='legend-item'>
          <span className='legend-icon declining'>↘️</span>
          <span>Declining (-5 or less)</span>
        </div>
        <div className='legend-item'>
          <span className='legend-icon baseline'>⏺️</span>
          <span>Baseline (first year)</span>
        </div>
      </div>
    </div>
  );
};

export default HistoricalChart;
