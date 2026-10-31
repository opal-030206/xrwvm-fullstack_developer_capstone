import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getJSON } from "../../api.js";
import { useAuth } from "../../auth.jsx";

function Stars({ value }) {
  return (
    <span className="stars" aria-label={`${value} out of 5`}>
      {"★".repeat(value)}
      <span className="stars-empty">{"★".repeat(5 - value)}</span>
    </span>
  );
}

export default function Dealers() {
  const { state } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [dealers, setDealers] = useState([]);
  const [allStates, setAllStates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getJSON("/get_dealers")
      .then((data) =>
        setAllStates([...new Set(data.map((dealer) => dealer.state))].sort())
      )
      .catch(() => setAllStates([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError("");
    const endpoint = state
      ? `/get_dealers/${encodeURIComponent(state)}`
      : "/get_dealers";
    getJSON(endpoint)
      .then(setDealers)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [state]);

  const heading = useMemo(
    () => (state ? `Dealers in ${state}` : "Our Dealerships"),
    [state]
  );

  function handleStateChange(event) {
    const value = event.target.value;
    navigate(value ? `/dealers/${encodeURIComponent(value)}` : "/");
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <h1>{heading}</h1>
          <p className="muted">
            {loading ? "Loading dealers..." : `${dealers.length} dealership(s) found`}
            {state ? ` \u00b7 filtered by state` : " \u00b7 nationwide"}
          </p>
        </div>
        <div className="filter">
          <label htmlFor="state-filter">Filter by state</label>
          <select
            id="state-filter"
            value={state || ""}
            onChange={handleStateChange}
          >
            <option value="">All states</option>
            {allStates.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="card empty-state">Loading dealerships…</div>
      ) : dealers.length === 0 ? (
        <div className="card empty-state">
          <h2>No dealers in {state}</h2>
          <Link className="btn btn-primary" to="/">
            Show all dealerships
          </Link>
        </div>
      ) : (
        <div className="dealer-grid">
          {dealers.map((dealer) => (
            <article className="dealer-card" key={dealer.id}>
              <img
                className="dealer-image"
                src={`/static/images/${dealer.image}`}
                alt={`${dealer.full_name} showroom`}
                loading="lazy"
              />
              <div className="dealer-body">
                <h2>{dealer.full_name}</h2>
                <p className="dealer-address">
                  {dealer.address}
                  <br />
                  {dealer.city}, {dealer.state} {dealer.zip}
                </p>
                <div className="dealer-meta">
                  <Stars value={4} />
                  <span className="pill">{dealer.state}</span>
                </div>
                <div className="dealer-actions">
                  <Link className="btn btn-primary btn-sm" to={`/dealer/${dealer.id}`}>
                    View Dealer
                  </Link>
                  {user ? (
                    <Link
                      className="btn btn-accent btn-sm"
                      to={`/postreview/${dealer.id}`}
                    >
                      Review Dealer
                    </Link>
                  ) : (
                    <Link className="btn btn-ghost btn-sm" to="/login">
                      Login to review
                    </Link>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
