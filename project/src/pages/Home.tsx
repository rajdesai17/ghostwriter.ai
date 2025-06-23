import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Copy, Lightbulb, Sparkles, ThumbsUp, ThumbsDown, RefreshCw } from 'lucide-react';
import { Button } from '../components/Button';
import { Select } from '../components/Select';
import { TextArea } from '../components/TextArea';
import { Card } from '../components/Card';
import { GradientText } from "@/components/ui/gradient-text";
import { useProfiles } from '../hooks/useProfiles';
import { useToastContext } from '../contexts/ToastContext';
import { useDebounce } from '../hooks/useDebounce';
import { usePerformance } from '../hooks/usePerformance';
import { api, FeedbackRequest } from '../api';

export function Home() {
  const [selectedProfile, setSelectedProfile] = useState('');
  const [context, setContext] = useState('');
  const [instructions, setInstructions] = useState('');
  const [result, setResult] = useState('');
  const [generating, setGenerating] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  // Feedback form state
  const [feedbackType, setFeedbackType] = useState<'positive' | 'negative' | 'refinement'>('positive');
  const [feedbackText, setFeedbackText] = useState('');
  const [refinementInstruction, setRefinementInstruction] = useState('');
  const [refining, setRefining] = useState(false);
  const [refinedPost, setRefinedPost] = useState('');

  const { profiles, loading: profilesLoading } = useProfiles();
  const { pushToast } = useToastContext();
  const { measureApiCall } = usePerformance();
  
  // Debounce context and instructions for better performance
  const debouncedContext = useDebounce(context, 300);
  const debouncedInstructions = useDebounce(instructions, 300);

  // Memoize expensive calculations
  const profileOptions = useMemo(() => 
    profiles.map(p => ({ 
      value: p.name, 
      label: p.name 
    })), [profiles]
  );

  const selectedProfileData = useMemo(() => 
    profiles.find(p => p.name === selectedProfile), 
    [profiles, selectedProfile]
  );

  const handleGenerate = useCallback(async () => {
    if (!selectedProfile || !debouncedContext.trim()) return;

    try {
      setGenerating(true);
      const response = await measureApiCall(
        'Generate post',
        () => api.generatePost({
          profile: selectedProfile,
          context: debouncedContext.trim(),
          instruction: debouncedInstructions.trim() || undefined,
        })
      );
      setResult(response.result);
      setShowFeedback(true);
      setRefinedPost('');
      pushToast({ type: 'success', message: 'Post generated successfully!' });
    } catch (error) {
      pushToast({ 
        type: 'error', 
        message: error instanceof Error ? error.message : 'Failed to generate post' 
      });
    } finally {
      setGenerating(false);
    }
  }, [selectedProfile, debouncedContext, debouncedInstructions, measureApiCall, pushToast]);

  const handleCopyToClipboard = async () => {
    try {
      const textToCopy = refinedPost || result;
      await navigator.clipboard.writeText(textToCopy);
      pushToast({ type: 'success', message: 'Copied to clipboard!' });
    } catch (error) {
      pushToast({ type: 'error', message: 'Failed to copy to clipboard' });
    }
  };

  const handleSubmitFeedback = async () => {
    if (!selectedProfile || !result || !feedbackText.trim()) {
      pushToast({ type: 'error', message: 'Please provide feedback text' });
      return;
    }

    try {
      const feedbackData: FeedbackRequest = {
        profile: selectedProfile,
        context: context.trim(),
        instruction: instructions.trim(),
        generated_post: result,
        feedback_type: feedbackType,
        feedback_text: feedbackText.trim(),
        refinement_instruction: refinementInstruction.trim() || undefined,
      };

      await api.submitFeedback(feedbackData);
      pushToast({ type: 'success', message: 'Feedback submitted!' });
      
      // Ask if user wants to regenerate with new learning
      const regenerateChoice = window.confirm(
        'Would you like to regenerate the post with your feedback applied?'
      );
      
      if (regenerateChoice) {
        try {
          setGenerating(true);
          const response = await api.regeneratePost({
            profile: selectedProfile,
            context: context.trim(),
            instruction: instructions.trim() || undefined,
          });
          setResult(response.result);
          setRefinedPost('');
          pushToast({ type: 'success', message: 'Post regenerated with your feedback!' });
        } catch (error) {
          pushToast({ 
            type: 'error', 
            message: error instanceof Error ? error.message : 'Failed to regenerate post' 
          });
        } finally {
          setGenerating(false);
        }
      }
      
      // Reset feedback form
      setFeedbackText('');
      setRefinementInstruction('');
      setShowFeedback(false);
      
    } catch (error) {
      pushToast({ 
        type: 'error', 
        message: error instanceof Error ? error.message : 'Failed to submit feedback' 
      });
    }
  };

  const handleRefinePost = async () => {
    if (!selectedProfile || !result || !refinementInstruction.trim()) {
      pushToast({ type: 'error', message: 'Please provide refinement instructions' });
      return;
    }

    try {
      setRefining(true);
      const response = await api.refinePost({
        profile: selectedProfile,
        original_post: result,
        feedback_text: refinementInstruction.trim(),
        context: context.trim(),
      });
      setRefinedPost(response.result);
      pushToast({ type: 'success', message: 'Post refined successfully!' });
    } catch (error) {
      pushToast({ 
        type: 'error', 
        message: error instanceof Error ? error.message : 'Failed to refine post' 
      });
    } finally {
      setRefining(false);
    }
  };

  return (
    <div className="space-y-12 max-w-4xl mx-auto">
      <div className="text-center">
        <h1 className="text-3xl md:text-4xl font-black text-gray-900 mb-2">
          Generate LinkedIn Post
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Create engaging content using your voice profiles
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Configuration Section */}
        <Card>
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Configuration</h2>
            
            <div className="space-y-4">
              <Select
                label="Voice Profile"
                value={selectedProfile}
                onChange={(e) => setSelectedProfile(e.target.value)}
                options={[
                  { value: '', label: profilesLoading ? 'Loading profiles...' : 'Select a profile' },
                  ...profileOptions,
                ]}
                disabled={profilesLoading}
              />
              
              {selectedProfileData && (
                <div className="flex items-center text-sm text-orange-700 bg-orange-50 px-4 py-3 rounded-xl border border-orange-200">
                  <Lightbulb className="h-4 w-4 mr-2 text-orange-600" />
                  <span className="font-medium">{selectedProfileData.sampleCount} writing samples in this profile</span>
                </div>
              )}

              <TextArea
                label="Context"
                placeholder="What would you like to write about? Describe your topic, experience, or idea..."
                value={context}
                onChange={(e) => setContext(e.target.value)}
                minRows={4}
                required
              />

              <TextArea
                label="Instructions (Optional)"
                placeholder="Any specific tone, style, or format you'd like? e.g., 'Make it more casual', 'Include a question', 'Keep it short'..."
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                minRows={3}
              />
            </div>

            <Button
              onClick={handleGenerate}
              disabled={!selectedProfile || !context.trim()}
              loading={generating}
              className="w-full bg-orange-500 hover:bg-orange-600 text-white"
              size="lg"
            >
              {generating ? 'Generating Post...' : 'Generate Post'}
            </Button>
          </div>
        </Card>

        {/* Generated Post Section */}
        <Card>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Generated Post</h2>
              {(result || refinedPost) && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyToClipboard}
                  className="flex items-center space-x-2"
                >
                  <Copy className="h-4 w-4" />
                  <span>Copy</span>
                </Button>
              )}
            </div>
            
            <TextArea
              placeholder="Your generated LinkedIn post will appear here..."
              value={refinedPost || result}
              readOnly
              minRows={16}
              className="resize-none bg-gray-50 border-gray-200"
            />

            {refinedPost && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-3">
                <p className="text-sm text-blue-800 font-medium">✨ Refined version based on your feedback</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Simplified Feedback Section */}
      {showFeedback && result && (
        <Card>
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Rate This Post</h3>
              <p className="text-gray-600">Help the AI learn your preferences for better future posts</p>
            </div>
            
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="grid grid-cols-3 gap-3">
                <Button
                  variant={feedbackType === 'positive' ? 'default' : 'outline'}
                  onClick={() => setFeedbackType('positive')}
                  className={`flex flex-col items-center py-6 ${feedbackType === 'positive' ? 'bg-green-500 hover:bg-green-600 text-white' : 'hover:border-green-300'}`}
                >
                  <ThumbsUp className="h-6 w-6 mb-2" />
                  <span className="text-sm font-medium">Love it!</span>
                </Button>
                <Button
                  variant={feedbackType === 'negative' ? 'default' : 'outline'}
                  onClick={() => setFeedbackType('negative')}
                  className={`flex flex-col items-center py-6 ${feedbackType === 'negative' ? 'bg-red-500 hover:bg-red-600 text-white' : 'hover:border-red-300'}`}
                >
                  <ThumbsDown className="h-6 w-6 mb-2" />
                  <span className="text-sm font-medium">Not quite</span>
                </Button>
                <Button
                  variant={feedbackType === 'refinement' ? 'default' : 'outline'}
                  onClick={() => setFeedbackType('refinement')}
                  className={`flex flex-col items-center py-6 ${feedbackType === 'refinement' ? 'bg-blue-500 hover:bg-blue-600 text-white' : 'hover:border-blue-300'}`}
                >
                  <RefreshCw className="h-6 w-6 mb-2" />
                  <span className="text-sm font-medium">Refine it</span>
                </Button>
              </div>

              <TextArea
                label="What would you change?"
                placeholder={
                  feedbackType === 'positive' 
                    ? "What made this perfect? e.g., 'Great tone', 'Perfect length', 'Exactly my style'..." 
                    : feedbackType === 'negative'
                    ? "What didn't work? e.g., 'Too formal', 'Wrong tone', 'Not personal enough'..."
                    : "How should it be improved? e.g., 'Make it more casual', 'Add emotion', 'Shorter sentences'..."
                }
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                minRows={3}
                required
              />

              {feedbackType === 'refinement' && (
                <div className="space-y-4">
                  <TextArea
                    label="Specific refinement instructions"
                    placeholder="Be specific about the changes you want. e.g., 'Make the tone more vulnerable', 'Add a call to action at the end', 'Use shorter sentences'..."
                    value={refinementInstruction}
                    onChange={(e) => setRefinementInstruction(e.target.value)}
                    minRows={3}
                  />
                  <Button
                    onClick={handleRefinePost}
                    disabled={!refinementInstruction.trim()}
                    loading={refining}
                    className="w-full bg-blue-500 hover:bg-blue-600 text-white"
                  >
                    {refining ? 'Creating refined version...' : 'Generate Refined Version'}
                  </Button>
                </div>
              )}

              <Button
                onClick={handleSubmitFeedback}
                disabled={!feedbackText.trim()}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white"
                size="lg"
              >
                Submit Feedback
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}