'use client';

import { useState, useCallback } from 'react';
import FileUpload from '@/components/FileUpload';
import ProgressIndicator from '@/components/ProgressIndicator';
import ResultsDisplay from '@/components/ResultsDisplay';
import BulkResultsDisplay from '@/components/BulkResultsDisplay';
import { analyzePresentation, analyzeBulk, exportExcel, downloadBlob, APIError } from '@/lib/api';
import { GradingResult, BulkAnalyzeResponse, UploadStatus, UploadMode } from '@/types';

export default function Home() {
  // Mode selection
  const [mode, setMode] = useState<UploadMode>('single');

  // Single mode state
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [onTime, setOnTime] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GradingResult | null>(null);

  // Bulk mode state
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [bulkResult, setBulkResult] = useState<BulkAnalyzeResponse | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  // Single file handlers
  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setError(null);
    setResult(null);
    setStatus('idle');
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!selectedFile) return;

    setStatus('uploading');
    setError(null);

    try {
      setStatus('analyzing');
      const response = await analyzePresentation(selectedFile, onTime);

      if (response.success && response.result) {
        setResult(response.result);
        setStatus('complete');
      } else {
        setError(response.error || 'Analiz basarisiz oldu');
        setStatus('error');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      if (err instanceof APIError) {
        setError(`Hata (${err.status}): ${err.message}`);
      } else {
        setError('Beklenmeyen bir hata olustu. Lutfen tekrar deneyin.');
      }
      setStatus('error');
    }
  }, [selectedFile, onTime]);

  // Bulk file handlers
  const handleFilesSelect = useCallback((files: File[]) => {
    setSelectedFiles(files);
    setError(null);
    setBulkResult(null);
    setStatus('idle');
  }, []);

  const handleBulkAnalyze = useCallback(async () => {
    if (selectedFiles.length === 0) return;

    setStatus('uploading');
    setError(null);

    try {
      setStatus('analyzing');
      const response = await analyzeBulk(selectedFiles, onTime);
      setBulkResult(response);
      setStatus('complete');
    } catch (err) {
      console.error('Bulk analysis error:', err);
      if (err instanceof APIError) {
        setError(`Hata (${err.status}): ${err.message}`);
      } else {
        setError('Beklenmeyen bir hata olustu. Lutfen tekrar deneyin.');
      }
      setStatus('error');
    }
  }, [selectedFiles, onTime]);

  const handleExportExcel = useCallback(async () => {
    if (selectedFiles.length === 0) return;

    setIsExporting(true);
    try {
      const blob = await exportExcel(selectedFiles, onTime);
      downloadBlob(blob, 'ogrenci_puanlari.xlsx');
    } catch (err) {
      console.error('Export error:', err);
      if (err instanceof APIError) {
        setError(`Excel olusturma hatasi: ${err.message}`);
      } else {
        setError('Excel olusturulurken bir hata olustu.');
      }
    } finally {
      setIsExporting(false);
    }
  }, [selectedFiles, onTime]);

  const handleReset = useCallback(() => {
    setStatus('idle');
    setSelectedFile(null);
    setSelectedFiles([]);
    setOnTime(false);
    setError(null);
    setResult(null);
    setBulkResult(null);
  }, []);

  // Show single result
  if (mode === 'single' && status === 'complete' && result) {
    return <ResultsDisplay result={result} onReset={handleReset} />;
  }

  // Show bulk results
  if (mode === 'bulk' && status === 'complete' && bulkResult) {
    return (
      <BulkResultsDisplay
        result={bulkResult}
        onReset={handleReset}
        onExportExcel={handleExportExcel}
        isExporting={isExporting}
      />
    );
  }

  // Show progress indicator during upload/analysis
  if (status === 'uploading' || status === 'analyzing') {
    return <ProgressIndicator status={status} />;
  }

  // Show upload form
  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Welcome message */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">
          Odev Sunumu Degerlendirmesi
        </h2>
        <p className="mt-2 text-gray-600">
          Ogrenci PowerPoint sunumunu yukleyin ve AI destekli degerlendirme alin.
        </p>
      </div>

      {/* Mode selector */}
      <div className="flex justify-center">
        <div className="inline-flex rounded-lg border border-gray-200 p-1 bg-gray-50">
          <button
            onClick={() => {
              setMode('single');
              handleReset();
            }}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === 'single'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Tekli Degerlendirme
          </button>
          <button
            onClick={() => {
              setMode('bulk');
              handleReset();
            }}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === 'bulk'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Toplu Degerlendirme
          </button>
        </div>
      </div>

      {/* File upload */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {mode === 'single' ? 'Sunum Dosyasi' : 'Sunum Dosyalari'}
        </h3>
        {mode === 'single' ? (
          <FileUpload
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            disabled={status !== 'idle'}
          />
        ) : (
          <FileUpload
            onFileSelect={() => {}}
            onFilesSelect={handleFilesSelect}
            selectedFiles={selectedFiles}
            disabled={status !== 'idle'}
            multiple
          />
        )}
      </div>

      {/* On-time toggle */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Zamaninda Teslim
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Odev zamaninda teslim edildiyse +10 puan eklenir
            </p>
          </div>
          <button
            type="button"
            onClick={() => setOnTime(!onTime)}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
              onTime ? 'bg-primary-600' : 'bg-gray-200'
            }`}
            role="switch"
            aria-checked={onTime}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                onTime ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start gap-3">
            <svg
              className="w-6 h-6 text-red-500 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <h3 className="text-lg font-semibold text-red-900">Hata</h3>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          </div>
          <button
            onClick={() => setError(null)}
            className="mt-4 text-sm text-red-600 hover:text-red-800"
          >
            Kapat
          </button>
        </div>
      )}

      {/* Analyze button */}
      <div className="text-center">
        {mode === 'single' ? (
          <>
            <button
              onClick={handleAnalyze}
              disabled={!selectedFile}
              className="btn-primary text-lg px-8 py-3"
            >
              Analiz Et
            </button>
            {!selectedFile && (
              <p className="text-sm text-gray-500 mt-2">
                Analiz icin once bir dosya secin
              </p>
            )}
          </>
        ) : (
          <>
            <button
              onClick={handleBulkAnalyze}
              disabled={selectedFiles.length === 0}
              className="btn-primary text-lg px-8 py-3"
            >
              Toplu Analiz Et ({selectedFiles.length} dosya)
            </button>
            {selectedFiles.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">
                Analiz icin once dosyalari secin
              </p>
            )}
          </>
        )}
      </div>

      {/* Info box */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          {mode === 'single' ? 'Degerlendirme Kriterleri' : 'Toplu Degerlendirme Bilgisi'}
        </h3>
        {mode === 'single' ? (
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-center gap-2">
              <span className="font-medium">15 puan:</span> Etik ilkeleri dogrulugu (en az 5 ilke)
            </li>
            <li className="flex items-center gap-2">
              <span className="font-medium">50 puan:</span> Sahne aciklamasi kalitesi
            </li>
            <li className="flex items-center gap-2">
              <span className="font-medium">15 puan:</span> Sablon uyumu
            </li>
            <li className="flex items-center gap-2">
              <span className="font-medium">10 puan:</span> Gorsel tasarim
            </li>
            <li className="flex items-center gap-2">
              <span className="font-medium">10 puan:</span> Zamaninda teslim
            </li>
          </ul>
        ) : (
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <span className="font-medium">Dosya Adi:</span>
              <span>isim_soyisim.pptx formatinda olmali</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-medium">Excel Ciktisi:</span>
              <span>Tum ogrencilerin puanlari ve detaylari</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-medium">Not:</span>
              <span>Her dosya sirayla AI tarafindan degerlendirilir</span>
            </li>
          </ul>
        )}
      </div>
    </div>
  );
}
