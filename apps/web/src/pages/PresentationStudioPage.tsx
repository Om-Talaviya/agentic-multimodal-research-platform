import React, { useState, useEffect } from 'react';
import {
  Presentation,
  Mic,
  Play,
  Pause,
  ChevronLeft,
  ChevronRight,
  Plus,
  Layers,
  Volume2,
  Clock,
  Radio,
  FileText,
  Quote,
  MessageSquare,
} from 'lucide-react';
import {
  SynthesisPresentation,
  PodcastBriefing,
  PresentationMetrics,
  GeneratePresentationPayload,
  GeneratePodcastPayload,
} from '../types/presentation';
import { useWorkspace } from '../context/WorkspaceContext';

export const PresentationStudioPage: React.FC = () => {
  const { currentWorkspace } = useWorkspace();
  const [activeTab, setActiveTab] = useState<'presentations' | 'podcasts'>('presentations');
  const [presentations, setPresentations] = useState<SynthesisPresentation[]>([]);
  const [selectedPresentation, setSelectedPresentation] = useState<SynthesisPresentation | null>(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState<number>(0);

  const [podcasts, setPodcasts] = useState<PodcastBriefing[]>([]);
  const [selectedPodcast, setSelectedPodcast] = useState<PodcastBriefing | null>(null);

  // Audio Playback simulation state
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);
  const [audioPlaybackSec, setAudioPlaybackSec] = useState<number>(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);

  const [metrics, setMetrics] = useState<PresentationMetrics>({
    total_presentations: 0,
    total_slides: 0,
    average_slides_per_deck: 0,
    total_podcasts: 0,
    total_audio_minutes: 0,
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [showDeckModal, setShowDeckModal] = useState<boolean>(false);
  const [showPodcastModal, setShowPodcastModal] = useState<boolean>(false);

  const [deckForm, setDeckForm] = useState<GeneratePresentationPayload>({
    title: '',
    subtitle: '',
    research_content: '',
    target_audience: 'executive',
    theme: 'midnight_slate',
  });

  const [podcastForm, setPodcastForm] = useState<GeneratePodcastPayload>({
    topic: '',
    key_findings: '',
    host_name: 'Dr. Elena Vance (Host)',
    expert_name: 'Prof. Marcus Sterling (Specialist)',
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const queryParams = currentWorkspace?.id ? `?workspace_id=${currentWorkspace.id}` : '';
      const [presRes, podRes, metRes] = await Promise.all([
        fetch(`/api/v1/presentations${queryParams}`),
        fetch(`/api/v1/presentations/podcasts${queryParams}`),
        fetch(`/api/v1/presentations/metrics`),
      ]);

      if (presRes.ok) {
        const presData = await presRes.json();
        setPresentations(presData);
        if (presData.length > 0 && !selectedPresentation) {
          fetchPresentationDetails(presData[0].id);
        }
      }
      if (podRes.ok) {
        const podData = await podRes.json();
        setPodcasts(podData);
        if (podData.length > 0 && !selectedPodcast) {
          fetchPodcastDetails(podData[0].id);
        }
      }
      if (metRes.ok) {
        const metData = await metRes.json();
        setMetrics(metData);
      }
    } catch (err) {
      console.error('Failed to load presentation studio data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPresentationDetails = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/presentations/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedPresentation(data);
        setCurrentSlideIndex(0);
      }
    } catch (err) {
      console.error('Failed to load presentation details:', err);
    }
  };

  const fetchPodcastDetails = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/presentations/podcasts/${id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedPodcast(data);
        setIsPlayingAudio(false);
        setAudioPlaybackSec(0);
      }
    } catch (err) {
      console.error('Failed to load podcast details:', err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentWorkspace]);

  // Audio timer ticker
  useEffect(() => {
    let interval: any;
    if (isPlayingAudio && selectedPodcast) {
      interval = setInterval(() => {
        setAudioPlaybackSec((prev) => {
          if (prev >= selectedPodcast.total_duration_sec) {
            setIsPlayingAudio(false);
            return 0;
          }
          return prev + 0.5 * playbackSpeed;
        });
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isPlayingAudio, selectedPodcast, playbackSpeed]);

  const handleGenerateDeck = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...deckForm,
        workspace_id: currentWorkspace?.id,
      };
      const res = await fetch('/api/v1/presentations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowDeckModal(false);
        setDeckForm({
          title: '',
          subtitle: '',
          research_content: '',
          target_audience: 'executive',
          theme: 'midnight_slate',
        });
        await fetchData();
      }
    } catch (err) {
      console.error('Failed to generate presentation deck:', err);
    }
  };

  const handleGeneratePodcast = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...podcastForm,
        workspace_id: currentWorkspace?.id,
      };
      const res = await fetch('/api/v1/presentations/podcasts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowPodcastModal(false);
        setPodcastForm({
          topic: '',
          key_findings: '',
          host_name: 'Dr. Elena Vance (Host)',
          expert_name: 'Prof. Marcus Sterling (Specialist)',
        });
        await fetchData();
        setActiveTab('podcasts');
      }
    } catch (err) {
      console.error('Failed to generate podcast briefing:', err);
    }
  };

  const currentSlide =
    selectedPresentation?.slides && selectedPresentation.slides.length > currentSlideIndex
      ? selectedPresentation.slides[currentSlideIndex]
      : null;

  return (
    <div className="space-y-6">
      {/* Top Banner & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Presentation className="w-8 h-8 text-primary" />
              Multimodal Scientific Presentation & Briefing Studio
            </h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20">
              Interactive Decks & Audio
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Automated slide deck synthesis with speaker notes and multi-speaker scientific audio podcast briefings.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowDeckModal(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition shadow-sm"
          >
            <Plus className="w-4 h-4" />
            New Slide Deck
          </button>
          <button
            onClick={() => setShowPodcastModal(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-card border border-border text-foreground text-xs font-medium hover:bg-muted transition shadow-sm"
          >
            <Mic className="w-4 h-4 text-purple-500" />
            New Audio Podcast
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Slide Decks</span>
            <Presentation className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_presentations}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Generated Slides</span>
            <Layers className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_slides}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Avg Deck Length</span>
            <FileText className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.average_slides_per_deck} slides</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Audio Podcasts</span>
            <Radio className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_podcasts}</div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between text-muted-foreground mb-1">
            <span className="text-xs font-medium uppercase tracking-wider">Total Audio</span>
            <Clock className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-foreground">{metrics.total_audio_minutes} min</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border flex items-center gap-6">
        <button
          onClick={() => setActiveTab('presentations')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'presentations'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Presentation className="w-4 h-4" />
          Interactive Slide Decks
        </button>

        <button
          onClick={() => setActiveTab('podcasts')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'podcasts'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Radio className="w-4 h-4" />
          Multi-Speaker Podcast Studio
        </button>
      </div>

      {/* Tab 1: Interactive Slide Decks */}
      {activeTab === 'presentations' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Deck Selector Sidebar */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
              Presentation Decks
            </h3>
            <div className="space-y-2">
              {presentations.map((p) => (
                <div
                  key={p.id}
                  onClick={() => fetchPresentationDetails(p.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition ${
                    selectedPresentation?.id === p.id
                      ? 'border-primary bg-primary/5 shadow-sm'
                      : 'border-border bg-card hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold uppercase text-primary">{p.target_audience}</span>
                    <span className="text-xs text-muted-foreground">{p.total_slides} slides</span>
                  </div>
                  <h4 className="font-medium text-foreground text-sm line-clamp-2">{p.title}</h4>
                  <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                    <Clock className="w-3.5 h-3.5" />
                    <span>~{p.estimated_duration_min} min read</span>
                  </div>
                </div>
              ))}
              {presentations.length === 0 && !loading && (
                <div className="text-center py-8 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                  No slide decks synthesized yet.
                </div>
              )}
            </div>
          </div>

          {/* Interactive Slide Viewer Canvas */}
          <div className="lg:col-span-2 space-y-4">
            {selectedPresentation && currentSlide ? (
              <div className="space-y-4">
                {/* Top Deck Info & Navigation */}
                <div className="flex items-center justify-between bg-card p-3 rounded-xl border border-border">
                  <div>
                    <h3 className="text-sm font-bold text-foreground line-clamp-1">{selectedPresentation.title}</h3>
                    <span className="text-xs text-muted-foreground">
                      Slide {currentSlideIndex + 1} of {selectedPresentation.slides?.length || 1} • {currentSlide.layout_type.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setCurrentSlideIndex((prev) => Math.max(0, prev - 1))}
                      disabled={currentSlideIndex === 0}
                      className="p-1.5 rounded-lg border border-border text-foreground hover:bg-muted disabled:opacity-30 transition"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() =>
                        setCurrentSlideIndex((prev) =>
                          Math.min((selectedPresentation.slides?.length || 1) - 1, prev + 1)
                        )
                      }
                      disabled={currentSlideIndex === (selectedPresentation.slides?.length || 1) - 1}
                      className="p-1.5 rounded-lg border border-border text-foreground hover:bg-muted disabled:opacity-30 transition"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* 16:9 Presentation Canvas */}
                <div className="relative aspect-[16/9] rounded-2xl border-2 border-border bg-gradient-to-br from-zinc-950 via-zinc-900 to-black text-white p-8 md:p-12 shadow-2xl flex flex-col justify-between overflow-hidden">
                  {/* Subtle Background Glow */}
                  <div className="absolute top-0 right-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none" />

                  {/* Slide Header */}
                  <div className="space-y-2 z-10">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-primary/20 text-primary border border-primary/30 uppercase tracking-wider">
                        Slide {currentSlide.slide_number}
                      </span>
                      {currentSlide.visual_metadata?.badge_text && (
                        <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-800 text-zinc-300">
                          {currentSlide.visual_metadata.badge_text}
                        </span>
                      )}
                    </div>
                    <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-zinc-100">
                      {currentSlide.headline}
                    </h2>
                  </div>

                  {/* Slide Body Content */}
                  <div className="my-auto py-4 z-10">
                    {currentSlide.layout_type === 'title' ? (
                      <div className="space-y-3">
                        {currentSlide.bullet_points?.map((bp, i) => (
                          <p key={i} className="text-lg text-zinc-300 font-light">
                            {bp}
                          </p>
                        ))}
                      </div>
                    ) : currentSlide.layout_type === 'two_column' ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {currentSlide.bullet_points?.map((bp, i) => (
                          <div key={i} className="p-4 rounded-xl bg-zinc-800/60 border border-zinc-700/60 text-sm leading-relaxed">
                            {bp}
                          </div>
                        ))}
                      </div>
                    ) : currentSlide.layout_type === 'callout_quote' ? (
                      <div className="p-6 rounded-2xl bg-primary/10 border border-primary/30 text-base leading-relaxed italic text-zinc-200">
                        <Quote className="w-6 h-6 text-primary mb-2 opacity-80" />
                        {currentSlide.bullet_points?.join(' ')}
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {currentSlide.bullet_points?.map((bp, i) => (
                          <div key={i} className="flex items-start gap-3">
                            <span className="w-2 h-2 rounded-full bg-primary mt-2 shrink-0 shadow-sm" />
                            <p className="text-sm md:text-base text-zinc-200 leading-relaxed">{bp}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Slide Footer */}
                  <div className="flex items-center justify-between text-xs text-zinc-500 border-t border-zinc-800/80 pt-3 z-10">
                    <span>Agentic Multimodal Research Platform</span>
                    <span>{selectedPresentation.title}</span>
                  </div>
                </div>

                {/* Speaker Notes Drawer */}
                {currentSlide.speaker_notes && (
                  <div className="p-4 rounded-xl border border-border bg-card shadow-sm space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      <MessageSquare className="w-3.5 h-3.5 text-primary" />
                      Presenter Speaker Notes
                    </div>
                    <p className="text-xs text-foreground leading-relaxed">{currentSlide.speaker_notes}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-20 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                Select a presentation deck from the left sidebar to start playback.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Multi-Speaker Podcast Studio */}
      {activeTab === 'podcasts' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Episode List */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
              Audio Podcast Briefings
            </h3>
            <div className="space-y-2">
              {podcasts.map((pod) => (
                <div
                  key={pod.id}
                  onClick={() => fetchPodcastDetails(pod.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition ${
                    selectedPodcast?.id === pod.id
                      ? 'border-purple-500 bg-purple-500/5 shadow-sm'
                      : 'border-border bg-card hover:border-purple-500/40'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-purple-500 flex items-center gap-1">
                      <Volume2 className="w-3.5 h-3.5" />
                      {pod.total_dialogue_turns} turns
                    </span>
                    <span className="text-xs text-muted-foreground">{Math.round(pod.total_duration_sec)}s</span>
                  </div>
                  <h4 className="font-medium text-foreground text-sm line-clamp-2">{pod.title}</h4>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{pod.episode_topic}</p>
                </div>
              ))}
              {podcasts.length === 0 && !loading && (
                <div className="text-center py-8 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                  No podcast audio briefings created yet.
                </div>
              )}
            </div>
          </div>

          {/* Interactive Player & Transcript */}
          <div className="lg:col-span-2 space-y-4">
            {selectedPodcast ? (
              <div className="space-y-4">
                {/* Audio Player Card */}
                <div className="p-5 rounded-2xl border border-border bg-card shadow-md space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-foreground">{selectedPodcast.title}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {selectedPodcast.host_name} & {selectedPodcast.expert_name}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setPlaybackSpeed((s) => (s === 1.0 ? 1.25 : s === 1.25 ? 1.5 : 1.0))}
                        className="px-2.5 py-1 rounded-lg border border-border text-xs font-mono font-medium hover:bg-muted transition"
                      >
                        {playbackSpeed}x
                      </button>
                      <button
                        onClick={() => setIsPlayingAudio(!isPlayingAudio)}
                        className="p-3 rounded-full bg-purple-600 hover:bg-purple-500 text-white shadow-lg transition"
                      >
                        {isPlayingAudio ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                      </button>
                    </div>
                  </div>

                  {/* Progress Bar & Waveform Simulation */}
                  <div className="space-y-1.5">
                    <div className="w-full bg-muted rounded-full h-2 overflow-hidden relative cursor-pointer">
                      <div
                        className="bg-purple-600 h-full transition-all"
                        style={{
                          width: `${Math.min(
                            100,
                            (audioPlaybackSec / Math.max(1, selectedPodcast.total_duration_sec)) * 100
                          )}%`,
                        }}
                      />
                    </div>
                    <div className="flex justify-between text-[11px] font-mono text-muted-foreground">
                      <span>{Math.floor(audioPlaybackSec)}s</span>
                      <span>{Math.round(selectedPodcast.total_duration_sec)}s</span>
                    </div>
                  </div>
                </div>

                {/* Synchronized Turn-by-Turn Dialogue Feed */}
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Dialogue Transcript & Turn Breakdown
                  </h4>

                  {selectedPodcast.dialogue_transcript_json?.map((turn, i) => {
                    const isCurrent =
                      audioPlaybackSec >= turn.timestamp_start_sec &&
                      audioPlaybackSec <= turn.timestamp_end_sec;
                    const isHost = turn.speaker.includes('Host');

                    return (
                      <div
                        key={i}
                        className={`p-4 rounded-xl border transition ${
                          isCurrent
                            ? 'border-purple-500 bg-purple-500/10 shadow-sm ring-1 ring-purple-500/30'
                            : 'border-border bg-card'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span
                            className={`text-xs font-bold px-2 py-0.5 rounded ${
                              isHost ? 'bg-blue-500/10 text-blue-500' : 'bg-purple-500/10 text-purple-500'
                            }`}
                          >
                            {turn.speaker}
                          </span>
                          <span className="text-[11px] font-mono text-muted-foreground">
                            [{turn.timestamp_start_sec}s - {turn.timestamp_end_sec}s]
                          </span>
                        </div>

                        {turn.audio_cue && (
                          <div className="text-[11px] italic text-muted-foreground mb-1">
                            Audio cue: {turn.audio_cue}
                          </div>
                        )}

                        <p className="text-xs text-foreground leading-relaxed">{turn.text}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="text-center py-20 border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                Select a podcast episode from the left sidebar to listen.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal: New Presentation Deck */}
      {showDeckModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-card border border-border rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Presentation className="w-5 h-5 text-primary" />
                Synthesize Presentation Deck
              </h3>
              <button
                onClick={() => setShowDeckModal(false)}
                className="text-muted-foreground hover:text-foreground text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleGenerateDeck} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Deck Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Next-Generation Multimodal Diagnostic Reasoning"
                  value={deckForm.title}
                  onChange={(e) => setDeckForm({ ...deckForm, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Target Audience</label>
                <select
                  value={deckForm.target_audience}
                  onChange={(e) =>
                    setDeckForm({
                      ...deckForm,
                      target_audience: e.target.value as 'executive' | 'scientific' | 'technical' | 'general',
                    })
                  }
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                >
                  <option value="executive">Executive & Leadership Briefing</option>
                  <option value="scientific">Scientific & Academic Peer Review</option>
                  <option value="technical">Engineering & Implementation Architecture</option>
                  <option value="general">General Stakeholder Summary</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">
                  Research Synthesis Content / Context
                </label>
                <textarea
                  required
                  rows={6}
                  placeholder="Paste research report findings or key conclusions here to generate slides..."
                  value={deckForm.research_content}
                  onChange={(e) => setDeckForm({ ...deckForm, research_content: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowDeckModal(false)}
                  className="px-4 py-2 rounded-lg border border-border text-xs font-medium text-muted-foreground hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition"
                >
                  Generate Slide Deck
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: New Podcast Briefing */}
      {showPodcastModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-card border border-border rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Mic className="w-5 h-5 text-purple-500" />
                Generate Audio Podcast Briefing
              </h3>
              <button
                onClick={() => setShowPodcastModal(false)}
                className="text-muted-foreground hover:text-foreground text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleGeneratePodcast} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Episode Topic</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Breakthroughs in Quantum Error Mitigation"
                  value={podcastForm.topic}
                  onChange={(e) => setPodcastForm({ ...podcastForm, topic: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Key Research Findings</label>
                <textarea
                  required
                  rows={5}
                  placeholder="Summary of empirical findings, debate conclusions, or SLR meta-analysis..."
                  value={podcastForm.key_findings}
                  onChange={(e) => setPodcastForm({ ...podcastForm, key_findings: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs text-foreground focus:outline-none focus:border-primary"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowPodcastModal(false)}
                  className="px-4 py-2 rounded-lg border border-border text-xs font-medium text-muted-foreground hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-purple-600 text-white text-xs font-medium hover:bg-purple-500 transition shadow-sm"
                >
                  Generate Dialogue Podcast
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
