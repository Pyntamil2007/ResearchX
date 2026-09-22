import React, { useState } from 'react';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Cell, Legend
} from 'recharts';
import {
  BarChart3,
  LineChart as LineChartIcon,
  Table as TableIcon,
  AlertCircle,
  TrendingUp,
  Award,
  Layers,
  Activity
} from 'lucide-react';

const COLORS = [
  '#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899',
  '#8b5cf6', '#3b82f6', '#14b8a6', '#f43f5e', '#a855f7'
];

export const ChartComponent = ({ visualizationData, data }) => {
  const vData = visualizationData || data;
  const [viewType, setViewType] = useState('bar'); // 'bar', 'area', 'table'

  if (!vData || !vData.has_visualizations || !vData.series || vData.series.length === 0) {
    return (
      <div className="no-viz-box" style={{
        padding: '2.5rem 1.5rem',
        textAlign: 'center',
        background: 'rgba(15, 23, 42, 0.6)',
        borderRadius: '12px',
        border: '1px dashed var(--border-color)',
        margin: '1.25rem 0'
      }}>
        <div style={{
          width: '52px',
          height: '52px',
          borderRadius: '50%',
          background: 'rgba(99, 102, 241, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1rem',
          color: 'var(--primary)'
        }}>
          <AlertCircle size={26} />
        </div>
        <h4 style={{ fontSize: '1.1rem', color: '#ffffff', marginBottom: '0.4rem', fontFamily: 'var(--font-heading)' }}>
          Research Visualizations
        </h4>
        <p style={{ maxWidth: '520px', margin: '0 auto', fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
          {vData?.message || "No suitable numerical data was found in the paper for this visualization."}
        </p>
      </div>
    );
  }

  const { series, table_rows = [], metrics_summary = [] } = vData;

  // Calculate highest performing model
  const sortedSeries = [...series].sort((a, b) => b.value - a.value);
  const bestModel = sortedSeries[0];
  const primaryMetric = metrics_summary[0] || (bestModel ? bestModel.metric : 'Performance');

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div style={{
          background: '#0f172a',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          borderRadius: '8px',
          padding: '12px 16px',
          boxShadow: '0 12px 30px rgba(0,0,0,0.6)',
          fontSize: '0.88rem',
          fontFamily: 'var(--font-sans)'
        }}>
          <p style={{ fontWeight: 700, color: '#ffffff', marginBottom: 4, fontSize: '0.95rem' }}>
            {item.name}
          </p>
          <p style={{ color: 'var(--accent)', margin: 0, fontWeight: 600 }}>
            {item.metric}: <span style={{ color: '#ffffff', fontWeight: 800 }}>{item.value}{item.value <= 100 && item.metric?.toLowerCase().includes('accuracy') ? '%' : ''}</span>
          </p>
          {item.group && (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: 6, borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 4 }}>
              Group: {item.group}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel visualization-box" style={{ padding: '1.75rem', borderRadius: '14px', border: '1px solid var(--border-color)', marginBottom: '1.75rem' }}>
      {/* Header with Title & KPI Chips */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14, marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <TrendingUp size={22} color="var(--accent)" />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#ffffff' }}>
              Empirical Results & Comparative Visualization
            </h3>
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: 0 }}>
            Benchmarking {series.length} model architectures across extracted evaluation metrics.
          </p>
        </div>

        {/* View Switcher Buttons */}
        <div style={{ display: 'flex', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px', padding: 4, gap: 4 }}>
          <button
            type="button"
            className={`btn btn-sm ${viewType === 'bar' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setViewType('bar')}
            style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          >
            <BarChart3 size={15} />
            <span>Bar Chart</span>
          </button>
          <button
            type="button"
            className={`btn btn-sm ${viewType === 'area' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setViewType('area')}
            style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          >
            <LineChartIcon size={15} />
            <span>Trend Area</span>
          </button>
          <button
            type="button"
            className={`btn btn-sm ${viewType === 'table' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setViewType('table')}
            style={{ padding: '6px 14px', fontSize: '0.85rem' }}
          >
            <TableIcon size={15} />
            <span>Comparison Table</span>
          </button>
        </div>
      </div>

      {/* KPI Metric Summary Badges */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: '1.5rem' }}>
        {bestModel && (
          <div style={{
            background: 'rgba(99, 102, 241, 0.12)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: '10px',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ffffff' }}>
              <Award size={20} />
            </div>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Top Benchmark</div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#ffffff' }}>{bestModel.name}</div>
            </div>
          </div>
        )}

        <div style={{
          background: 'rgba(6, 182, 212, 0.12)',
          border: '1px solid rgba(6, 182, 212, 0.25)',
          borderRadius: '10px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: 12
        }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0f172a' }}>
            <Activity size={20} />
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Primary Metric</div>
            <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#ffffff' }}>{primaryMetric}</div>
          </div>
        </div>

        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: '10px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: 12
        }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ffffff' }}>
            <Layers size={20} />
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Evaluated Systems</div>
            <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#ffffff' }}>{series.length} Models</div>
          </div>
        </div>
      </div>

      {/* Chart Renderings */}
      {viewType === 'bar' && (
        <div className="chart-wrapper" style={{ height: '360px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={series} margin={{ top: 20, right: 30, left: 20, bottom: 65 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.08)" vertical={false} />
              <XAxis
                dataKey="name"
                stroke="#94a3b8"
                angle={-25}
                textAnchor="end"
                interval={0}
                tick={{ fontSize: 12, fill: '#f1f5f9', fontFamily: 'var(--font-sans)' }}
              />
              <YAxis
                stroke="#94a3b8"
                tick={{ fontSize: 12, fill: '#94a3b8', fontFamily: 'var(--font-sans)' }}
                domain={[0, 'auto']}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {series.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {viewType === 'area' && (
        <div className="chart-wrapper" style={{ height: '360px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={series} margin={{ top: 20, right: 30, left: 20, bottom: 65 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.6}/>
                  <stop offset="95%" stopColor="var(--accent)" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.08)" vertical={false} />
              <XAxis
                dataKey="name"
                stroke="#94a3b8"
                angle={-25}
                textAnchor="end"
                interval={0}
                tick={{ fontSize: 12, fill: '#f1f5f9', fontFamily: 'var(--font-sans)' }}
              />
              <YAxis
                stroke="#94a3b8"
                tick={{ fontSize: 12, fill: '#94a3b8', fontFamily: 'var(--font-sans)' }}
                domain={[0, 'auto']}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="value"
                stroke="var(--accent)"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorValue)"
                dot={{ r: 6, fill: 'var(--primary)', stroke: '#ffffff', strokeWidth: 2 }}
                activeDot={{ r: 8, fill: 'var(--accent)' }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {viewType === 'table' && (
        <div className="table-container" style={{ marginTop: '0.5rem' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Model / Architecture</th>
                <th>Evaluated Metric</th>
                <th>Reported Value</th>
                <th>Benchmark / Group</th>
              </tr>
            </thead>
            <tbody>
              {table_rows.map((row, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600, color: '#ffffff' }}>{row.model}</td>
                  <td><span className="badge badge-admin">{row.metric}</span></td>
                  <td style={{ fontWeight: 800, color: 'var(--accent)', fontFamily: 'var(--font-mono)' }}>
                    {row.value}
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{row.benchmark}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
