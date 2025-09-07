import React from "react";
import Head from "next/head";

export default function FAQPage() {
  return (
    <>
      <Head>
        <title>FAQ | Digital Luxe Market</title>
        <meta name="description" content="Frequently asked questions about Digital Luxe Market's premium digital products, delivery, payments, and support." />
      </Head>
      <main className="max-w-3xl mx-auto py-12 px-4" aria-labelledby="faq-title">
        <h1 id="faq-title" className="text-4xl font-bold text-[#FFD700] mb-8 text-center">Frequently Asked Questions</h1>
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-[#22d3ee]">How do I receive my product after purchase?</h2>
            <p className="text-gray-200">You will receive an instant download link after payment. You can also access your downloads from your account page.</p>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-[#22d3ee]">What payment methods do you accept?</h2>
            <p className="text-gray-200">We accept PayPal, Ozow, PayFast, and major credit cards. All payments are secure and encrypted.</p>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-[#22d3ee]">Can I get a refund?</h2>
            <p className="text-gray-200">Due to the digital nature of our products, all sales are final. Please contact us if you have any issues.</p>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-[#22d3ee]">How do I contact support?</h2>
            <p className="text-gray-200">You can reach us via the contact form on the Contact page or email us at support@example.com.</p>
          </div>
        </div>
      </main>
    </>
  );
}
