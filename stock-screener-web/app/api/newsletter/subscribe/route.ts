import { NextRequest, NextResponse } from "next/server";
import { createServerSupabaseClient } from "@/lib/supabase";

export async function POST(request: NextRequest) {
  try {
    const { email, source = "website" } = await request.json();

    if (!email || typeof email !== "string") {
      return NextResponse.json(
        { error: "Valid email is required" },
        { status: 400 }
      );
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: "Invalid email format" },
        { status: 400 }
      );
    }

    const supabase = createServerSupabaseClient();

    // Check if already subscribed
    const { data: existing } = await supabase
      .from("newsletter_subscribers")
      .select("id, subscribed")
      .eq("email", email.toLowerCase())
      .single();

    if (existing) {
      if (existing.subscribed) {
        return NextResponse.json(
          { message: "Already subscribed!" },
          { status: 200 }
        );
      } else {
        // Re-subscribe
        await supabase
          .from("newsletter_subscribers")
          .update({ subscribed: true, unsubscribed_at: null })
          .eq("id", existing.id);

        return NextResponse.json(
          { message: "Welcome back! You've been re-subscribed." },
          { status: 200 }
        );
      }
    }

    // Create new subscription
    const { error } = await supabase.from("newsletter_subscribers").insert({
      email: email.toLowerCase(),
      source,
      subscribed: true,
    });

    if (error) {
      console.error("Newsletter subscription error:", error);
      return NextResponse.json(
        { error: "Failed to subscribe. Please try again." },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { message: "Successfully subscribed to the newsletter!" },
      { status: 201 }
    );
  } catch (error) {
    console.error("Newsletter API error:", error);
    return NextResponse.json(
      { error: "An error occurred. Please try again." },
      { status: 500 }
    );
  }
}
