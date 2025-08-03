'use client';

import { useState, useRef, useCallback } from 'react';
import { Camera, Upload, Scan, X } from 'lucide-react';
import Webcam from 'react-webcam';
import { getAuthHeaders, getUserToken } from '@/utils/userToken';

interface BarcodeScannerProps {
  onAnalysis: (result: any) => void;
  onLoading: (loading: boolean) => void;
}

export default function BarcodeScanner({ onAnalysis, onLoading }: BarcodeScannerProps) {
  const [isScanning, setIsScanning] = useState(false);
  const [barcode, setBarcode] = useState('');
  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const analyzeBarcode = async (barcodeValue: string) => {
    onLoading(true);
    try {
      const authHeaders = await getAuthHeaders();
      const response = await fetch('http://localhost:8000/analyze/barcode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders,
        },
        body: JSON.stringify({
          barcode: barcodeValue,
        }),
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const responseText = await response.text();
          try {
            const errorData = JSON.parse(responseText);
            errorMessage = errorData.detail || errorMessage;
          } catch (jsonError) {
            // If JSON parsing fails, provide user-friendly messages based on status code
            if (response.status === 400) {
              errorMessage = 'Invalid barcode format. Please check the barcode and try again.';
            } else if (response.status === 404) {
              errorMessage = 'No product found for this barcode. Please verify the barcode is correct.';
            } else if (response.status === 500) {
              errorMessage = 'Server error occurred. Please try again.';
            } else {
              errorMessage = responseText || errorMessage;
            }
          }
        } catch (readError) {
          console.warn('Failed to read error response:', readError);
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      onAnalysis(result);
    } catch (error) {
      console.error('Barcode analysis failed:', error);
      onAnalysis({
        success: false,
        error: error instanceof Error ? error.message : 'Barcode analysis failed',
      });
    } finally {
      onLoading(false);
    }
  };

  const capturePhoto = useCallback(async () => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) return;

    onLoading(true);
    try {
      // Convert base64 data URL to blob using fetch (simpler and more reliable)
      const response = await fetch(imageSrc);
      const blob = await response.blob();

      // Ensure it's a JPEG blob with proper MIME type
      const jpegBlob = new Blob([blob], { type: 'image/jpeg' });

      console.log('Image blob size:', jpegBlob.size, 'type:', jpegBlob.type);

      const formData = new FormData();
      formData.append('file', jpegBlob, 'barcode.jpg');

      const userToken = await getUserToken();
      const analysisResponse = await fetch('http://localhost:8000/analyze/image', {
        method: 'POST',
        headers: {
          'X-User-Token': userToken,
          // Don't set Content-Type for FormData - browser will set it automatically with boundary
        },
        body: formData,
      });

      if (!analysisResponse.ok) {
        let errorMessage = `HTTP error! status: ${analysisResponse.status}`;
        try {
          const responseText = await analysisResponse.text();
          try {
            const errorData = JSON.parse(responseText);
            errorMessage = errorData.detail || errorMessage;
          } catch (jsonError) {
            // If JSON parsing fails, use the raw text
            errorMessage = responseText || errorMessage;
          }
        } catch (readError) {
          console.warn('Failed to read error response:', readError);
        }
        throw new Error(errorMessage);
      }

      const result = await analysisResponse.json();
      onAnalysis(result);
      setIsScanning(false);
    } catch (error) {
      console.error('Camera capture analysis failed:', error);
      onAnalysis({
        success: false,
        error: error instanceof Error ? error.message : 'Camera capture failed',
      });
    } finally {
      onLoading(false);
    }
  }, [onAnalysis, onLoading]);

  const validateBarcode = (code: string): { isValid: boolean; error?: string } => {
    const trimmedCode = code.trim();

    // Check if it's empty
    if (!trimmedCode) {
      return { isValid: false, error: 'Please enter a barcode' };
    }

    // Check if it contains only digits (most common barcode format)
    if (!/^\d+$/.test(trimmedCode)) {
      return { isValid: false, error: 'Barcode should contain only numbers' };
    }

    // Check common barcode lengths (UPC, EAN, etc.)
    const validLengths = [8, 12, 13, 14]; // UPC-A, EAN-8, EAN-13, ITF-14
    if (!validLengths.includes(trimmedCode.length)) {
      return { isValid: false, error: 'Barcode should be 8, 12, 13, or 14 digits long' };
    }

    return { isValid: true };
  };

  const handleBarcodeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!barcode.trim()) return;

    // Validate barcode before sending to API
    const validation = validateBarcode(barcode);
    if (!validation.isValid) {
      onAnalysis({
        success: false,
        error: validation.error || 'Invalid barcode',
      });
      return;
    }

    analyzeBarcode(barcode.trim());
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    onLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const userToken = await getUserToken();
      const response = await fetch('http://localhost:8000/analyze/image', {
        method: 'POST',
        headers: {
          'X-User-Token': userToken,
          // Don't set Content-Type for FormData - browser will set it automatically with boundary
        },
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);

        // Provide more specific error messages
        let errorMessage = 'Image analysis failed';
        if (response.status === 400) {
          errorMessage = 'No barcode found in the image. Please ensure the barcode is clearly visible and try again.';
        } else if (response.status === 404) {
          errorMessage = 'Product not found for this barcode. The barcode was detected but no product information is available.';
        } else if (response.status === 500) {
          errorMessage = 'Server error occurred during analysis. Please try again.';
        }

        throw new Error(errorMessage);
      }

      const result = await response.json();
      onAnalysis(result);
    } catch (error) {
      console.error('Image analysis failed:', error);
      onAnalysis({
        success: false,
        error: error instanceof Error ? error.message : 'Image analysis failed',
      });
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-4">Barcode Scanner</h3>
        <p className="text-gray-700 mb-6">
          Scan a product barcode using your camera or upload an image containing a barcode.
        </p>
      </div>

      {/* Manual Barcode Entry */}
      <form onSubmit={handleBarcodeSubmit} className="space-y-4">
        <div>
          <label htmlFor="barcode-input" className="block text-sm font-medium text-gray-800 mb-2">
            Enter Barcode Manually
          </label>
          <input
            id="barcode-input"
            type="text"
            value={barcode}
            onChange={(e) => setBarcode(e.target.value)}
            placeholder="e.g., 1234567890123"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-600 text-gray-900"
          />
        </div>
        <button
          type="submit"
          disabled={!barcode.trim()}
          className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
        >
          <Scan className="h-5 w-5" />
          <span>Analyze Barcode</span>
        </button>
      </form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-700">Or scan with camera</span>
        </div>
      </div>

      {/* Camera Scanner */}
      {!isScanning ? (
        <div className="space-y-4">
          <button
            onClick={() => setIsScanning(true)}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors flex items-center justify-center space-x-2"
          >
            <Camera className="h-5 w-5" />
            <span>Open Camera Scanner</span>
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors flex items-center justify-center space-x-2"
          >
            <Upload className="h-5 w-5" />
            <span>Upload Barcode Image</span>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative bg-black rounded-lg overflow-hidden">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              className="w-full h-64 object-cover"
            />
            <div className="absolute inset-0 border-2 border-green-400 rounded-lg pointer-events-none">
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-48 h-32 border-2 border-green-400 rounded-lg">
                <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-green-400"></div>
                <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-green-400"></div>
                <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-green-400"></div>
                <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-green-400"></div>
              </div>
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={capturePhoto}
              className="flex-1 bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors flex items-center justify-center space-x-2"
            >
              <Camera className="h-5 w-5" />
              <span>Capture & Analyze</span>
            </button>
            <button
              onClick={() => setIsScanning(false)}
              className="bg-gray-600 text-white py-3 px-4 rounded-lg hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors flex items-center justify-center"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-bold text-gray-800 mb-2">Tips for better scanning:</h4>
        <ul className="space-y-1 text-sm text-gray-700">
          <li>• Ensure good lighting</li>
          <li>• Hold the camera steady</li>
          <li>• Position the barcode within the frame</li>
          <li>• Make sure the barcode is clearly visible</li>
        </ul>
      </div>
    </div>
  );
}
