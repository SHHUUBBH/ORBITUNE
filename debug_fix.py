with open(r'AI-ML/audio_processor/youtube_downloader.py', 'rb') as f:
    content = f.read()

old = b"if 'SSL' in error_msg or 'EOF' in error_msg or 'SSL in error_msg:"
print('Old:', repr(old))
idx = content.find(old)
print('Found exact:', idx >= 0)

idx2 = content.find(b"'SSL in error_msg:")
print('Found partial:', idx2 >= 0)
if idx2 >= 0:
    print('Around:', repr(content[idx2-40:idx2+40]))