import { useState } from 'react';
import { Heart, Clock, Music, ListMusic, Plus, Search, Play } from 'lucide-react';
import { useMusic } from '@/contexts/MusicContext';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

type Tab = 'all' | 'recent' | 'favorites' | 'playlists';

const Sidebar = () => {
    const { state, dispatch } = useMusic();
    const [activeTab, setActiveTab] = useState<Tab>('all');
    const [searchQuery, setSearchQuery] = useState('');

    const filteredSongs = state.allSongs.filter(song =>
        song.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        song.artist.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handlePlaySong = (song: typeof state.allSongs[0]) => {
        dispatch({ type: 'PLAY_SONG', payload: song });
        dispatch({ type: 'SET_QUEUE', payload: filteredSongs });
    };

    const toggleFavorite = (song: typeof state.allSongs[0], e: React.MouseEvent) => {
        e.stopPropagation();
        const isFavorite = state.favoriteSongs.some(s => s.id === song.id);
        if (isFavorite) {
            dispatch({ type: 'REMOVE_FROM_FAVORITES', payload: song.id });
        } else {
            dispatch({ type: 'ADD_TO_FAVORITES', payload: song });
        }
    };

    const tabs = [
        { id: 'all' as Tab, label: 'All Songs', icon: Music },
        { id: 'recent' as Tab, label: 'Recent', icon: Clock },
        { id: 'favorites' as Tab, label: 'Favorites', icon: Heart },
        { id: 'playlists' as Tab, label: 'Playlists', icon: ListMusic },
    ];

    const getSongsForTab = () => {
        switch (activeTab) {
            case 'recent':
                return state.recentSongs;
            case 'favorites':
                return state.favoriteSongs;
            case 'playlists':
                return [];
            default:
                return filteredSongs;
        }
    };

    const songsToDisplay = getSongsForTab();

    return (
        <div className="glass-strong rounded-xl lg:rounded-2xl xl:rounded-3xl p-3 sm:p-4 lg:p-5 xl:p-6 max-h-[600px] flex flex-col border border-white/10 shadow-2xl">
            {/* Header */}
            <div className="mb-4 lg:mb-5 flex-shrink-0">
                {/* Title with stats */}
                <div className="flex items-center justify-between mb-3 lg:mb-4">
                    <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-gradient font-orbitron">Library</h2>
                    <div className="glass px-2.5 py-1 rounded-lg border border-white/10">
                        <span className="text-xs font-medium text-muted-foreground font-electrolize">
                            {state.allSongs.length} songs
                        </span>
                    </div>
                </div>

                {/* Search - Enhanced */}
                <div className="relative mb-3 lg:mb-4 group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    <Input
                        placeholder="Search your library..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 pr-4 glass bg-background/30 border-white/10 focus:border-primary/50 text-sm lg:text-base h-10 transition-all"
                    />
                </div>

                {/* Tabs - Grid layout for better mobile */}
                <div className="grid grid-cols-2 sm:flex sm:flex-wrap gap-3 lg:gap-4">
                    {tabs.map(tab => {
                        const Icon = tab.icon;
                        const isActive = activeTab === tab.id;
                        return (
                            <Button
                                key={tab.id}
                                variant={isActive ? "default" : "ghost"}
                                size="sm"
                                onClick={() => setActiveTab(tab.id)}
                                className={cn(
                                    "flex items-center justify-center sm:justify-start gap-1.5 lg:gap-2 whitespace-nowrap font-electrolize text-[10px] sm:text-xs lg:text-sm flex-shrink-0 h-9 lg:h-10 transition-all",
                                    isActive && "bg-gradient-to-r from-primary via-secondary to-accent shadow-lg ring-2 ring-primary/20"
                                )}
                            >
                                <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                                <span className="hidden xs:inline sm:inline">{tab.label}</span>
                            </Button>
                        );
                    })}
                </div>
            </div>

            {/* Content */}
            <ScrollArea className="flex-1 -mr-2 lg:-mr-4 pr-2 lg:pr-4 max-h-[calc(100vh-320px)] overflow-y-auto">
                {activeTab === 'playlists' ? (
                    <div className="space-y-3 lg:space-y-4">
                        <Button
                            variant="outline"
                            className="w-full justify-start gap-2 glass hover:glass-strong text-sm"
                            onClick={() => {
                                const name = prompt('Enter playlist name:');
                                if (name) {
                                    dispatch({ type: 'CREATE_PLAYLIST', payload: { name } });
                                }
                            }}
                        >
                            <Plus className="w-4 h-4" />
                            Create Playlist
                        </Button>

                        {state.playlists.map(playlist => (
                            <div
                                key={playlist.id}
                                className="glass hover:glass-strong p-3 lg:p-4 rounded-lg lg:rounded-xl cursor-pointer transition-all"
                            >
                                <div className="flex items-center gap-2 lg:gap-3">
                                    <div className="w-10 h-10 lg:w-12 lg:h-12 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center flex-shrink-0">
                                        <ListMusic className="w-5 h-5 lg:w-6 lg:h-6 text-primary" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-semibold truncate font-orbitron text-sm lg:text-base">{playlist.name}</h3>
                                        <p className="text-xs lg:text-sm text-muted-foreground font-electrolize">
                                            {playlist.songs.length} songs
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="space-y-3 lg:space-y-4">
                        {songsToDisplay.length === 0 ? (
                            <div className="text-center py-8 lg:py-12 text-muted-foreground font-electrolize text-sm">
                                {activeTab === 'recent' && 'No recent songs'}
                                {activeTab === 'favorites' && 'No favorite songs yet'}
                                {activeTab === 'all' && 'No songs found'}
                            </div>
                        ) : (
                            songsToDisplay.map(song => {
                                const isFavorite = state.favoriteSongs.some(s => s.id === song.id);
                                const isPlaying = state.currentSong?.id === song.id && state.isPlaying;

                                return (
                                    <div
                                        key={song.id}
                                        onClick={() => handlePlaySong(song)}
                                        className={cn(
                                            "glass hover:glass-strong p-3 sm:p-3.5 lg:p-4 rounded-lg lg:rounded-xl cursor-pointer transition-all group border border-white/5 hover:border-white/20 hover:scale-[1.01]",
                                            isPlaying && "ring-2 ring-primary shadow-lg shadow-primary/20 bg-primary/5"
                                        )}
                                    >
                                        <div className="flex items-center gap-3 sm:gap-3.5 lg:gap-4">
                                            {/* Thumbnail */}
                                            <div className="relative w-11 h-11 sm:w-12 sm:h-12 lg:w-14 lg:h-14 flex-shrink-0">
                                                <img
                                                    src={song.thumbnail}
                                                    alt={song.title}
                                                    className="w-full h-full object-cover rounded-md lg:rounded-lg shadow-md"
                                                />
                                                {/* Play button overlay */}
                                                {!isPlaying && (
                                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-md lg:rounded-lg z-10">
                                                        <Play className="w-4 h-4 lg:w-5 lg:h-5 text-white drop-shadow-lg" fill="white" />
                                                    </div>
                                                )}
                                            </div>

                                            {/* Info */}
                                            <div className="flex-1 min-w-0">
                                                <h3 className={cn(
                                                    "font-semibold truncate font-orbitron text-xs sm:text-sm lg:text-base transition-colors",
                                                    isPlaying && "text-primary"
                                                )}>
                                                    {song.title}
                                                </h3>
                                                <p className="text-[10px] sm:text-xs text-muted-foreground truncate font-electrolize">
                                                    {song.artist}
                                                </p>
                                            </div>

                                            {/* Duration & Favorite */}
                                            <div className="flex items-center gap-1.5 sm:gap-2 lg:gap-3 flex-shrink-0">
                                                <span className="text-[10px] sm:text-xs text-muted-foreground font-electrolize hidden sm:inline">
                                                    {Math.floor(song.duration / 60)}:{(song.duration % 60).toString().padStart(2, '0')}
                                                </span>
                                                <button
                                                    onClick={(e) => toggleFavorite(song, e)}
                                                    className={cn(
                                                        "transition-all hover:scale-110",
                                                        isFavorite ? "opacity-100" : "opacity-0 group-hover:opacity-100"
                                                    )}
                                                    title={isFavorite ? "Remove from favorites" : "Add to favorites"}
                                                >
                                                    <Heart
                                                        className={cn(
                                                            "w-4 h-4 lg:w-4.5 lg:h-4.5 transition-all",
                                                            isFavorite ? "fill-red-500 text-red-500 drop-shadow-lg" : "text-muted-foreground hover:text-red-500"
                                                        )}
                                                    />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                )}
            </ScrollArea>
        </div>
    );
};

export default Sidebar;
