# 批次圖片壓縮工具

這是一個用 Python 製作的命令列工具，可以批次壓縮指定資料夾內所有圖片，並將壓縮後的圖片輸出到指定資料夾。支援多種常見圖片格式，並可自訂壓縮品質。

---

## 功能特色
- 支援 JPG、JPEG、PNG、BMP、WEBP、TIFF 等格式
- 可遞迴處理子資料夾，並保留原有目錄結構
- 可自訂壓縮品質（0~100）
- 自動將 PNG、透明圖等轉為 JPEG
- 顯示每張圖片壓縮前後大小與縮減比例
- 統計總壓縮成效

---

## 安裝方式

1. 安裝 Python 3.7 以上版本
2. 安裝 Pillow 影像處理函式庫：

```bash
pip install Pillow
```

---

## 使用說明

### 基本指令

```bash
python compress_images.py -i <輸入資料夾> -o <輸出資料夾> [-q 壓縮品質]
```

### 參數說明

| 參數 | 必填 | 說明 |
|------|------|------|
| `-i`, `--input`  | 是 | 輸入圖片資料夾路徑 |
| `-o`, `--output` | 是 | 輸出壓縮圖片資料夾路徑（自動建立） |
| `-q`, `--quality`| 否 | 壓縮品質（0~100，預設 70，數字越小壓縮越大） |

### 範例

1. 將 `C:\Photos\原始` 資料夾內所有圖片壓縮到 `C:\Photos\壓縮`，品質 70：

```bash
python compress_images.py -i "C:\Photos\原始" -o "C:\Photos\壓縮"
```

2. 指定壓縮品質為 50：

```bash
python compress_images.py -i "C:\Photos\原始" -o "C:\Photos\壓縮" -q 50

python compress_images.py -i "C:\Users\arif1\Downloads\未命名的轉存\生活日常_260224" -o "C:\Users\arif1\Downloads\未命名的轉存\compress" -q 50
```

3. 查看說明：

```bash
python compress_images.py --help
```

---

## 注意事項
- 輸出圖片皆為 JPEG 格式，原始透明度會消失。
- 若原始圖片已為 JPEG，會以指定品質重新壓縮。
- 輸出資料夾若不存在會自動建立。
- 壓縮過程中若遇到無法處理的檔案會自動略過並顯示錯誤訊息。

---

## 授權
本工具僅供學習與個人用途，請勿用於非法用途。

---

## 聯絡方式
如有問題歡迎提出 issue 或聯絡作者。
# PhotoEditor

照片壓縮工具

