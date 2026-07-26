from pathlib import Path
from .config import ROOT

def upload_video(video_path: Path, description: str) -> bool:
    """
    Uploads a video to TikTok using the tiktok-uploader library.
    Returns True if successful, False otherwise.
    """
    try:
        import tiktok_uploader.upload as u
        from tiktok_uploader.upload import upload_video as tiktok_upload
        
        # Monkey patch _set_description to bypass the tutorial popup overlay
        original_set_desc = u._set_description
        def patched_set_desc(page, description):
            try:
                page.evaluate('''() => {
                    var el = document.querySelector(".react-joyride__overlay");
                    if(el) el.remove();
                    var portal = document.getElementById("react-joyride-portal");
                    if(portal) portal.remove();
                }''')
            except Exception as e:
                print(f"    [TikTok] Popup bypass failed: {e}")
            original_set_desc(page, description)
        
        u._set_description = patched_set_desc
        
    except ImportError:
        print("    [Error] tiktok-uploader not installed. Run 'pip install tiktok-uploader'")
        return False

    cookies_path = ROOT / "tiktok_cookies.txt"
    if not cookies_path.exists():
        print(f"    [Error] TikTok cookies not found at {cookies_path}")
        return False

    print(f"    [TikTok] Starting upload for {video_path.name}...")
    try:
        # tiktok_uploader default headless is False. We should set headless=True for Github Actions!
        failed = tiktok_upload(
            str(video_path),
            description=description,
            cookies=str(cookies_path),
            headless=True
        )
        if failed:
            print("    [TikTok] Upload failed (returned True/errors).")
            return False
        
        print("    [TikTok] Video successfully uploaded to TikTok!")
        return True
    except Exception as e:
        print(f"    [TikTok] Upload crashed: {e}")
        return False
