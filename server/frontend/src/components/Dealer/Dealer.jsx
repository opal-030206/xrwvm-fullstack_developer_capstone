import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getJSON } from "../../api.js";
import { useAuth } from "../../auth.jsx";

const SENTIMENT_LABEL = {
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
};

export default function Dealer() {
  const { id } = useParams();
  const { user } = useAuth();

  const [dealer, setDealer] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");

    Promise.all([
      getJSON(`/get_dealer/${id}`),
      getJSON(`/reviews/dealer/${id}`),
    ])
      .then(([dealerData, reviewData]) => {
        if (cancelled) return;
        setDealer(dealerData);
        setReviews(reviewData);
      })
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return <div className="card empty-state">Loading dealer details…</div>;
  }

  if (error) {
    return (
      <div className="card empty-state">
        <h2>Dealer not available</h2>
        <p className="muted">{error}</p>
        <Link className="btn btn-primary" to="/">
          Back to all dealers
        </Link>
      </div>
    );
  }

  const positive = reviews.filter((r) => r.sentiment === "positive").length;

  return (
    <section>
      <nav className="breadcrumb" aria-label="Breadcrumb">
        <Link to="/">Home</Link>
        <span>/</span>
        <span>Dealer {dealer.id}</span>
      </nav>

      <article className="dealer-hero">
        <img
          className="dealer-hero-image"
          src={`/static/images/${dealer.image}`}
          alt={`${dealer.full_name} showroom`}
        />
        <div className="dealer-hero-body">
          <p className="eyebrow">Dealer ID {dealer.id}</p>
          <h1>{dealer.full_name}</h1>
          <p className="dealer-address">
            {dealer.address}
            <br />
            {dealer.city}, {dealer.state} {dealer.zip}
          </p>
          <p className="muted">
            Coordinates: {dealer.lat}, {dealer.long}
          </p>
          <div className="dealer-actions">
            {user ? (
              <Link className="btn btn-accent" to={`/postreview/${dealer.id}`}>
                Review Dealer
              </Link>
            ) : (
              <Link className="btn btn-primary" to="/login">
                Login to review this dealer
              </Link>
            )}
            <Link className="btn btn-ghost" to="/">
              Back to dealers
            </Link>
          </div>
        </div>
      </article>

      <div className="review-summary">
        <h2>Customer reviews</h2>
        <p className="muted">
          {reviews.length} review(s) &middot; {positive} positive sentiment
        </p>
      </div>

      {reviews.length === 0 ? (
        <div className="card empty-state">
          <p>No reviews for this dealership yet.</p>
          {user && (
            <Link className="btn btn-accent" to={`/postreview/${dealer.id}`}>
              Be the first to review
            </Link>
          )}
        </div>
      ) : (
        <div className="review-list">
          {reviews.map((review) => (
            <article className="review-card" key={review.id}>
              <header className="review-head">
                <div>
                  <h3>{review.name}</h3>
                  <p className="muted small">
                    {review.car_year} {review.car_make} {review.car_model}
                    {review.purchase ? " \u00b7 verified purchase" : ""}
                  </p>
                </div>
                <span className={`badge badge-${review.sentiment}`}>
                  {SENTIMENT_LABEL[review.sentiment] || review.sentiment}
                </span>
              </header>
              <p className="review-text">{review.review}</p>
              <footer className="review-foot muted small">
                {review.purchase_date
                  ? `Purchased ${review.purchase_date}`
                  : `Posted ${new Date(review.created_at).toLocaleDateString()}`}
              </footer>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
