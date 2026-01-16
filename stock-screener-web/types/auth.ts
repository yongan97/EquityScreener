// Auth and subscription types

import { User } from "@supabase/supabase-js";

export interface Profile {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  stripe_customer_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  id: string;
  user_id: string;
  stripe_subscription_id: string | null;
  stripe_price_id: string | null;
  status: SubscriptionStatus;
  tier: SubscriptionTier;
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  created_at: string;
  updated_at: string;
}

export type SubscriptionStatus =
  | "active"
  | "canceled"
  | "past_due"
  | "trialing"
  | "inactive";

export type SubscriptionTier = "free" | "premium";

export interface NewsletterSubscriber {
  id: string;
  email: string;
  user_id: string | null;
  subscribed: boolean;
  source: string;
  created_at: string;
  unsubscribed_at: string | null;
}

// Auth context type
export interface AuthContextType {
  user: User | null;
  profile: Profile | null;
  subscription: Subscription | null;
  isLoading: boolean;
  isPremium: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, fullName?: string) => Promise<void>;
  signOut: () => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  refreshSubscription: () => Promise<void>;
}

// Pricing constants
export const PRICING = {
  premium: {
    price: 5,
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID || "",
    features: [
      "Access to ALL stock picks (100+ daily)",
      "Complete AI trade ideas with entry/exit points",
      "Full AI score breakdown",
      "CSV export",
      "Historical data access",
      "Daily newsletter",
    ],
  },
  free: {
    price: 0,
    features: [
      "1 sample stock pick per day",
      "Title-only trade ideas",
      "Basic AI score (number only)",
    ],
  },
} as const;
