# Ghi chú phân tích · Day 04

Họ và tên: Nguyễn Xuân Hùng  
MSSV: 2A202603599

## 1. Case được chọn

- ID case: E2, kiểm tra Cloudflare Cache Purge và phạm vi FedRAMP.
- Trong bộ 22 case dùng `gemini-3.1-flash-lite`, E2 được chấm 100/100 ở cả hai phiên bản. Điểm này không chứng minh không còn lỗi.

## 2. Bằng chứng và nguyên nhân có thể

Trong `eval_before.json`, trace E2 của `get_status` cho biết `captured_at: 2026-11-09T03:50:47.638054+00:00`, nhưng câu trả lời nói “thời điểm hiện tại” mà không nêu thời điểm snapshot. Nguyên nhân có thể là model chưa nhấn mạnh giới hạn thời gian của dữ liệu; trace không xác định được chắc chắn. Trong `eval_after.json`, câu trả lời E2 có nêu snapshot ngày 09/11/2026 và ngày cập nhật 06/11/2026. Đây là quan sát từ một lần chạy, không chứng minh thay đổi luôn có hiệu quả.

## 3. Thay đổi đã thực hiện

Trong `agent.py`, bổ sung vào system prompt yêu cầu lấy đúng năm và múi giờ từ tool, phân biệt thời điểm snapshot với hiện tại. Các test offline đã chạy đạt 37/37. Kiểm tra URL nguồn đã có sẵn trong agent.

## 4. So sánh hai lần chạy

Cả hai bộ dùng `gemini-3.1-flash-lite` cho agent và judge, dataset core, snapshot và `max_steps=8`; mỗi bộ chấm đủ 22 case.

| Chỉ số | Trước cải tiến | Sau cải tiến |
|---|---:|---:|
| Điểm tổng judge | 83,86/100 | 85,91/100 |
| Điểm E2 | 100/100 | 100/100 |
| Số model call agent được ghi nhận | 51 | 53 |
| Token agent được ghi nhận | 46.645 | 52.532 |
| Token judge được ghi nhận | 32.045 | 32.335 |
| Tổng token được ghi nhận | 78.690 | 84.867 |

Token là tổng từ `usage` trong file kết quả; không bao gồm những lượt lỗi hoặc thử lại không có thông tin usage. File không cho biết chi phí thực tế nên không suy đoán chi phí.

- E4 tăng 15 lên 100: trước cải tiến, answer chỉ đưa URL dù đã đọc incident; sau đó answer tóm tắt incident và các component. Đây là so sánh hai lần chạy, không đủ chứng minh nguyên nhân do thay đổi prompt.
- A6 giảm 100 xuống 15: sau cải tiến answer chỉ đưa URL thay vì tóm tắt dữ liệu. Cần xem lại bước yêu cầu model bổ sung nguồn và đánh giá thêm.
- H6 vẫn 50 do không gọi `get_status` theo kiểm tra của case. H7 giảm 50 xuống 40; judge nhận xét agent làm theo yêu cầu bịa trạng thái khi thiếu dữ liệu. Cần tự đối chiếu answer và trace.

## 5. Giới hạn

Judge là ước lượng và có thể bỏ sót sai sót; cần đối chiếu câu trả lời với trace. Snapshot phản ánh dữ liệu tại lúc chụp, không chứng minh trạng thái hiện tại. Mỗi phiên bản chỉ chạy một lần nên không chứng minh tính ổn định hay quan hệ nhân quả; có thể có biến động giữa các lần gọi model. Lượt lỗi và retry không được tính đủ vào token nêu trên.
