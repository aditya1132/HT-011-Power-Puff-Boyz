import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Import global styles
import './index.css';

// Get the root element
const container = document.getElementById('root');

if (!container) {
  throw new Error(
    'Root element with id "root" not found. ' +
    'This might happen if the HTML template was modified. ' +
    'Please ensure there is a div with id="root" in your public/index.html file.'
  );
}

// Create root and render app
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Performance monitoring
// You can pass a function to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
if (process.env.NODE_ENV === 'development') {
  reportWebVitals(console.log);
} else {
  // In production, you might want to send to analytics service
  // reportWebVitals(sendToAnalytics);
  reportWebVitals();
}

// Enable hot module replacement in development
if (process.env.NODE_ENV === 'development' && module.hot) {
  module.hot.accept('./App', () => {
    const NextApp = require('./App').default;
    root.render(
      <React.StrictMode>
        <NextApp />
      </React.StrictMode>
    );
  });
}

// Register service worker for offline functionality (optional)
// This is disabled by default. To enable, see:
// https://create-react-app.dev/docs/making-a-progressive-web-app/
// if ('serviceWorker' in navigator) {
//   window.addEventListener('load', () => {
//     navigator.serviceWorker.register('/sw.js')
//       .then((registration) => {
//         console.log('SW registered: ', registration);
//       })
//       .catch((registrationError) => {
//         console.log('SW registration failed: ', registrationError);
//       });
//   });
// }

// Global error handling
window.addEventListener('error', (event) => {
  console.error('Global error caught:', event.error);
  // You could send this to an error reporting service
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  // You could send this to an error reporting service
  event.preventDefault();
});
