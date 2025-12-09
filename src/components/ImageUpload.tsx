'use client';

import React, { useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';

interface DetectedObject {
  name: string;
  confidence: number;
  bbox: number[];
}

interface DetectionResult {
  image_path: string;
  filename: string;
  detected_objects: DetectedObject[];
  processing_time: number;
  created_at: string;
}

interface UploadResponse {
  project_id: string;
  uploaded_files: string[];
  detection_results: DetectionResult[];
  total_objects_detected: number;
  processing_summary: {
    total_files_uploaded: number;
    total_files_processed: number;
    total_objects_detected: number;
    average_processing_time: number;
  };
}

interface ImageUploadProps {
  projectId: string;
  onUploadComplete?: (results: UploadResponse) => void;
}

interface FileWithPreview extends File {
  preview?: string;
}

export default function ImageUpload({ projectId, onUploadComplete }: ImageUploadProps) {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<UploadResponse | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const maxFiles = 10;
  const maxFileSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];

  const validateFile = (file: File): string | null => {
    if (!allowedTypes.includes(file.type)) {
      return `${file.name}: Unsupported file type. Please use JPEG, PNG, BMP, or TIFF.`;
    }
    if (file.size > maxFileSize) {
      return `${file.name}: File too large. Maximum size is 10MB.`;
    }
    if (file.size === 0) {
      return `${file.name}: File is empty.`;
    }
    return null;
  };

  const handleFiles = useCallback((newFiles: FileList | File[]) => {
    const fileArray = Array.from(newFiles);
    
    // Validate total number of files
    if (files.length + fileArray.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed. You currently have ${files.length} files.`);
      return;
    }

    // Validate each file
    const validFiles: FileWithPreview[] = [];
    const errors: string[] = [];

    fileArray.forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors.push(error);
      } else {
        const fileWithPreview = file as FileWithPreview;
        fileWithPreview.preview = URL.createObjectURL(file);
        validFiles.push(fileWithPreview);
      }
    });

    if (errors.length > 0) {
      setError(errors.join('\n'));
      return;
    }

    setFiles(prev => [...prev, ...validFiles]);
    setError(null);
  }, [files.length]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  }, [handleFiles]);

  const removeFile = (index: number) => {
    setFiles(prev => {
      const newFiles = [...prev];
      if (newFiles[index].preview) {
        URL.revokeObjectURL(newFiles[index].preview!);
      }
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      setError('Please select at least one image to upload.');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/projects/${projectId}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result: UploadResponse = await response.json();
      setResults(result);
      
      if (onUploadComplete) {
        onUploadComplete(result);
      }

      // Clean up file previews
      files.forEach(file => {
        if (file.preview) {
          URL.revokeObjectURL(file.preview);
        }
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const proceedToDashboard = () => {
    router.push(`/projects/${projectId}/dashboard`);
  };

  // Show results if upload completed
  if (results) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
            <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Complete!</h2>
          <p className="text-gray-600">
            Successfully processed {results.processing_summary.total_files_processed} images
          </p>
        </div>

        {/* Processing Summary */}
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {results.processing_summary.total_files_uploaded}
              </div>
              <div className="text-sm text-gray-600">Files Uploaded</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {results.processing_summary.total_files_processed}
              </div>
              <div className="text-sm text-gray-600">Files Processed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {results.total_objects_detected}
              </div>
              <div className="text-sm text-gray-600">Objects Detected</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {results.processing_summary.average_processing_time.toFixed(1)}s
              </div>
              <div className="text-sm text-gray-600">Avg Processing Time</div>
            </div>
          </div>
        </div>

        {/* Detection Results */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Detection Results</h3>
          <div className="space-y-4">
            {results.detection_results.map((result, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-900">{result.filename}</h4>
                  <span className="text-sm text-gray-500">
                    {result.processing_time.toFixed(2)}s
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-2">
                  {result.detected_objects.length} objects detected
                </div>
                {result.detected_objects.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {result.detected_objects.map((obj, objIndex) => (
                      <span
                        key={objIndex}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {obj.name} ({(obj.confidence * 100).toFixed(1)}%)
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => {
              setResults(null);
              setFiles([]);
            }}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Upload More Images
          </button>
          <button
            onClick={proceedToDashboard}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            View Progress Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Room Images</h2>
        <p className="text-gray-600">
          Upload 4-5 images of your rooms for AI-powered object detection and progress analysis.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <svg className="h-5 w-5 text-red-400 mr-2 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-red-700 whitespace-pre-line">{error}</div>
          </div>
        </div>
      )}

      {/* Drag and Drop Area */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={allowedTypes.join(',')}
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
        
        <div className="space-y-4">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          
          <div>
            <p className="text-lg text-gray-600">
              Drag and drop your images here, or{' '}
              <button
                type="button"
                className="text-blue-600 hover:text-blue-800 font-medium"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
              >
                browse files
              </button>
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Supports JPEG, PNG, BMP, TIFF • Max {maxFiles} files • Max 10MB each
            </p>
          </div>
        </div>
      </div>

      {/* File Preview */}
      {files.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Selected Images ({files.length}/{maxFiles})
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {files.map((file, index) => (
              <div key={index} className="relative group">
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={file.preview}
                    alt={file.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
                  disabled={uploading}
                >
                  ×
                </button>
                <p className="mt-2 text-sm text-gray-600 truncate">{file.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Progress */}
      {uploading && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Processing images...</span>
            <span className="text-sm text-gray-600">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-2">
            This may take a few moments while we analyze your images with AI...
          </p>
        </div>
      )}

      {/* Upload Button */}
      <div className="mt-8 flex justify-center">
        <button
          onClick={uploadFiles}
          disabled={files.length === 0 || uploading}
          className="px-8 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? 'Processing...' : `Upload ${files.length} Image${files.length !== 1 ? 's' : ''}`}
        </button>
      </div>
    </div>
  );
}