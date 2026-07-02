// src/App.tsx
import { AuthProvider } from "./context/AuthContext";
import { AlertProvider } from "./context/AlertContext";
import AppRouter from "./router/AppRouter";

const App = () => (
  <AuthProvider>
    <AlertProvider>
      <AppRouter />
    </AlertProvider>
  </AuthProvider>
);

export default App;