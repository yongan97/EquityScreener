"use client";

import { useState } from "react";
import { useAuth, AuthModal } from "@/components/auth";
import { Button } from "@/components/ui/button";
import { PRICING } from "@/types/auth";
import {
  Check,
  X,
  Loader2,
  TrendingUp,
  BarChart3,
  Download,
  Mail,
  Star,
  Clock,
  Zap,
} from "lucide-react";
import Link from "next/link";

export default function PricingPage() {
  const { user, isPremium } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  const handleUpgrade = async () => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("/api/stripe/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: user.id,
          email: user.email,
          priceId: PRICING.premium.priceId,
        }),
      });

      const { url, error } = await response.json();
      if (error) throw new Error(error);
      if (url) window.location.href = url;
    } catch (error) {
      console.error("Checkout error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const freeFeatures = [
    { included: true, text: "1 sample stock pick daily" },
    { included: true, text: "Basic AI score (number only)" },
    { included: false, text: "Full trade idea analysis" },
    { included: false, text: "AI score breakdown" },
    { included: false, text: "CSV export" },
    { included: false, text: "Historical data" },
    { included: false, text: "Daily newsletter" },
  ];

  const premiumFeatures = [
    { icon: TrendingUp, text: "ALL stock picks (100+ daily)" },
    { icon: Star, text: "Complete AI trade ideas" },
    { icon: BarChart3, text: "Full AI score breakdown" },
    { icon: Download, text: "CSV export" },
    { icon: Clock, text: "Historical data access" },
    { icon: Mail, text: "Daily newsletter" },
    { icon: Zap, text: "Priority support" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <Link
            href="/"
            className="text-sm text-muted-foreground hover:text-foreground mb-4 inline-block"
          >
            ← Back to Screener
          </Link>
          <h1 className="text-4xl font-bold mb-4">
            Unlock AI-Powered Stock Picks
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Get daily GARP stock recommendations with complete AI analysis,
            trade ideas, and entry/exit points.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Free Tier */}
          <div className="border rounded-xl p-8 bg-card">
            <h2 className="text-2xl font-bold mb-2">Free Sample</h2>
            <p className="text-muted-foreground mb-6">
              Preview our AI quality
            </p>
            <div className="text-4xl font-bold mb-6">
              $0
              <span className="text-base font-normal text-muted-foreground">
                /month
              </span>
            </div>

            <ul className="space-y-3 mb-8">
              {freeFeatures.map((feature, index) => (
                <li key={index} className="flex items-center gap-3">
                  {feature.included ? (
                    <Check className="h-5 w-5 text-green-600 dark:text-green-400" />
                  ) : (
                    <X className="h-5 w-5 text-muted-foreground" />
                  )}
                  <span
                    className={
                      feature.included ? "" : "text-muted-foreground line-through"
                    }
                  >
                    {feature.text}
                  </span>
                </li>
              ))}
            </ul>

            <Button variant="outline" className="w-full" asChild>
              <Link href="/">View Free Sample</Link>
            </Button>
          </div>

          {/* Premium Tier */}
          <div className="border-2 border-amber-500 rounded-xl p-8 bg-gradient-to-br from-amber-50/50 to-orange-50/50 dark:from-amber-950/20 dark:to-orange-950/20 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-amber-500 text-white px-4 py-1 rounded-full text-sm font-medium">
              Most Popular
            </div>

            <h2 className="text-2xl font-bold mb-2">Premium</h2>
            <p className="text-muted-foreground mb-6">Full access to everything</p>
            <div className="text-4xl font-bold mb-6">
              ${PRICING.premium.price}
              <span className="text-base font-normal text-muted-foreground">
                /month
              </span>
            </div>

            <ul className="space-y-3 mb-8">
              {premiumFeatures.map((feature, index) => (
                <li key={index} className="flex items-center gap-3">
                  <feature.icon className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  <span>{feature.text}</span>
                </li>
              ))}
            </ul>

            {isPremium ? (
              <Button className="w-full" disabled>
                <Check className="mr-2 h-4 w-4" />
                Current Plan
              </Button>
            ) : (
              <Button
                className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                size="lg"
                onClick={handleUpgrade}
                disabled={isLoading}
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {user ? "Upgrade Now" : "Sign Up & Upgrade"}
              </Button>
            )}

            <p className="text-xs text-center text-muted-foreground mt-3">
              Cancel anytime. No questions asked.
            </p>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="max-w-2xl mx-auto mt-16">
          <h2 className="text-2xl font-bold text-center mb-8">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">What is GARP screening?</h3>
              <p className="text-muted-foreground">
                GARP (Growth At a Reasonable Price) combines growth investing
                with value investing. We find stocks with strong growth
                potential that aren&apos;t overvalued.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">How often is data updated?</h3>
              <p className="text-muted-foreground">
                Our AI analyzes the market every weekday at 6 AM EST, providing
                fresh picks before market open.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Can I cancel anytime?</h3>
              <p className="text-muted-foreground">
                Yes! You can cancel your subscription at any time from your
                account settings. You&apos;ll retain access until the end of your
                billing period.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-muted-foreground">
                We accept all major credit cards through Stripe, our secure
                payment processor.
              </p>
            </div>
          </div>
        </div>
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultMode="signup"
      />
    </div>
  );
}
