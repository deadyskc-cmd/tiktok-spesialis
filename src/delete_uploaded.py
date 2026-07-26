import argparse
from . import upload, state
from .state import load


def list_videos():
    s = load()
    published = s.get("published", [])
    if not published:
        print("Tidak ada video yang pernah diupload.")
        return
    print(f"{'#':>3}  {'Tanggal':<20} {'Video ID':<15} {'Judul'}")
    print("-" * 80)
    for i, v in enumerate(published, 1):
        vid = v.get("video_id") or "-"
        print(f"{i:>3}  {v['ts']:<20} {vid:<15} {v['title']}")
    return published


def main():
    p = argparse.ArgumentParser(description="Hapus video yang sudah diupload dari YouTube")
    p.add_argument("--list", action="store_true", help="Tampilkan semua video yang sudah diupload")
    p.add_argument("--id", type=str, default=None,
                   help="Video ID yang akan dihapus")
    p.add_argument("--all", action="store_true",
                   help="Hapus SEMUA video yang pernah diupload")
    p.add_argument("--force", action="store_true",
                   help="Langsung hapus tanpa konfirmasi")
    args = p.parse_args()

    if args.list:
        list_videos()
        return

    if args.id:
        video_id = args.id
    elif args.all:
        published = load().get("published", [])
        if not published:
            print("Tidak ada video untuk dihapus.")
            return
        if not args.force:
            print(f"{len(published)} video akan dihapus dari YouTube.")
            confirm = input("Lanjutkan? (y/N): ")
            if confirm.lower() != "y":
                print("Dibatalkan.")
                return
        for v in published:
            vid = v.get("video_id")
            if vid:
                print(f"Menghapus {v['title']} ({vid})...")
                try:
                    upload.delete_video(vid)
                    state.remove_published(vid)
                    print(f"  OK")
                except Exception as e:
                    print(f"  GAGAL: {e}")
        print("Selesai.")
        return

    if not args.id:
        published = list_videos()
        if not published:
            return
        print()
        idx = input("Nomor video yang akan dihapus (atau 0 untuk batal): ")
        try:
            idx = int(idx)
            if idx < 1 or idx > len(published):
                print("Dibatalkan.")
                return
            v = published[idx - 1]
        except ValueError:
            print("Input tidak valid.")
            return
        video_id = v.get("video_id")
        if not video_id:
            print("Video ini belum diupload (tidak memiliki video_id).")
            return

    if not args.force:
        confirm = input(f"Hapus video '{v['title']}' ({video_id})? (y/N): ")
        if confirm.lower() != "y":
            print("Dibatalkan.")
            return

    print(f"Menghapus {video_id}...")
    try:
        upload.delete_video(video_id)
        state.remove_published(video_id)
        print("OK.")
    except Exception as e:
        print(f"GAGAL: {e}")


if __name__ == "__main__":
    main()
