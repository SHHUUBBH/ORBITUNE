import Header from '@/components/Header';
import OrbitBackground from '@/components/OrbitBackground';
import MusicPlayer from '@/components/MusicPlayer';
import FeaturedTracks from '@/components/FeaturedTracks';
import HeroSection from '@/components/HeroSection';
import WelcomeNoticeModal from '@/components/WelcomeNoticeModal';

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      <OrbitBackground />
      <Header />
      <WelcomeNoticeModal />

      {/* Main Content Area - Full width focused on 3D Audio Experience */}
      <div className="flex-1 flex relative z-10 overflow-hidden pt-14 sm:pt-16 md:pt-18 pb-28">
        <main className="flex-1 flex flex-col overflow-hidden w-full">
          <div className="flex-1 overflow-y-auto">
            <div className="container mx-auto px-3 xs:px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 max-w-[1500px]">
              {/* Hero Section */}
              <section className="mb-6 sm:mb-8 lg:mb-12">
                <HeroSection />
              </section>

              {/* Instant 3D Audio Master Tracks Grid */}
              <FeaturedTracks />
            </div>
          </div>
        </main>
      </div>

      {/* Music Player - Fixed at bottom */}
      <MusicPlayer />
    </div>
  );
};

export default Index;
