import React from "react";
import Head from "next/head";

export default function AccountPage() {
  // Demo: No real authentication, just a placeholder for user account features
  return (
    <>
      <Head>
        <title>My Account | Digital Luxe Market</title>
        <meta name="description" content="View your order history, downloads, and account details at Digital Luxe Market." />
      </Head>
      <main className="max-w-2xl mx-auto py-12 px-4" aria-labelledby="account-title">
        <h1 id="account-title" className="text-4xl font-bold text-[#FFD700] mb-8 text-center">My Account</h1>
        <div className="bg-[#23272F] rounded-xl shadow-xl p-8 mb-8">
          <h2 className="text-2xl font-semibold text-[#22d3ee] mb-4">Order History</h2>
          <ul className="space-y-4">
            <li className="bg-[#181A20] rounded-lg p-4 flex flex-col md:flex-row md:items-center md:justify-between">
              <span className="text-[#FFD700] font-bold">Ultimate Trading Guide.pdf</span>
              <a href="/sample_download.pdf" download className="mt-2 md:mt-0 text-[#22d3ee] underline hover:text-[#FFD700]">Download</a>
            </li>
            <li className="bg-[#181A20] rounded-lg p-4 flex flex-col md:flex-row md:items-center md:justify-between">
              <span className="text-[#FFD700] font-bold">Pro Forex Templates.zip</span>
              <a href="/sample_download.pdf" download className="mt-2 md:mt-0 text-[#22d3ee] underline hover:text-[#FFD700]">Download</a>
            </li>
          </ul>
        </div>
        <div className="bg-[#23272F] rounded-xl shadow-xl p-8">
          <h2 className="text-2xl font-semibold text-[#22d3ee] mb-4">Account Details</h2>
          <p className="text-gray-200 mb-2">Email: <span className="text-[#FFD700]">demo@example.com</span></p>
          <button className="mt-4 px-6 py-2 rounded-lg bg-[#FFD700] text-[#181A20] font-bold shadow hover:bg-[#22d3ee] hover:text-[#181A20] transition">Log Out</button>
        </div>
      </main>
    </>
  );
}
