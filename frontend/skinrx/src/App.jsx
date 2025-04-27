import React, { useState } from 'react';
import { Loader2 } from 'lucide-react';

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/predict', { method: 'POST', body: formData });
      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      alert('Prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-6 space-y-6">
        <h1 className="text-2xl font-bold text-center">Face Skin Analyzer</h1>

        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none"
        />

        <button
          onClick={handleSubmit}
          disabled={!file || loading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
        >
          {loading && <Loader2 className="animate-spin w-5 h-5 mr-2" />}
          Analyze
        </button>

        {result && (
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-xl font-semibold">Result: {result.label}</h2>
            <p className="mt-2">Confidence: {(result.confidence * 100).toFixed(1)}%</p>

            {result.recommendations && result.recommendations.length > 0 && (
              <>
                <h3 className="mt-4 text-lg font-semibold">Recommended Solutions</h3>
                <div className="grid grid-cols-2 gap-4 mt-2">
                  {result.recommendations.map((rec, idx) => (
                    <a
                      key={idx}
                      href={rec.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block rounded-lg overflow-hidden shadow hover:shadow-lg transition-shadow"
                    >
                      <img
                        src={rec.image}
                        alt="Product"
                        className="w-full h-32 object-cover"
                      />
                    </a>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}