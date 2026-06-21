import { useState, useRef } from 'react';
import { Send, Sparkles, Music, MessageCircle, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { searchYoutubeSongs, sendChatMessage, type YoutubeSuggestion } from '@/lib/api';

interface ConversationalInputProps {
  onSend: (message: string, type: 'song' | 'mood') => void;
  onSongSelected: (suggestion: YoutubeSuggestion) => void;
  onChatResponse?: (userMessage: string, response: string, intent: string, songs?: any[]) => void;
}

const ConversationalInput = ({ onSend, onSongSelected, onChatResponse }: ConversationalInputProps) => {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [inputMode, setInputMode] = useState<'search' | 'chat'>('search'); // Tab-switchable mode
  const [suggestions, setSuggestions] = useState<YoutubeSuggestion[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const searchTimeoutRef = useRef<number | null>(null);


  const triggerSearch = (value: string) => {
    // Only trigger search if in SEARCH mode
    if (inputMode !== 'search') {
      setSuggestions([]);
      setIsSearching(false);
      return;
    }

    const trimmed = value.trim();
    if (!trimmed || trimmed.length < 3) {
      setSuggestions([]);
      setIsSearching(false);
      return;
    }

    if (searchTimeoutRef.current !== null) {
      window.clearTimeout(searchTimeoutRef.current);
    }

    setIsSearching(true);
    searchTimeoutRef.current = window.setTimeout(async () => {
      const results = await searchYoutubeSongs(trimmed);
      setSuggestions(results);
      setIsSearching(false);
    }, 350);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;

    if (inputMode === 'chat') {
      // CHAT MODE: Send to chatbot API only
      setIsChatting(true);
      try {
        const userId = localStorage.getItem('orbitune-user-id') || 'default-user';
        const response = await sendChatMessage(userId, input);
        
        // Call callback with chatbot response
        if (onChatResponse) {
          const songs = response.songResults?.map(s => ({
            title: s.title,
            artist: s.artist,
            album: s.album,
            duration: s.duration
          }));
          onChatResponse(userMessage, response.response, response.intent, songs);
        }
        
        setInput('');
        setIsTyping(false);
      } catch (error) {
        console.error('Chat error:', error);
        if (onChatResponse) {
          onChatResponse(
            userMessage,
            'Sorry, I\'m having trouble connecting. Please make sure the backend server is running! 😅',
            'error'
          );
        }
      } finally {
        setIsChatting(false);
      }
    } else {
      // SEARCH MODE: YouTube search only
      // If user presses enter with no suggestions, show message
      if (suggestions.length === 0) {
        onSend(input, 'song');
      }
      setInput('');
      setIsTyping(false);
      setSuggestions([]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Tab key to switch modes
    if (e.key === 'Tab') {
      e.preventDefault();
      setInputMode(prev => prev === 'search' ? 'chat' : 'search');
      setSuggestions([]); // Clear suggestions when switching
    }
  };

  return (
    <div className="relative">
      {/* Mode Indicator Badge */}
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
            inputMode === 'search'
              ? 'bg-primary/20 text-primary border border-primary/30'
              : 'bg-accent/20 text-accent border border-accent/30'
          }`}>
            {inputMode === 'search' ? (
              <>
                <Search className="w-3 h-3" />
                <span>Search Mode</span>
              </>
            ) : (
              <>
                <MessageCircle className="w-3 h-3" />
                <span>Chat Mode</span>
              </>
            )}
          </div>
          <span className="text-xs text-muted-foreground font-electrolize">
            Press <kbd className="px-1.5 py-0.5 bg-background/50 border border-white/20 rounded text-[10px] font-mono">Tab</kbd> to switch
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="relative">
        <div className={`glass-strong rounded-3xl p-2 transition-all ${
          inputMode === 'search' ? 'glow-primary' : 'glow-accent'
        }`}>
          <div className="flex items-center gap-3 px-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => {
                  const value = e.target.value;
                  setInput(value);
                  setIsTyping(value.length > 0);
                  // Trigger search based on mode
                  triggerSearch(value);
                }}
                onKeyDown={handleKeyDown}
                placeholder={
                  inputMode === 'search'
                    ? "🔍 Search for a song or artist..."
                    : "💬 Tell me what you're feeling or ask anything..."
                }
                className="w-full bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground py-4 text-lg"
              />
              
              {/* Type indicator */}
              {(isTyping || isChatting) && (
                <div className="absolute -top-8 left-0 flex items-center gap-2 text-xs text-muted-foreground animate-fade-in">
                  {isChatting ? (
                    <>
                      <Sparkles className="w-3 h-3 text-accent animate-pulse" />
                      <span>AI is thinking...</span>
                    </>
                  ) : inputMode === 'chat' ? (
                    <>
                      <MessageCircle className="w-3 h-3 text-accent" />
                      <span>Ready to chat</span>
                    </>
                  ) : isSearching ? (
                    <>
                      <Music className="w-3 h-3 text-primary animate-pulse" />
                      <span>Searching YouTube...</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-3 h-3 text-primary" />
                      <span>Type to search songs</span>
                    </>
                  )}
                </div>
              )}
            </div>

            <Button
              type="submit"
              size="icon"
              className="rounded-full h-12 w-12 bg-gradient-to-r from-primary via-secondary to-accent hover:scale-110 transition-transform duration-300 glow-primary"
              disabled={!input.trim() || isChatting}
            >
              {isChatting ? (
                <Sparkles className="w-5 h-5 animate-pulse" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </div>
        </div>
      </form>

      {/* Song suggestions when typing in SEARCH mode */}
      {inputMode === 'search' && (isSearching || suggestions.length > 0) && (
        <div className="mt-3 glass-strong rounded-2xl border border-white/10 p-3 sm:p-4 shadow-lg space-y-2">
          <div className="flex items-center justify-between text-xs sm:text-sm text-muted-foreground font-electrolize">
            <span>
              {isSearching
                ? 'Searching YouTube for the best matches...'
                : 'Select a song to generate ultra‑realistic 3D audio'}
            </span>
          </div>

          <div className="max-h-64 overflow-y-auto space-y-2">
            {suggestions.map((sugg) => (
              <button
                key={sugg.videoId}
                onClick={() => {
                  onSongSelected(sugg);
                  setSuggestions([]);
                  setInput('');
                  setIsTyping(false);
                }}
                className="w-full flex items-center gap-3 glass hover:glass-strong rounded-xl px-2.5 py-2.5 sm:px-3 sm:py-3 transition-all duration-200 hover:scale-[1.01] text-left"
              >
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg overflow-hidden flex-shrink-0 bg-gradient-to-br from-primary via-secondary to-accent">
                  {sugg.thumbnail && (
                    <img
                      src={sugg.thumbnail}
                      alt={sugg.title}
                      className="w-full h-full object-cover"
                    />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-xs sm:text-sm font-semibold text-foreground truncate">
                      {sugg.title}
                    </p>
                    <span className="text-[10px] sm:text-xs text-muted-foreground font-mono">
                      {sugg.durationString}
                    </span>
                  </div>
                  <p className="text-[10px] sm:text-xs text-muted-foreground truncate">
                    {sugg.artist}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Floating hints - mode-specific */}
      <div className="mt-4 flex gap-2 flex-wrap">
        {inputMode === 'search' ? (
          // Search mode hints
          ['Bohemian Rhapsody', 'Imagine Dragons', 'Arijit Singh', 'Beatles'].map((hint, i) => (
            <button
              key={i}
              onClick={() => {
                setInput(hint);
                setIsTyping(true);
                triggerSearch(hint);
              }}
              className="px-4 py-2 rounded-full glass text-sm hover:glass-strong transition-all duration-300 hover:scale-105"
            >
              🔍 {hint}
            </button>
          ))
        ) : (
          // Chat mode hints
          ['I feel energetic', 'Chill vibes', 'Something romantic', 'Recommend music'].map((hint, i) => (
            <button
              key={i}
              onClick={async () => {
                setInput(hint);
                setIsTyping(true);
                setIsChatting(true);
                try {
                  const userId = localStorage.getItem('orbitune-user-id') || 'default-user';
                  const response = await sendChatMessage(userId, hint);
                  if (onChatResponse) {
                    const songs = response.songResults?.map(s => ({
                      title: s.title,
                      artist: s.artist,
                      album: s.album,
                      duration: s.duration
                    }));
                    onChatResponse(hint, response.response, response.intent, songs);
                  }
                  setInput('');
                  setIsTyping(false);
                } catch (error) {
                  console.error('Chat error:', error);
                  if (onChatResponse) {
                    onChatResponse(hint, 'Sorry, backend server is not responding!', 'error');
                  }
                } finally {
                  setIsChatting(false);
                }
              }}
              className="px-4 py-2 rounded-full glass text-sm hover:glass-strong transition-all duration-300 hover:scale-105"
            >
              💬 {hint}
            </button>
          ))
        )}
      </div>
    </div>
  );
};

export default ConversationalInput;
