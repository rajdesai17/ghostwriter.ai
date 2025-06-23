import { useState, useEffect, useCallback } from 'react';
import { api, Profile, CreateProfileRequest, AppendSamplesRequest } from '../api';

export function useProfiles() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfiles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProfiles();
      setProfiles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch profiles');
    } finally {
      setLoading(false);
    }
  }, []);

  const createProfile = useCallback(async (data: CreateProfileRequest) => {
    await api.createProfile(data);
    await fetchProfiles();
  }, [fetchProfiles]);

  const appendSamples = useCallback(async (name: string, data: AppendSamplesRequest) => {
    await api.appendSamples(name, data);
    await fetchProfiles();
  }, [fetchProfiles]);

  useEffect(() => {
    fetchProfiles();
  }, [fetchProfiles]);

  return {
    profiles,
    loading,
    error,
    refetch: fetchProfiles,
    createProfile,
    appendSamples,
  };
}