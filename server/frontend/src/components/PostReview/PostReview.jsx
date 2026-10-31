import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getJSON, postJSON } from "../../api.js";
import { useAuth } from "../../auth.jsx";

const EMPTY_FORM = {
  purchase: false,
  purchase_date: "",
  car_make: "",
  car_model: "",
  car_year: "",
  review: "",
};

export default function PostReview() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();

  const [dealer, setDealer] = useState(null);
  const [carMakes, setCarMakes] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getJSON(`/get_dealer/${id}`).then(setDealer).catch(() => setDealer(null));
    getJSON("/get_cars").then(setCarMakes).catch(() => setCarMakes([]));
  }, [id]);

  const modelsForMake = useMemo(() => {
    const make = carMakes.find((item) => item.CarMake === form.car_make);
    return make ? make.CarModels : [];
  }, [carMakes, form.car_make]);

  function update(field, value) {
    setForm((current) => {
      const next = { ...current, [field]: value };
      if (field === "car_make") next.car_model = "";
      return next;
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!form.review.trim()) {
      setError("Please write your review before submitting.");
      return;
    }

    setSubmitting(true);
    try {
      await postJSON("/add_review", {
        dealer_id: Number(id),
        ...form,
        purchase: Boolean(form.purchase),
      });
      navigate(`/dealer/${id}?reviewed=1`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading) {
    return <div className="card empty-state">Checking your session…</div>;
  }

  if (!user) {
    return (
      <div className="card empty-state">
        <h2>Please sign in to review a dealer</h2>
        <p className="muted">
          Reviews are linked to your account so other customers know they are genuine.
        </p>
        <div className="dealer-actions">
          <Link className="btn btn-primary" to="/login">
            Login
          </Link>
          <Link className="btn btn-ghost" to="/register">
            Create an account
          </Link>
        </div>
      </div>
    );
  }

  return (
    <section className="form-page">
      <div className="page-heading">
        <div>
          <h1>Post a review</h1>
          <p className="muted">
            {dealer ? dealer.full_name : `Dealer ${id}`} &middot; signed in as{" "}
            <strong>{user.userName}</strong>
          </p>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <form className="card form-card" onSubmit={handleSubmit}>
        <div className="form-row">
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.purchase}
              onChange={(e) => update("purchase", e.target.checked)}
            />
            <span>I purchased a vehicle from this dealer</span>
          </label>
        </div>

        <div className="form-grid">
          <div className="form-row">
            <label htmlFor="purchase_date">Purchase date</label>
            <input
              id="purchase_date"
              type="date"
              value={form.purchase_date}
              onChange={(e) => update("purchase_date", e.target.value)}
              disabled={!form.purchase}
            />
          </div>

          <div className="form-row">
            <label htmlFor="car_make">Car make</label>
            <select
              id="car_make"
              value={form.car_make}
              onChange={(e) => update("car_make", e.target.value)}
            >
              <option value="">Select a make</option>
              {carMakes.map((make) => (
                <option key={make.id} value={make.CarMake}>
                  {make.CarMake}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label htmlFor="car_model">Car model</label>
            <select
              id="car_model"
              value={form.car_model}
              onChange={(e) => update("car_model", e.target.value)}
              disabled={!modelsForMake.length}
            >
              <option value="">Select a model</option>
              {modelsForMake.map((model) => (
                <option key={model.id} value={model.name}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label htmlFor="car_year">Car year</label>
            <input
              id="car_year"
              type="number"
              min="1950"
              max="2030"
              value={form.car_year}
              onChange={(e) => update("car_year", e.target.value)}
              placeholder="2024"
            />
          </div>
        </div>

        <div className="form-row">
          <label htmlFor="review">Your review</label>
          <textarea
            id="review"
            rows="6"
            value={form.review}
            onChange={(e) => update("review", e.target.value)}
            placeholder="Tell other customers about your experience…"
            required
          />
          <p className="hint">
            Your review is scored by the sentiment analysis service before it is saved.
          </p>
        </div>

        <div className="form-actions">
          <button className="btn btn-accent" type="submit" disabled={submitting}>
            {submitting ? "Submitting…" : "Submit review"}
          </button>
          <Link className="btn btn-ghost" to={`/dealer/${id}`}>
            Cancel
          </Link>
        </div>
      </form>
    </section>
  );
}
