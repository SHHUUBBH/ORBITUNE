import os
from huggingface_hub import HfApi

token = os.environ.get('HF_TOKEN', '')
api = HfApi(token=token)

with open(r'AI-ML/audio_processor/youtube_downloader.py', 'r') as f:
    content = f.read()

content = content.replace(
    "if 'SSL' in error_msg or 'EOF in error_msg or 'SSL in error_msg:",
    "if 'SSL' in error_msg or 'EOF' in error_msg or 'SSL' in error_msg:"
)

content = content.replace(
    "if 'SSL' in error_msg or 'EOF' in error_msg or 'SSL in error_msg:",
    "if 'SSL' in error_msg or 'EOF' in error_msg or 'SSL' in error_msg:"
)

api.upload_file(
    path_or_fileobj=content.encode('utf-8'),
    path_in_repo='AI-ML/audio_processor/youtube_downloader.py',
    repo_id='YOSHIMITSU-777/orbitune-api',
    repo_type='space'
)
print('Fixed file uploaded')