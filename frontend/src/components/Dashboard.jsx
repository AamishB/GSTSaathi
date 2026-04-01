import React from 'react';
import { motion } from 'framer-motion';
import { 
  IndianRupee, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp,
  TrendingDown,
  Upload,
  ArrowRight
} from 'lucide-react';

const Dashboard = ({ analysis, onFileUpload }) => {
  if (!analysis) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue mx-auto mb-4"></div>
          <p className="text-slate-gray dark:text-slate-gray-light">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const totalSales = analysis.total_invoices * 25000;
  const gstPayable = totalSales * 0.18;
  const complianceScore = (analysis.matched_count / analysis.total_invoices) * 100;

  const metrics = [
    {
      title: 'Total Sales',
      value: `₹${(totalSales / 100000).toFixed(2)}L`,
      subvalue: `₹${totalSales.toLocaleString('en-IN')}`,
      icon: IndianRupee,
      color: 'text-accent-blue',
      bgColor: 'bg-accent-blue bg-opacity-10',
      trend: '+12.5%',
      trendUp: true,
    },
    {
      title: 'GST Payable',
      value: `₹${(gstPayable / 100000).toFixed(2)}L`,
      subvalue: `₹${gstPayable.toLocaleString('en-IN')}`,
      icon: FileText,
      color: 'text-slate-gray',
      bgColor: 'bg-slate-gray bg-opacity-10',
      trend: 'On track',
      trendUp: null,
    },
    {
      title: 'ITC at Risk',
      value: `₹${(analysis.itc_at_risk / 100000).toFixed(2)}L`,
      subvalue: `₹${analysis.itc_at_risk.toLocaleString('en-IN')}`,
      icon: AlertTriangle,
      color: 'text-error-red',
      bgColor: 'bg-error-red bg-opacity-10',
      trend: 'Requires action',
      trendUp: false,
    },
    {
      title: 'Matched Invoices',
      value: analysis.matched_count,
      subvalue: `of ${analysis.total_invoices} total`,
      icon: CheckCircle,
      color: 'text-success-green',
      bgColor: 'bg-success-green bg-opacity-10',
      trend: `${complianceScore.toFixed(0)}%`,
      trendUp: true,
    },
  ];

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.1, duration: 0.4 },
    }),
  };

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="gradient-accent rounded-2xl p-8 text-white shadow-lg"
      >
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-3">Welcome to GSTSaathi</h2>
            <p className="text-white text-opacity-90 mb-6 max-w-2xl">
              Your AI-powered GST compliance assistant. Automatically detect mismatches, 
              recover ITC, and file returns with confidence.
            </p>
            <div className="flex space-x-4">
              <button
                onClick={onFileUpload}
                className="bg-white text-charcoal px-6 py-3 rounded-lg font-semibold hover:bg-off-white transition-colors flex items-center space-x-2 shadow-md"
              >
                <Upload className="w-5 h-5" />
                <span>Upload Invoices</span>
              </button>
              <button
                onClick={() => document.getElementById('mismatches-tab')?.click()}
                className="bg-charcoal bg-opacity-30 text-white px-6 py-3 rounded-lg font-semibold hover:bg-opacity-40 transition-colors flex items-center space-x-2 backdrop-blur-sm"
              >
                <span>View Mismatches</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="bg-white bg-opacity-20 backdrop-blur-md rounded-xl p-6">
              <div className="text-center">
                <p className="text-sm text-white text-opacity-80 mb-1">Compliance Score</p>
                <p className="text-5xl font-bold mb-2">{complianceScore.toFixed(0)}%</p>
                <div className="w-32 bg-white bg-opacity-30 rounded-full h-2 mx-auto">
                  <div
                    className="bg-white rounded-full h-2 transition-all duration-500"
                    style={{ width: `${complianceScore}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.title}
            custom={index}
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            className="card"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`p-3 rounded-xl ${metric.bgColor}`}>
                <metric.icon className={`w-6 h-6 ${metric.color}`} />
              </div>
              {metric.trend && (
                <div className={`flex items-center space-x-1 text-sm font-medium ${
                  metric.trendUp === true ? 'text-success-green' :
                  metric.trendUp === false ? 'text-error-red' :
                  'text-slate-gray'
                }`}>
                  {metric.trendUp === true && <TrendingUp className="w-4 h-4" />}
                  {metric.trendUp === false && <TrendingDown className="w-4 h-4" />}
                  <span>{metric.trend}</span>
                </div>
              )}
            </div>
            <h3 className="text-slate-gray dark:text-slate-gray-light text-sm font-medium mb-1">
              {metric.title}
            </h3>
            <p className={`text-2xl font-bold ${metric.color}`}>
              {metric.value}
            </p>
            <p className="text-xs text-slate-gray dark:text-slate-gray-light mt-1">
              {metric.subvalue}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Detailed Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compliance Status */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h3 className="text-lg font-bold text-charcoal dark:text-white mb-6">
            📊 Compliance Status
          </h3>
          <div className="space-y-4">
            {[
              { label: 'Total Invoices', value: analysis.total_invoices, color: 'text-charcoal' },
              { label: 'Matched', value: analysis.matched_count, color: 'text-success-green', suffix: `(${((analysis.matched_count / analysis.total_invoices) * 100).toFixed(1)}%)` },
              { label: 'Mismatched', value: analysis.mismatch_count, color: 'text-warning-orange' },
              { label: 'Missing in GSTR-2A', value: analysis.missing_count, color: 'text-error-red' },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between py-3 border-b border-light-gray dark:border-charcoal-light last:border-0">
                <span className="text-slate-gray dark:text-slate-gray-light">{item.label}</span>
                <span className={`font-bold ${item.color}`}>
                  {item.value} {item.suffix && <span className="text-sm text-slate-gray">{item.suffix}</span>}
                </span>
              </div>
            ))}
          </div>

          {/* Progress Bar */}
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-gray dark:text-slate-gray-light">Compliance Score</span>
              <span className="font-bold text-accent-blue">
                {complianceScore.toFixed(0)}%
              </span>
            </div>
            <div className="w-full bg-light-gray dark:bg-charcoal rounded-full h-3">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${complianceScore}%` }}
                transition={{ duration: 1, delay: 0.5 }}
                className="bg-gradient-to-r from-accent-blue to-slate-gray h-3 rounded-full"
              ></motion.div>
            </div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h3 className="text-lg font-bold text-charcoal dark:text-white mb-6">
            ⚡ Quick Actions
          </h3>
          <div className="space-y-3">
            {[
              {
                label: 'Upload Invoice Data',
                description: 'Import from Excel/CSV',
                icon: Upload,
                onClick: onFileUpload,
                color: 'bg-accent-blue hover:bg-accent-blue-hover',
              },
              {
                label: 'Review Mismatches',
                description: `${analysis.missing_count} invoices at risk`,
                icon: AlertTriangle,
                onClick: () => document.getElementById('mismatches-tab')?.click(),
                color: 'bg-error-red hover:bg-error-red-hover',
              },
              {
                label: 'View Audit Trail',
                description: 'Compliance history',
                icon: CheckCircle,
                onClick: () => document.getElementById('audit-tab')?.click(),
                color: 'bg-success-green hover:bg-success-green-hover',
              },
            ].map((action) => (
              <button
                key={action.label}
                onClick={action.onClick}
                className={`w-full ${action.color} text-white px-5 py-4 rounded-xl font-semibold transition-all duration-200 text-left flex items-center space-x-4 shadow-md hover:shadow-lg active:scale-98`}
              >
                <action.icon className="w-6 h-6" />
                <div>
                  <p className="text-base">{action.label}</p>
                  <p className="text-sm text-white text-opacity-80">{action.description}</p>
                </div>
              </button>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Info Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-gradient-to-r from-off-white to-light-gray dark:from-charcoal-dark dark:to-charcoal border-l-4 border-accent-blue p-6 rounded-xl shadow-sm"
      >
        <h4 className="font-bold text-charcoal dark:text-white mb-2">
          💡 Did you know?
        </h4>
        <p className="text-slate-gray dark:text-slate-gray-light">
          Missing invoices in GSTR-2A can result in complete loss of Input Tax Credit (ITC). 
          GSTSaathi's AI agents automatically identify mismatches, send multilingual reminders 
          to your vendors, and help you recover up to 85% of at-risk ITC within 30 days.
        </p>
      </motion.div>
    </div>
  );
};

export default Dashboard;
