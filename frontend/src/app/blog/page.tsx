import React from "react";
import Head from "next/head";

export default function BlogPage() {
  return (
    <>
      <Head>
        <title>Blog & Resources | Digital Luxe Market</title>
        <meta name="description" content="Read tips, guides, and resources for entrepreneurs and creators from Digital Luxe Market." />
      </Head>
      <main className="max-w-3xl mx-auto py-12 px-4" aria-labelledby="blog-title">
        <h1 id="blog-title" className="text-4xl font-bold text-[#FFD700] mb-8 text-center">Blog & Resources</h1>
        <div className="space-y-8">
          <article className="bg-[#23272F] rounded-xl shadow-xl p-8">
            <h2 className="text-2xl font-semibold text-[#22d3ee] mb-2">How to Choose the Right Digital Product for You</h2>
            <p className="text-gray-200 mb-2">A quick guide to picking the best templates, tools, and guides for your needs.</p>
            <a href="#" className="text-[#FFD700] underline hover:text-[#22d3ee]">Read More</a>
          </article>
          <article className="bg-[#23272F] rounded-xl shadow-xl p-8">
            <h2 className="text-2xl font-semibold text-[#22d3ee] mb-2">Top 5 Productivity Hacks for Entrepreneurs</h2>
            <p className="text-gray-200 mb-2">Boost your workflow and results with these proven strategies.</p>
            <a href="#" className="text-[#FFD700] underline hover:text-[#22d3ee]">Read More</a>
          </article>
        </div>
      </main>
    </>
  );
}
