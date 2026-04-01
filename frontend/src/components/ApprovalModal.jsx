import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { X, CheckCircle, XCircle, FileText, IndianRupee, AlertTriangle } from 'lucide-react';

const ApprovalModal = ({ analysis, onApprove, onReject, onClose }) => {
  const [notes, setNotes] = useState('');
  const [confirming, setConfirming] = useState(false);

  if (!analysis) return null;

  const totalSales = analysis.total_invoices * 25000;
  const gstPayable = totalSales * 0.18;
  const itcClaimable = gstPayable - analysis.itc_at_risk;

  const handleApprove = () => {
    setConfirming(true);
    setTimeout(() => {
      onApprove(notes);
      setConfirming(false);
    }, 1000);
  };

  const handleReject = () => {
    setConfirming(true);
    setTimeout(() => {
      onReject(notes);
      setConfirming(false);
    }, 1000);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="bg-white dark:bg-charcoal-dark rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-charcoal to-slate-gray text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8" />
              <div>
                <h2 className="text-2xl font-bold">Review & File GST Return</h2>
                <p className="text-sm text-white text-opacity-80">AI-powered filing with human oversight</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors">
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-off-white dark:bg-charcoal rounded-xl p-4 border-2 border-accent-blue">
              <div className="flex items-center justify-between mb-2">
                <IndianRupee className="w-6 h-6 text-accent-blue" />
                <span className="text-xs text-slate-gray">Total Sales</span>
              </div>
              <p className="text-2xl font-bold text-charcoal dark:text-white">₹{totalSales.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
            </div>
            <div className="bg-off-white dark:bg-charcoal rounded-xl p-4 border-2 border-accent-blue">
              <div className="flex items-center justify-between mb-2">
                <FileText className="w-6 h-6 text-accent-blue" />
                <span className="text-xs text-slate-gray">GST Payable</span>
              </div>
              <p className="text-2xl font-bold text-charcoal dark:text-white">₹{gstPayable.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
            </div>
            <div className="bg-off-white dark:bg-charcoal rounded-xl p-4 border-2 border-error-red">
              <div className="flex items-center justify-between mb-2">
                <AlertTriangle className="w-6 h-6 text-error-red" />
                <span className="text-xs text-slate-gray">ITC at Risk</span>
              </div>
              <p className="text-2xl font-bold text-error-red">₹{analysis.itc_at_risk.toLocaleString('en-IN')}</p>
            </div>
          </div>

          {/* Filing Summary */}
          <div className="border-2 border-light-gray dark:border-charcoal-light rounded-xl p-4">
            <h3 className="font-bold text-charcoal dark:text-white mb-4">📋 Filing Summary</h3>
            <div className="space-y-3">
              {[
                { label: 'Total Invoices', value: analysis.total_invoices },
                { label: 'Matched Invoices', value: analysis.matched_count, color: 'text-success-green' },
                { label: 'Mismatched', value: analysis.mismatch_count, color: 'text-warning-orange' },
                { label: 'Missing in GSTR-2A', value: analysis.missing_count, color: 'text-error-red' },
              ].map((item) => (
                <div key={item.label} className="flex justify-between py-2 border-b border-light-gray dark:border-charcoal-light last:border-0">
                  <span className="text-slate-gray dark:text-slate-gray-light">{item.label}</span>
                  <span className={`font-semibold ${item.color || 'text-charcoal dark:text-white'}`}>{item.value}</span>
                </div>
              ))}
              <div className="flex justify-between pt-3 font-bold">
                <span className="text-charcoal dark:text-white">Net ITC Claimable</span>
                <span className="text-accent-blue">₹{itcClaimable.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
              </div>
            </div>
          </div>

          {/* Warning */}
          {analysis.missing_count > 0 && (
            <div className="bg-error-red bg-opacity-5 dark:bg-error-red dark:bg-opacity-10 border-l-4 border-error-red p-4 rounded-xl">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-6 h-6 text-error-red flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-error-red mb-1">Warning: Missing Invoices</h4>
                  <p className="text-sm text-slate-gray dark:text-slate-gray-light">
                    {analysis.missing_count} invoices are missing in GSTR-2A. Filing now will result in 
                    loss of ₹{analysis.itc_at_risk.toLocaleString('en-IN')} Input Tax Credit.
                  </p>
                  <p className="text-sm text-slate-gray dark:text-slate-gray-light mt-2">
                    <strong>Recommendation:</strong> Send WhatsApp reminders first, wait for vendors to upload, then file.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-sm font-semibold text-charcoal dark:text-white mb-2">
              Additional Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any notes for your CA or records..."
              className="input-field resize-none"
              rows={3}
              disabled={confirming}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="bg-off-white dark:bg-charcoal p-6 rounded-b-2xl border-t border-light-gray dark:border-charcoal-light">
          <div className="flex items-center justify-between">
            <div className="text-sm text-slate-gray dark:text-slate-gray-light">
              By filing, you confirm the information is accurate to the best of your knowledge.
            </div>
            <div className="flex space-x-4">
              <button
                onClick={handleReject}
                disabled={confirming}
                className="flex items-center space-x-2 px-6 py-3 bg-error-red hover:bg-error-red-hover text-white rounded-lg font-bold transition-all disabled:opacity-50"
              >
                <XCircle className="w-5 h-5" />
                <span>{confirming ? 'Processing...' : 'Reject & Follow-up'}</span>
              </button>
              <button
                onClick={handleApprove}
                disabled={confirming}
                className="flex items-center space-x-2 px-6 py-3 bg-accent-blue hover:bg-accent-blue-hover text-white rounded-lg font-bold transition-all disabled:opacity-50"
              >
                <CheckCircle className="w-5 h-5" />
                <span>{confirming ? 'Filing...' : 'Approve & File GST'}</span>
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ApprovalModal;
