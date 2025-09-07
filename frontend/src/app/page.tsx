      {/* Newsletter Signup */}
      <section className="w-full flex flex-col items-center py-16 px-4 bg-gradient-to-br from-[#e6fff2] via-[#fffbe6] to-[#f3f3f3] dark:from-[#23272F] dark:via-[#181A20] dark:to-[#101014]">
        <div className="max-w-2xl w-full flex flex-col items-center bg-white/80 dark:bg-[#23272F] rounded-2xl shadow-xl p-10">
          <h2 className="text-3xl font-bold text-[#181A20] dark:text-[#FFD700] mb-4">Stay in the Loop</h2>
          <p className="text-lg text-[#23272F] dark:text-[#FFC857] mb-6 text-center">Get exclusive offers, new product drops, and premium tips straight to your inbox.</p>
          <form className="w-full flex flex-col sm:flex-row gap-4 items-center justify-center">
            <input
              type="email"
              required
              placeholder="Your email address"
              className="w-full sm:w-72 px-4 py-3 rounded-full border border-[#FFD700] bg-white dark:bg-[#181A20] text-[#181A20] dark:text-white placeholder-[#FFD700] focus:outline-none focus:ring-2 focus:ring-[#FFD700]"
            />
            <button
              type="submit"
              className="px-8 py-3 rounded-full bg-[#FFD700] text-[#181A20] font-bold text-lg shadow-lg hover:bg-[#FFC857] transition"
            >
              Subscribe
            </button>
          </form>
          <span className="mt-4 text-xs text-gray-400">No spam. Unsubscribe anytime.</span>
        </div>
      </section>
import FeaturedProductsCarousel from "./FeaturedProductsCarousel";



import Link from "next/link";
import { products } from "./product/products";

export default function Home() {

  return (
    <>
      {/* Hero Section with Gradient and Decorative Shape */}
      <section className="relative flex flex-col items-center justify-center min-h-[60vh] px-4 text-center gap-10 overflow-hidden bg-gradient-to-br from-[#e6fff2] via-[#fffbe6] to-[#f3f3f3] dark:from-[#181A20] dark:via-[#23272F] dark:to-[#101014]">
        {/* Premium gold and greenery accents */}
        <div className="absolute -top-32 -left-32 w-[500px] h-[500px] bg-[#FFD700]/20 rounded-full blur-3xl z-0" />
        <svg className="absolute left-10 top-10 w-32 h-32 z-0 opacity-30" viewBox="0 0 100 100" fill="none"><ellipse cx="50" cy="50" rx="50" ry="20" fill="#6ee7b7" /><path d="M50 10 Q60 40 90 50 Q60 60 50 90 Q40 60 10 50 Q40 40 50 10 Z" fill="#34d399" /></svg>
        <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-[#FFD700]/10 rounded-full blur-2xl z-0" />
        <div className="max-w-2xl mx-auto z-10">
          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-6 text-[#181A20] dark:text-[#FFD700] drop-shadow-lg">
            Welcome to <span className="text-[#FFD700] dark:text-[#FFD700]">Digital Luxe Market</span>
          </h1>
          <p className="text-lg sm:text-xl text-[#23272F] dark:text-[#FFC857] mb-8">
            Discover premium digital products designed to elevate your workflow, creativity, and success. Curated for professionals, creators, and entrepreneurs who demand the best.
          </p>
          <div className="mb-4">
            <span className="inline-block bg-[#FFD700]/20 text-[#181A20] dark:text-[#FFD700] px-4 py-2 rounded-full font-medium text-base shadow-sm">
              The #1 destination for high-end digital assets
            </span>
          </div>
          <a
            href="/product"
            className="inline-block bg-[#FFD700] text-[#181A20] font-semibold rounded-full px-8 py-3 text-lg shadow-lg hover:bg-[#FFC857] transition-colors"
          >
            Browse Products
          </a>
        </div>
        {/* Navigation Bar */}
        <nav className="flex justify-center gap-8 py-6 z-20">
          <a href="/" className="text-lg font-bold text-[#FFD700] hover:text-[#22d3ee] transition">Home</a>
          <a href="/product" className="text-lg font-bold text-[#FFD700] hover:text-[#22d3ee] transition">Products</a>
          <a href="/checkout" className="text-lg font-bold text-[#FFD700] hover:text-[#22d3ee] transition">Checkout</a>
          <a href="/faq" className="text-lg font-bold text-[#FFD700] hover:text-[#22d3ee] transition">FAQ</a>
          <a href="/contact" className="text-lg font-bold text-[#FFD700] hover:text-[#22d3ee] transition">Contact</a>
          <a href="/account" className="text-lg font-bold text-[#FFD700] hover:text-[#22d3ee] transition">Account</a>
          <a href="/blog" className="text-lg font-bold text-[#FFD700] hover:text-[#22d3ee] transition">Blog</a>
        </nav>
        {/* Stacked Product Images in Hero */}
        <div className="relative w-full flex justify-center mt-12 z-10">
          <div className="relative w-[340px] h-[220px]">
            <div className="absolute left-8 top-8 w-[220px] h-[140px] bg-[#FFD700]/30 rounded-xl blur-[2px] z-0" />
            <img
              src={products[0].image}
              alt={products[0].name}
              className="absolute left-4 top-4 w-[220px] h-[140px] object-cover rounded-xl shadow-xl border-4 border-[#FFD700] z-10"
            />
            <img
              src={products[1].image}
              alt={products[1].name}
              className="absolute left-2 top-2 w-[220px] h-[140px] object-cover rounded-xl shadow-xl border-4 border-[#FFD700] z-20"
            />
            <img
              src={products[2].image}
              alt={products[2].name}
              className="absolute left-0 top-0 w-[220px] h-[140px] object-cover rounded-xl shadow-xl border-4 border-[#FFD700] z-30"
              style={{ transform: 'rotate(-6deg)' } as React.CSSProperties}
            />
          </div>
        </div>
      </section>
      {/* Featured Products */}
  <section className="w-full flex flex-col items-center py-12 px-4 bg-[#181A20]">
        <h2 className="text-3xl font-bold text-[#FFD700] mb-8 flex items-center gap-3">
          <svg className="w-8 h-8 inline-block opacity-60" viewBox="0 0 100 100" fill="none"><ellipse cx="50" cy="50" rx="50" ry="20" fill="#6ee7b7" /><path d="M50 10 Q60 40 90 50 Q60 60 50 90 Q40 60 10 50 Q40 40 50 10 Z" fill="#34d399" /></svg>
          Featured Products
        </h2>
  {/* Carousel */}
  <FeaturedProductsCarousel products={products.slice(0, 6)} />
      </section>

      {/* How it works */}
  <section className="w-full flex flex-col items-center py-12 px-4 bg-white dark:bg-[#101014]">
        <h2 className="text-3xl font-bold text-primary mb-8">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl">
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 bg-[#FFD700] rounded-full flex items-center justify-center text-2xl font-bold mb-4">1</div>
            <h4 className="font-bold mb-2">Browse & Choose</h4>
            <p className="text-center text-muted-foreground">Explore our curated collection of premium digital products and pick what fits your needs.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 bg-[#FFD700] rounded-full flex items-center justify-center text-2xl font-bold mb-4">2</div>
            <h4 className="font-bold mb-2">Instant Checkout</h4>
            <p className="text-center text-muted-foreground">Add to cart, pay securely, and get instant access to your downloads—no waiting.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 bg-[#FFD700] rounded-full flex items-center justify-center text-2xl font-bold mb-4">3</div>
            <h4 className="font-bold mb-2">Level Up</h4>
            <p className="text-center text-muted-foreground">Use your new tools, templates, and guides to boost your productivity and results.</p>
          </div>
        </div>
      </section>

      {/* Customer Testimonials */}
      <section className="w-full flex flex-col items-center py-16 px-4 bg-[#181A20]" aria-label="Customer Testimonials">
        <h2 className="text-3xl font-bold text-[#FFD700] mb-10">What Our Customers Say</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 w-full max-w-6xl">
          <div className="flex flex-col items-center bg-[#23272F] rounded-2xl shadow-lg p-8" aria-label="Testimonial by Thabo Nkosi">
            <img src="https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&w=200&h=200&fit=crop" alt="Thabo Nkosi, smiling African man" className="w-20 h-20 rounded-full border-4 border-[#FFD700] mb-4 shadow-xl" />
            <p className="text-lg text-white mb-4 text-center">“Absolutely worth every rand! The templates and workflow saved me hours and my posts look 10x better.”</p>
            <span className="font-bold text-[#FFD700]">Thabo Nkosi</span>
            <span className="text-xs text-gray-400">Entrepreneur</span>
          </div>
          <div className="flex flex-col items-center bg-[#23272F] rounded-2xl shadow-lg p-8" aria-label="Testimonial by Zanele Dlamini">
            <img src="https://images.pexels.com/photos/1181696/pexels-photo-1181696.jpeg?auto=compress&w=200&h=200&fit=crop" alt="Zanele Dlamini, smiling African woman" className="w-20 h-20 rounded-full border-4 border-[#FFD700] mb-4 shadow-xl" />
            <p className="text-lg text-white mb-4 text-center">“Professional, actionable, and easy to use. I launched my brand in a week!”</p>
            <span className="font-bold text-[#FFD700]">Zanele Dlamini</span>
            <span className="text-xs text-gray-400">Brand Owner</span>
          </div>
          <div className="flex flex-col items-center bg-[#23272F] rounded-2xl shadow-lg p-8" aria-label="Testimonial by Lerato Mokoena">
            <img src="https://images.pexels.com/photos/1707828/pexels-photo-1707828.jpeg?auto=compress&w=200&h=200&fit=crop" alt="Lerato Mokoena, happy African woman" className="w-20 h-20 rounded-full border-4 border-[#FFD700] mb-4 shadow-xl" />
            <p className="text-lg text-white mb-4 text-center">“My proposals look so professional now. Landed two clients in a week!”</p>
            <span className="font-bold text-[#FFD700]">Lerato Mokoena</span>
            <span className="text-xs text-gray-400">Consultant</span>
          </div>
        </div>
      </section>
      {/* Why choose us */}
      <section className="w-full flex flex-col items-center py-12 px-4 bg-[#181A20]">
        <h2 className="text-3xl font-bold text-[#FFD700] mb-8">Why Choose Us?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl">
          <div className="flex flex-col items-center">
            <span className="text-4xl mb-2">🌟</span>
            <h4 className="font-bold mb-2 text-[#FFD700]">Premium Quality</h4>
            <p className="text-center text-gray-300">Every product is crafted by experts and tested for real-world results.</p>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-4xl mb-2">⚡</span>
            <h4 className="font-bold mb-2 text-[#FFD700]">Instant Delivery</h4>
            <p className="text-center text-gray-300">Get access to your downloads immediately after purchase—no delays.</p>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-4xl mb-2">💬</span>
            <h4 className="font-bold mb-2 text-[#FFD700]">Support & Updates</h4>
            <p className="text-center text-gray-300">Enjoy lifetime updates and responsive support for every product.</p>
          </div>
        </div>
      </section>
    </>
  );
}
