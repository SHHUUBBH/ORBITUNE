import { Song } from '@/types/music';

export const demoTracks: Song[] = [
    {
        id: 'demo-tu',
        title: 'Tu',
        artist: 'Talwiinder, Sanjoy',
        album: 'Featured Demo',
        duration: 240,
        thumbnail: 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/0951e67dd6c8.jpg',
        audioUrl: 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/Tu.mp3',
        genre: 'Punjabi',
        releaseYear: 2024
    },
    {
        id: 'demo-voodoo',
        title: 'Voodoo',
        artist: 'Badshah, J Balvin, Tainy',
        album: 'Featured Demo',
        duration: 200,
        thumbnail: 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/2f4318853dfa.jpg',
        audioUrl: 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/voodoo.mp3',
        genre: 'Hip Hop',
        releaseYear: 2024
    },
    {
        id: 'demo-sunflower',
        title: 'Sunflower - Spider-Man: Into the Spider-Verse',
        artist: 'Post Malone, Swae Lee, Carter Lang',
        album: 'Featured Demo',
        duration: 158,
        thumbnail: 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/e6fe274df9d1.jpg',
        audioUrl: 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/sunflower.mp3',
        genre: 'Pop',
        releaseYear: 2018
    },
    {
        id: 'demo-blinding-lights',
        title: 'Blinding Lights',
        artist: 'The Weeknd',
        album: 'Featured Demo',
        duration: 200,
        thumbnail: 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/f1608ba400be.jpg',
        audioUrl: 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/blinding%20lights.mp3',
        genre: 'Synth-pop',
        releaseYear: 2019
    }
];

export const getDemoTracks = (): Song[] => demoTracks;