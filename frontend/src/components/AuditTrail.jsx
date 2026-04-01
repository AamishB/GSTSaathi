import React from 'react';
import { motion } from 'framer-motion';
import { FileCheck, Clock, CheckCircle, XCircle, Download } from 'lucide-react';

const AuditTrail = ({ records }) => {
  if (!records || records.length === 0) {
    return (
      <div className="card text-center py-20">
        <FileCheck className="w-20 h-20 mx-auto text-slate-gray opacity-30 mb-4" />
        <h3 className="text-2xl font-bold text-charcoal dark:text-white mb-2">No Filings Yet</h3>
        <p className="text-slate-gray dark:text-slate-gray-light">
          Your GST filing history will appear here once you file your first return.
        </p>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'filed':
        return (
          <span className="badge badge-success flex items-center space-x-1">
            <CheckCircle className="w-3 h-3" />
            <span>FILED</span>
          </span>
        );
      case 'pending':
        return (
          <span className="badge badge-warning flex items-center space-x-1">
            <Clock className="w-3 h-3" />
            <span>PENDING</span>
          </span>
        );
      case 'rejected':
        return (
          <span className="badge badge-error flex items-center space-x-1">
            <XCircle className="w-3 h-3" />
            <span>REJECTED</span>
          </span>
        );
      default:
        return <span className="badge badge-info">{status.toUpperCase()}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card bg-gradient-to-r from-charcoal to-slate-gray text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-2">📜 Audit Trail</h2>
            <p className="text-white text-opacity-80">
              Complete history of your GST filings and compliance records
            </p>
          </div>
          <FileCheck className="w-16 h-16 opacity-30" />
        </div>
      </motion.div>

      {/* Filings Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-charcoal dark:text-white">
            Filing History ({records.length})
          </h3>
          <button className="btn-secondary flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
        <div className="overflow-x-auto rounded-xl border border-light-gray dark:border-charcoal-light">
          <table className="w-full">
            <thead className="bg-charcoal text-white">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">ARN</th>
                <th className="px-4 py-3 text-left font-semibold">Period</th>
                <th className="px-4 py-3 text-left font-semibold">Filing Date</th>
                <th className="px-4 py-3 text-right font-semibold">Total Sales</th>
                <th className="px-4 py-3 text-right font-semibold">GST Payable</th>
                <th className="px-4 py-3 text-right font-semibold">ITC Claimed</th>
                <th className="px-4 py-3 text-center font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record, index) => (
                <tr
                  key={index}
                  className={`${
                    index % 2 === 0 ? 'bg-off-white dark:bg-charcoal-dark' : 'bg-white dark:bg-charcoal'
                  } hover:bg-accent-blue hover:bg-opacity-5 transition-colors border-b border-light-gray dark:border-charcoal-light last:border-0`}
                >
                  <td className="px-4 py-3 font-mono text-sm font-semibold text-accent-blue">{record.arn}</td>
                  <td className="px-4 py-3 font-semibold text-charcoal dark:text-white">{record.period}</td>
                  <td className="px-4 py-3 text-sm text-slate-gray dark:text-slate-gray-light">
                    {new Date(record.filing_date).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-charcoal dark:text-white">
                    ₹{record.total_sales.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="px-4 py-3 text-right font-bold text-accent-blue">
                    ₹{record.gst_payable.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="px-4 py-3 text-right font-bold text-success-green">
                    ₹{record.itc_claimed.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="px-4 py-3 text-center">{getStatusBadge(record.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Statistics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        {[
          { label: 'Total Filings', value: records.length, color: 'text-charcoal' },
          { label: 'Successfully Filed', value: records.filter(r => r.status === 'filed').length, color: 'text-success-green' },
          { 
            label: 'Total ITC Claimed', 
            value: `₹${(records.reduce((sum, r) => sum + r.itc_claimed, 0) / 100000).toFixed(2)}L`,
            color: 'text-accent-blue'
          },
          { label: 'Avg Processing Time', value: '< 1 min', color: 'text-slate-gray' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 + index * 0.05 }}
            className="card text-center"
          >
            <p className="text-slate-gray dark:text-slate-gray-light text-sm mb-2">{stat.label}</p>
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};

export default AuditTrail;
