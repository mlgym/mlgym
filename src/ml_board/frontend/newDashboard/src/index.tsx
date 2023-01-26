// external deps
import React             from 'react';
import { createRoot    } from 'react-dom/client';
import { Provider      } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';

// internal deps
import { store         } from './redux/store';
import App               from './app/App';

// styles
import './index.scss';

const container = document.getElementById ('root')!;
const root      = createRoot (container);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
);
