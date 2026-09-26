import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Headphones, Sparkles, ExternalLink, Music2, ShieldAlert } from 'lucide-react';

interface WelcomeNoticeModalProps {
  githubUrl?: string;
}

export const WelcomeNoticeModal: React.FC<WelcomeNoticeModalProps> = ({
  githubUrl = 'https://github.com/SHHUUBBH/ORBITUNE',
}) => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    try {
      const hasSeenNotice = localStorage.getItem('orbitune_welcome_notice_seen');
      if (!hasSeenNotice) {
        // Small delay to ensure smooth initial page render before dialog pops up
        const timer = setTimeout(() => {
          setIsOpen(true);
        }, 600);
        return () => clearTimeout(timer);
      }
    } catch (e) {
      console.error('Error reading localStorage for welcome notice:', e);
    }
  }, []);

  const handleAcknowledge = () => {
    try {
      localStorage.setItem('orbitune_welcome_notice_seen', 'true');
    } catch (e) {
      console.error('Error setting localStorage for welcome notice:', e);
    }
    setIsOpen(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => {
      if (!open) {
        handleAcknowledge();
      } else {
        setIsOpen(true);
      }
    }}>
      <DialogContent className="sm:max-w-md border border-primary/30 bg-background/95 backdrop-blur-2xl p-6 sm:p-7 shadow-2xl rounded-2xl overflow-hidden">
        {/* Glow ambient background effect */}
        <div className="absolute -top-16 -right-16 w-36 h-36 bg-primary/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-16 -left-16 w-36 h-36 bg-secondary/20 rounded-full blur-3xl pointer-events-none" />

        <DialogHeader className="space-y-3 text-center sm:text-center">
          {/* Top Badge & Icon */}
          <div className="flex justify-center">
            <div className="relative">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary via-purple-500 to-accent flex items-center justify-center shadow-lg shadow-primary/25 animate-pulse">
                <Headphones className="w-7 h-7 text-white" />
              </div>
              <span className="absolute -bottom-1 -right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-accent"></span>
              </span>
            </div>
          </div>

          <DialogTitle className="text-xl sm:text-2xl font-bold font-orbitron text-gradient tracking-wide">
            Welcome to ORBITUNE
          </DialogTitle>

          <DialogDescription className="text-xs sm:text-sm font-electrolize text-muted-foreground tracking-wide leading-relaxed pt-1">
            Immersive 3D Spatial Audio Experience
          </DialogDescription>
        </DialogHeader>

        {/* Informative Note Box */}
        <div className="my-4 space-y-3.5">
          <div className="p-4 rounded-xl bg-primary/10 border border-primary/20 backdrop-blur-md">
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
              <div className="text-xs sm:text-sm text-foreground/90 font-electrolize leading-relaxed">
                <p className="font-semibold text-primary mb-1">Preview & Demo Notice</p>
                <p>
                  The personal library and live AI chatbot features are currently offline in this web preview.
                </p>
                <p className="mt-1.5 text-muted-foreground">
                  You can enjoy listening to all our curated <span className="text-primary font-semibold">3D Spatial demo tracks</span> right here in the dashboard!
                </p>
              </div>
            </div>
          </div>

          {/* GitHub Repository Reference Card */}
          <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 hover:border-primary/40 transition-colors flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-black/40 border border-white/10">
                <Music2 className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="text-xs font-semibold font-orbitron text-foreground">Full Architecture & Source</p>
                <p className="text-[11px] text-muted-foreground font-electrolize">Explore the project on our GitHub repository</p>
              </div>
            </div>
            <a
              href={githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-medium text-primary hover:text-primary/80 transition-colors px-2.5 py-1.5 rounded-lg hover:bg-primary/10"
            >
              GitHub <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-2 flex flex-col sm:flex-row gap-2.5 justify-end">
          <Button
            onClick={handleAcknowledge}
            className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-orbitron font-semibold tracking-wider text-xs sm:text-sm py-5 rounded-xl shadow-lg shadow-primary/20 transition-all hover:scale-[1.02]"
          >
            Start Listening Now
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default WelcomeNoticeModal;
