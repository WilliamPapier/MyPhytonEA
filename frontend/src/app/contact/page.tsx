import React from "react";
import Head from "next/head";

export default function ContactPage() {
  return (
    <>
      <Head>
        <title>Contact | Digital Luxe Market</title>
        <meta name="description" content="Contact Digital Luxe Market for support, questions, or partnership opportunities. We're here to help!" />
      </Head>
      <main className="max-w-2xl mx-auto py-12 px-4" aria-labelledby="contact-title">
        <h1 id="contact-title" className="text-4xl font-bold text-[#FFD700] mb-8 text-center">Contact Us</h1>
        <form className="space-y-6 bg-[#23272F] p-8 rounded-xl shadow-xl" aria-label="Contact form">
          <div>
            <label htmlFor="name" className="block text-[#FFD700] font-semibold mb-2">Name</label>
            <input id="name" type="text" className="w-full px-4 py-2 rounded-lg bg-[#181A20] text-white border border-[#FFD700]" required aria-required="true" />
          </div>
          <div>
            <label htmlFor="email" className="block text-[#FFD700] font-semibold mb-2">Email</label>
            <input id="email" type="email" className="w-full px-4 py-2 rounded-lg bg-[#181A20] text-white border border-[#FFD700]" required aria-required="true" />
          </div>
          <div>
            <label htmlFor="message" className="block text-[#FFD700] font-semibold mb-2">Message</label>
            <textarea id="message" className="w-full px-4 py-2 rounded-lg bg-[#181A20] text-white border border-[#FFD700]" rows={5} required aria-required="true"></textarea>
          </div>
          <button type="submit" className="w-full py-3 rounded-lg bg-[#22d3ee] border-2 border-[#FFD700] text-[#181A20] font-bold text-lg shadow-lg hover:bg-[#FFD700] hover:text-[#181A20] transition">Send Message</button>
        </form>
        <div className="mt-8 text-center text-gray-200">
          <p>Email: <a href="mailto:support@example.com" className="text-[#FFD700] underline">support@example.com</a></p>
          <p>We aim to respond within 24 hours.</p>
        </div>
      </main>
    </>
  );
}
