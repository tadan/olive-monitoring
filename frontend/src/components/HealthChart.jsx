/**
 * Time-series chart showing olive grove health metrics
 */
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { format } from 'date-fns';
import './HealthChart.css';

// Design System Colors (Chart.js needs hex values, not CSS vars)
const CHART_COLORS = {
  success: '#2da44e',
  successBg: 'rgba(45, 164, 78, 0.1)',
  data: '#0969da',
  dataBg: 'rgba(9, 105, 218, 0.1)',
  warning: '#bf8700',
  warningBg: 'rgba(191, 135, 0, 0.1)',
  danger: '#cf222e',
  dangerBg: 'rgba(207, 34, 46, 0.1)',
  info: '#8b5cf6',
  infoBg: 'rgba(139, 92, 246, 0.1)',
};

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const HealthChart = ({ healthData }) => {
  if (!healthData || healthData.length === 0) {
    return (
      <div className="health-chart-placeholder" role="status" aria-live="polite">
        <p>No health data available</p>
      </div>
    );
  }

  // Sort by date ascending
  const sortedData = [...healthData].sort((a, b) =>
    new Date(a.date) - new Date(b.date)
  );

  const chartData = {
    labels: sortedData.map(d => format(new Date(d.date), 'MMM dd')),
    datasets: [
      {
        label: 'Health Score',
        data: sortedData.map(d => d.health_score),
        borderColor: CHART_COLORS.success,
        backgroundColor: CHART_COLORS.successBg,
        fill: true,
        tension: 0.3,
        yAxisID: 'y',
      },
      {
        label: 'NDVI',
        data: sortedData.map(d => d.ndvi_mean * 100), // Scale NDVI to 0-100
        borderColor: CHART_COLORS.data,
        backgroundColor: CHART_COLORS.dataBg,
        fill: true,
        tension: 0.3,
        yAxisID: 'y',
      },
      {
        label: 'ARVI',
        data: sortedData.map(d => d.arvi_mean ? d.arvi_mean * 100 : null),
        borderColor: CHART_COLORS.warning,
        backgroundColor: CHART_COLORS.warningBg,
        fill: true,
        tension: 0.3,
        yAxisID: 'y',
        spanGaps: true,
      },
      {
        label: 'OSAVI',
        data: sortedData.map(d => d.osavi_mean ? d.osavi_mean * 100 : null),
        borderColor: CHART_COLORS.danger,
        backgroundColor: CHART_COLORS.dangerBg,
        fill: true,
        tension: 0.3,
        yAxisID: 'y',
        spanGaps: true,
      },
      {
        label: 'NDMI',
        data: sortedData.map(d => d.ndmi_mean * 100), // Scale NDMI to 0-100
        borderColor: CHART_COLORS.info,
        backgroundColor: CHART_COLORS.infoBg,
        fill: true,
        tension: 0.3,
        yAxisID: 'y',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Olive Grove Health Trends',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.dataset.label === 'Health Score') {
              label += context.parsed.y + '/100';
            } else {
              label += (context.parsed.y / 100).toFixed(3); // Show original scale
            }
            return label;
          },
        },
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'Value (0-100)',
        },
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
  };

  return (
    <div className="health-chart-container" role="img" aria-label="Time series chart showing olive grove health metrics over the past 30 days">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default HealthChart;
