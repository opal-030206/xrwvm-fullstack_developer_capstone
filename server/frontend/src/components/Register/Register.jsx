import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { postJSON } from "../../api.js";
import { useAuth } from "../../auth.jsx";

const INITIAL = {
  userName: "",
  firstName: "",
  lastName: "",
  email: "",
  password: "",
};

export default function Register() {
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const [form, setForm] = useState(INITIAL);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const data = await postJSON("/register", form);
      setUser(data);
      navigate("/");
    } catch (err) {
      setError(err.message || "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="form-page narrow">
      <h1>Sign-up</h1>
      <p className="muted">
        Create your Cars Dealership account to review dealerships.
      </p>

      {error && <div className="alert alert-error">{error}</div>}

      <form className="card form-card" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="register-username">Username</label>
          <input
            id="register-username"
            value={form.userName}
            onChange={(e) => update("userName", e.target.value)}
            autoComplete="username"
            required
          />
        </div>

        <div className="form-grid">
          <div className="form-row">
            <label htmlFor="register-firstname">First Name</label>
            <input
              id="register-firstname"
              value={form.firstName}
              onChange={(e) => update("firstName", e.target.value)}
              autoComplete="given-name"
              required
            />
          </div>

          <div className="form-row">
            <label htmlFor="register-lastname">Last Name</label>
            <input
              id="register-lastname"
              value={form.lastName}
              onChange={(e) => update("lastName", e.target.value)}
              autoComplete="family-name"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <label htmlFor="register-email">Email</label>
          <input
            id="register-email"
            type="email"
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
            autoComplete="email"
            required
          />
        </div>

        <div className="form-row">
          <label htmlFor="register-password">Password</label>
          <input
            id="register-password"
            type="password"
            value={form.password}
            onChange={(e) => update("password", e.target.value)}
            autoComplete="new-password"
            required
          />
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? "Registering…" : "Register"}
          </button>
          <Link className="btn btn-ghost" to="/login">
            Already registered?
          </Link>
        </div>
      </form>
    </section>
  );
}
