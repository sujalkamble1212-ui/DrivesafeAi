import React from 'react';
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  PointElement, LineElement, Title, Tooltip, Legend, Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export const AttentionChart = ({ chartData = [] }) => {
  const labels        = chartData.map(d => d.time);
  const safetyScores  = chartData.map(d => d.safety);
  const attentionScores = chartData.map(d => d.attention);

  const data = {
    labels: labels.length ? labels : ['00:00','00:05','00:10','00:15','00:20'],
    datasets: [
      {
        label: 'Safety Score',
        data: safetyScores.length ? safetyScores : [100,100,95,98,100],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.07)',
        fill: true, tension: 0.4, pointRadius: 2,
      },
      {
        label: 'Attention Score',
        data: attentionScores.length ? attentionScores : [100,95,90,96,100],
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37,99,235,0.06)',
        fill: true, tension: 0.4, pointRadius: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: { color: '#6b7a99', font: { size: 12, weight: '600' }, usePointStyle: true },
      },
      tooltip: {
        backgroundColor: '#fff',
        titleColor: '#1a2747',
        bodyColor: '#6b7a99',
        borderColor: '#e2e8f4',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(26,39,71,0.05)' },
        ticks: { color: '#9ba8c4', font: { size: 11 } },
      },
      y: {
        min: 0, max: 100,
        grid: { color: 'rgba(26,39,71,0.05)' },
        ticks: { color: '#9ba8c4', font: { size: 11 } },
      },
    },
  };

  return (
    <div className="card rounded-2xl p-5 flex flex-col" style={{ height: 280 }}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold" style={{ color: '#1a2747' }}>Live Attention & Safety</h3>
        <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full"
              style={{ background: '#dbeafe', color: '#1e40af' }}>Real-time</span>
      </div>
      <div className="flex-1 w-full">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};
