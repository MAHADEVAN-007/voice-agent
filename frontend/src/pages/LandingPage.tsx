import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import PhoneInput from "react-phone-number-input";
import "react-phone-number-input/style.css";
import { motion, AnimatePresence, useScroll, useSpring } from "motion/react";
import * as Accordion from "@radix-ui/react-accordion";
import {
  Phone,
  MessageSquareText,
  Warehouse,
  Languages,
  Headphones,
  CheckCircle2,
  ChevronDown,
  ShoppingCart,
  TrendingUp,
  Clock,
  ChevronRight,
  Menu,
  X,
  Shield,
  Zap,
  Store,
  Truck,
} from "lucide-react";

/* ──────────────── Data ──────────────── */

const phrases = [
  "AI-Powered Wholesale Ordering",
  "Order in Hindi or English",
  "Get WhatsApp Confirmation",
  "Real-time Inventory Updates",
  "500+ Retailers Trust Us",
];

const steps = [
  { icon: Phone, title: "Enter Your Number", desc: "Type your phone — VocalKart calls you within seconds" },
  { icon: Headphones, title: "AI Takes Your Order", desc: "Natural conversation in Hindi or English. No bots, no IVR" },
  { icon: CheckCircle2, title: "Confirmed on WhatsApp", desc: "Order summary lands on your WhatsApp. Inventory updates live" },
];

const features = [
  { icon: Headphones, title: "AI Voice Agent", desc: "VocalKart handles the entire conversation — understands context, remembers your preferences, and never puts you on hold" },
  { icon: Languages, title: "Bilingual & Natural", desc: "Seamlessly switch between Hindi and English mid-conversation. It speaks like a real person" },
  { icon: MessageSquareText, title: "Instant WhatsApp Summary", desc: "Every order is confirmed via WhatsApp with itemized bill. No missed orders, no confusion" },
  { icon: Warehouse, title: "Real-Time Inventory Sync", desc: "Stock updates the moment you order. Never order out-of-stock items again" },
  { icon: ShoppingCart, title: "Bulk Ordering Made Easy", desc: "Designed for kirana shops — order by case, get scheme discounts, track past orders" },
  { icon: TrendingUp, title: "Smart Recommendations", desc: "Suggests relevant products based on your order history and current schemes" },
];



const faqs = [
  { q: "Is this free to use?", a: "Yes! VocalKart is completely free for retailers. You only pay for what you order, just like a regular phone call to your distributor." },
  { q: "Do I need a smartphone?", a: "Nope. Any phone works. VocalKart calls you, you speak, order is placed. That's it." },
  { q: "What languages does it understand?", a: "Hindi and English — and Hinglish (mixing both). It speaks Hindi naturally and understands common English product names." },
  { q: "How do I get my order confirmation?", a: "VocalKart sends a detailed WhatsApp message with every item, quantity, price, and total amount right after you confirm." },
];

const useCases = [
  { icon: Store, title: "Kirana Stores", desc: "Daily restocking for shopkeepers. Order by case, get scheme discounts automatically" },
  { icon: Warehouse, title: "Wholesalers", desc: "Handle hundreds of retailer orders without a dedicated call center team" },
  { icon: Truck, title: "Distributors", desc: "Streamlined order-to-delivery pipeline with auto-inventory sync" },
  { icon: Store, title: "Department Stores", desc: "Multi-category ordering with smart suggestions based on season" },
];




/* ──────────────── Component ──────────────── */

export default function LandingPage() {
  const [phoneNumber, setPhoneNumber] = useState<string>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const isValid = phoneNumber && phoneNumber.length >= 10;

  const handleCall = async () => {
    if (!isValid) return;
    setIsLoading(true);
    setError("");
    try {
      const res = await fetch("/api/create-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: phoneNumber }),
      });
      if (!res.ok) {
        let msg = `Server error: ${res.status}`;
        try { const errBody = await res.json(); msg = errBody.detail || msg; }
        catch { msg = (await res.text()) || msg; }
        throw new Error(msg);
      }
      const data = await res.json();
      navigate(`/call/${data.room_name}`, { state: { token: data.token, wsUrl: data.ws_url } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start call");
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    setMobileMenuOpen(false);
  };

  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30 });

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.06, delayChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 24 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] as const } }
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.96 },
    visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] as const } },
    hover: { y: -5, borderColor: "rgba(59,130,246,0.3)", transition: { duration: 0.25 } }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white overflow-x-hidden relative">
      {/* Page-level background */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-400/12 via-purple-400/8 to-transparent" />
        <motion.div
          animate={{ scale: [1, 1.1, 1], rotate: [0, 5, 0] }}
          transition={{ duration: 20, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          className="absolute -top-40 -left-40 w-[800px] h-[800px] bg-blue-500/15 rounded-full blur-[120px]"
        />
        <motion.div
          animate={{ scale: [1, 1.15, 1], rotate: [0, -5, 0] }}
          transition={{ duration: 25, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          className="absolute -bottom-40 -right-40 w-[700px] h-[700px] bg-purple-500/10 rounded-full blur-[120px]"
        />
      </div>

      {/* Scroll Progress Bar */}
      <motion.div className="fixed top-0 left-0 right-0 h-1 origin-left z-50 bg-scroll-gradient" style={{ scaleX }} />

      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-40 backdrop-blur-xl bg-neutral-950/70 border-b border-neutral-800/50">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <button onClick={() => scrollToSection("hero")} className="flex items-center gap-2">
            <span className="text-lg font-bold text-blue-400">VocalKart</span>
          </button>
          <div className="hidden md:flex items-center gap-8 text-sm">
            {[
              { id: "how", label: "How it Works" },
              { id: "demo", label: "Live Demo" },
              { id: "features", label: "Features" },
              { id: "faq", label: "FAQ" },
            ].map((link) => (
              <button key={link.id} onClick={() => scrollToSection(link.id)} className="text-neutral-400 hover:text-white transition-colors">{link.label}</button>
            ))}
            <button onClick={() => scrollToSection("hero")} className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium transition-all">
              Get Started
            </button>
          </div>
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="md:hidden text-neutral-400">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden bg-neutral-900/95 backdrop-blur-xl border-b border-neutral-800 md:hidden">
              <div className="flex flex-col p-4 gap-2 text-sm">
                {[
                  { id: "how", label: "How it Works" },
                  { id: "demo", label: "Live Demo" },
                  { id: "features", label: "Features" },
                  { id: "faq", label: "FAQ" },
                ].map((link) => (
                  <button key={link.id} onClick={() => scrollToSection(link.id)} className="text-left py-2.5 px-3 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800 transition-all">{link.label}</button>
                ))}
                <button onClick={() => scrollToSection("hero")} className="bg-blue-600 text-white px-4 py-2.5 rounded-lg text-center font-medium mt-2">Get Started</button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* ========== HERO ========== */}
      <section id="hero" className="relative min-h-screen flex flex-col items-center justify-center px-4 pt-24 pb-20 text-center overflow-hidden bg-gradient-to-b from-blue-400/15 via-purple-400/10 to-transparent">
        <div className="relative z-10 max-w-4xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-blue-600/10 border border-blue-500/20 text-blue-400 text-xs sm:text-sm font-medium mb-6">
              <Zap className="w-3.5 h-3.5" /> AI-Powered Voice Ordering Platform
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl sm:text-7xl lg:text-8xl font-extrabold text-white leading-tight text-balance"
          >
            VocalKart
          </motion.h1>

          <AnimatedPhrases />

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-6 text-neutral-400 max-w-2xl mx-auto text-sm sm:text-base leading-relaxed"
          >
            Your AI ordering assistant. VocalKart calls you, takes your order in <span className="text-blue-400 font-medium">Hindi</span> or <span className="text-purple-400 font-medium">English</span>, sends WhatsApp confirmation, and updates inventory, all in one phone call.
          </motion.p>

          {/* Hero Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="flex items-center justify-center gap-6 sm:gap-10 mt-8 text-sm"
          >
            {[
              { value: "No app", label: "works on any phone" },
              { value: "Hindi + English", label: "bilingual by default" },
              { value: "WhatsApp", label: "instant confirmation" },
              { value: "Real-time", label: "inventory sync" },
            ].map((m) => (
              <div key={m.label} className="text-center">
                <p className="font-bold text-base sm:text-lg text-blue-400">{m.value}</p>
                <p className="text-neutral-500 text-xs">{m.label}</p>
              </div>
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="mt-10 w-full max-w-sm mx-auto"
          >
            <div className="relative p-[1px] rounded-2xl bg-gradient-to-b from-blue-400/40 via-purple-400/30 to-blue-400/20">
              <div className="rounded-2xl bg-neutral-900/80 backdrop-blur-sm p-6 space-y-4">
                <PhoneInput
                  international
                  countryCallingCodeEditable={false}
                  defaultCountry="IN"
                  value={phoneNumber}
                  onChange={setPhoneNumber}
                  className="w-full [&_.PhoneInputCountry]:bg-blue-600/15 [&_.PhoneInputCountry]:border [&_.PhoneInputCountry]:border-blue-500/30 [&_.PhoneInputCountry]:rounded-lg [&_.PhoneInputCountry]:px-2 [&_.PhoneInputCountry]:py-1.5 [&_.PhoneInputCountry]:transition-colors [&_.PhoneInputInput]:bg-transparent [&_.PhoneInputInput]:border [&_.PhoneInputInput]:border-neutral-700 [&_.PhoneInputInput]:rounded-lg [&_.PhoneInputInput]:px-4 [&_.PhoneInputInput]:py-3 [&_.PhoneInputInput]:text-white [&_.PhoneInputInput]:placeholder:text-neutral-500 [&_.PhoneInputInput]:focus:border-blue-500/50 [&_.PhoneInputInput]:focus:outline-none"
                />

                {error && <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-red-500 text-sm">{error}</motion.p>}

                <button
                  onClick={handleCall}
                  disabled={!isValid || isLoading}
                  className={`group relative text-white font-semibold px-8 py-3.5 rounded-xl text-lg transition-all w-full flex items-center justify-center gap-2 overflow-hidden ${!isValid || isLoading ? "bg-neutral-700 cursor-not-allowed" : "bg-gradient-to-r from-blue-400 to-purple-400 hover:brightness-110"}`}
                >
                  <motion.span animate={isLoading ? { rotate: 360 } : {}} transition={isLoading ? { repeat: Number.POSITIVE_INFINITY, duration: 1, ease: "linear" } : {}}>
                    <Phone className="w-5 h-5" />
                  </motion.span>
                  {isLoading ? "Connecting..." : "Call Agent"}
                </button>

              </div>
            </div>
          </motion.div>
        </div>

        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          onClick={() => scrollToSection("demo")}
          className="absolute bottom-6 left-1/2 -translate-x-1/2 text-neutral-600 hover:text-neutral-400 transition-colors"
        >
          <motion.div animate={{ y: [0, 6, 0] }} transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }} className="flex flex-col items-center gap-1">
            <span className="text-xs">See how it works</span>
            <ChevronDown className="w-5 h-5" />
          </motion.div>
        </motion.button>
      </section>

      {/* ========== USE CASES ========== */}
      <section className="px-4 py-16 max-w-6xl mx-auto">
        <SectionHeading title="Who is VocalKart for?" />
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {useCases.map((uc) => (
            <motion.div
              key={uc.title}
              variants={itemVariants}
              whileHover="hover"
              className="p-5 rounded-xl bg-neutral-900/40 border border-neutral-800/60 hover:border-blue-500/30 transition-colors hover:bg-neutral-900/60"
            >
              <uc.icon className="w-8 h-8 text-blue-400 mb-3" />
              <h3 className="font-semibold text-sm mb-1">{uc.title}</h3>
              <p className="text-neutral-500 text-xs leading-relaxed">{uc.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ========== HOW IT WORKS ========== */}
      <section id="how" className="px-4 py-24 max-w-5xl mx-auto scroll-mt-20">
          <SectionHeading
            title="How it works"
            subtitle="From number entry to order confirmation — VocalKart handles everything in one seamless call"
          />

          <div className="relative">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-8 relative"
            >
              {steps.map((step, i) => (
                <motion.div
                  key={step.title}
                  variants={cardVariants}
                  whileHover="hover"
                  className="relative flex flex-col items-center text-center gap-4 p-8 rounded-2xl bg-neutral-900/60 border border-neutral-800/70 hover:border-blue-500/30 transition-colors group"
                >
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-neutral-950 px-3 text-neutral-500 text-xs font-bold">
                    Step {i + 1}
                  </div>
                  <motion.div
                    whileHover={{ scale: 1.15, rotate: [0, -10, 10, 0] }}
                    transition={{ duration: 0.4 }}
                    className="w-14 h-14 rounded-full bg-blue-600/15 flex items-center justify-center"
                  >
                    <step.icon className="w-7 h-7 text-blue-400" />
                  </motion.div>
                  <h3 className="font-bold text-lg">{step.title}</h3>
                  <p className="text-neutral-400 text-sm leading-relaxed">{step.desc}</p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

      {/* ========== FEATURES ========== */}
      <section id="features" className="px-4 py-24 max-w-6xl mx-auto scroll-mt-20">
          <SectionHeading
            title="Why VocalKart?"
            subtitle="Built for kirana stores, wholesalers, and distributors who want ordering as simple as a phone call"
          />

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {features.map((f) => (
              <motion.div
                key={f.title}
                variants={cardVariants}
                whileHover="hover"
                className="p-6 rounded-2xl bg-neutral-900/40 border border-neutral-800/60 hover:border-blue-500/30 transition-colors"
              >
                <motion.div
                  whileHover={{ scale: 1.1, rotate: [0, -5, 5, 0] }}
                  transition={{ duration: 0.3 }}
                  className="w-10 h-10 rounded-lg bg-blue-600/15 flex items-center justify-center mb-4"
                >
                  <f.icon className="w-5 h-5 text-blue-400" />
                </motion.div>
                <h3 className="font-semibold text-base mb-2">{f.title}</h3>
                <p className="text-neutral-400 text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

      {/* ========== CTA ========== */}
      <section className="px-4 py-24 max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] as const }}
            className="relative p-10 sm:p-14 rounded-3xl bg-blue-600/5 border border-blue-500/20 overflow-hidden"
          >
            <motion.div
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 20, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
              className="absolute -top-20 -right-20 w-40 h-40 bg-blue-500/15 rounded-full blur-3xl"
            />
            <motion.div
              animate={{ rotate: [360, 0] }}
              transition={{ duration: 25, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
              className="absolute -bottom-20 -left-20 w-40 h-40 bg-blue-500/15 rounded-full blur-3xl"
            />
            <div className="relative z-10 space-y-5">
              <h2 className="text-3xl sm:text-4xl font-bold">Ready to Simplify Your Ordering?</h2>
              <p className="text-neutral-400 max-w-lg mx-auto">Join 500+ retailers who've switched to VocalKart. Your AI assistant is one call away. No app. No training. Just a phone call.</p>
              <motion.button
                onClick={() => scrollToSection("hero")}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3.5 rounded-xl text-lg transition-colors mt-2"
              >
                Get Started Free
                <motion.span
                  animate={{ x: [0, 4, 0] }}
                  transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
                >
                  <ChevronRight className="w-5 h-5" />
                </motion.span>
              </motion.button>
              <p className="text-neutral-600 text-xs"><Shield className="w-3 h-3 inline mr-1" /> No credit card required. Free to use.</p>
            </div>
          </motion.div>
        </section>

      {/* ========== FAQ ========== */}
      <section id="faq" className="px-4 py-24 max-w-3xl mx-auto scroll-mt-20">
          <SectionHeading title="Frequently Asked Questions" />

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
          >
            <Accordion.Root type="single" collapsible className="space-y-3">
              {faqs.map((faq, i) => (
                <motion.div key={i} variants={itemVariants}>
                  <Accordion.Item value={`faq-${i}`}>
                    <Accordion.Header>
                      <Accordion.Trigger className="group flex w-full items-center justify-between p-5 rounded-xl bg-neutral-900/40 border border-neutral-800/60 hover:border-blue-500/30 transition-all text-left">
                        <span className="font-medium text-sm sm:text-base pr-4">{faq.q}</span>
                        <motion.div
                          animate={{ rotate: i === 0 ? 0 : undefined }}
                          transition={{ duration: 0.2 }}
                        >
                          <ChevronDown className="w-5 h-5 text-neutral-500 shrink-0 group-data-[state=open]:rotate-180 transition-transform" />
                        </motion.div>
                      </Accordion.Trigger>
                    </Accordion.Header>
                    <Accordion.Content className="overflow-hidden data-[state=open]:animate-accordion-slide-down data-[state=closed]:animate-accordion-slide-up">
                      <div className="px-5 pb-5 pt-2 text-neutral-400 text-sm leading-relaxed">
                        {faq.a}
                      </div>
                    </Accordion.Content>
                  </Accordion.Item>
                </motion.div>
              ))}
            </Accordion.Root>
          </motion.div>
        </section>

      {/* ========== FOOTER ========== */}
      <motion.footer
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="border-t border-neutral-800 py-12 px-4"
        >
          <motion.div
            initial={{ y: 20 }}
            whileInView={{ y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4"
          >
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">VocalKart</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-neutral-500">
              <button onClick={() => scrollToSection("hero")} className="hover:text-neutral-300 transition-colors">Home</button>
              <button onClick={() => scrollToSection("features")} className="hover:text-neutral-300 transition-colors">Features</button>
              <button onClick={() => scrollToSection("faq")} className="hover:text-neutral-300 transition-colors">FAQ</button>
            </div>
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-neutral-600 text-sm"
            >
              &copy; {new Date().getFullYear()} VocalKart. All rights reserved.
            </motion.p>
          </motion.div>
        </motion.footer>
    </div>
  );
}

/* ──────────────── Sub-Components ──────────────── */

function AnimatedPhrases() {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setIndex((i) => (i + 1) % phrases.length), 3000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="h-10 mt-4 overflow-hidden">
      <AnimatePresence mode="wait">
        <motion.p
          key={index}
          initial={{ y: 24, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -24, opacity: 0 }}
          transition={{ duration: 0.35 }}
          className="text-xl sm:text-2xl text-transparent bg-gradient-to-r from-neutral-200 to-neutral-400 bg-clip-text font-semibold"
        >
          {phrases[index]}
        </motion.p>
      </AnimatePresence>
    </div>
  );
}

function SectionHeading({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] as const }}
      className="text-center mb-16"
    >
      <h2 className="text-3xl sm:text-4xl font-bold">{title}</h2>
      {subtitle && <p className="text-neutral-400 mt-3 max-w-md mx-auto">{subtitle}</p>}
      <motion.div
        initial={{ scaleX: 0 }}
        whileInView={{ scaleX: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
        className="h-0.5 w-16 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 mx-auto mt-4 rounded-full"
      />
    </motion.div>
  );
}





