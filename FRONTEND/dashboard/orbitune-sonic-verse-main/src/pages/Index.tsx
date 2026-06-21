import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from '@/components/Header';
import OrbitBackground from '@/components/OrbitBackground';
import ConversationalInput from '@/components/ConversationalInput';
import ChatMessage from '@/components/ChatMessage';
import MusicPlayer from '@/components/MusicPlayer';
import HeroSection from '@/components/HeroSection';
import Sidebar from '@/components/Sidebar';
import ProcessingModal from '@/components/ProcessingModal';
import { ScrollArea } from '@/components/ui/scroll-area';
import { createSongFromYoutube, type YoutubeSuggestion } from '@/lib/api';
import { useMusic } from '@/contexts/MusicContext';

interface Message {
  id: string;
  type: 'user' | 'ai' | 'song' | 'mood';
  content: string;
  timestamp: Date;
  songs?: Array<{
    title: string;
    artist: string;
    album: string;
    duration: number;
  }>;
}

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content:
        'Welcome to ORBITUNE! I am your AI music companion. Tell me how you are feeling or search for any song.',
      timestamp: new Date(),
    },
  ]);

  const { state: musicState, dispatch } = useMusic();
  const [showChat, setShowChat] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingInfo, setProcessingInfo] = useState({
    songTitle: '',
    currentStep: 0,
    totalSteps: 3,
    stepDescription: ''
  });

  const handleSend = async (content: string, type: 'song' | 'mood') => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    if (type === 'song') {
      // For song queries, suggestions will appear while typing;
      // here we simply acknowledge the message.
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content:
          'Great choice! Select a song from the suggestions above to generate 3D audio.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
    } else {
      // Mood-based: open chat window with animations
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content:
          'I heard your story. Let me curate the perfect 3D experience based on your mood.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
      setShowChat(true);
    }
  };

  const handleChatResponse = (userMessage: string, response: string, intent: string, songs?: any[]) => {
    // Add user's message
    const userMsg: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    
    // Add AI response
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'ai',
      content: response,
      timestamp: new Date(),
      songs: songs || []
    };
    
    setMessages(prev => [...prev, userMsg, aiMessage]);
    setShowChat(true); // Open chat window to show response
  };

  const handleSongSelected = async (suggestion: YoutubeSuggestion) => {
    const baseId = Date.now().toString();

    const userMessage: Message = {
      id: baseId,
      type: 'user',
      content: `Generate 3D audio for: ${suggestion.title} – ${suggestion.artist}`,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    // Show processing modal
    const steps = [
      `Downloading highest-quality audio...`,
      'Separating into stems (vocals, drums, bass, other)...',
      'Creating 3D spatial positioning...'
    ];

    setIsProcessing(true);
    setProcessingInfo({
      songTitle: `${suggestion.title} – ${suggestion.artist}`,
      currentStep: 1,
      totalSteps: 3,
      stepDescription: steps[0]
    });

    let cancelled = false;

    // Schedule smooth step transitions while backend works
    steps.slice(1).forEach((text, index) => {
      const delay = (index + 1) * 1600; // 1.6s between steps
      window.setTimeout(() => {
        if (cancelled) return;
        setProcessingInfo(prev => ({
          ...prev,
          currentStep: index + 2,
          stepDescription: text
        }));
      }, delay);
    });

    try {
      const youtubeUrl = `https://www.youtube.com/watch?v=${suggestion.videoId}`;
      const newSong = await createSongFromYoutube(youtubeUrl);

      const mergedSongs = [
        ...musicState.allSongs.filter((s) => s.id !== newSong.id),
        newSong,
      ];
      dispatch({ type: 'SET_ALL_SONGS', payload: mergedSongs });
      // Immediately play the newly created 3D song
      dispatch({ type: 'SET_QUEUE', payload: [newSong] });
      dispatch({ type: 'PLAY_SONG', payload: newSong });

      cancelled = true; // stop further status updates
      setIsProcessing(false);

      // Add success message
      const finalMessage: Message = {
        id: `${baseId}-done`,
        type: 'ai',
        content:
          '✅ Your 3D song is ready! Playing now in full spatial audio.',
        timestamp: new Date(),
        songs: [
          {
            title: newSong.title,
            artist: newSong.artist,
            album: newSong.album,
            duration: newSong.duration,
          },
        ],
      };

      setMessages(prev => [...prev, finalMessage]);
    } catch (error) {
      console.error('createSongFromYoutube error', error);
      cancelled = true;
      setIsProcessing(false);

      const errorMessage: Message = {
        id: `${baseId}-error`,
        type: 'ai',
        content:
          '❌ Something went wrong while creating 3D audio. Please check the YouTube link or try a different song.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleCancelProcessing = () => {
    setIsProcessing(false);
    const cancelMessage: Message = {
      id: Date.now().toString(),
      type: 'ai',
      content: '⚠️ Processing cancelled. Feel free to try another song!',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, cancelMessage]);
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      <OrbitBackground />
      <Header />

      {/* Main Content Area */}
      <div className="flex-1 flex relative z-10 overflow-hidden pt-12 sm:pt-14 md:pt-16">
        {/* Sidebar - Hidden on mobile, visible on large tablets and desktop */}
        <aside className="hidden lg:flex w-80 xl:w-96 2xl:w-[440px] flex-shrink-0">
          <div className="w-full h-full p-3 lg:p-4 2xl:p-6">
            <Sidebar />
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden w-full">
          <div className="flex-1 overflow-y-auto">
            <div className="container mx-auto px-2 xs:px-3 sm:px-4 md:px-6 lg:px-8 py-3 xs:py-4 sm:py-6 lg:py-8 max-w-[1600px]">
              {/* Hero Section */}
              <section className="mb-4 xs:mb-6 sm:mb-8 lg:mb-14">
                <HeroSection />
              </section>

              {/* AI Chatbot Section */}
              <section className="mb-16 xs:mb-20 sm:mb-24 lg:mb-32">
                <div className="max-w-5xl mx-auto">
                  {/* Section Header */}
                  <div className="mb-3 xs:mb-4 sm:mb-5 lg:mb-6">
                    <h2 className="text-base xs:text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-gradient font-orbitron mb-1 xs:mb-1.5 sm:mb-2">
                      AI Music Companion
                    </h2>
                    <p className="text-[10px] xs:text-xs sm:text-sm lg:text-base text-muted-foreground font-electrolize">
                      Tell me your mood or search for songs — I'll curate the perfect 3D audio experience
                    </p>
                  </div>

                  {/* Chat Container */}
                  <div className="glass-strong rounded-lg xs:rounded-xl sm:rounded-2xl lg:rounded-3xl overflow-hidden shadow-2xl border border-white/10">
                    <AnimatePresence>
                      {showChat && (
                        <motion.div
                          key="chat-window"
                          initial={{ opacity: 0, y: 24, scale: 0.96 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          exit={{ opacity: 0, y: 24, scale: 0.96 }}
                          transition={{ duration: 0.35, ease: 'easeOut' }}
                        >
                          {/* Chat Header */}
                          <div className="px-2 xs:px-3 sm:px-4 md:px-6 py-2 xs:py-3 sm:py-4 border-b border-white/10 bg-gradient-to-r from-primary/5 via-secondary/5 to-accent/5">
                            <div className="flex items-center gap-1.5 xs:gap-2 sm:gap-3">
                              <div className="w-1 h-1 xs:w-1.5 xs:h-1.5 sm:w-2 sm:h-2 rounded-full bg-accent animate-pulse" />
                              <span className="text-[9px] xs:text-[10px] sm:text-xs lg:text-sm font-medium text-foreground/80 font-electrolize uppercase tracking-wider">
                                Active Session
                              </span>
                            </div>
                          </div>

                          {/* Messages Area */}
                          <ScrollArea className="h-[280px] xs:h-[320px] sm:h-[350px] md:h-[400px] lg:h-[500px] px-2 xs:px-3 sm:px-4 md:px-6 py-3 xs:py-4 sm:py-5 lg:py-6">
                            <div className="space-y-3 xs:space-y-4 sm:space-y-5 lg:space-y-7">
                              {messages.map((msg) => (
                                <ChatMessage key={msg.id} message={msg} />
                              ))}
                            </div>
                          </ScrollArea>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Input Area (always visible) */}
                    <div className="px-2 xs:px-3 sm:px-4 md:px-6 py-2 xs:py-3 sm:py-4 lg:py-5 border-t border-white/10 bg-background/40">
                      <ConversationalInput 
                        onSend={handleSend} 
                        onSongSelected={handleSongSelected}
                        onChatResponse={handleChatResponse}
                      />
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </main>
      </div>

      {/* Music Player - Fixed at bottom */}
      <MusicPlayer />

      {/* Processing Modal */}
      <ProcessingModal
        isOpen={isProcessing}
        songTitle={processingInfo.songTitle}
        currentStep={processingInfo.currentStep}
        totalSteps={processingInfo.totalSteps}
        stepDescription={processingInfo.stepDescription}
        onCancel={handleCancelProcessing}
      />
    </div>
  );
};

export default Index;
