import inspect
from skills.skill_download_youtube import download_video

def test_download_interface():
    params = inspect.signature(download_video).parameters
    assert "video_url" in params
