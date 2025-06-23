const API_BASE = 'http://localhost:8000';

async function fetchJSON(url: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export interface Profile {
  name: string;
  sampleCount: number;
  feedbackCount?: number;
  learningScore?: number;
}

export interface GenerateRequest {
  profile: string;
  context: string;
  instruction?: string;
}

export interface CreateProfileRequest {
  name: string;
  samples: string;
}

export interface AppendSamplesRequest {
  samples: string;
}

export interface FeedbackRequest {
  profile: string;
  context: string;
  instruction: string;
  generated_post: string;
  feedback_type: 'positive' | 'negative' | 'refinement';
  feedback_text: string;
  refinement_instruction?: string;
}

export interface RefineRequest {
  profile: string;
  original_post: string;
  feedback_text: string;
  context: string;
}

export interface FeedbackSummary {
  total_feedback: number;
  positive: number;
  negative: number;
  refinements: number;
  learning_score: number;
  recent_patterns: Array<{
    feedback_text: string;
    feedback_type: string;
    timestamp: string;
  }>;
}

export const api = {
  getProfiles: (): Promise<Profile[]> => fetchJSON('/profiles'),
  
  createProfile: (data: CreateProfileRequest): Promise<void> => 
    fetchJSON('/profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  appendSamples: (name: string, data: AppendSamplesRequest): Promise<void> => 
    fetchJSON(`/profiles/${encodeURIComponent(name)}/samples`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  generatePost: (data: GenerateRequest): Promise<{ result: string }> => 
    fetchJSON('/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Feedback endpoints
  submitFeedback: (data: FeedbackRequest): Promise<{ status: string; message: string }> =>
    fetchJSON('/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  refinePost: (data: RefineRequest): Promise<{ result: string }> =>
    fetchJSON('/refine', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getFeedbackSummary: (profileName: string): Promise<FeedbackSummary> =>
    fetchJSON(`/profiles/${encodeURIComponent(profileName)}/feedback`),

  getRelevantFeedback: (profileName: string, context: string, feedbackType?: string): Promise<{ feedback: any[] }> =>
    fetchJSON(`/profiles/${encodeURIComponent(profileName)}/feedback/relevant?context=${encodeURIComponent(context)}${feedbackType ? `&feedback_type=${feedbackType}` : ''}`),

  regeneratePost: (data: GenerateRequest): Promise<{ result: string }> =>
    fetchJSON('/regenerate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};