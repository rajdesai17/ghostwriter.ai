"use client";
import React from "react";
import { motion, MotionProps } from "motion/react";

import { cn } from "@/lib/utils";

interface GradientTextProps extends Omit<React.HTMLAttributes<HTMLElement>, keyof MotionProps> {
  className?: string;
  children: React.ReactNode;
  as?: React.ElementType;
}

function GradientText({ className, children, as: Component = "span", ...props }: GradientTextProps) {
  // @ts-ignore -- create is not typed in motion/react yet
  const MotionComponent = motion.create(Component);

  return (
    <MotionComponent
      className={cn(
        "relative inline-block bg-gradient-to-r from-pink-500 via-purple-500 via-blue-500 to-cyan-500 bg-clip-text text-transparent",
        "bg-[length:200%_200%] animate-gradient-shift",
        className,
      )}
      {...props}
    >
      {children}
    </MotionComponent>
  );
}

export { GradientText }; 