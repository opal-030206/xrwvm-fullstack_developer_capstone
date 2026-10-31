import { Link, NavLink } from "react-router-dom";

export default function Header({ user, onLogout }) {
  return (
    <header className="site-header">
      <div className="header-inner">
        <Link className="brand" to="/">
          <svg
            className="brand-mark"
            viewBox="0 0 24 24"
            aria-hidden="true"
            focusable="false"
          >
            <path
              fill="currentColor"
              d="M5 11l1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11h1a1 1 0 0 1 1 1v4h-2v-1H5v1H3v-4a1 1 0 0 1 1-1h1zm2.1 0h9.8l-1-3H8.1l-1 3zM6.5 12.5a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm11 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"
            />
          </svg>
          <span>Cars Dealership</span>
        </Link>

        <nav className="main-nav" aria-label="Main navigation">
          <NavLink to="/" end>
            Home
          </NavLink>
          <a href="/about">About Us</a>
          <a href="/contact">Contact Us</a>
        </nav>

        <div className="auth-nav">
          {user ? (
            <>
              <span className="user-chip" title="Signed in user">
                {user.userName}
              </span>
              <button className="btn btn-ghost" type="button" onClick={onLogout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link className="btn btn-ghost" to="/login">
                Login
              </Link>
              <Link className="btn btn-primary btn-sm" to="/register">
                Sign-up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
