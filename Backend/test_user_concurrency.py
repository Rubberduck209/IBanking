import asyncio
import httpx
import time

# ================= CẤU HÌNH =================
# Sửa lại port nếu User Service của bạn chạy port khác
API_URL = "http://127.0.0.1:8000/users/me/deduct" 

# BẮT BUỘC: Dán access_token của 'nguyenvana' vào đây
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZ3V5ZW52YW5hIiwidXNlcl9pZCI6MSwiZXhwIjoxNzkwMzExNDc0fQ.i0kHB3cjYi_8E-MmX_CdziHduG4EM_RQARujajBcOyw" 

# Số tiền muốn trừ (10 triệu)
PAYLOAD = {"amount": 10000000.00} 
# ============================================

async def fire_request(client, req_id):
    print(f"🚀 Luồng {req_id} đang gửi lệnh trừ tiền...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Gửi request POST
    response = await client.post(API_URL, json=PAYLOAD, headers=headers)
    print(f"[{req_id}] HTTP {response.status_code} - {response.json()}")

async def main():
    print("Bắt đầu kiểm thử: 5 luồng cùng trừ 10 triệu từ tài khoản có 15 triệu...")
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        # Bắn 5 request cùng lúc
        tasks = [fire_request(client, i) for i in range(1, 6)]
        await asyncio.gather(*tasks)
        
    print(f"Hoàn thành trong {time.time() - start_time:.3f} giây.")

if __name__ == "__main__":
    asyncio.run(main())