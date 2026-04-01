import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const UploadZone = ({ onFileUpload, loading }) => {
  const [selectedFile, setSelectedFile] = useState(null);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      toast.error('Invalid file type. Please upload Excel (.xlsx) or CSV files only.');
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 1,
    disabled: loading,
  });

  const handleUpload = () => {
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <h2 className="text-2xl font-bold text-charcoal dark:text-white mb-2">
          📁 Upload Invoice Data
        </h2>
        <p className="text-slate-gray dark:text-slate-gray-light">
          Upload your sales/purchase invoice data in Excel or CSV format. 
          Our AI agents will automatically match it with GSTR-2A and identify discrepancies.
        </p>
      </motion.div>

      {/* Dropzone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-all duration-300 ${
            isDragActive
              ? 'border-accent-blue bg-accent-blue bg-opacity-5 scale-105'
              : 'border-light-gray dark:border-charcoal-light hover:border-accent-blue hover:bg-off-white dark:hover:bg-charcoal'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} disabled={loading} />
          
          <motion.div
            animate={isDragActive ? { scale: 1.1, y: -5 } : { scale: 1, y: 0 }}
            className="mb-6"
          >
            <div className="bg-gradient-to-br from-accent-blue to-slate-gray p-4 rounded-2xl inline-block shadow-lg">
              <Upload className="w-12 h-12 text-white" />
            </div>
          </motion.div>
          
          {isDragActive ? (
            <div>
              <p className="text-lg font-semibold text-accent-blue mb-2">
                Drop the file here...
              </p>
              <p className="text-sm text-slate-gray dark:text-slate-gray-light">
                Release to upload
              </p>
            </div>
          ) : (
            <div>
              <p className="text-lg font-semibold text-charcoal dark:text-white mb-2">
                Drag & drop your invoice file here
              </p>
              <p className="text-slate-gray dark:text-slate-gray-light mb-4">
                or click to browse
              </p>
              <p className="text-sm text-slate-gray dark:text-slate-gray-light">
                Supported formats: Excel (.xlsx), CSV
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Selected File Preview */}
      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card bg-off-white dark:bg-charcoal"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-accent-blue bg-opacity-10 p-3 rounded-xl">
                <FileText className="w-10 h-10 text-accent-blue" />
              </div>
              <div>
                <p className="font-bold text-charcoal dark:text-white">{selectedFile.name}</p>
                <p className="text-sm text-slate-gray dark:text-slate-gray-light">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <button
              onClick={handleClear}
              disabled={loading}
              className="p-2 hover:bg-error-red hover:bg-opacity-10 rounded-full transition-colors disabled:opacity-50"
            >
              <X className="w-6 h-6 text-error-red" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Upload Button */}
      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex space-x-4"
        >
          <button
            onClick={handleUpload}
            disabled={loading}
            className="flex-1 btn-accent flex items-center justify-center space-x-2 py-3"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                <span>Upload & Analyze</span>
              </>
            )}
          </button>
          <button
            onClick={handleClear}
            disabled={loading}
            className="px-6 py-3 border-2 border-light-gray dark:border-charcoal-light rounded-lg font-semibold hover:bg-light-gray dark:hover:bg-charcoal transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
        </motion.div>
      )}

      {/* Instructions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card gradient-subtle"
      >
        <h3 className="text-lg font-bold text-charcoal dark:text-white mb-4">
          📋 File Format Guide
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-accent-blue mb-3">Required Columns:</h4>
            <ul className="space-y-2 text-sm text-slate-gray dark:text-slate-gray-light">
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>invoice_number</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>invoice_date</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>vendor_name</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>vendor_gstin</span>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-accent-blue mb-3">Tax Columns:</h4>
            <ul className="space-y-2 text-sm text-slate-gray dark:text-slate-gray-light">
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>taxable_value</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>cgst</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>sgst</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>igst</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-success-green" />
                <span>total_value</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-6 p-4 bg-accent-blue bg-opacity-5 dark:bg-accent-blue dark:bg-opacity-10 rounded-xl">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-accent-blue flex-shrink-0 mt-0.5" />
            <p className="text-sm text-slate-gray dark:text-slate-gray-light">
              <strong>Tip:</strong> Download our sample template to ensure your file is formatted correctly.
              The AI will automatically validate your data and provide detailed error messages if any issues are found.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default UploadZone;
