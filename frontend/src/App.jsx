import './App.css'

import ProcessMetrics from './ProcessMetrics'
import ProcessForm from './ProcessForm'


function App() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'flex-start',
      gap: 32,
      padding: '2.5rem 0',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0fdfa 0%, #e0e7ff 100%)',
    }}>
      <div style={{ flex: 1, maxWidth: 480 }}>
        <ProcessForm />
      </div>
      <div style={{ flex: 2, minWidth: 400 }}>
        <ProcessMetrics />
      </div>
    </div>
  );
}

export default App
