import { Song } from '@/types/music';

// Mock song data with real song information
export const mockSongs: Song[] = [
    {
        id: '1',
        title: 'Ullu Ka Pattha',
        artist: 'Pritam, Arijit Singh, Nikhita Gandhi',
        album: 'Jagga Jasoos',
        duration: 264,
        thumbnail: 'https://c.saavncdn.com/191/Jagga-Jasoos-Hindi-2017-20230623121016-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
        genre: 'Bollywood',
        releaseYear: 2017
    },
    {
        id: '2',
        title: 'Galti Se Mistake',
        artist: 'Arijit Singh, Amit Mishra',
        album: 'Jagga Jasoos',
        duration: 227,
        thumbnail: 'https://c.saavncdn.com/191/Jagga-Jasoos-Hindi-2017-20230623121016-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3',
        genre: 'Bollywood',
        releaseYear: 2017
    },
    {
        id: '3',
        title: 'Tum Hi Ho',
        artist: 'Arijit Singh',
        album: 'Aashiqui 2',
        duration: 262,
        thumbnail: 'https://c.saavncdn.com/088/Aashiqui-2-Hindi-2013-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3',
        genre: 'Bollywood',
        releaseYear: 2013
    },
    {
        id: '4',
        title: 'Channa Mereya',
        artist: 'Arijit Singh',
        album: 'Ae Dil Hai Mushkil',
        duration: 298,
        thumbnail: 'https://c.saavncdn.com/742/Ae-Dil-Hai-Mushkil-Hindi-2016-20221216102447-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3',
        genre: 'Bollywood',
        releaseYear: 2016
    },
    {
        id: '5',
        title: 'Tera Ban Jaunga',
        artist: 'Akhil Sachdeva, Tulsi Kumar',
        album: 'Kabir Singh',
        duration: 232,
        thumbnail: 'https://c.saavncdn.com/100/Kabir-Singh-Hindi-2019-20190621151221-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3',
        genre: 'Bollywood',
        releaseYear: 2019
    },
    {
        id: '6',
        title: 'Kesariya',
        artist: 'Arijit Singh',
        album: 'Brahmastra',
        duration: 268,
        thumbnail: 'https://c.saavncdn.com/250/Brahmastra-Hindi-2022-20220808141409-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3',
        genre: 'Bollywood',
        releaseYear: 2022
    },
    {
        id: '7',
        title: 'Tujhe Kitna Chahne Lage',
        artist: 'Arijit Singh',
        album: 'Kabir Singh',
        duration: 284,
        thumbnail: 'https://c.saavncdn.com/100/Kabir-Singh-Hindi-2019-20190621151221-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3',
        genre: 'Bollywood',
        releaseYear: 2019
    },
    {
        id: '8',
        title: 'Shayad',
        artist: 'Arijit Singh',
        album: 'Love Aaj Kal',
        duration: 240,
        thumbnail: 'https://c.saavncdn.com/905/Love-Aaj-Kal-Hindi-2020-20200213151106-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3',
        genre: 'Bollywood',
        releaseYear: 2020
    },
    {
        id: '9',
        title: 'Raabta',
        artist: 'Arijit Singh',
        album: 'Agent Vinod',
        duration: 240,
        thumbnail: 'https://c.saavncdn.com/734/Agent-Vinod-Hindi-2012-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3',
        genre: 'Bollywood',
        releaseYear: 2012
    },
    {
        id: '10',
        title: 'Pal',
        artist: 'Arijit Singh, Shreya Ghoshal',
        album: 'Jalebi',
        duration: 261,
        thumbnail: 'https://c.saavncdn.com/405/Jalebi-Hindi-2018-20181005-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3',
        genre: 'Bollywood',
        releaseYear: 2018
    },
    {
        id: '11',
        title: 'Apna Bana Le',
        artist: 'Arijit Singh, Sachin-Jigar',
        album: 'Bhediya',
        duration: 252,
        thumbnail: 'https://c.saavncdn.com/191/Bhediya-Hindi-2022-20221123121501-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3',
        genre: 'Bollywood',
        releaseYear: 2022
    },
    {
        id: '12',
        title: 'Deva Deva',
        artist: 'Arijit Singh, Jonita Gandhi',
        album: 'Brahmastra',
        duration: 245,
        thumbnail: 'https://c.saavncdn.com/250/Brahmastra-Hindi-2022-20220808141409-500x500.jpg',
        audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3',
        genre: 'Bollywood',
        releaseYear: 2022
    }
];

export const getRandomSongs = (count: number): Song[] => {
    const shuffled = [...mockSongs].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
};

export const getSongById = (id: string): Song | undefined => {
    return mockSongs.find(song => song.id === id);
};
