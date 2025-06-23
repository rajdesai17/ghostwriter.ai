import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-white border border-gray-200 rounded-2xl shadow-sm p-8 hover:shadow-md transition-shadow duration-200 ${className}`}>
      {children}
    </div>
  );
}