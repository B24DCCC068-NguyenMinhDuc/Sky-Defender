1. S - Specific (Tính cụ thể: Xây dựng cấu trúc "Xương sống")
Mục tiêu là tạo ra một sản phẩm hoàn chỉnh về mặt kỹ thuật (Vertical Slice) mang tên **Sky Defender - Bảo Vệ Bầu Trời**, đảm bảo người chơi có cảm giác hành động liên tục và kịch tính.
Cơ chế Người chơi (Player Mechanics):
Điều khiển máy bay trong không gian 2D bằng hệ tọa độ $(x, y)$ với phím mũi tên hoặc WASD, di chuyển chéo được chuẩn hóa bằng hệ số $\frac{1}{\sqrt{2}} \approx 0.7071$ để không bị "nhanh chéo".
Hệ thống bắn đạn: **Auto-fire liên tục** với cooldown 200ms (giữ phím không cần thiết, máy bay tự bắn khi còn sống).
Quản lý trạng thái: Bình thường → bị thương (tint đỏ nháy trong 400ms + bất tử 900ms) → nổ tung (5 frame animation).
Hai chế độ chơi:
- **Time Attack**: sống sót 5 hoặc 10 phút, boss sinh ra đều đặn mỗi 90 giây.
- **Campaign**: mỗi màn 3 boss, hạ đủ 3 boss → lên level (boss khỏe hơn, quái nhanh hơn, hồi 2 HP).
Hệ thống Kẻ địch (Enemy Ecosystem):
Tier 1 (Scout): Bay thẳng từ trên xuống với vận tốc ngẫu nhiên 3.0–5.0 × bội số độ khó, máu 1 (một phát đạn chết). Đôi khi sinh theo đội hình 3–4 con hàng ngang mỗi 5.5 giây.
Tier 2 (Interceptor): Xuất hiện từ hai bên góc màn hình, bay chéo (vx ≈ 60% vy) để cắt mặt người chơi, máu 2+ theo level.
The Mother Ship (Boss): Một thực thể khổng lồ xuất hiện ở giây thứ 90 (hoặc 90s sau khi hạ boss trước ở Campaign). **3 giai đoạn chuyển theo % HP**: Phase 1 (>66% HP) bắn đạn đơn nhắm vào người chơi → Phase 2 (33–66% HP) bắn tỏa 5 tia → Phase 3 (<33% HP) bắn tỏa rộng hơn + triệu hồi 2 Scout mỗi 3.5 giây.
Vật phẩm (Power-ups), rơi 18% từ quái thường, rơi **chắc chắn cả 3 loại** khi hạ boss:
Blue Crystal: Nâng cấp súng thành "Triple Shot" (3 tia, chéo ±15°) trong 8 giây.
Red Heart: Hồi 2 HP (tương đương 25% thanh máu tối đa 8 HP).
Golden Shield: Tạo vòng vàng quanh máy bay, chặn đúng 1 lần va chạm.

2. M - Measurable (Tính đo lường: Chỉ số định lượng thành công)
Chúng ta sẽ quản lý tiến độ thông qua các "Key Performance Indicators" (KPI) cụ thể:
Tài nguyên Đồ họa: Tái sử dụng bộ **Kenney Space Shooter Extension** + asset nội bộ, đảm bảo tối thiểu 15 sprite (3 loại máy bay ally/scout/interceptor, 1 boss, 3 loại đạn player/enemy/boss, 5 frame explosion, 3 power-up, heart HUD, 3 nút menu).
Hiệu suất kỹ thuật:
Duy trì ổn định 60 FPS (clock.tick(FPS) trong mọi vòng lặp).
Thời gian phản hồi đầu vào (Input Latency) dưới 16ms (1 frame @ 60 FPS).
Quản lý bộ nhớ: Mọi Bullet / Enemy / Explosion / PowerUp tự gọi `self.kill()` khi rời khỏi tọa độ màn hình hoặc hết animation để pygame Group giải phóng reference.
Trải nghiệm người dùng (UX):
Menu chính và Menu chọn chế độ: nút và mục phóng to 6–8% khi di chuột qua, đổi màu vàng/xám khi đang focus.
Hệ thống điểm cao (High Score) phải lưu riêng 3 biến `time_5`, `time_10`, `campaign` vào `highscore.json` và còn nguyên sau khi tắt game.

3. A - Achievable (Tính khả thi: Phân phối năng lực nhóm)
Để hoàn thành khối lượng việc khổng lồ này trong 3 tuần, nhóm cần chia nhỏ module (Component-based):
Thành viên 1 (Engine & Core Logic): Phụ trách các Class kế thừa `pygame.sprite.Sprite` (Player, Bullet, Scout, Interceptor, Boss, Explosion, PowerUp), logic va chạm `rect.colliderect` giữa các Group, `ScreenShake` và `StarField` parallax 2 lớp.
Thành viên 2 (Level Designer & AI Programmer):
Thiết lập thuật toán "Spawning" (cooldown giảm dần theo `elapsed`, speed/hp multiplier tăng theo level + thời gian).
Lập trình 3 phase của Boss: bắn đơn homing, bắn tỏa 5 tia `sin/cos`, triệu hồi minion; chuyển pha theo tỉ lệ HP.
Thành viên 3 (Technical Artist & UI):
Thiết kế HUD: thanh trái tim theo PLAYER_MAX_HP, SCORE/HI góc phải, đồng hồ đếm ngược hoặc `LEVEL x BOSS y/3` giữa, chỉ báo Triple Shot & Shield dưới đáy; thanh HP boss có nhãn PHASE đổi màu xanh → vàng → đỏ.
Tìm kiếm và chuẩn hóa asset (Kenney), sinh thêm vài sprite bằng `generate_assets.py` / `generate_airplanes.py` nếu cần.

4. R - Realistic (Tính thực tế: Đối mặt với giới hạn)
Đây là phần quan trọng nhất để dự án không trở thành "bom xịt". Chúng ta cần thực tế hóa các tham vọng:
Thực tế về Gameplay: Thay vì làm 5–10 màn chơi khác nhau (tốn thời gian vẽ map), dùng **01 nền starfield parallax cuộn vô tận** (2 lớp sao: 90 sao xa chậm + 45 sao gần nhanh). Độ khó được điều chỉnh qua code: `speed_mult = 1 + elapsed/220 + (level-1)*0.15`, `spawn_cd = max(450, 1200 - elapsed*4)`.
Thực tế về Đồ họa: Không tự vẽ tay — dùng **Kenney Space Shooter Extension** (thư mục `shooter_assets/kenney_space-shooter-extension`) làm nguồn chính để mọi sprite cùng phong cách, tránh "râu ông nọ cắm cằm bà kia". Enemy/boss sprite flip dọc để hướng xuống.
Thực tế về Tính năng: Bỏ qua chơi mạng (Online) và đăng nhập tài khoản. Tập trung 100% vào cảm giác "súng có lực": screen shake 7 khi trúng đạn, shake 22 khi boss chết, shake 14/16 khi boss xuất hiện; cảnh báo "! BOSS INCOMING !" 8 giây trước khi boss tới trong Campaign.

5. T - Time-bound (Thời hạn: Lộ trình 21 ngày chi tiết)
Tuần 1: Khởi tạo và Cơ chế gốc (The Foundation)
Ngày 1-2: Thiết lập môi trường PyGame, tạo cửa sổ $800 \times 720$ (tối ưu cho laptop — kể cả màn 1366×768 khi trừ taskbar vẫn hiển thị trọn vẹn), code logic di chuyển nhân vật chính (8 hướng, chuẩn hóa chéo) không lỗi.
Ngày 3-5: Xây dựng hệ thống đạn auto-fire (cooldown 200ms) và Triple Shot 3 tia. Triển khai `Bullet.update()` tự kill khi ra khỏi màn.
Ngày 6-7: Tạo Scout và Interceptor, va chạm sơ bộ bằng `rect.colliderect`. Cuối tuần phải có bản "Tech Demo" (máy bay bắn nổ các khối vuông/sprite tạm).
Tuần 2: Hình ảnh và Sự đa dạng (The Content)
Ngày 8-10: Thay đồ họa tạm bằng sprite Kenney thật, thêm Explosion 5 frame, starfield 2 lớp parallax, screen shake.
Ngày 11-12: Lập trình 3 Power-up (Blue Crystal / Red Heart / Golden Shield), drop rate 18% từ quái thường, drop chắc chắn cả 3 khi hạ boss.
Ngày 13-14: Thiết kế Boss Mother Ship: chuyển động qua lại, 3 phase bắn theo HP%, triệu hồi minion ở phase 3, thanh máu + nhãn phase đổi màu.
Tuần 3: Đánh bóng và Xuất bản (The Masterpiece)
Ngày 15-17: Menu chính + Menu chọn chế độ (Time Attack 5/10 phút, Campaign), Game Over / Pause overlay, high score persist `highscore.json`, chèn âm thanh (cấu trúc `assets/sounds` đã sẵn).
Ngày 18-19: Playtest & Bug Fixing ít nhất 50 ván để tìm lỗi logic (ví dụ: boss chết nhưng đạn của nó vẫn còn trong `enemy_bullets`; power-up không kill khi rơi quá màn).
Ngày 20: Tối ưu dung lượng, viết `README.md` hướng dẫn cài đặt và chơi.
Ngày 21: Đóng gói sản phẩm thành file thực thi `.exe` (PyInstaller). Thuyết trình dự án trước nhóm/lớp.
