"use client";
import React, { useRef, useState } from "react";
import Link from "next/link";

type Product = {
  id: string;
  name: string;
  description: string;
  image: string;
};

interface CarouselProps {
  products: Product[];
}

export default function FeaturedProductsCarousel({ products }: CarouselProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [scrollIndex, setScrollIndex] = useState(0);
  const visibleCount = 3;

  const scrollTo = (index: number) => {
    if (scrollRef.current) {
      const cardWidth = scrollRef.current.offsetWidth / visibleCount;
      scrollRef.current.scrollTo({
        left: cardWidth * index,
        behavior: "smooth",
      });
    }
    setScrollIndex(index);
  };

  const handlePrev = () => {
    if (scrollIndex > 0) scrollTo(scrollIndex - 1);
  };
  const handleNext = () => {
    if (scrollIndex < products.length - visibleCount) scrollTo(scrollIndex + 1);
  };

  return (
    <div className="relative w-full max-w-6xl">
      <button
        onClick={handlePrev}
        className="absolute left-0 top-1/2 -translate-y-1/2 z-20 bg-[#FFD700] text-[#181A20] rounded-full p-2 shadow-lg hover:bg-[#FFC857] transition disabled:opacity-40"
        disabled={scrollIndex === 0}
        aria-label="Previous"
      >
        &#8592;
      </button>
      <div
        ref={scrollRef}
        className="flex overflow-x-auto no-scrollbar gap-8 py-2 px-12 snap-x snap-mandatory"
        style={{ scrollBehavior: "smooth" }}
      >
        {products.map((product) => (
          <div
            key={product.id}
            className="min-w-[320px] max-w-xs bg-[#23272F] rounded-2xl shadow-lg p-6 flex flex-col items-center snap-center"
          >
            <div className="relative w-full h-48 mb-4">
              <div className="absolute left-4 top-4 w-full h-full bg-[#FFD700] rounded-xl opacity-30 z-0" style={{ filter: 'blur(2px)' }}></div>
              <div className="absolute left-2 top-2 w-full h-full bg-[#FFD700] rounded-xl opacity-50 z-10" style={{ filter: 'blur(1px)' }}></div>
              <img
                src={product.image}
                alt={product.name}
                className="relative rounded-xl shadow-xl w-full h-full object-cover border-4 border-[#FFD700] z-20"
              />
            </div>
            <h3 className="text-xl font-bold text-[#FFD700] mb-2 text-center">{product.name}</h3>
            <p className="text-base text-[#FFC857] mb-4 text-center">{product.description}</p>
            <Link href={`/product/${product.id}`} className="w-full">
              <button className="w-full py-2 rounded-lg bg-[#FFD700] text-[#181A20] font-bold text-base shadow-lg hover:bg-[#FFC857] transition mb-2">
                View Details
              </button>
            </Link>
          </div>
        ))}
      </div>
      <button
        onClick={handleNext}
        className="absolute right-0 top-1/2 -translate-y-1/2 z-20 bg-[#FFD700] text-[#181A20] rounded-full p-2 shadow-lg hover:bg-[#FFC857] transition disabled:opacity-40"
        disabled={scrollIndex >= products.length - visibleCount}
        aria-label="Next"
      >
        &#8594;
      </button>
    </div>
  );
}