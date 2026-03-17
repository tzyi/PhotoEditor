import os
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image, ImageOps

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}


def compress_image(input_path: Path, output_path: Path, quality: int) -> tuple[int, int]:
    """
    壓縮單張圖片並儲存至指定路徑。
    回傳 (原始大小 bytes, 壓縮後大小 bytes)。
    """
    img = Image.open(input_path)

    # 依據 EXIF 方向資訊旋轉圖片，避免壓縮後照片翻轉
    img = ImageOps.exif_transpose(img)

    # RGBA / Palette 模式轉為 RGB，才能以 JPEG 格式儲存
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 統一輸出為 JPEG
    out_file = output_path.with_suffix(".jpg")
    img.save(out_file, "JPEG", optimize=True, quality=quality)

    return input_path.stat().st_size, out_file.stat().st_size


def _worker(img_file: Path, input_path: Path, output_path: Path,
            quality: int, print_lock: threading.Lock) -> tuple[int, int]:
    """單一圖片的壓縮工作，供執行緒呼叫。"""
    relative = img_file.relative_to(input_path)
    out_file = output_path / relative
    original_size, compressed_size = compress_image(img_file, out_file, quality)
    ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    with print_lock:
        print(
            f"  [OK] {relative}"
            f"  {original_size // 1024} KB → {compressed_size // 1024} KB"
            f"  (縮減 {ratio:.1f}%)"
        )
    return original_size, compressed_size


def compress_folder(input_dir: str, output_dir: str, quality: int, threads: int) -> None:
    """
    遍歷 input_dir 中所有支援的圖片檔案（含子資料夾），
    壓縮後保留相同的目錄結構輸出到 output_dir。
    使用多執行緒並行加速處理。
    """
    input_path = Path(input_dir).resolve()
    output_path = Path(output_dir).resolve()

    if not input_path.exists():
        print(f"[錯誤] 輸入資料夾不存在：{input_path}")
        return

    if not input_path.is_dir():
        print(f"[錯誤] 指定路徑不是資料夾：{input_path}")
        return

    # 收集所有符合副檔名的圖片
    image_files = [
        f for f in input_path.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not image_files:
        print(f"[提示] 在 {input_path} 中找不到任何支援的圖片檔案。")
        print(f"       支援格式：{', '.join(SUPPORTED_EXTENSIONS)}")
        return

    print(f"找到 {len(image_files)} 張圖片，開始壓縮（品質：{quality}%，執行緒數：{threads}）...")
    print(f"輸入資料夾：{input_path}")
    print(f"輸出資料夾：{output_path}")
    print("-" * 60)

    total_original = 0
    total_compressed = 0
    success_count = 0
    fail_count = 0
    print_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(_worker, img_file, input_path, output_path, quality, print_lock): img_file
            for img_file in image_files
        }

        for future in as_completed(futures):
            img_file = futures[future]
            relative = img_file.relative_to(input_path)
            try:
                original_size, compressed_size = future.result()
                total_original += original_size
                total_compressed += compressed_size
                success_count += 1
            except Exception as e:
                with print_lock:
                    print(f"  [失敗] {relative}  原因：{e}")
                fail_count += 1

    print("-" * 60)
    print(f"完成！成功：{success_count} 張  失敗：{fail_count} 張")
    if total_original > 0:
        overall_ratio = (1 - total_compressed / total_original) * 100
        print(
            f"總大小：{total_original // 1024} KB → {total_compressed // 1024} KB"
            f"  (整體縮減 {overall_ratio:.1f}%)"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="批次壓縮資料夾中的所有圖片",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        metavar="INPUT_DIR",
        help="輸入資料夾路徑（含所有要壓縮的圖片）",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        metavar="OUTPUT_DIR",
        help="輸出資料夾路徑（壓縮後的圖片會存放於此）",
    )
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=70,
        metavar="0-100",
        help="壓縮品質，範圍 0（最差）~ 100（最佳），預設 70",
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=min(8, (os.cpu_count() or 4)),
        metavar="N",
        help=f"並行執行緒數，預設為 CPU 核心數（最多 8），可自行調高",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not (0 <= args.quality <= 100):
        print("[錯誤] 品質參數必須介於 0 到 100 之間。")
        return

    if args.threads < 1:
        print("[錯誤] 執行緒數必須至少為 1。")
        return

    compress_folder(args.input, args.output, args.quality, args.threads)


if __name__ == "__main__":
    main()
