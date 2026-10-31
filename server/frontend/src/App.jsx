import { Link, Route, Routes, useNavigate } from "react-router-dom";

import { postJSON } from "./api.js";
import { useAuth } from "./auth.jsx";
import Header from "./components/Header/Header.jsx";
import Dealers from "./components/Dealers/Dealers.jsx";
import Dealer from "./components/Dealer/Dealer.jsx";
import PostReview from "./components/PostReview/PostReview.jsx";
import Login from "./components/Login/Login.jsx";
import Register from "./components/Register/Register.jsx";

function NotFound() {
  return (
    <section className="card empty-state">
      <h2>Page not found</h2>
      <p>The page you asked for does not exist or has moved.</p>
      <Link className="btn btn-primary" to="/">
        Back to all dealers
      </Link>
    </section>
  );
}

export default function App() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await postJSON("/logout", {});
    } finally {
      setUser(null);
      navigate("/");
    }
  }

  return (
    <div className="app-shell">
      <Header user={user} onLogout={handleLogout} />
      <main className="container">
        <Routes>
          <Route path="/" element={<Dealers />} />
          <Route path="/dealers/:state" element={<Dealers />} />
          <Route path="/dealer/:id" element={<Dealer />} />
          <Route path="/postreview/:id" element={<PostReview />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <footer className="site-footer">
        <p>Cars Dealership &middot; National car retailer across the United States</p>
        <p className="muted">
          Django + React + Flask sentiment analysis &middot; deployed as containers
        </p>
      </footer>
    </div>
  );
}
