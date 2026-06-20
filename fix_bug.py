with open(r'AI-ML/audio_processor/youtube_downloader.py', 'rb') as f:
    content = f.read()

old = b"if 'SSL' in error_msg or 'EOF' in error_msg or 'SSL in error_msg:"
new = b"if 'SSL' in error_msg or 'EOF' in error_msg:"

print('Old:', repr(old))
print('New:', repr(new))

idx = content.find(old)
print('Found exact:', idx >= 0)

if idx >= 0:
    content = content.replace(old, new)
    with open(r'AI-ML/audio_processor/youtube_downloader.py', 'wb') as f:
        f.write(content)
    print('Fixed!')
else:
    print('Not found')