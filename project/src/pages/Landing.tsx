import React from 'react';
import { Link } from 'react-router-dom';
import { PenTool, Sparkles, Users, Zap, ArrowRight } from 'lucide-react';
import { Button } from '../components/Button';
import { GradientText } from "@/components/ui/gradient-text";
import { GhostwriterNavbar } from "@/components/ui/ghostwriter-navbar";

export function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-orange-50">
      {/* Navigation */}
      <GhostwriterNavbar />

      {/* Hero Section */}
      <div className="relative z-10 px-6 lg:px-8 pt-16 pb-24">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-black text-gray-900 mb-8 leading-tight tracking-tighter">
            Write Like {" "}
            <GradientText className="px-1 font-extrabold text-gray-900">Humans</GradientText>
            <span className="block">Not {" "}
            <GradientText className="px-1 font-extrabold text-gray-900">ChatGPT</GradientText></span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed font-medium">
            Ghostwriter doesn't write for you — it writes like you. Raw. Real. Readable.
          </p>
          <Link to="/generate">
            <Button size="lg" className="bg-gray-900 hover:bg-gray-800 text-white px-8 py-4 text-lg font-semibold rounded-full inline-flex items-center space-x-2 shadow-lg">
              <span>Get Started</span>
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Product Showcase */}
      <div className="relative z-10 px-6 lg:px-8 pb-24">
        <div className="max-w-7xl mx-auto">
          <div className="relative">
            {/* Subtle gradient background */}
            <div className="absolute inset-0 bg-gradient-to-r from-orange-100 via-orange-50 to-orange-100 rounded-3xl transform rotate-1 scale-105 opacity-60"></div>
            
            {/* Product Interface Mockup */}
            <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
              {/* Browser Header */}
              <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                  </div>
                  <div className="flex-1 bg-white rounded-lg px-4 py-2 ml-4 border border-gray-200">
                    <span className="text-gray-500 text-sm font-medium">ghostwriter.app</span>
                  </div>
                </div>
              </div>

              {/* App Interface */}
              <div className="p-8">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                  {/* Left Sidebar */}
                  <div className="lg:col-span-3 space-y-6">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 mb-4">Navigation</h3>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-3 p-3 bg-orange-50 rounded-lg border border-orange-200">
                          <PenTool className="h-4 w-4 text-orange-600" />
                          <span className="text-sm font-semibold text-orange-900">Generate Posts</span>
                        </div>
                        <div className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                          <Users className="h-4 w-4 text-gray-500" />
                          <span className="text-sm font-medium text-gray-700">Voice Profiles</span>
                        </div>
                        <div className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                          <Sparkles className="h-4 w-4 text-gray-500" />
                          <span className="text-sm font-medium text-gray-700">Analytics</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Main Content */}
                  <div className="lg:col-span-6 space-y-6">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-2">Generate LinkedIn Post</h2>
                      <p className="text-gray-600 mb-6">Create engaging content using your voice profiles</p>
                    </div>

                    <div className="space-y-4">
                      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                        <label className="text-sm font-semibold text-gray-700 mb-2 block">Voice Profile</label>
                        <div className="bg-white rounded-lg px-4 py-3 border border-gray-200 font-medium text-gray-900">
                          Professional Thought Leader
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                        <label className="text-sm font-semibold text-gray-700 mb-2 block">Context</label>
                        <div className="bg-white rounded-lg px-4 py-3 border border-gray-200 text-gray-700 min-h-[80px]">
                          Share insights about AI transformation in modern business and how teams can adapt to new technologies...
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Right Panel */}
                  <div className="lg:col-span-3 space-y-6">
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                      <h3 className="text-sm font-semibold text-gray-700 mb-3">Generated Post</h3>
                      <div className="bg-white rounded-lg p-4 border border-gray-200 text-sm text-gray-700 space-y-2 min-h-[200px]">
                        <p className="font-medium">🚀 AI isn't just changing how we work—it's redefining what's possible.</p>
                        <p>After implementing AI solutions across three major projects, I've seen firsthand how the right approach can transform entire workflows.</p>
                        <p className="text-gray-500">Key insights from our journey...</p>
                        <div className="pt-2 border-t border-gray-100">
                          <span className="text-xs text-gray-400">Generated with Professional voice</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features-section" className="relative z-10 px-6 lg:px-8 pb-24">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300 group-hover:-translate-y-1">
                <div className="bg-blue-50 rounded-2xl p-4 w-16 h-16 mx-auto mb-6 flex items-center justify-center">
                  <Users className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Voice Profiles</h3>
                <p className="text-gray-600 leading-relaxed">Train AI on your unique writing style with custom voice profiles that capture your authentic voice.</p>
              </div>
            </div>
            <div className="text-center group">
              <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300 group-hover:-translate-y-1">
                <div className="bg-purple-50 rounded-2xl p-4 w-16 h-16 mx-auto mb-6 flex items-center justify-center">
                  <Zap className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Llama3 Powered</h3>
                <p className="text-gray-600 leading-relaxed">Powered by Llama3:8B, the optimal AI model for generating authentic and engaging LinkedIn content.</p>
              </div>
            </div>
            <div className="text-center group">
              <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300 group-hover:-translate-y-1">
                <div className="bg-orange-50 rounded-2xl p-4 w-16 h-16 mx-auto mb-6 flex items-center justify-center">
                  <Sparkles className="h-8 w-8 text-orange-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Authentic Content</h3>
                <p className="text-gray-600 leading-relaxed">Generate posts that sound genuinely like you, not generic AI content that lacks personality.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subtle background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-32 w-64 h-64 bg-orange-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
        <div className="absolute bottom-1/4 -right-32 w-64 h-64 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
      </div>
    </div>
  );
}