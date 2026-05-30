<!-- tags: game-dev, jx-online, equipment, modding -->
# 🔧 Chỉnh Sửa Võ Lâm Offline — Trang Bị, Drop Rate & Scripts

> Hướng dẫn chi tiết cách chỉnh sửa drop rate, thuộc tính trang bị (opt), đồ Bạch Kim, skill, và scripts hỗ trợ tân thủ trong VLTK Offline

📅 Ngày tạo: 2026-03-22 · 🔄 Cập nhật: 2026-03-22 · ⏱️ 22 phút đọc

| Aspect        | Detail                                          |
| ------------- | ----------------------------------------------- |
| **Chủ đề**    | Chỉnh sửa trang bị, drop rate, skills & scripts |
| **Phiên bản** | JX 6.0 – 8.0                                    |
| **Ngôn ngữ**  | Lua, INI config, TXT config, C++                |
| **Cấp độ**    | Sơ cấp → Chuyên gia (10-60)                     |
| **Nguồn**     | Cộng đồng Hội quán Võ Lâm, CLB GameSVN          |

---

![Xưởng Mod Game — Nơi kiếm hiệp gặp lập trình](./images/jx-modding-workshop.png)

---

## 1. DEFINE

### Hệ thống trang bị JX hoạt động thế nào?

Mỗi trang bị trong VLTK được quản lý bởi **nhiều file cấu hình phối hợp** với nhau. Hiểu mối quan hệ giữa chúng là chìa khóa để mod game hiệu quả.

### Hệ thống phân cấp chất lượng trang bị

| Cấp | Tên       | Màu | Dòng thuộc tính    | File cấu hình                                     |
| --- | --------- | --- | ------------------ | ------------------------------------------------- |
| 1   | Trắng     | ⬜  | 0 dòng             | `magicattrib.txt`                                 |
| 2   | Xanh      | 🟦  | 1-4 dòng random    | `magicattrib.txt`                                 |
| 3   | Tím       | 🟪  | Cố định, mạnh hơn  | `magicattriblevel.txt`                            |
| 4   | Hoàng Kim | 🟨  | Đặc biệt, cực mạnh | `magicattrib_ge.txt` + `goldequip.txt`            |
| 5   | Bạch Kim  | ⬛  | 2 dòng ẩn đặc biệt | `platina_magicattr.txt` + `platina_magicrate.txt` |

### Các file cấu hình then chốt

| File                    | Đường dẫn            | Vai trò                                       |
| ----------------------- | -------------------- | --------------------------------------------- |
| `magicattrib.txt`       | `settings/`          | Thông số opt cho đồ xanh (MAGIC_ID, min, max) |
| `magicattrib_ge.txt`    | `settings/`          | Thông số opt cho đồ Hoàng Kim                 |
| `magicattriblevel.txt`  | `settings/`          | Thông số opt cho đồ Tím                       |
| `platina_magicattr.txt` | `settings/item/`     | Thuộc tính dòng ẩn đồ Bạch Kim                |
| `platina_magicrate.txt` | `settings/item/`     | Tỉ lệ ra option theo cấp đồ Bạch Kim          |
| `npcdroprate*.ini`      | `settings/droprate/` | Tỉ lệ rớt đồ theo map                         |
| `maplist.ini`           | `server1/maps/`      | Mapping map → file droprate                   |
| `npcs.txt`              | `settings/`          | EXP, tiền, drop file của từng NPC             |
| `skill.txt`             | `settings/`          | Cấu hình skills (chủ động/tự động)            |
| `magicscript.txt`       | `settings/`          | ID item dùng trong drop config                |

### Actors & Luồng dữ liệu

| Component             | Vai trò                    | Input              | Output                  |
| --------------------- | -------------------------- | ------------------ | ----------------------- |
| **maplist.ini**       | Router — map → droprate    | Map ID             | Đường dẫn file droprate |
| **npcdroprate\*.ini** | Drop config — item + rate  | Monster kill event | Items rơi ra            |
| **magicattrib\*.txt** | Stat engine — opt + range  | Item tier          | Random thuộc tính       |
| **npcs.txt**          | NPC stats — EXP, tiền      | NPC ID             | Giá trị EXP, drop file  |
| **skill.txt**         | Skill config — type, level | Skill ID           | Hành vi skill           |
| **Lua scripts**       | Logic engine — buff, items | Player state       | Buff, items, UI actions |

### Failure Modes

| Lỗi                                          | Hậu quả                        | Giải pháp                                       |
| -------------------------------------------- | ------------------------------ | ----------------------------------------------- |
| Tổng RandRate vượt RandRange                 | Items rớt sai tỉ lệ            | Đảm bảo `sum(RandRate) <= RandRange`            |
| Sai ID item (Genre-Detail-Particular)        | Item không tồn tại, crash      | Cross-check với `magicscript.txt`               |
| Quên đồng bộ server ↔ client                 | Client crash hoặc hiển thị sai | Copy file đã sửa sang cả 2 phía                 |
| Chỉnh skill type sai                         | Skill không hoạt động          | So sánh `autoreply_skill` vs `autoattack_skill` |
| Xóa item trong droprate không cập nhật Count | Items phía sau bị lệch index   | Cập nhật Count và re-index lại section numbers  |

---

## 2. VISUAL

### Hệ thống Equipment & Loot

![Hệ thống trang bị và drop — 4 tier từ Trắng đến Hoàng Kim](./images/jx-equipment-system.png)

### Kiến trúc file cấu hình Drop System

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                        DROP SYSTEM ARCHITECTURE                          │
│                                                                          │
│  ┌─────────────────┐       ┌───────────────────────┐                    │
│  │  maplist.ini     │──────▶│  npcdroprate*.ini     │                    │
│  │                  │       │  (per map)            │                    │
│  │  Map 53 (Ba Lăng)│       │  ┌─────────────────┐ │                    │
│  │  → droprate10.ini│       │  │ [Main]           │ │                    │
│  │                  │       │  │ Count=2          │ │                    │
│  │  Map 93 (Tiến Cúc)       │  │ RandRange=100    │ │                    │
│  │  → droprate90.ini│       │  │ MagicRate=50     │ │                    │
│  └─────────────────┘       │  │ MoneyRate=50     │ │                    │
│                             │  │ MoneyScale=10    │ │                    │
│                             │  ├─────────────────┤ │                    │
│  ┌─────────────────┐       │  │ [1]              │ │                    │
│  │  npcs.txt        │       │  │ Genre=4          │ │                    │
│  │                  │       │  │ Detail=99        │ │                    │
│  │  ExpParam=800000 │───┐   │  │ Particular=1     │ │                    │
│  │  DropRateFile=   │   │   │  │ RandRate=25      │ │                    │
│  │   songjing.ini   │   │   │  └─────────────────┘ │                    │
│  └─────────────────┘   │   └───────────┬───────────┘                    │
│                         │               │                                │
│                         ▼               ▼                                │
│  ┌──────────────────────────────────────────────────────┐               │
│  │                  LOOT CALCULATION                     │               │
│  │                                                      │               │
│  │  Treasure = EXP-based (from npcs.txt)                │               │
│  │  Actual drops = Treasure × MagicRate%                │               │
│  │  Money drops  = Treasure × MoneyRate%                │               │
│  │  Money value  = ExpParam × MoneyScale%               │               │
│  │  Item chance  = RandRate / RandRange                  │               │
│  │  Item quality = random(MinItemLevel, MaxItemLevel)   │               │
│  └──────────────────────────────────────────────────────┘               │
│                                                                          │
│  ┌────────┐  ┌──────────────────┐  ┌───────────────────┐               │
│  │ Trắng  │  │ Xanh (opt)       │  │ Tím (cố định)     │               │
│  │ Level 1│  │ Level 2-5        │  │ magicattriblevel  │               │
│  │ 0 dòng │  │ 1-4 dòng random  │  │ thuộc tính cố định │               │
│  └────────┘  └──────────────────┘  └───────────────────┘               │
│                                                                          │
│  ┌──────────────────┐  ┌─────────────────────────────┐                  │
│  │ Hoàng Kim (gold) │  │ Bạch Kim (platina)          │                  │
│  │ magicattrib_ge   │  │ platina_magicattr.txt       │                  │
│  │ goldequip.txt    │  │ platina_magicrate.txt       │                  │
│  │ opt đặc biệt     │  │ 2 dòng ẩn, rate theo level  │                  │
│  └──────────────────┘  └─────────────────────────────┘                  │
└──────────────────────────────────────────────────────────────────────────┘
```

### Luồng tính toán Drop khi Monster chết

```text
Monster chết (ExpParam = 800,000)
       │
       ├── Treasure = 24 (số món tối đa có thể rớt)
       │
       ├── MoneyRate = 50% → 24 × 50% = 12 đống tiền
       │   └── Mỗi đống = ExpParam × MoneyScale%
       │       └── = 800,000 × 10% = 80,000 lượng/đống
       │
       ├── MagicRate = 50% → 24 × 50% = 12 món đồ
       │   ├── [1] RandRate=25/100 = 25% → 12 × 25% = 3 Nhạc Vương Kiếm
       │   ├── [2] RandRate=50/100 = 50% → 12 × 50% = 6 cây đao
       │   └── Còn lại: 12 - 3 - 6 = 3 (không rớt, vì Count=2)
       │
       └── Item Quality: random(MinItemLevel=1, MaxItemLevel=5)
           ├── Level 1 → Đồ trắng, 0 dòng opt
           ├── Level 5 → Đồ xanh, nhiều dòng opt cao
           └── Level Scale → Yêu cầu đẳng cấp (cấp 9, 18, 27...)
```

---

## 3. CODE

### Example 1: Basic — Cấu hình Drop Rate cho Map cụ thể

Hiểu cách `maplist.ini` liên kết map → file droprate, và cấu trúc file droprate.

```ini
; ============================================================
; maplist.ini — Mapping Map → Drop Rate Files
; Đường dẫn: server1/maps/maplist.ini
; ============================================================

; ── Map Ba Lăng Huyện (ID: 53) ──
; Quái thường dùng file droprate level 10-20
53_NormalDropRate=\settings\droprate\npcdroprate10.ini
; Boss xanh dùng file riêng, drop rate cao hơn
53_GoldenDropRate=\settings\droprate\goldennpc\golden_lv40.ini

; ── Map Tiến Cúc Động (ID: 93) ──
93_NormalDropRate=\settings\droprate\npcdroprate90.ini
93_GoldenDropRate=\settings\droprate\goldennpc\90_02droprate.ini

; ── Map Tống Kim (chiến trường) ──
; File droprate riêng cho boss Tống Kim
; ExpParam rất cao → rớt nhiều tiền + đồ xịn
```

```ini
; ============================================================
; npcdroprate*.ini — Cấu hình chi tiết drop cho map
; File mẫu: settings/droprate/songjing.ini (Tống Kim)
; ============================================================

[Main]
; ✅ Count = số loại item có thể rớt
Count=2
; ✅ RandRange = mẫu số cho tính tỉ lệ
RandRange=100
; ✅ MagicRate = % rớt đồ (50% của Treasure)
MagicRate=50
; ✅ MoneyRate = % rớt tiền (50% của Treasure)
MoneyRate=50
; ✅ MoneyScale = % giá trị mỗi đống tiền / ExpParam
MoneyScale=10
; ✅ Item quality range: 1=trắng → 10=xanh nhiều opt
MinItemLevel=1
MaxItemLevel=5
; ✅ Yêu cầu đẳng cấp: scale 1-10
; (1=không yêu cầu, 2=cấp 9, 3=cấp 18...)
MinItemLevelScale=1
MaxItemLevelScale=10

; ── Nhạc Vương Kiếm ──
; ⚠️ Genre-Detail-Particular = ID item (tra magicscript.txt)
[1]
Genre=4
Detail=99
Particular=1
RandRate=25          ; 25/100 = 25% khả năng rớt

; ── Đao ngẫu nhiên ──
[2]
Genre=0
Detail=0
Particular=1
RandRate=50          ; 50/100 = 50% khả năng rớt

; ⚠️ Công thức: Tổng RandRate <= RandRange
; 25 + 50 = 75 <= 100 ✅
; Còn 25% không match → không rớt item nào
```

**Kết luận**: Mỗi map có file droprate riêng, được link qua `maplist.ini`. Trong droprate file, `Count` quyết định số loại item, `MagicRate/MoneyRate` quyết định tỉ lệ đồ vs tiền, và `RandRate/RandRange` quyết định tỉ lệ từng item cụ thể.

---

### Example 2: Intermediate — Thuộc tính trang bị (Opt) & Đồ Bạch Kim

Hiểu cách chỉnh dòng opt cho đồ xanh và cấu hình 2 dòng ẩn đặc biệt của đồ Bạch Kim.

```text
; ============================================================
; magicattrib.txt — Thuộc tính opt cho đồ xanh
; Cấu trúc (giải thích từ DOCX gốc):
;
; Cột D: Mức độ (1-10) mà dòng opt có thể rớt
; Cột E: MAGIC_ID của thông số dòng
; Cột F: Giá trị Min
; Cột G: Giá trị Max
; Cột L: Chú thích tên dòng
; Cột M-W: Tỉ lệ rớt tương ứng loại trang bị
;           (vũ khí tầm gần, tầm xa, áo, giày, bao tay...)
; ============================================================

; Ví dụ: Dòng "Tăng hiệu quả sát thương" (MAGIC_ID = 126)
; 10 mức độ, mỗi mức có min/max khác nhau:
;
; Mức 1:  Min=5,   Max=10   → Rate: Vũ khí gần=100000, xa=100000
; Mức 2:  Min=10,  Max=20   → Rate: Vũ khí gần=80000,  xa=80000
; Mức 3:  Min=20,  Max=30   → Rate: Vũ khí gần=50000,  xa=50000
; ...
; Mức 10: Min=80,  Max=100  → Rate: Vũ khí gần=1000,   xa=1000
;
; ⚠️ Chỉ vũ khí mới có opt "tăng hiệu quả sát thương"
;    → Các cột áo, giày, bao tay = 0 (không thể rớt dòng này)
```

```text
; ============================================================
; Đồ Bạch Kim — 2 file cấu hình dòng ẩn
; ============================================================
;
; ── File 1: platina_magicattr.txt ──
; Xác định option của đồ, quan tâm cột AttributeType và Value1
; Mã dòng = số thứ tự (bắt đầu từ 1)
;
; Ví dụ: Dòng Sinh lực tối đa (AttributeType = 85)
; STT  AttributeType  Value1
;  4       85           800      ← Sinh lực +800
;  5       85          1200      ← Sinh lực +1200
;  6       85          1500      ← Sinh lực +1500
;  7       85          2000      ← Sinh lực +2000
;
; ── File 2: platina_magicrate.txt ──
; Quy định tỉ lệ ra option theo cấp độ đồ
;
; PlatinaItem: Mã đồ (lấy STT trong Platinaequip.txt)
; Level: Cấp độ (5-9, dưới 5 = mức thấp nhất)
; SkillNo: 1 = dòng ẩn 1, 2 = dòng ẩn 2
; ActiveRate: Luôn 100%
; Rate1, Rate2, Rate3: Tỉ lệ % ra từng option
; MagicIDx: Chiếu sang STT trong platina_magicattr.txt
;
; Ví dụ: Bao tay Tứ Không (2 dòng ẩn)
; ┌──────┬───────┬─────────┬─────────┬─────────┬──────────────────┐
; │Level │SkillNo│ Rate1   │ Rate2   │ Rate3   │ Explanation      │
; ├──────┼───────┼─────────┼─────────┼─────────┼──────────────────┤
; │  5   │  1    │  95%    │   5%    │   0%    │ SL 800(95%)/1200 │
; │  6   │  1    │  80%    │  15%    │   5%    │ Dần tăng tier    │
; │  7   │  1    │  50%    │  35%    │  15%    │ Cân bằng hơn     │
; │  8   │  1    │  20%    │  50%    │  30%    │ Thiên tier cao   │
; │  9   │  1    │   0%    │   0%    │ 100%    │ Luôn SL +1500    │
; └──────┴───────┴─────────┴─────────┴─────────┴──────────────────┘
```

**Kết luận**: Đồ Bạch Kim có cơ chế đặc biệt — 2 dòng ẩn (SkillNo 1 & 2) với tỉ lệ ra option phụ thuộc vào cấp độ đồ. Cấp càng cao, option càng mạnh. Chỉnh file `platina_magicattr.txt` để set mốc giá trị, và `platina_magicrate.txt` để set tỉ lệ.

---

### Example 3: Advanced — Chỉnh Skill và đồng bộ Server-Client

Chuyển skill "Cửu Kiếm Hợp Nhất" từ tự động sang chủ động, và hiểu cách đồng bộ dữ liệu giữa server và client.

```lua
-- ============================================================
-- Chuyển skill Cửu Kiếm Hợp Nhất → Chủ động (Manual Cast)
-- Quy trình 4 bước
-- ============================================================

-- ── BƯỚC 1: settings/skill.txt ──
-- Tìm "Cửu Kiếm Hợp Nhất" trong skill.txt
-- Kéo ngang tìm cột "autoreply_skill"
-- ⚠️ autoreply_skill = tự động phát chiêu
--    autoattack_skill = nhấn thủ công mới phát
--
-- Thay:  autoreply_skill → autoattack_skill
--
-- Trước: ... jiujian_heyi ... autoreply_skill ...
-- Sau:   ... jiujian_heyi ... autoattack_skill ...

-- ── BƯỚC 2: script/skill/huashan.lua ──
-- Tìm function jiujian_heyi (9 kiếm hợp nhất)
-- Thay đổi tương tự:

-- ❌ TRƯỚC (tự động)
-- function jiujian_heyi_autoreply_skill(...)

-- ✅ SAU (chủ động)
-- function jiujian_heyi_autoattack_skill(...)

-- ── BƯỚC 3: Lưu cả 2 file ──
-- ⚠️ PHẢI lưu cả skill.txt VÀ huashan.lua

-- ── BƯỚC 4: ĐỒNG BỘ ──
-- ⚠️ Đây là bước QUAN TRỌNG NHẤT mà nhiều người quên!
-- Sửa trên server1 → phải copy sang client game
--
-- Cách đồng bộ:
--   1. Copy file skill.txt từ server1/settings/ → client/settings/
--   2. Copy thư mục script/ từ server1/ → client/
--   3. Nếu client đã có file → chỉ copy file đã sửa đè lên
```

```bash
#!/bin/bash
# ============================================================
# Sync Script: Đồng bộ file giữa Server và Client
# ⚠️ LUÔN backup trước khi sync!
# ============================================================

SERVER_DIR="/home/jxser/server1"
CLIENT_DIR="/path/to/client/game"
BACKUP_DIR="/home/jxser/backup/sync_$(date +%Y%m%d_%H%M%S)"

# ── 1. Backup trước khi đồng bộ ──
sync_with_backup() {
    local file="$1"
    local relative_path="${file#$SERVER_DIR/}"

    echo "📦 Syncing: $relative_path"

    # Backup client file cũ (nếu có)
    if [ -f "$CLIENT_DIR/$relative_path" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname $relative_path)"
        cp "$CLIENT_DIR/$relative_path" \
           "$BACKUP_DIR/$relative_path"
        echo "  💾 Backup: $BACKUP_DIR/$relative_path"
    fi

    # Copy server → client
    mkdir -p "$CLIENT_DIR/$(dirname $relative_path)"
    cp "$file" "$CLIENT_DIR/$relative_path"
    echo "  ✅ Synced: $relative_path"
}

# ── 2. Đồng bộ skill files ──
sync_skills() {
    echo "===== SYNCING SKILL FILES ====="
    sync_with_backup "$SERVER_DIR/settings/skill.txt"
    sync_with_backup "$SERVER_DIR/script/skill/huashan.lua"

    # ✅ Sync tất cả file liên quan
    find "$SERVER_DIR/script/skill" -name "*.lua" -newer \
         "$CLIENT_DIR/script/skill/huashan.lua" 2>/dev/null | \
    while read file; do
        sync_with_backup "$file"
    done
}

# ── 3. Đồng bộ settings ──
sync_settings() {
    echo "===== SYNCING SETTINGS ====="
    local files=(
        "settings/skill.txt"
        "settings/magicattrib.txt"
        "settings/magicattrib_ge.txt"
        "settings/magicattriblevel.txt"
        "settings/item/platina_magicattr.txt"
        "settings/item/platina_magicrate.txt"
    )

    for file in "${files[@]}"; do
        if [ -f "$SERVER_DIR/$file" ]; then
            sync_with_backup "$SERVER_DIR/$file"
        fi
    done
}

# ── Main ──
case "$1" in
    skills)    sync_skills ;;
    settings)  sync_settings ;;
    all)       sync_skills && sync_settings ;;
    *)
        echo "🔄 JX Sync Tool"
        echo "Usage: $0 {skills|settings|all}"
        ;;
esac
```

**Kết luận**: Mỗi lần chỉnh sửa skill hay settings trên server, **bắt buộc phải đồng bộ sang client**. Không đồng bộ → client crash hoặc skill không hoạt động. Script sync tự động giúp tránh sai sót.

---

### Example 4: Expert — Scripts hỗ trợ: Túi máu & Siêu buff Tân Thủ

Hai script Lua phổ biến nhất trong cộng đồng: túi máu vĩnh viễn và siêu hỗ trợ tân thủ (max buff).

```lua
-- ============================================================
-- Túi máu vĩnh viễn — Nguyễn Anh
-- Tự động fill hành trang bằng thuốc hồi sinh
-- ⚠️ Chỉ dùng cho nhân vật chuyển sinh ≤ 5 lần
-- ============================================================

IncludeLib("SETTING");
Include("\\script\\lib\\awardtemplet.lua");
Include("\\script\\dailogsys\\dailogsay.lua");

function main(nItemIndex)
    -- ① Load script phụ trợ
    dofile("script/global/general/hotrotanthu/tuimautanthu.lua")

    -- ② Kiểm tra giới hạn chuyển sinh
    -- ⚠️ Giới hạn ≤ 5 lần chuyển sinh để cân bằng game
    if (ST_GetTransLifeCount() > 5) then
        Talk(1, "", "Chỉ hỗ trợ người chơi chuyển sinh 5 lần trở xuống!")
        return 1
    end

    -- ③ Đếm số ô trống trong hành trang
    local nFreeItemCellCount = CalcFreeItemCellCount()
    if nFreeItemCellCount <= 0 then
        Talk(1, "", "Hành trang đã đầy, không thể nhận máu hỗ trợ.")
        return 1
    end

    -- ④ Tạo bảng phần thưởng
    -- tbProp = {Genre, Detail, Particular, BindType, ...}
    -- ⚠️ nCount = số ô trống → fill đầy hành trang
    local tbAward = {
        tbProp = {1, 8, 0, 4, 0, 0},    -- Hồi Thiên Tái Tạo Đơn (Khóa BH)
        nCount = nFreeItemCellCount       -- Số vật phẩm = số ô trống
    }
    tbAwardTemplet:GiveAwardByList(tbAward, "Túi máu tân thủ")

    return 1
end
```

```lua
-- ============================================================
-- Siêu hỗ trợ tân thủ — Muoibay Conkhi & Hoàng Tùng
-- Max tất cả buff, hỗ trợ đến cấp 200, thời gian vô hạn
-- ⚠️ Chỉnh cho phù hợp server, không nên max tất cả!
-- ============================================================

-- ① Phiên bản gốc — Muoibay Conkhi
-- Đơn giản, trực tiếp, dễ hiểu
function hotrotanthu_v1()
    -- ⚠️ Chỉ apply cho level < 201
    -- Muốn giới hạn thấp hơn → thay 201 thành số mong muốn
    if GetLevel() < 201 then
        -- Tốc độ tấn công (max level = 20)
        AddSkillState(511, 20, 1, 60000*24*60*60*18)
        -- Tốc độ di chuyển
        AddSkillState(512, 20, 1, 60000*24*60*60*18)
        -- Tăng máu tối đa
        AddSkillState(527, 20, 1, 60000*24*60*60*18)
        -- Tăng máu + mana tối đa
        AddSkillState(529, 20, 1, 60000*24*60*60*18)
        -- Tăng kháng (vòng sáng dưới chân)
        AddSkillState(313, 20, 1, 60000*24*60*60*18)
        -- Hồi máu + mana (vòng sáng dưới chân)
        AddSkillState(314, 20, 1, 60000*24*60*60*18)
        -- Tăng may mắn (hình rồng bay)
        AddSkillState(546, 20, 1, 60000*24*60*60*18)
    end
end

-- ② Phiên bản cải tiến — Hoàng Tùng
-- Gọn hơn, dễ chỉnh thời gian
function hotrotanthu_v2()
    if GetLevel() < 201 then
        -- ✅ Tính thời gian 1 lần, dùng cho tất cả
        -- 18 ngày × 24h × 60m × 60s × 18 (multiplier)
        local nTime = 18 * 24 * 60 * 60 * 18

        -- ⚠️ Số 20 = max skill level, giảm nếu muốn yếu hơn
        -- ⚠️ nTime = thời gian buff, giảm nếu muốn ngắn hơn
        AddSkillState(511, 20, 1, nTime)  -- attackspeed
        AddSkillState(512, 20, 1, nTime)  -- fastwalkrun
        AddSkillState(527, 20, 1, nTime)  -- lifemax
        AddSkillState(529, 20, 1, nTime)  -- lifemax + manamax
        AddSkillState(313, 20, 1, nTime)  -- allrest (vòng sáng)
        AddSkillState(314, 20, 1, nTime)  -- lifereplenish
        AddSkillState(546, 20, 1, nTime)  -- lucky (rồng bay)
    end
end

-- ③ Bảng tham khảo Skill State IDs
--
-- ┌──────┬────────────────────┬─────────────────────────────┐
-- │  ID  │ Tên                │ Hiệu ứng                   │
-- ├──────┼────────────────────┼─────────────────────────────┤
-- │ 313  │ allrest            │ Tăng kháng (vòng sáng chân) │
-- │ 314  │ lifereplenish      │ Hồi máu + mana liên tục    │
-- │ 511  │ attackspeed        │ Tăng tốc độ tấn công       │
-- │ 512  │ fastwalkrun        │ Tăng tốc độ di chuyển      │
-- │ 527  │ lifemax            │ Tăng máu tối đa            │
-- │ 529  │ lifemax + manamax  │ Tăng cả máu lẫn mana      │
-- │ 546  │ lucky              │ Tăng may mắn + rồng bay    │
-- └──────┴────────────────────┴─────────────────────────────┘
```

```cpp
// ============================================================
// Fix hiệu ứng NPC bị đổi màu khi trúng độc/băng
// Source: Core/Src/KNpcRes.cpp
// ⚠️ Chỉ sửa ảnh hưởng nhân vật, giữ nguyên chiêu thức,
//     vòng sáng, danh hiệu không bị ảnh hưởng
//
// Ref: https://www.facebook.com/share/p/17e3Ldibbz/
// ============================================================

// Trong hàm KNpcRes::Draw():
// void KNpcRes::Draw(int nNpcIdx, int nDir, int nAllFrame,
//                    int nCurFrame, BOOL bInMenu, BOOL bPaintBody)
//
// Tìm đoạn xử lý hiệu ứng trúng độc (xanh đen)
// và đóng băng (lam) — chỉ apply cho nhân vật (body),
// KHÔNG apply cho:
//   - Chiêu thức (skill effects)
//   - Vòng sáng (aura)
//   - Danh hiệu (title)
//
// ⚠️ Đây là chỉnh sửa source C++ → cần compile lại client
// ⚠️ LUÔN backup KNpcRes.cpp gốc trước khi sửa!
```

**Kết luận**: Scripts hỗ trợ tân thủ rất phổ biến trong cộng đồng JX offline. Túi máu giúp newbie không lo thiếu thuốc, siêu buff giúp farm dễ dàng. Tuy nhiên, **nên giới hạn** (level, thời gian, số lần) để giữ cân bằng game.

---

## 4. PITFALLS

| #   | Lỗi                                               | Hậu quả                        | Fix                                               |
| --- | ------------------------------------------------- | ------------------------------ | ------------------------------------------------- |
| 1   | Tổng RandRate > RandRange                         | Drop rate vượt 100%, sai logic | Luôn kiểm tra `sum(RandRate) <= RandRange`        |
| 2   | Xóa item trong droprate quên cập nhật Count       | Items sau bị lệch, crash       | Re-index section numbers + cập nhật Count         |
| 3   | Chỉnh server không đồng bộ client                 | Client crash, skill vô hiệu    | Tạo script sync tự động (xem Example 3)           |
| 4   | Dùng sai ID item (Genre-Detail-Particular)        | Item không tồn tại hoặc sai    | Cross-check `magicscript.txt` hoặc `questkey.txt` |
| 5   | Buff tân thủ quá mạnh (max tất cả skill level 20) | Game mất thử thách, chán nhanh | Giảm level buff (5-10), giới hạn cấp áp dụng      |
| 6   | Chỉnh `MoneyScale` quá cao                        | Lạm phát tiền tệ server        | Giữ MoneyScale 5-15%, test với nhiều player       |
| 7   | Sai `autoreply_skill` / `autoattack_skill`        | Skill không hoạt động          | Phải đổi ở CẢ HAI: `skill.txt` + `*.lua`          |

### Anti-pattern: Xóa item trong droprate không cập nhật

```ini
; ❌ SAI — Xóa [53] (Khiêu Chiến Lệnh) mà quên chỉnh Count và index

[Main]
Count=70              ; ⚠️ Vẫn là 70 nhưng thực tế chỉ 69 items!

[52]
Genre=6
Detail=1
Particular=1400
RandRate=2000

; [53] đã xóa nhưng [54] vẫn giữ nguyên index
[54]                  ; ⚠️ SAI — phải đổi thành [53]!
Genre=5
Detail=2
Particular=100
RandRate=1500

; ✅ ĐÚNG — Sau khi xóa [53]:
; 1. Đổi Count=69
; 2. Re-index: [54]→[53], [55]→[54], [56]→[55]...
```

---

## 5. REF

| Resource                    | Link                                                                    | Tác giả        |
| --------------------------- | ----------------------------------------------------------------------- | -------------- |
| Chỉnh sửa VL Offline        | [DOCX gốc](../../public/dowloads/Chỉnh%20sửa%20Vo%20Lam%20offline.docx) | Cộng đồng      |
| Túi máu vĩnh viễn           | [Facebook](https://www.facebook.com/share/p/17qx7r3cYi/)                | Nguyễn Anh     |
| Siêu hỗ trợ tân thủ         | Cộng đồng offline                                                       | Muoibay Conkhi |
| Fix hiệu ứng NPC            | [Facebook](https://www.facebook.com/share/p/17e3Ldibbz/)                | Cộng đồng      |
| Chỉnh đồ Bạch Kim           | [Facebook](https://www.facebook.com/share/p/19zaAJD2dA/)                | Cộng đồng      |
| Hướng dẫn droprate chi tiết | [CLB GameSVN](http://www.clbgamesvn.com/diendan/showthread.php?t=31079) | CLB GameSVN    |
| Hội quán Võ Lâm Offline     | [Facebook Group](https://www.facebook.com/groups/volamquan)             | Cộng đồng      |

---

## 6. RECOMMEND

| Mở rộng                        | Khi nào                  | Lý do                                                   |
| ------------------------------ | ------------------------ | ------------------------------------------------------- |
| **Drop Rate Calculator (Web)** | Khi cần cân bằng economy | Tool web tính toán RandRate, preview drop table         |
| **Item Database Browser**      | Khi quản lý nhiều items  | Parse magicscript.txt + magicattrib ra web, search dễ   |
| **Auto Sync Watcher**          | Khi dev liên tục         | inotifywait watch file changes, auto sync server→client |
| **Skill Editor GUI**           | Khi chỉnh nhiều skills   | Tool GUI chỉnh skill.txt, preview thay đổi realtime     |
| **Bạch Kim Simulator**         | Khi test đồ Bạch Kim     | Random 1000 lần → thống kê tỉ lệ ra option thực tế      |
| **Economy Monitor Dashboard**  | Khi server > 10 players  | Track tiền/đồ in/out, phát hiện lạm phát sớm            |

---

[← Bài trước: Phong Lăng Độ & Boss System](./02-phong-lang-do-boss-system.md) · [→ Về trang chủ](../README.md)
