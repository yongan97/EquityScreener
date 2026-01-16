"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useAuth } from "./AuthProvider";
import { AuthModal } from "./AuthModal";
import { PRICING } from "@/types/auth";
import {
  Loader2,
  Check,
  Lock,
  TrendingUp,
  BarChart3,
  Download,
  Mail,
  Star,
} from "lucide-react";

interface PaywallModalProps {
  isOpen: boolean;
  onClose: () => void;
  feature?: string;
}

export function PaywallModal({ isOpen, onClose, feature }: PaywallModalProps) {
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

  if (isPremium) {
    onClose();
    return null;
  }

  const features = [
    { icon: TrendingUp, text: "Access to ALL stock picks (100+ daily)" },
    { icon: Star, text: "Complete AI trade ideas with entry/exit points" },
    { icon: BarChart3, text: "Full AI score breakdown (6 components)" },
    { icon: Download, text: "CSV export for your own analysis" },
    { icon: BarChart3, text: "Historical data & performance tracking" },
    { icon: Mail, text: "Daily newsletter with top picks" },
  ];

  return (
    <>
      <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-amber-500" />
              Unlock Premium Access
            </DialogTitle>
            <DialogDescription>
              {feature
                ? `"${feature}" is a premium feature. `
                : "You're viewing our free sample. "}
              Upgrade to get full access to all AI-powered stock picks.
            </DialogDescription>
          </DialogHeader>

          <div className="mt-4">
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 rounded-lg p-6 border border-amber-200 dark:border-amber-800">
              <div className="flex items-baseline gap-2 mb-4">
                <span className="text-4xl font-bold">
                  ${PRICING.premium.price}
                </span>
                <span className="text-muted-foreground">/month</span>
              </div>

              <ul className="space-y-3">
                {features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-green-600 dark:text-green-400 shrink-0 mt-0.5" />
                    <span className="text-sm">{feature.text}</span>
                  </li>
                ))}
              </ul>

              <Button
                className="w-full mt-6 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                size="lg"
                onClick={handleUpgrade}
                disabled={isLoading}
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {user ? "Upgrade Now" : "Sign Up & Upgrade"}
              </Button>

              <p className="text-xs text-center text-muted-foreground mt-3">
                Cancel anytime. No questions asked.
              </p>
            </div>

            <div className="mt-4 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-center text-muted-foreground">
                <span className="font-medium">Free tier:</span> View 1 sample
                stock pick daily to preview our AI analysis quality.
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultMode="signup"
      />
    </>
  );
}
