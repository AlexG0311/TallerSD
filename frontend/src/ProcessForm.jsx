import React, { useState } from 'react';

const defaultWorkers = {
  descarga: 8,
  redimension: 4,
  formato: 4,
  marca_agua: 4,
};


export default function ProcessForm() {
  const [urls, setUrls] = useState('');
  const [workers, setWorkers] = useState(defaultWorkers);
  const [loading, setLoading] = useState(false);
  const [processId, setProcessId] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setWorkers({
      ...workers,
      [e.target.name]: Number(e.target.value),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setProcessId(null);
    const urlList = urls
      .split(/[\n,]+/)
      .map((u) => u.trim())
      .filter((u) => u.length > 0);
    try {
      const res = await fetch('http://127.0.0.1:8000/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: urlList, workers }),
      });
      const data = await res.json();
      // Mostrar solo el ID del proceso si existe
      if (data && data.process_id) {
        setProcessId(data.process_id);
      } else if (typeof data === 'string') {
        setProcessId(data);
      } else {
        setError('Respuesta inesperada del servidor');
      }
    } catch (err) {
      setError('Error al enviar la solicitud');
    } finally {
      setLoading(false);
    }
  };

  // Spinner animado
  const Spinner = () => (
    <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '1.5rem 0'}}>
      <div style={{
        width: 36, height: 36, border: '4px solid #6366f1', borderTop: '4px solid #06b6d4', borderRadius: '50%',
        animation: 'spin 1s linear infinite',
      }} />
      <style>{`@keyframes spin { 0% { transform: rotate(0deg);} 100% {transform: rotate(360deg);} }`}</style>
    </div>
  );

  return (
    <div style={{
      maxWidth: 480,
      margin: '0 auto',
      padding: '2.5rem 2rem',
      background: 'linear-gradient(135deg, #f0fdfa 0%, #e0e7ff 100%)',
      borderRadius: 22,
      boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.18)',
      border: '1.5px solid #e0e7ff',
      fontFamily: 'Segoe UI, sans-serif',
      position: 'relative',
      overflow: 'hidden',
      minWidth: 320,
    }}>
      {/* Círculos decorativos */}
      <div style={{position: 'absolute', top: -60, right: -60, width: 160, height: 160, background: 'radial-gradient(circle, #6366f1 0%, #e0e7ff 80%)', opacity: 0.13, borderRadius: '50%', zIndex: 0}} />
      <div style={{position: 'absolute', bottom: -50, left: -50, width: 120, height: 120, background: 'radial-gradient(circle, #06b6d4 0%, #f0fdfa 80%)', opacity: 0.13, borderRadius: '50%', zIndex: 0}} />
      <h2 style={{
        textAlign: 'center',
        color: '#2d3a4a',
        fontWeight: 800,
        letterSpacing: 1,
        marginBottom: 32,
        fontSize: 30,
        zIndex: 1,
        position: 'relative',
        textShadow: '0 2px 8px #e0e7ff',
      }}>
        <span style={{color: '#6366f1'}}>Procesar</span> Imágenes
      </h2>
      <form onSubmit={handleSubmit} style={{
        background: '#fff',
        borderRadius: 14,
        boxShadow: '0 2px 12px 0 rgba(99,102,241,0.10)',
        padding: '1.3rem 1.1rem',
        zIndex: 1,
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        gap: 18,
      }}>
        <label style={{fontWeight: 600, color: '#6366f1', fontSize: 16, marginBottom: 2}}>
          URLs de imágenes
          <textarea
            value={urls}
            onChange={(e) => setUrls(e.target.value)}
            rows={5}
            style={{ width: '100%', marginTop: 6, marginBottom: 8, borderRadius: 8, border: '1.5px solid #6366f1', padding: 8, fontSize: 15, outline: 'none', resize: 'vertical' }}
            placeholder="https://ejemplo.com/imagen1.jpg, https://ejemplo.com/imagen2.jpg"
          />
        </label>
        <div style={{ display: 'flex', gap: 16, marginBottom: 8 }}>
          {Object.keys(workers).map((key) => (
            <label key={key} style={{ flex: 1, fontWeight: 600, color: '#06b6d4', fontSize: 15 }}>
              {key.charAt(0).toUpperCase() + key.slice(1)}
              <input
                type="number"
                name={key}
                min={1}
                value={workers[key]}
                onChange={handleChange}
                style={{ width: '100%', borderRadius: 7, border: '1.5px solid #06b6d4', padding: 5, fontSize: 15, marginTop: 3 }}
              />
            </label>
          ))}
        </div>
        <button type="submit" disabled={loading} style={{
          width: '100%',
          padding: '0.8rem 0',
          background: 'linear-gradient(90deg, #6366f1 0%, #06b6d4 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: 9,
          fontWeight: 700,
          fontSize: 17,
          cursor: loading ? 'not-allowed' : 'pointer',
          letterSpacing: 1,
          transition: 'background 0.2s',
          marginTop: 8,
        }}>
          {loading ? 'Procesando...' : 'Enviar'}
        </button>
        {error && <div style={{ color: '#ef4444', marginTop: 6, fontWeight: 500, textAlign: 'center' }}>{error}</div>}
        {loading && <Spinner />}
        {processId && (
          <div style={{
            marginTop: 16,
            background: 'linear-gradient(90deg, #f0fdfa 0%, #e0e7ff 100%)',
            padding: '1.1rem 0.9rem',
            borderRadius: 12,
            fontSize: 18,
            color: '#6366f1',
            fontWeight: 700,
            textAlign: 'center',
            letterSpacing: 1,
            boxShadow: '0 1px 6px 0 rgba(99,102,241,0.08)',
            border: '1.5px solid #e0e7ff',
          }}>
            ID del proceso: <span style={{color: '#0ea5e9'}}>{processId}</span>
          </div>
        )}
      </form>
    </div>
  );
}
