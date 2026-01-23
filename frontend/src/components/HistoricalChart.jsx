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
import { ChartColors, colorWithOpacity, resolveColor } from '../design-system';
import './HistoricalChart.css';

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
          if (!h.has_data) return colorWithOpacity('var(--color-stone-400)', 0.3);
          if (h.trend === 'improving') return colorWithOpacity(ChartColors.improving, 0.7);
          if (h.trend === 'declining') return colorWithOpacity(ChartColors.declining, 0.7);
          if (h.trend === 'stable') return colorWithOpacity(ChartColors.stable, 0.7);
          return colorWithOpacity(ChartColors.baseline, 0.7);
        }),
        borderColor: history.map((h) => {
          if (!h.has_data) return colorWithOpacity('var(--color-stone-400)', 0.5);
          if (h.trend === 'improving') return resolveColor(ChartColors.improving);
          if (h.trend === 'declining') return resolveColor(ChartColors.declining);
          if (h.trend === 'stable') return resolveColor(ChartColors.stable);
          return resolveColor(ChartColors.baseline);
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
    <div className='historical-chart-container'>
      <Bar data={chartData} options={options} />
      <div className='historical-legend'>
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
