"use client";
import React, { useContext } from "react";
import { CartContext } from "@/components/CartProvider";

export default function CheckoutPage() {
  const { cart } = useContext(CartContext);
  const total = cart.reduce((sum, item) => sum + item.price, 0);
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#e6fff2] px-4 py-16">
      <div className="bg-white rounded-2xl shadow-2xl p-10 max-w-lg w-full flex flex-col items-center">
        <h1 className="text-3xl font-bold text-[#34d399] mb-4">Checkout</h1>
        <p className="mb-6 text-gray-700 text-center">Secure payment and instant delivery. (Demo only – payment integration coming soon!)</p>
        {/* Cart summary */}
        <div className="w-full mb-6">
          <h2 className="text-lg font-semibold mb-2 text-[#181A20]">Order Summary</h2>
          {cart.length === 0 ? (
            <p className="text-gray-400">Your cart is empty.</p>
          ) : (
            <ul className="mb-2">
              {cart.map((item, i) => (
                <li key={i} className="flex justify-between py-1 border-b border-gray-100">
                  <span>{item.name}</span>
                  <span className="font-bold text-[#FFD700]">R{item.price}</span>
                </li>
              ))}
            </ul>
          )}
          <div className="flex justify-between font-bold text-lg mt-2">
            <span>Total</span>
            <span className="text-[#34d399]">R{total}</span>
          </div>
        </div>
        <form className="w-full flex flex-col gap-4">
          <input className="border rounded-lg px-4 py-2" type="text" placeholder="Full Name" required />
          <input className="border rounded-lg px-4 py-2" type="email" placeholder="Email Address" required />
          <div className="flex flex-col gap-3 mt-4">
            <button type="button" className="w-full py-3 rounded-lg bg-[#ffc439] text-[#181A20] font-bold text-lg shadow-lg hover:bg-[#ffe082] transition flex items-center justify-center gap-2">
              <img src="https://www.paypalobjects.com/webstatic/icon/pp258.png" alt="PayPal" className="w-6 h-6" />
              Pay with PayPal (Demo)
            </button>
            <button type="button" className="w-full py-3 rounded-lg bg-[#00b686] text-white font-bold text-lg shadow-lg hover:bg-[#34d399] transition flex items-center justify-center gap-2">
              <img src="https://www.ozow.com/wp-content/uploads/2022/10/ozow-logo-green.svg" alt="Ozow" className="w-6 h-6 bg-white rounded-full" />
              Pay with Ozow (Demo)
            </button>
            <button type="button" className="w-full py-3 rounded-lg bg-[#ff6600] text-white font-bold text-lg shadow-lg hover:bg-[#ff944d] transition flex items-center justify-center gap-2">
              <img src="https://www.payfast.co.za/wp-content/uploads/2022/05/PayFast-Logo-Icon-White.svg" alt="PayFast" className="w-6 h-6 bg-white rounded-full" />
              Pay with PayFast (Demo)
            </button>
          </div>
        </form>
  <p className="mt-6 text-xs text-gray-400">Payments are not processed in this demo. For a real store, integrate PayPal, Ozow, or PayFast. All prices are shown in your selected currency, with checkout processed in ZAR (South African Rand).</p>
      </div>
    </div>
  );
}
