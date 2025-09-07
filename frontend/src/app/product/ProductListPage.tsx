"use client";
"use client";
"use client";
import React, { useState } from "react";
import Link from "next/link";
import { products } from "./products";

type Product = {
  id: string;
  name: string;
  description: string;
  features: string[];
  price: number;
  oldPrice?: number;
  discount?: string;
  image: string;
  includes: string;
  reviews: { text: string; author: string }[];
  category: string;
};

type QuickViewProduct = Product | null;

export default function ProductListPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [currency, setCurrency] = useState("ZAR");
  const [quickView, setQuickView] = useState<QuickViewProduct>(null);
  const rates: Record<string, number> = { ZAR: 1, USD: 0.055, EUR: 0.051, GBP: 0.044 };
  const currencySymbols: Record<string, string> = { ZAR: "R", USD: "$", EUR: "€", GBP: "£" };
  const productsTyped: Product[] = products as Product[];
  const categories: string[] = Array.from(new Set(productsTyped.map((p) => p.category)));
  const filteredProducts: Product[] = productsTyped.filter((p) => {
    const matchesCategory = selectedCategory ? p.category === selectedCategory : true;
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-[#181A20] text-white flex flex-col items-center py-16 px-4">
      <h1 className="text-4xl font-extrabold text-[#FFD700] mb-6 drop-shadow-lg">Our Premium Products</h1>
      <div className="flex flex-col sm:flex-row gap-4 mb-10 w-full max-w-4xl items-center">
        <div className="flex gap-2 items-center mb-2 sm:mb-0">
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
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full sm:w-72 px-4 py-2 rounded-full border border-[#FFD700] bg-[#181A20] text-white placeholder-[#FFD700] focus:outline-none focus:ring-2 focus:ring-[#FFD700] mb-2 sm:mb-0"
        />
        <button
          className={`px-4 py-2 rounded-full font-semibold border ${selectedCategory === null ? 'bg-[#FFD700] text-[#181A20]' : 'bg-[#23272F] text-[#FFD700] border-[#FFD700]'}`}
          onClick={() => setSelectedCategory(null)}
        >
          All
        </button>
        {categories.map((cat: string) => (
          <button
            key={cat}
            className={`px-4 py-2 rounded-full font-semibold border ${selectedCategory === cat ? 'bg-[#FFD700] text-[#181A20]' : 'bg-[#23272F] text-[#FFD700] border-[#FFD700]'}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10 w-full max-w-6xl">
        {filteredProducts.map((product: Product) => (
          <div
            key={product.id}
            className="bg-[#23272F] rounded-2xl shadow-lg p-6 flex flex-col items-center hover:scale-105 transition-transform relative"
          >
            <img
              src={product.image}
              alt={product.name}
              className="rounded-xl shadow-xl w-full max-w-xs border-4 border-[#FFD700] mb-4 cursor-pointer"
              onClick={() => setQuickView(product)}
            />
            <h2 className="text-2xl font-bold text-[#FFD700] mb-2 text-center">{product.name}</h2>
            <p className="text-base text-[#FFC857] mb-4 text-center">{product.description}</p>
            <ul className="mb-4 space-y-1 text-sm text-gray-200 text-left">
              {product.features.map((feature: string, i: number) => (
                <li key={i}>✔️ {feature}</li>
              ))}
            </ul>
            <div className="mb-4">
              <span className="text-xl font-bold text-[#FFD700]">{currencySymbols[currency]}{(product.price * rates[currency]).toFixed(2)}</span>
              {product.oldPrice && (
                <span className="ml-2 text-base text-gray-400 line-through">{currencySymbols[currency]}{(product.oldPrice * rates[currency]).toFixed(2)}</span>
              )}
              {product.discount && (
                <span className="ml-4 text-green-400 font-semibold">{product.discount}</span>
              )}
            </div>
            <div className="flex w-full gap-2">
              <button
                className="w-full py-2 rounded-lg bg-[#FFD700] text-[#181A20] font-bold text-base shadow-lg hover:bg-[#FFC857] transition mb-2"
                onClick={() => setQuickView(product)}
              >
                Quick View
              </button>
              <Link href={`/product/${product.id}`} className="w-full">
                <button className="w-full py-2 rounded-lg bg-[#23272F] border border-[#FFD700] text-[#FFD700] font-bold text-base shadow-lg hover:bg-[#FFD700] hover:text-[#181A20] transition mb-2">
                  Full Details
                </button>
              </Link>
            </div>
          </div>
        ))}
      </div>
      {/* Quick View Modal */}
      {quickView && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-[#23272F] rounded-2xl shadow-2xl p-8 max-w-lg w-full relative animate-fade-in">
            <button
              className="absolute top-4 right-4 text-2xl text-[#FFD700] hover:text-white"
              onClick={() => setQuickView(null)}
              aria-label="Close"
            >
              &times;
            </button>
            <img
              src={quickView.image}
              alt={quickView.name}
              className="rounded-xl shadow-xl w-full max-w-xs border-4 border-[#FFD700] mb-4 mx-auto"
            />
            <h2 className="text-2xl font-bold text-[#FFD700] mb-2 text-center">{quickView.name}</h2>
            <p className="text-base text-[#FFC857] mb-4 text-center">{quickView.description}</p>
            <ul className="mb-4 space-y-1 text-sm text-gray-200 text-left">
              {quickView.features.map((feature: string, i: number) => (
                <li key={i}>✔️ {feature}</li>
              ))}
            </ul>
            <div className="mb-4 text-center">
              <span className="text-xl font-bold text-[#FFD700]">{currencySymbols[currency]}{(quickView.price * rates[currency]).toFixed(2)}</span>
              {quickView.oldPrice && (
                <span className="ml-2 text-base text-gray-400 line-through">{currencySymbols[currency]}{(quickView.oldPrice * rates[currency]).toFixed(2)}</span>
              )}
              {quickView.discount && (
                <span className="ml-4 text-green-400 font-semibold">{quickView.discount}</span>
              )}
            </div>
            <a
              href="/sample_download.pdf"
              download
              className="w-full block py-3 rounded-lg bg-[#22d3ee] border-2 border-[#FFD700] text-[#181A20] font-bold text-lg shadow-lg hover:bg-[#FFD700] hover:text-[#181A20] transition text-center mb-2"
            >
              &#8681; Download Free Sample
            </a>
            <Link href={`/product/${quickView.id}`} className="w-full">
              <button className="w-full py-2 rounded-lg bg-[#FFD700] text-[#181A20] font-bold text-base shadow-lg hover:bg-[#FFC857] transition mb-2">
                View Full Details
              </button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
