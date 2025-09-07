// This file contains the product data for the store. Add more products as needed.
export const products = [
  // ...existing products (updated below)...
  {
    id: "1",
    name: "Ultimate Social Media Design System",
    description: "Templates, Workflows & Pro Secrets",
    features: [
      "50+ Canva templates for posts, stories, carousels, ads",
      "Step-by-step design workflow & pro tips",
      "Bonus: Icon packs, color palettes, and checklists",
      "Instant download after purchase"
    ],
    price: 799,
    oldPrice: 1200,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&w=600&q=80", // Social media design system
    includes: "PDF guide, Canva templates, bonus assets, and lifetime updates.",
    category: "Design, Professional",
    reviews: [
      { text: "Absolutely worth every rand! The templates and workflow saved me hours and my posts look 10x better.", author: "Lerato M." },
      { text: "Professional, actionable, and easy to use. I launched my brand in a week!", author: "Sipho D." }
    ]
  },
  {
    id: "2",
    name: "Business Proposal Power Pack",
    description: "Winning Templates & Pitch Decks",
    features: [
      "10+ ready-to-use business proposal templates",
      "Editable pitch deck slides (PowerPoint & Canva)",
      "Financial model spreadsheet included",
      "Instant download after purchase"
    ],
    price: 599,
    oldPrice: 900,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/2102416/pexels-photo-2102416.jpeg?auto=compress&w=600&q=80", // Business proposal pack
    includes: "Proposal templates (Word, PDF), pitch decks, financial model, and guide.",
    category: "Business, Professional",
    reviews: [
      { text: "My proposals look so professional now. Landed two clients in a week!", author: "Nomsa K." }
    ]
  },
  {
    id: "3",
    name: "Personal Finance Master Toolkit",
    description: "Trackers, Planners & Budgeting Tools",
    features: [
      "Comprehensive Excel/Google Sheets budget tracker",
      "Goal planner, debt payoff calculator, and more",
      "Printable PDF planners included",
      "Instant download after purchase"
    ],
    price: 399,
    oldPrice: 600,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/4386375/pexels-photo-4386375.jpeg?auto=compress&w=600&q=80", // Personal finance toolkit
    includes: "Excel/Sheets trackers, PDF planners, and bonus guides.",
    category: "Finance, Need",
    reviews: [
      { text: "Finally got my finances organized. The tracker is a game changer!", author: "Thabo S." }
    ]
  },
  // 17 more diverse, premium, and categorized products:
  {
    id: "4",
    name: "AI Content Generator Pro",
    description: "Create blog posts, ads, and social content in seconds.",
    features: ["Unlimited AI text generation", "SEO-optimized output", "Multiple languages", "Instant download after purchase"],
    price: 999,
    oldPrice: 1500,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg?auto=compress&w=600&q=80", // AI Content Generator Pro
    includes: "Web app access, PDF guide, and prompt library.",
    category: "AI, Professional",
    reviews: [
      { text: "My content workflow is 5x faster!", author: "Jade P." }
    ]
  },
  {
    id: "5",
    name: "Essential Resume & CV Kit",
    description: "Modern templates and expert writing guide.",
    features: ["10+ ATS-friendly resume templates", "Cover letter samples", "Step-by-step writing guide", "Instant download"],
    price: 299,
    oldPrice: 450,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/1181672/pexels-photo-1181672.jpeg?auto=compress&w=600&q=80", // Resume & CV Kit
    includes: "Word, PDF, and Google Docs templates.",
    category: "Career, Need",
    reviews: [
      { text: "Landed my dream job!", author: "Mandla T." }
    ]
  },
  {
    id: "6",
    name: "Ultimate Productivity Planner",
    description: "Digital planner for daily, weekly, and monthly goals.",
    features: ["Printable & digital formats", "Goal tracking", "Habit builder", "Instant download"],
    price: 199,
    oldPrice: 350,
    discount: "Save 43%",
  image: "https://images.pexels.com/photos/669996/pexels-photo-669996.jpeg?auto=compress&w=600&q=80", // Productivity Planner
    includes: "PDF, GoodNotes, and Notion templates.",
    category: "Productivity, Need",
    reviews: [
      { text: "Keeps me focused every day!", author: "Zanele N." }
    ]
  },
  {
    id: "7",
    name: "Brand Identity Starter Pack",
    description: "Logos, color palettes, and branding guides.",
    features: ["20+ logo templates", "Editable color palettes", "Brand guidelines PDF", "Instant download"],
    price: 499,
    oldPrice: 750,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/1037992/pexels-photo-1037992.jpeg?auto=compress&w=600&q=80", // Brand Identity Starter Pack
    includes: "AI, PSD, and PDF files.",
    category: "Design, Need",
    reviews: [
      { text: "My brand looks so professional now!", author: "Kabelo S." }
    ]
  },
  {
    id: "8",
    name: "E-commerce Launch Kit",
    description: "Everything you need to start selling online.",
    features: ["Shopify & WooCommerce templates", "Product photo presets", "Marketing checklist", "Instant download"],
    price: 899,
    oldPrice: 1300,
    discount: "Save 31%",
  image: "https://images.pexels.com/photos/265087/pexels-photo-265087.jpeg?auto=compress&w=600&q=80", // E-commerce Launch Kit
    includes: "Templates, guides, and bonus resources.",
    category: "Business, Professional",
    reviews: [
      { text: "Launched my store in a weekend!", author: "Aisha M." }
    ]
  },
  {
    id: "9",
    name: "Freelancer Contract Bundle",
    description: "Legal templates for freelancers and agencies.",
    features: ["Service agreement", "NDA", "Invoice template", "Instant download"],
    price: 349,
    oldPrice: 500,
    discount: "Save 30%",
  image: "https://images.pexels.com/photos/267614/pexels-photo-267614.jpeg?auto=compress&w=600&q=80", // Freelancer Contract Bundle
    includes: "Word, PDF, and Google Docs files.",
    category: "Business, Need",
    reviews: [
      { text: "Saved me from legal headaches!", author: "Lindiwe R." }
    ]
  },
  {
    id: "10",
    name: "Notion Life OS",
    description: "All-in-one Notion template for life & work.",
    features: ["Task manager", "Finance tracker", "Goal planner", "Instant download"],
    price: 249,
    oldPrice: 400,
    discount: "Save 38%",
  image: "https://images.pexels.com/photos/1181673/pexels-photo-1181673.jpeg?auto=compress&w=600&q=80", // Notion Life OS
    includes: "Notion template and setup guide.",
    category: "Productivity, Need",
    reviews: [
      { text: "My life is so much more organized!", author: "Sibusiso D." }
    ]
  },
  {
    id: "11",
    name: "Digital Marketing Playbook",
    description: "Step-by-step strategies for online growth.",
    features: ["SEO, social, email, ads", "Templates & checklists", "Case studies", "Instant download"],
    price: 699,
    oldPrice: 1000,
    discount: "Save 30%",
  image: "https://images.pexels.com/photos/267614/pexels-photo-267614.jpeg?auto=compress&w=600&q=80", // Digital Marketing Playbook
    includes: "PDF, video lessons, and templates.",
    category: "Marketing, Professional",
    reviews: [
      { text: "Grew my business 2x in 3 months!", author: "Tebogo F." }
    ]
  },
  {
    id: "12",
    name: "Canva Instagram Story Pack",
    description: "100+ editable story templates for Canva.",
    features: ["Trendy designs", "Easy to edit", "Mobile optimized", "Instant download"],
    price: 149,
    oldPrice: 250,
    discount: "Save 40%",
  image: "https://images.pexels.com/photos/1707828/pexels-photo-1707828.jpeg?auto=compress&w=600&q=80", // Canva Instagram Story Pack
    includes: "Canva links and PDF guide.",
    category: "Design, Need",
    reviews: [
      { text: "My stories look amazing!", author: "Nomvula Z." }
    ]
  },
  {
    id: "13",
    name: "Remote Work Success Kit",
    description: "Guides, checklists, and tools for remote teams.",
    features: ["Team onboarding guide", "Productivity checklist", "Meeting templates", "Instant download"],
    price: 299,
    oldPrice: 450,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/267614/pexels-photo-267614.jpeg?auto=compress&w=600&q=80", // Remote Work Success Kit
    includes: "PDFs, templates, and bonus resources.",
    category: "Productivity, Professional",
    reviews: [
      { text: "Remote work is so much easier now!", author: "Mpho L." }
    ]
  },
  {
    id: "14",
    name: "AI Art Generator Toolkit",
    description: "Create stunning AI art with prompts and guides.",
    features: ["Prompt library", "Step-by-step guide", "Bonus: AI art gallery", "Instant download"],
    price: 499,
    oldPrice: 800,
    discount: "Save 38%",
  image: "https://images.pexels.com/photos/1181674/pexels-photo-1181674.jpeg?auto=compress&w=600&q=80", // AI Art Generator Toolkit
    includes: "PDF, prompt files, and gallery access.",
    category: "AI, Professional",
    reviews: [
      { text: "My art is now next-level!", author: "Nandi P." }
    ]
  },
  {
    id: "15",
    name: "Essential Startup Legal Kit",
    description: "Legal templates for new businesses.",
    features: ["Company registration guide", "Shareholder agreement", "Employment contract", "Instant download"],
    price: 599,
    oldPrice: 950,
    discount: "Save 37%",
  image: "https://images.pexels.com/photos/2102417/pexels-photo-2102417.jpeg?auto=compress&w=600&q=80", // Essential Startup Legal Kit
    includes: "Word, PDF, and Google Docs files.",
    category: "Business, Need",
    reviews: [
      { text: "Made my startup launch stress-free!", author: "Siphesihle G." }
    ]
  },
  {
    id: "16",
    name: "Digital Course Launch Planner",
    description: "Plan, build, and launch your online course.",
    features: ["Course outline template", "Launch checklist", "Marketing plan", "Instant download"],
    price: 499,
    oldPrice: 800,
    discount: "Save 38%",
  image: "https://images.pexels.com/photos/1181675/pexels-photo-1181675.jpeg?auto=compress&w=600&q=80", // Digital Course Launch Planner
    includes: "PDF, Notion, and Google Sheets files.",
    category: "Education, Professional",
    reviews: [
      { text: "Launched my first course with confidence!", author: "Thuli N." }
    ]
  },
  {
    id: "17",
    name: "Ultimate Canva Template Bundle",
    description: "500+ templates for social, business, and more.",
    features: ["Editable in Canva", "Modern designs", "Bonus: Icon pack", "Instant download"],
    price: 799,
    oldPrice: 1200,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/1707829/pexels-photo-1707829.jpeg?auto=compress&w=600&q=80", // Ultimate Canva Template Bundle
    includes: "Canva links and PDF guide.",
    category: "Design, Professional",
    reviews: [
      { text: "So many templates!", author: "Ayanda Q." }
    ]
  },
  {
    id: "18",
    name: "Essential Website Launch Kit",
    description: "Checklists, templates, and guides for new sites.",
    features: ["SEO checklist", "Content planner", "Launch timeline", "Instant download"],
    price: 399,
    oldPrice: 600,
    discount: "Save 33%",
  image: "https://images.pexels.com/photos/1037993/pexels-photo-1037993.jpeg?auto=compress&w=600&q=80", // Essential Website Launch Kit
    includes: "PDFs, templates, and bonus resources.",
    category: "Web, Need",
    reviews: [
      { text: "My website launch was flawless!", author: "Lwazi V." }
    ]
  },
  {
    id: "19",
    name: "Professional Invoice Generator",
    description: "Create branded invoices in seconds.",
    features: ["Customizable templates", "PDF export", "Branding options", "Instant download"],
    price: 249,
    oldPrice: 400,
    discount: "Save 38%",
  image: "https://images.pexels.com/photos/4386376/pexels-photo-4386376.jpeg?auto=compress&w=600&q=80", // Professional Invoice Generator
    includes: "Web app access and PDF templates.",
    category: "Business, Professional",
    reviews: [
      { text: "My invoices look so professional!", author: "Gugu M." }
    ]
  },
  {
    id: "20",
    name: "AI-Powered Resume Analyzer",
    description: "Get instant feedback and tips for your CV.",
    features: ["AI scoring", "Actionable tips", "ATS check", "Instant download"],
    price: 349,
    oldPrice: 500,
    discount: "Save 30%",
  image: "https://images.pexels.com/photos/1181676/pexels-photo-1181676.jpeg?auto=compress&w=600&q=80", // AI-Powered Resume Analyzer
    includes: "Web app access and PDF report.",
    category: "AI, Need",
    reviews: [
      { text: "Helped me get more interviews!", author: "Bongani J." }
    ]
  }
];
