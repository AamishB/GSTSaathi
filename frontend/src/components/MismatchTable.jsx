import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, MessageCircle, FileCheck, CheckCircle, TrendingDown } from 'lucide-react';

const MismatchTable = ({ analysis, onSendWhatsApp, onFileGST, whatsappSent, loading }) => {
  if (!analysis || !analysis.mismatches) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue mx-auto mb-4"></div>
          <p className="text-slate-gray dark:text-slate-gray-light">Loading mismatches...</p>
        </div>
      </div>
    );
  }

  const missingInvoices = analysis.mismatches.filter(m => m.status === 'missing');
  const mismatchedInvoices = analysis.mismatches.filter(m => m.status === 'mismatch');

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            title: 'Missing in GSTR-2A',
            value: analysis.missing_count,
            subtitle: `ITC at risk: ₹${analysis.itc_at_risk.toLocaleString('en-IN')}`,
            color: 'from-error-red to-error-red-hover',
            icon: AlertTriangle,
          },
          {
            title: 'Value Mismatches',
            value: analysis.mismatch_count,
            subtitle: 'Requires review',
            color: 'from-warning-orange to-warning-orange',
            icon: AlertTriangle,
          },
          {
            title: 'Matched Invoices',
            value: analysis.matched_count,
            subtitle: 'Perfect match',
            color: 'from-success-green to-success-green-hover',
            icon: CheckCircle,
          },
        ].map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`bg-gradient-to-br ${card.color} rounded-2xl p-6 text-white shadow-lg`}
          >
            <div className="flex items-center justify-between mb-4">
              <card.icon className="w-10 h-10 opacity-80" />
              <span className="text-4xl font-bold">{card.value}</span>
            </div>
            <h3 className="text-lg font-semibold mb-1">{card.title}</h3>
            <p className="text-sm text-white text-opacity-80">{card.subtitle}</p>
          </motion.div>
        ))}
      </div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-charcoal dark:text-white">
            📋 Mismatch Details
          </h3>
          <div className="flex space-x-4">
            <button
              onClick={onSendWhatsApp}
              disabled={loading || whatsappSent || missingInvoices.length === 0}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-bold transition-all ${
                whatsappSent
                  ? 'bg-success-green text-white'
                  : 'bg-accent-blue hover:bg-accent-blue-hover text-white'
              } disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg`}
            >
              {whatsappSent ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  <span>Reminders Sent!</span>
                </>
              ) : (
                <>
                  <MessageCircle className="w-5 h-5" />
                  <span>Send WhatsApp Reminders</span>
                </>
              )}
            </button>

            <button
              onClick={onFileGST}
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-3 bg-charcoal hover:bg-charcoal-light text-white rounded-lg font-bold transition-all shadow-md hover:shadow-lg disabled:opacity-50"
            >
              <FileCheck className="w-5 h-5" />
              <span>Review & File GST</span>
            </button>
          </div>
        </div>

        {/* Missing Invoices Table */}
        {missingInvoices.length > 0 && (
          <div className="mb-8">
            <h4 className="font-bold text-error-red mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Missing Invoices ({missingInvoices.length})
            </h4>
            <div className="overflow-x-auto rounded-xl border border-light-gray dark:border-charcoal-light">
              <table className="w-full">
                <thead className="bg-charcoal text-white">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold">Vendor</th>
                    <th className="px-4 py-3 text-left font-semibold">GSTIN</th>
                    <th className="px-4 py-3 text-left font-semibold">Invoice</th>
                    <th className="px-4 py-3 text-right font-semibold">Amount</th>
                    <th className="px-4 py-3 text-right font-semibold">Tax at Risk</th>
                    <th className="px-4 py-3 text-center font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {missingInvoices.map((m, i) => (
                    <tr
                      key={i}
                      className={`${
                        i % 2 === 0 ? 'bg-off-white dark:bg-charcoal-dark' : 'bg-white dark:bg-charcoal'
                      } hover:bg-accent-blue hover:bg-opacity-5 transition-colors border-b border-light-gray dark:border-charcoal-light last:border-0`}
                    >
                      <td className="px-4 py-3 font-semibold text-charcoal dark:text-white">{m.vendor_name}</td>
                      <td className="px-4 py-3 text-sm font-mono text-slate-gray dark:text-slate-gray-light">{m.vendor_gstin}</td>
                      <td className="px-4 py-3 text-sm text-charcoal dark:text-white">{m.invoice_number}</td>
                      <td className="px-4 py-3 text-right font-semibold text-charcoal dark:text-white">₹{m.our_record_amount.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3 text-right font-bold text-error-red">₹{m.tax_at_risk?.toLocaleString('en-IN') || '0'}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="badge badge-error">MISSING</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Mismatched Invoices */}
        {mismatchedInvoices.length > 0 && (
          <div>
            <h4 className="font-bold text-warning-orange mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Value Mismatches ({mismatchedInvoices.length})
            </h4>
            <div className="overflow-x-auto rounded-xl border border-light-gray dark:border-charcoal-light">
              <table className="w-full">
                <thead className="bg-warning-orange text-white">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold">Vendor</th>
                    <th className="px-4 py-3 text-left font-semibold">GSTIN</th>
                    <th className="px-4 py-3 text-left font-semibold">Invoice</th>
                    <th className="px-4 py-3 text-right font-semibold">Our Records</th>
                    <th className="px-4 py-3 text-right font-semibold">GSTR-2A</th>
                    <th className="px-4 py-3 text-right font-semibold">Difference</th>
                    <th className="px-4 py-3 text-center font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {mismatchedInvoices.map((m, i) => (
                    <tr
                      key={i}
                      className={`${
                        i % 2 === 0 ? 'bg-off-white dark:bg-charcoal-dark' : 'bg-white dark:bg-charcoal'
                      } hover:bg-warning-orange hover:bg-opacity-5 transition-colors border-b border-light-gray dark:border-charcoal-light last:border-0`}
                    >
                      <td className="px-4 py-3 font-semibold">{m.vendor_name}</td>
                      <td className="px-4 py-3 text-sm font-mono text-slate-gray">{m.vendor_gstin}</td>
                      <td className="px-4 py-3 text-sm">{m.invoice_number}</td>
                      <td className="px-4 py-3 text-right font-semibold">₹{m.our_record_amount.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3 text-right">₹{m.gstr2a_amount?.toLocaleString('en-IN') || 'N/A'}</td>
                      <td className="px-4 py-3 text-right font-bold text-warning-orange">{m.difference > 0 ? '+' : ''}{m.difference.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="badge badge-warning">MISMATCH</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* No Mismatches */}
        {analysis.mismatches.length === 0 && (
          <div className="text-center py-16">
            <CheckCircle className="w-20 h-20 mx-auto text-success-green mb-4" />
            <h3 className="text-2xl font-bold text-success-green mb-2">Perfect Match! 🎉</h3>
            <p className="text-slate-gray dark:text-slate-gray-light mb-6">
              All {analysis.total_invoices} invoices match with GSTR-2A
            </p>
            <button onClick={onFileGST} className="btn-accent inline-flex items-center space-x-2">
              <FileCheck className="w-5 h-5" />
              <span>Proceed to File GST Return</span>
            </button>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default MismatchTable;
