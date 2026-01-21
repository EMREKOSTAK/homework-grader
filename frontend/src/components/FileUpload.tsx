'use client';

import { useState, useCallback, useRef } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFilesSelect?: (files: File[]) => void;
  disabled?: boolean;
  selectedFile?: File | null;
  selectedFiles?: File[];
  multiple?: boolean;
}

export default function FileUpload({
  onFileSelect,
  onFilesSelect,
  disabled = false,
  selectedFile,
  selectedFiles = [],
  multiple = false,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const validateFiles = useCallback((files: FileList): File[] => {
    const validFiles: File[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.name.toLowerCase().endsWith('.pptx')) {
        validFiles.push(file);
      }
    }
    return validFiles;
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      if (disabled) return;

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        if (multiple && onFilesSelect) {
          const validFiles = validateFiles(files);
          if (validFiles.length > 0) {
            onFilesSelect(validFiles);
          } else {
            alert('Sadece .pptx dosyaları kabul edilir');
          }
        } else {
          const file = files[0];
          if (file.name.toLowerCase().endsWith('.pptx')) {
            onFileSelect(file);
          } else {
            alert('Sadece .pptx dosyaları kabul edilir');
          }
        }
      }
    },
    [disabled, onFileSelect, onFilesSelect, multiple, validateFiles]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        if (multiple && onFilesSelect) {
          const validFiles = validateFiles(files);
          if (validFiles.length > 0) {
            onFilesSelect(validFiles);
          } else {
            alert('Sadece .pptx dosyaları kabul edilir');
          }
        } else {
          const file = files[0];
          if (file.name.toLowerCase().endsWith('.pptx')) {
            onFileSelect(file);
          } else {
            alert('Sadece .pptx dosyaları kabul edilir');
          }
        }
      }
    },
    [onFileSelect, onFilesSelect, multiple, validateFiles]
  );

  const handleClick = useCallback(() => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, [disabled]);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const hasFiles = multiple ? selectedFiles.length > 0 : !!selectedFile;

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''} ${
        hasFiles ? 'has-file' : ''
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pptx"
        className="hidden"
        disabled={disabled}
        multiple={multiple}
      />

      {multiple && selectedFiles.length > 0 ? (
        <div className="space-y-2">
          <div className="flex items-center justify-center">
            <svg
              className="w-12 h-12 text-green-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <p className="text-lg font-medium text-gray-900">
            {selectedFiles.length} dosya secildi
          </p>
          <div className="max-h-32 overflow-y-auto text-sm text-gray-600">
            {selectedFiles.slice(0, 5).map((file, idx) => (
              <p key={idx}>{file.name}</p>
            ))}
            {selectedFiles.length > 5 && (
              <p className="text-gray-400">
                ve {selectedFiles.length - 5} dosya daha...
              </p>
            )}
          </div>
          <p className="text-sm text-gray-500">
            Toplam: {formatFileSize(selectedFiles.reduce((acc, f) => acc + f.size, 0))}
          </p>
          {!disabled && (
            <p className="text-sm text-primary-600">
              Degistirmek icin tiklayin veya birakin
            </p>
          )}
        </div>
      ) : selectedFile ? (
        <div className="space-y-2">
          <div className="flex items-center justify-center">
            <svg
              className="w-12 h-12 text-green-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <p className="text-lg font-medium text-gray-900">{selectedFile.name}</p>
          <p className="text-sm text-gray-500">
            {formatFileSize(selectedFile.size)}
          </p>
          {!disabled && (
            <p className="text-sm text-primary-600">
              Degistirmek icin tiklayin veya birakin
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center justify-center">
            <svg
              className="w-12 h-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          <p className="text-lg font-medium text-gray-900">
            {multiple ? 'PowerPoint dosyalarini yukleyin' : 'PowerPoint dosyasini yukleyin'}
          </p>
          <p className="text-sm text-gray-500">
            {multiple ? 'Dosyalari buraya surukleyin veya ' : 'Dosyayi buraya surukleyin veya '}
            <span className="text-primary-600">tiklayarak secin</span>
          </p>
          <p className="text-xs text-gray-400">
            {multiple
              ? 'Sadece .pptx dosyalari - Dosya adi: isim_soyisim.pptx'
              : 'Sadece .pptx dosyalari (max 15MB)'}
          </p>
        </div>
      )}
    </div>
  );
}
