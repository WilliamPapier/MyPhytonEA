
"use client";

"use client";
import React, { useContext, useState } from "react";
import { notFound, useParams } from "next/navigation";
import { products } from "../products";
import { CartContext } from "@/components/CartProvider";

interface ProductDetailPageProps {
  params: { id: string };
}






export default function ProductDetailPage() {
  const { addToCart } = useContext(CartContext);
  const params = useParams();
  const id = Array.isArray(params.id) ? params.id[0] : params.id;
  const product = products.find((p) => p.id === id);
  const [reviews, setReviews] = useState(product?.reviews || []);
  const [reviewText, setReviewText] = useState("");
  const [reviewAuthor, setReviewAuthor] = useState("");
  const [currency, setCurrency] = useState("ZAR");
  const rates: Record<string, number> = { ZAR: 1, USD: 0.055, EUR: 0.051, GBP: 0.044 };
  const currencySymbols: Record<string, string> = { ZAR: "R", USD: "$", EUR: "€", GBP: "£" };
  if (!product) return notFound();

  const handleReviewSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (reviewText.trim() && reviewAuthor.trim()) {
      setReviews([
        ...reviews,
        { text: reviewText.trim(), author: reviewAuthor.trim() },
      ]);
      setReviewText("");
      setReviewAuthor("");
    }
  };

  return (
    <div className="min-h-screen bg-[#181A20] text-white flex flex-col items-center py-12 px-4">
      <div className="max-w-4xl w-full bg-[#23272F] rounded-2xl shadow-lg p-8 flex flex-col md:flex-row gap-8">
        {/* Product Image */}
        <div className="flex-1 flex items-center justify-center">
          <img
            src={product.image}
            alt={product.name}
            className="rounded-xl shadow-xl w-full max-w-xs border-4 border-[#FFD700]"
          />
        </div>
        {/* Product Details */}
        <div className="flex-1 flex flex-col justify-between">
          <div>
            <h1 className="text-3xl font-bold text-[#FFD700] mb-2">{product.name}</h1>
            <p className="text-lg text-[#FFC857] mb-4">{product.description}</p>
            <ul className="mb-6 space-y-2 text-base text-gray-200">
              {product.features.map((feature, i) => (
                <li key={i}>✔️ {feature}</li>
              ))}
            </ul>
            <div className="mb-6">
              <div className="flex gap-2 items-center mb-2">
                <label htmlFor="currency" className="text-[#FFD700] font-semibold">Currency:</label>
                <select
                  id="currency"
                  value={currency}
                  onChange={e => setCurrency(e.target.value)}
                  className="px-2 py-1 rounded border border-[#FFD700] bg-[#181A20] text-white"
                >
                  <option value="ZAR">ZAR</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
              <span className="text-2xl font-bold text-[#FFD700]">{currencySymbols[currency]}{(product.price * rates[currency]).toFixed(2)}</span>
              {product.oldPrice && (
                <span className="ml-2 text-base text-gray-400 line-through">{currencySymbols[currency]}{(product.oldPrice * rates[currency]).toFixed(2)}</span>
              )}
              {product.discount && (
                <span className="ml-4 text-green-400 font-semibold">{product.discount}</span>
              )}
            </div>
            <button
              className="w-full py-3 rounded-lg bg-[#FFD700] text-[#181A20] font-bold text-lg shadow-lg hover:bg-[#FFC857] transition mb-3"
              onClick={() => addToCart({ name: product.name, price: product.price })}
            >
              Add to Cart
            </button>
            {/* Download Sample Button */}
            <a
              href="/sample_download.pdf"
              download
              className="w-full block py-3 rounded-lg bg-[#22d3ee] border-2 border-[#FFD700] text-[#181A20] font-bold text-lg shadow-lg hover:bg-[#FFD700] hover:text-[#181A20] transition text-center mb-2"
            >
              &#8681; Download Free Sample
            </a>
          </div>
          <div className="mt-8 text-sm text-gray-400">
            <p>Includes: {product.includes}</p>
            <p className="mt-2">Secure checkout • Instant delivery • 24/7 support</p>
          </div>
        </div>
      </div>
      {/* Reviews */}
      <div className="max-w-2xl w-full mt-12 bg-[#23272F] rounded-xl p-6 shadow-md">
        <h2 className="text-xl font-bold text-[#FFD700] mb-4">What Buyers Say</h2>
        <div className="space-y-4">
          {reviews.length > 0 ? (
            reviews.map((review, i) => (
              <div key={i} className="bg-[#181A20] rounded-lg p-4">
                <p className="text-base text-white">“{review.text}”</p>
                <span className="block mt-2 text-xs text-[#FFC857]">— {review.author}</span>
              </div>
            ))
          ) : (
            <p className="text-gray-400">No reviews yet. Be the first to review this product!</p>
          )}
        </div>
        {/* Review Submission Form */}
        <form onSubmit={handleReviewSubmit} className="mt-8 flex flex-col gap-4">
          <textarea
            className="w-full p-3 rounded-lg bg-[#181A20] border border-[#FFD700] text-white resize-none"
            rows={3}
            placeholder="Write your review..."
            value={reviewText}
            onChange={e => setReviewText(e.target.value)}
            required
          />
          <input
            className="w-full p-3 rounded-lg bg-[#181A20] border border-[#FFD700] text-white"
            type="text"
            placeholder="Your name"
            value={reviewAuthor}
            onChange={e => setReviewAuthor(e.target.value)}
            required
          />
          <button
            type="submit"
            className="py-2 px-6 rounded-lg bg-[#FFD700] text-[#181A20] font-bold text-base shadow-lg hover:bg-[#FFC857] transition self-end"
          >
            Submit Review
          </button>
        </form>
      </div>
    </div>
  );
}
