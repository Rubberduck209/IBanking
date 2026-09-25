import asyncio
import httpx
import time

# Cấu hình API của Tuition Service (Đảm bảo service đang chạy ở port 8001)
API_URL = "http://127.0.0.1:8001/api/tuitions/TDTU24001/status"
PAYLOAD = {"status_": "Đã thanh toán"}

async def fire_request(client, req_id):
    print(f"🚀 Luồng {req_id} đang gửi request...")
    
    # Gửi request PUT
    response = await client.put(API_URL, json=PAYLOAD)
    
    # In kết quả trả về
    print(f"[{req_id}] Kết quả: HTTP {response.status_code} - {response.json()}")

async def main():
    print("Bắt đầu kiểm thử Concurrency (5 luồng đồng thời)...")
    start_time = time.time()
    
    # Khởi tạo Async Client để bắn request song song
    async with httpx.AsyncClient() as client:
        # Tạo danh sách 5 tác vụ
        tasks = [fire_request(client, i) for i in range(1, 6)]
        
        # asyncio.gather sẽ kích hoạt cả 5 request chạy cùng 1 tích tắc
        await asyncio.gather(*tasks)
        
    print(f"Hoàn thành trong {time.time() - start_time:.3f} giây.")

if __name__ == "__main__":
    asyncio.run(main())