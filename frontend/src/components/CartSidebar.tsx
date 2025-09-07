"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";

type CartItem = {
  name: string;
  price: number;
};

interface CartSidebarProps {
  cart: CartItem[];
  onClose: () => void;
  onCheckout: () => void;
}

export default function CartSidebar({ cart, onClose, onCheckout }: CartSidebarProps) {
  const router = useRouter();
  return (
    <div className="fixed top-0 right-0 h-full w-80 bg-[#23272F] text-white shadow-2xl z-50 flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-[#FFD700]">
        <h2 className="text-xl font-bold text-[#FFD700]">Your Cart</h2>
        <button onClick={onClose} className="text-white text-2xl">×</button>
      </div>
      <div className="flex-1 p-4 overflow-y-auto">
        {cart.length === 0 ? (
          <p className="text-gray-400">Your cart is empty.</p>
        ) : (
          <ul className="space-y-4">
            {cart.map((item: CartItem, i: number) => (
              <li key={i} className="flex items-center justify-between">
                <span>{item.name}</span>
                <span className="font-bold text-[#FFD700]">R{item.price}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="p-4 border-t border-[#FFD700]">
        <button
          className="w-full py-2 rounded-lg bg-[#34d399] text-white font-bold text-base shadow-lg hover:bg-[#6ee7b7] transition"
          disabled={cart.length === 0}
          onClick={() => {
            onClose();
            router.push("/checkout");
          }}
        >
          Checkout
        </button>
      </div>
    </div>
  );
}
