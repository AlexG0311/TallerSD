import { useState } from 'react';

function ProcessMetrics() {
  const [processId, setProcessId] = useState('');
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastFinishedId, setLastFinishedId] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Si el proceso ya fue consultado y está terminado, mostrar error
    if (
      lastFinishedId === processId &&
      data &&
      ["COMPLETADO", "COMPLETADO_CON_ERRORES", "FALLIDO"].includes(data?.informacion_general?.status)
    ) {
      setError('Este proceso ya fue consultado y está finalizado. Por favor, ingresa otro ID.');
      return;
    }

    setLoading(true);
    setData(null);
    try {
      const res = await fetch(`http://127.0.0.1:8000/process/${processId}`);
      if (!res.ok) throw new Error('No se encontró el proceso');
      const json = await res.json();
      setData(json);
      // Si el proceso está terminado, guardar el ID
      if (["COMPLETADO", "COMPLETADO_CON_ERRORES", "FALLIDO"].includes(json.informacion_general.status)) {
        setLastFinishedId(processId);
      } else {
        setLastFinishedId(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Animación de carga (spinner)
  const Spinner = () => (
    <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '1.5rem 0'}}>
      <div style={{
        width: 36, height: 36, border: '4px solid #6366f1', borderTop: '4px solid #06b6d4', borderRadius: '50%',
        animation: 'spin 1s linear infinite',
      }} />
      <style>{`@keyframes spin { 0% { transform: rotate(0deg);} 100% {transform: rotate(360deg);} }`}</style>
    </div>
  );

  // Badge de estado
  const StatusBadge = ({ status }) => {
    let color = '#6366f1', bg = '#eef2ff', icon = '⏳';
    if (status === 'COMPLETADO') { color = '#10b981'; bg = '#ecfdf5'; icon = '✅'; }
    else if (status === 'COMPLETADO_CON_ERRORES') { color = '#f59e42'; bg = '#fff7ed'; icon = '⚠️'; }
    else if (status === 'FALLIDO') { color = '#ef4444'; bg = '#fef2f2'; icon = '❌'; }
    return (
      <span style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        background: bg, color, fontWeight: 600, borderRadius: 16, fontSize: 15, padding: '0.25em 0.9em',
        border: `1.5px solid ${color}`
      }}>{icon} {status.replace(/_/g, ' ')}</span>
    );
  };

  // Íconos para etapas
  const etapaIcon = {
    descarga: '⬇️',
    redimension: '📐',
    formato: '🖼️',
    marca_agua: '💧',
  };

  return (
    <div style={{
      maxWidth: 750,
      margin: '2.5rem auto',
      padding: '2.5rem 2rem',
      background: 'linear-gradient(135deg, #f0fdfa 0%, #e0e7ff 100%)',
      borderRadius: 22,
      boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.18)',
      border: '1.5px solid #e0e7ff',
      fontFamily: 'Segoe UI, sans-serif',
      position: 'relative',
      overflow: 'hidden',
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
        <span style={{color: '#6366f1'}}>Consulta de Estado</span> y Métricas
      </h2>
      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 12,
          marginBottom: 32,
          background: '#fff',
          borderRadius: 14,
          boxShadow: '0 2px 12px 0 rgba(99,102,241,0.10)',
          padding: '1.3rem 1.1rem',
          zIndex: 1,
          position: 'relative',
        }}
      >
        <span style={{fontSize: 22, color: '#6366f1', marginRight: 4}}>🔎</span>
        <input
          type="text"
          placeholder="ID de procesamiento"
          value={processId}
          onChange={e => setProcessId(e.target.value)}
          style={{
            padding: '0.8rem 1.1rem',
            width: 320,
            border: '1.5px solid #6366f1',
            borderRadius: 9,
            fontSize: 17,
            outline: 'none',
            transition: 'border 0.2s',
            boxShadow: '0 1px 4px 0 rgba(99,102,241,0.09)',
          }}
          required
        />
        <button
          type="submit"
          style={{
            padding: '0.8rem 1.7rem',
            background: 'linear-gradient(90deg, #6366f1 0%, #06b6d4 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: 9,
            fontWeight: 700,
            fontSize: 17,
            cursor: 'pointer',
            boxShadow: '0 2px 12px 0 rgba(99,102,241,0.13)',
            letterSpacing: 1,
            transition: 'background 0.2s',
            display: 'flex', alignItems: 'center', gap: 7
          }}
        >
          <span style={{fontSize: 19}}>🚀</span> Consultar
        </button>
      </form>
      {loading && <Spinner />}
      {error && <p style={{color: '#ef4444', textAlign: 'center', fontWeight: 500}}>{error}</p>}
      {data && (
        <div style={{marginTop: 24, zIndex: 1, position: 'relative'}}>
          <div style={{
            background: 'linear-gradient(90deg, #f0fdfa 0%, #e0e7ff 100%)',
            borderRadius: 14,
            padding: '1.7rem 1.3rem',
            marginBottom: 24,
            boxShadow: '0 1px 8px 0 rgba(99,102,241,0.09)'
          }}>
            <h3 style={{color: '#6366f1', marginBottom: 12, fontWeight: 800, fontSize: 21, letterSpacing: 0.5}}>Información General</h3>
            <ul style={{listStyle: 'none', padding: 0, fontSize: 17, display: 'flex', flexWrap: 'wrap', gap: 18}}>
              <li><b>ID:</b> <span style={{color: '#0ea5e9'}}>{data.informacion_general.process_id}</span></li>
              <li><b>Estado:</b> <StatusBadge status={data.informacion_general.status} /></li>
              <li><b>Inicio:</b> {data.informacion_general.start_time || 'N/A'}</li>
              <li><b>Fin:</b> {data.informacion_general.end_time || 'N/A'}</li>
              <li><b>Tiempo total:</b> {data.informacion_general.tiempo_total_ejecucion ?? 'N/A'} seg</li>
            </ul>
          </div>
          <div style={{
            background: '#fff',
            borderRadius: 14,
            padding: '1.7rem 1.3rem',
            marginBottom: 24,
            boxShadow: '0 1px 8px 0 rgba(99,102,241,0.09)'
          }}>
            <h3 style={{color: '#06b6d4', marginBottom: 12, fontWeight: 800, fontSize: 21, letterSpacing: 0.5}}>Métricas por Etapa</h3>
            <div style={{display: 'flex', flexWrap: 'wrap', gap: 18}}>
              {Object.entries(data.metricas_por_etapa).map(([etapa, m]) => (
                <div key={etapa} style={{
                  flex: '1 1 220px',
                  background: 'linear-gradient(90deg, #e0e7ff 0%, #f0fdfa 100%)',
                  borderRadius: 12,
                  padding: '1.1rem 0.9rem',
                  marginBottom: 8,
                  boxShadow: '0 1px 6px 0 rgba(99,102,241,0.08)',
                  position: 'relative',
                  minWidth: 210
                }}>
                  <span style={{position: 'absolute', top: 12, right: 16, fontSize: 22, opacity: 0.7}}>{etapaIcon[etapa]}</span>
                  <b style={{color: '#6366f1', fontSize: 16}}>{etapa.charAt(0).toUpperCase() + etapa.slice(1)}:</b>
                  <ul style={{listStyle: 'none', padding: 0, fontSize: 15, marginTop: 6}}>
                    <li>Total procesados: <b style={{color: '#10b981'}}>{m.total_procesados}</b></li>
                    <li>Total fallidos: <b style={{color: '#ef4444'}}>{m.total_fallidos}</b></li>
                    <li>Tiempo total acumulado: <b>{m.tiempo_total_acumulado}</b> seg</li>
                    <li>Tiempo promedio por archivo: <b>{m.tiempo_promedio}</b> seg</li>
                  </ul>
                </div>
              ))}
            </div>
          </div>
          <div style={{
            background: 'linear-gradient(90deg, #e0e7ff 0%, #f0fdfa 100%)',
            borderRadius: 14,
            padding: '1.7rem 1.3rem',
            boxShadow: '0 1px 8px 0 rgba(99,102,241,0.09)'
          }}>
            <h3 style={{color: '#6366f1', marginBottom: 12, fontWeight: 800, fontSize: 21, letterSpacing: 0.5}}>Resumen Global</h3>
            <ul style={{listStyle: 'none', padding: 0, fontSize: 17, display: 'flex', flexWrap: 'wrap', gap: 18}}>
              <li>Total archivos recibidos: <b style={{color: '#0ea5e9'}}>{data.resumen_global.total_archivos_recibidos}</b></li>
              <li>Total archivos con error: <b style={{color: '#ef4444'}}>{data.resumen_global.total_archivos_con_error}</b></li>
              <li>Porcentaje de éxito: <b style={{color: '#10b981'}}>{data.resumen_global.porcentaje_exito}%</b></li>
              <li>Porcentaje de fallo: <b style={{color: '#ef4444'}}>{data.resumen_global.porcentaje_fallo}%</b></li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProcessMetrics;
