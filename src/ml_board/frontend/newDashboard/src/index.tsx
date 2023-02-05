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
  // NOTE: Multiple componentDidMount calls may be caused by using <React.StrictMode> around your component. After removing it double calls are gone. This is intended behavior to help detect unexpected side effects. You can read more about it in the `docs`. It happens only in development environment, while in production componentDidMount is called only once even with <React.StrictMode>
  // However, Strict Mode is also a common problem and this question comes up high in google results.
  // `docs`: https://reactjs.org/docs/strict-mode.html#detecting-unexpected-side-effects

  // <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Provider>
  // </React.StrictMode>
);
