import React, { useState } from 'react';
import { Plus, ChevronDown, ChevronUp, Users, FileText, Sparkles } from 'lucide-react';
import { Button } from '../components/Button';
import { InputField } from '../components/InputField';
import { TextArea } from '../components/TextArea';
import { Card } from '../components/Card';
import { useProfiles } from '../hooks/useProfiles';
import { useToastContext } from '../contexts/ToastContext';

export function Profiles() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [newProfileSamples, setNewProfileSamples] = useState('');
  const [creating, setCreating] = useState(false);
  const [expandedProfile, setExpandedProfile] = useState<string | null>(null);
  const [appendSamples, setAppendSamples] = useState<Record<string, string>>({});
  const [appending, setAppending] = useState<string | null>(null);

  const { profiles, loading, createProfile, appendSamples: appendProfileSamples } = useProfiles();
  const { pushToast } = useToastContext();

  const handleCreateProfile = async () => {
    if (!newProfileName.trim() || !newProfileSamples.trim()) return;

    try {
      setCreating(true);
      await createProfile({
        name: newProfileName.trim(),
        samples: newProfileSamples.trim(),
      });
      setNewProfileName('');
      setNewProfileSamples('');
      setShowCreateForm(false);
      pushToast({ type: 'success', message: 'Profile created successfully!' });
    } catch (error) {
      pushToast({ 
        type: 'error', 
        message: error instanceof Error ? error.message : 'Failed to create profile' 
      });
    } finally {
      setCreating(false);
    }
  };

  const handleAppendSamples = async (profileName: string) => {
    const samples = appendSamples[profileName]?.trim();
    if (!samples) return;

    try {
      setAppending(profileName);
      await appendProfileSamples(profileName, { samples });
      setAppendSamples(prev => ({ ...prev, [profileName]: '' }));
      pushToast({ type: 'success', message: 'Samples added successfully!' });
    } catch (error) {
      pushToast({ 
        type: 'error', 
        message: error instanceof Error ? error.message : 'Failed to add samples' 
      });
    } finally {
      setAppending(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-orange-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-12">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-blue-100 rounded-2xl p-3">
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <h1 className="text-4xl md:text-5xl font-black text-gray-900 mb-4 tracking-tight">
          Voice Profiles
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed mb-8">
          Manage your writing samples to train AI on your unique voice and style.
        </p>
        <Button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-orange-500 hover:bg-orange-600 text-white inline-flex items-center space-x-2"
          size="lg"
        >
          <Plus className="h-5 w-5" />
          <span>New Profile</span>
        </Button>
      </div>

      {showCreateForm && (
        <Card>
          <div className="space-y-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="bg-green-100 rounded-xl p-2">
                <Sparkles className="h-5 w-5 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Create New Profile</h3>
            </div>
            <InputField
              label="Profile Name"
              placeholder="e.g., Professional, Thought Leader, Technical..."
              value={newProfileName}
              onChange={(e) => setNewProfileName(e.target.value)}
            />
            <TextArea
              label="Writing Samples"
              placeholder="Paste your writing samples here. Include multiple examples of your writing style..."
              value={newProfileSamples}
              onChange={(e) => setNewProfileSamples(e.target.value)}
              minRows={8}
            />
            <div className="flex space-x-4">
              <Button
                onClick={handleCreateProfile}
                disabled={!newProfileName.trim() || !newProfileSamples.trim()}
                loading={creating}
                className="bg-orange-500 hover:bg-orange-600 text-white"
              >
                Create Profile
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowCreateForm(false);
                  setNewProfileName('');
                  setNewProfileSamples('');
                }}
              >
                Cancel
              </Button>
            </div>
          </div>
        </Card>
      )}

      <div className="space-y-6">
        {profiles.length === 0 ? (
          <Card>
            <div className="text-center py-16">
              <div className="bg-gray-100 rounded-2xl p-4 w-16 h-16 mx-auto mb-6 flex items-center justify-center">
                <Users className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">No profiles yet</h3>
              <p className="text-gray-600 mb-8 max-w-md mx-auto leading-relaxed">
                Create your first voice profile to get started with AI post generation.
              </p>
              <Button 
                onClick={() => setShowCreateForm(true)}
                className="bg-orange-500 hover:bg-orange-600 text-white"
                size="lg"
              >
                Create Your First Profile
              </Button>
            </div>
          </Card>
        ) : (
          profiles.map((profile) => (
            <Card key={profile.name}>
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="bg-blue-100 rounded-xl p-3">
                      <FileText className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{profile.name}</h3>
                      <p className="text-gray-600 font-medium">{profile.sampleCount} samples</p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setExpandedProfile(
                      expandedProfile === profile.name ? null : profile.name
                    )}
                    className="flex items-center space-x-2"
                  >
                    <span>Append Samples</span>
                    {expandedProfile === profile.name ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                {expandedProfile === profile.name && (
                  <div className="pt-6 border-t border-gray-200 space-y-6">
                    <TextArea
                      label="Additional Samples"
                      placeholder="Add more writing samples to improve this profile..."
                      value={appendSamples[profile.name] || ''}
                      onChange={(e) => setAppendSamples(prev => ({
                        ...prev,
                        [profile.name]: e.target.value
                      }))}
                      minRows={6}
                    />
                    <Button
                      onClick={() => handleAppendSamples(profile.name)}
                      disabled={!appendSamples[profile.name]?.trim()}
                      loading={appending === profile.name}
                      className="bg-orange-500 hover:bg-orange-600 text-white"
                    >
                      Append Samples
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}