import React from 'react';

export default function SampleProductPage() {
  return (
    <div className="min-h-screen bg-[#181A20] text-white flex flex-col items-center py-12 px-4">
      <div className="max-w-4xl w-full bg-[#23272F] rounded-2xl shadow-lg p-8 flex flex-col md:flex-row gap-8">
        {/* Product Image */}
        <div className="flex-1 flex items-center justify-center">
          <img
            src="/mockup-product.png"
            alt="Premium Digital Product"
            className="rounded-xl shadow-xl w-full max-w-xs border-4 border-[#FFD700]"
          />
        </div>
        {/* Product Details */}
        <div className="flex-1 flex flex-col justify-between">
          <div>
            <h1 className="text-3xl font-bold text-[#FFD700] mb-2">Ultimate Social Media Design System</h1>
            <p className="text-lg text-[#FFC857] mb-4">Templates, Workflows & Pro Secrets</p>
            <ul className="mb-6 space-y-2 text-base text-gray-200">
              <li>✔️ 50+ Canva templates for posts, stories, carousels, ads</li>
              <li>✔️ Step-by-step design workflow & pro tips</li>
              <li>✔️ Bonus: Icon packs, color palettes, and checklists</li>
              <li>✔️ Instant download after purchase</li>
            </ul>
            <div className="mb-6">
              <span className="text-2xl font-bold text-[#FFD700]">R799</span>
              <span className="ml-2 text-base text-gray-400 line-through">R1,200</span>
              <span className="ml-4 text-green-400 font-semibold">Save 33%</span>
            </div>
            <button className="w-full py-3 rounded-lg bg-[#FFD700] text-[#181A20] font-bold text-lg shadow-lg hover:bg-[#FFC857] transition">Buy Now</button>
          </div>
          <div className="mt-8 text-sm text-gray-400">
            <p>Includes: PDF guide, Canva templates, bonus assets, and lifetime updates.</p>
            <p className="mt-2">Secure checkout • Instant delivery • 24/7 support</p>
          </div>
        </div>
      </div>
      {/* Reviews */}
      <div className="max-w-2xl w-full mt-12 bg-[#23272F] rounded-xl p-6 shadow-md">
        <h2 className="text-xl font-bold text-[#FFD700] mb-4">What Buyers Say</h2>
        <div className="space-y-4">
          <div className="bg-[#181A20] rounded-lg p-4">
            <p className="text-base text-white">“Absolutely worth every rand! The templates and workflow saved me hours and my posts look 10x better.”</p>
            <span className="block mt-2 text-xs text-[#FFC857]">— Lerato M.</span>
          </div>
          <div className="bg-[#181A20] rounded-lg p-4">
            <p className="text-base text-white">“Professional, actionable, and easy to use. I launched my brand in a week!”</p>
            <span className="block mt-2 text-xs text-[#FFC857]">— Sipho D.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
