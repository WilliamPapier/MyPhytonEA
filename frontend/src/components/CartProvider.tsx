"use client";
import React, { useState, ReactNode } from "react";
import CartSidebar from "@/components/CartSidebar";

type CartItem = {
  name: string;
  price: number;
};

interface CartContextType {
  cart: CartItem[];
  addToCart: (product: CartItem) => void;
  open: boolean;
  setOpen: (open: boolean) => void;
}

export const CartContext = React.createContext<CartContextType>({
  cart: [],
  addToCart: () => {},
  open: false,
  setOpen: () => {},
});

interface CartProviderProps {
  children: ReactNode;
}

export default function CartProvider({ children }: CartProviderProps) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [open, setOpen] = useState(false);

  const addToCart = (product: CartItem) => {
    setCart((prev) => [...prev, product]);
    setOpen(true);
  };

  const onCheckout = () => {
    alert("Checkout coming soon!");
  };

  return (
    <CartContext.Provider value={{ cart, addToCart, open, setOpen }}>
      {children}
      {open && (
        <CartSidebar cart={cart} onClose={() => setOpen(false)} onCheckout={onCheckout} />
      )}
    </CartContext.Provider>
  );
}
