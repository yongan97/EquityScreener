"use client";

import { useState } from "react";
import { useAuth } from "./AuthProvider";
import { AuthModal } from "./AuthModal";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  User,
  LogOut,
  CreditCard,
  Crown,
  Loader2,
  Settings,
} from "lucide-react";

export function UserMenu() {
  const { user, profile, isPremium, isLoading, signOut } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isPortalLoading, setIsPortalLoading] = useState(false);

  const handleManageSubscription = async () => {
    if (!user) return;

    setIsPortalLoading(true);
    try {
      const response = await fetch("/api/stripe/portal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: user.id }),
      });

      const { url, error } = await response.json();
      if (error) throw new Error(error);
      if (url) window.location.href = url;
    } catch (error) {
      console.error("Portal error:", error);
    } finally {
      setIsPortalLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Button variant="ghost" size="icon" disabled>
        <Loader2 className="h-4 w-4 animate-spin" />
      </Button>
    );
  }

  if (!user) {
    return (
      <>
        <Button variant="outline" onClick={() => setShowAuthModal(true)}>
          Sign In
        </Button>
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      </>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="flex items-center gap-2">
          {isPremium && <Crown className="h-4 w-4 text-amber-500" />}
          <User className="h-4 w-4" />
          <span className="hidden sm:inline-block max-w-[150px] truncate">
            {profile?.full_name || user.email?.split("@")[0]}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">
              {profile?.full_name || "User"}
            </p>
            <p className="text-xs leading-none text-muted-foreground truncate">
              {user.email}
            </p>
            {isPremium && (
              <span className="inline-flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400 mt-1">
                <Crown className="h-3 w-3" />
                Premium Member
              </span>
            )}
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {isPremium ? (
          <DropdownMenuItem
            onClick={handleManageSubscription}
            disabled={isPortalLoading}
          >
            {isPortalLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Settings className="mr-2 h-4 w-4" />
            )}
            Manage Subscription
          </DropdownMenuItem>
        ) : (
          <DropdownMenuItem
            onClick={() => {
              window.location.href = "/pricing";
            }}
          >
            <CreditCard className="mr-2 h-4 w-4" />
            Upgrade to Premium
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => signOut()}>
          <LogOut className="mr-2 h-4 w-4" />
          Sign Out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
