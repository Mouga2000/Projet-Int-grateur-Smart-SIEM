// src/App.tsx
import { AuthProvider } from "./context/AuthContext";
import AppRouter from "./router/AppRouter";

const App = () => (
  <AuthProvider>
    <AppRouter />
  </AuthProvider>
);

export default App;