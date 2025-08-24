import { render } from 'solid-js/web';
import App from './App';

// Remove loading state when app starts
document.body.classList.add('app-loaded');

// Render the app
const root = document.getElementById('root');
if (root) {
  render(() => <App />, root);
}

// Register service worker for offline support (optional)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  navigator.serviceWorker.register('/sw.js').catch(console.error);
}