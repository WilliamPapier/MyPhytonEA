import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="w-full flex items-center justify-between py-6 px-8 bg-white/80 dark:bg-black/80 shadow-md fixed top-0 left-0 z-50 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <span className="font-bold text-xl tracking-tight text-primary">YourStore</span>
      </div>
      <div className="flex gap-8 items-center text-base font-medium">
        <Link href="/" className="hover:text-primary transition-colors">Home</Link>
        <Link href="/product" className="hover:text-primary transition-colors">Products</Link>
        <Link href="#about" className="hover:text-primary transition-colors">About</Link>
        <Link href="#contact" className="hover:text-primary transition-colors">Contact</Link>
      </div>
    </nav>
  );
}
