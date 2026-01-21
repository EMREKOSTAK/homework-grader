'use client';

interface ProgressIndicatorProps {
  status: 'uploading' | 'analyzing';
}

export default function ProgressIndicator({ status }: ProgressIndicatorProps) {
  const steps = [
    { key: 'upload', label: 'Dosya Yukleniyor', icon: UploadIcon },
    { key: 'parse', label: 'Icerik Ayristiriliyor', icon: ParseIcon },
    { key: 'analyze', label: 'AI Analizi', icon: AIIcon },
    { key: 'complete', label: 'Tamamlandi', icon: CheckIcon },
  ];

  const currentStepIndex = status === 'uploading' ? 0 : 2;

  return (
    <div className="card">
      <div className="flex flex-col items-center space-y-6">
        {/* Spinner */}
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary-200 rounded-full animate-spin border-t-primary-600" />
        </div>

        {/* Status text */}
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900">
            {status === 'uploading' ? 'Dosya Yukleniyor...' : 'Sunum Analiz Ediliyor...'}
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {status === 'uploading'
              ? 'Lutfen bekleyin, dosyaniz yukleniyor.'
              : 'AI degerlendirmesi yapiliyor. Bu birkaç saniye surebilir.'}
          </p>
        </div>

        {/* Progress steps */}
        <div className="w-full max-w-md">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const StepIcon = step.icon;
              const isActive = index === currentStepIndex;
              const isCompleted = index < currentStepIndex;

              return (
                <div key={step.key} className="flex flex-col items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                      isCompleted
                        ? 'bg-green-500 text-white'
                        : isActive
                        ? 'bg-primary-500 text-white animate-pulse'
                        : 'bg-gray-200 text-gray-400'
                    }`}
                  >
                    <StepIcon className="w-5 h-5" />
                  </div>
                  <span
                    className={`text-xs mt-2 ${
                      isActive ? 'text-primary-600 font-medium' : 'text-gray-500'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Progress line */}
          <div className="relative mt-4">
            <div className="absolute top-0 left-0 w-full h-1 bg-gray-200 rounded" />
            <div
              className="absolute top-0 left-0 h-1 bg-primary-500 rounded transition-all duration-500"
              style={{ width: `${(currentStepIndex / (steps.length - 1)) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function UploadIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
      />
    </svg>
  );
}

function ParseIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
      />
    </svg>
  );
}

function AIIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
      />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M5 13l4 4L19 7"
      />
    </svg>
  );
}
