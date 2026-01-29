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
import { ChartColors, colorWithOpacity, resolveColor } from '../design-system';
import './HealthChart.css';

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
      <div className="health-chart-placeholder">
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
        borderColor: resolveColor(ChartColors.health),
        backgroundColor: colorWithOpacity(ChartColors.health, 0.1),
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: 'NDVI',
        data: sortedData.map(d => d.ndvi_mean * 100), // Scale NDVI to 0-100
        borderColor: resolveColor(ChartColors.ndvi),
        backgroundColor: colorWithOpacity(ChartColors.ndvi, 0.1),
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: 'ARVI',
        data: sortedData.map(d => d.arvi_mean ? d.arvi_mean * 100 : null), // Scale ARVI to 0-100
        borderColor: resolveColor(ChartColors.arvi),
        backgroundColor: colorWithOpacity(ChartColors.arvi, 0.1),
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
        spanGaps: true, // Connect line across null values
      },
      {
        label: 'OSAVI',
        data: sortedData.map(d => d.osavi_mean ? d.osavi_mean * 100 : null), // Scale OSAVI to 0-100
        borderColor: resolveColor(ChartColors.osavi),
        backgroundColor: colorWithOpacity(ChartColors.osavi, 0.1),
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
        spanGaps: true, // Connect line across null values
      },
      {
        label: 'NDMI',
        data: sortedData.map(d => d.ndmi_mean * 100), // Scale NDMI to 0-100
        borderColor: resolveColor(ChartColors.ndmi),
        backgroundColor: colorWithOpacity(ChartColors.ndmi, 0.1),
        fill: true,
        tension: 0.4,
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
    <div className="health-chart-container">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default HealthChart;
