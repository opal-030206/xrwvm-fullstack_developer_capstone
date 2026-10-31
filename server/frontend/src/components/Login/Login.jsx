import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { postJSON } from "../../api.js";
import { useAuth } from "../../auth.jsx";

export default function Login() {
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const data = await postJSON("/login", { userName, password });
      setUser(data);
      navigate("/");
    } catch (err) {
      setError(err.message || "Login failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="form-page narrow">
      <h1>Login</h1>
      <p className="muted">Sign in to review a dealership.</p>

      {error && <div className="alert alert-error">{error}</div>}

      <form className="card form-card" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="login-username">Username</label>
          <input
            id="login-username"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            autoComplete="username"
            required
          />
        </div>

        <div className="form-row">
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Login"}
          </button>
          <Link className="btn btn-ghost" to="/register">
            Need an account?
          </Link>
        </div>
      </form>

      <p className="hint">
        Demo accounts: <code>root / root123</code>, <code>jdoe / jdoe123</code>
      </p>
    </section>
  );
}
