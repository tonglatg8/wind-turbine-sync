import os
import sys
import requests
import time
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------
# กำหนด Timezone เวลาประเทศไทย (UTC+7)
# ---------------------------------------------------------
THAI_TZ = timezone(timedelta(hours=7))

# ---------------------------------------------------------
# 1. ตั้งค่า Configuration (ดึงค่าปลอดภัยผ่าน GitHub Secrets)
# ---------------------------------------------------------
GREENBYTE_TOKEN = os.getenv("GREENBYTE_TOKEN")
MAINTAINX_TOKEN = os.getenv("MAINTAINX_TOKEN")

# ตรวจสอบว่ามี API Token หรือไม่ ถ้าไม่มีให้หยุดรันและแจ้ง Error ทันที
if not GREENBYTE_TOKEN or not MAINTAINX_TOKEN:
    print("[CRITICAL ERROR] Missing GREENBYTE_TOKEN or MAINTAINX_TOKEN in Secrets!")
    sys.exit(1)

# ข้อมูลจับคู่ กังหันทั้งหมด 90 ต้น (FKW 45 ต้น + KR2 45 ต้น)
TURBINE_MAPPING = {
    # --- โครงการ FKW (45 ต้น) ---
    "146": {"name": "FKW-01B", "mx_id": "20645430"},
    "147": {"name": "FKW-02B", "mx_id": "20645432"},
    "148": {"name": "FKW-03B", "mx_id": "20645433"},
    "149": {"name": "FKW-04B", "mx_id": "20645434"},
    "150": {"name": "FKW-05B", "mx_id": "20645435"},
    "151": {"name": "FKW-06B", "mx_id": "20645436"},
    "152": {"name": "FKW-07B", "mx_id": "20645437"},
    "153": {"name": "FKW-08B", "mx_id": "20645438"},
    "154": {"name": "FKW-09B", "mx_id": "20645439"},
    "155": {"name": "FKW-10B", "mx_id": "20645440"},
    "156": {"name": "FKW-11B", "mx_id": "20645441"},
    "157": {"name": "FKW-12B", "mx_id": "20645442"},
    "158": {"name": "FKW-13B", "mx_id": "20645443"},
    "159": {"name": "FKW-14B", "mx_id": "20645444"},
    "160": {"name": "FKW-15B", "mx_id": "20645445"},
    "161": {"name": "FKW-16B", "mx_id": "20645446"},
    "162": {"name": "FKW-17B", "mx_id": "20645447"},
    "163": {"name": "FKW-18B", "mx_id": "20645448"},
    "164": {"name": "FKW-19B", "mx_id": "20645449"},
    "165": {"name": "FKW-20B", "mx_id": "20645450"},
    "166": {"name": "FKW-21B", "mx_id": "20645451"},
    "167": {"name": "FKW-22B", "mx_id": "20645452"},
    "168": {"name": "FKW-23B", "mx_id": "20645453"},
    "169": {"name": "FKW-24B", "mx_id": "20645454"},
    "170": {"name": "FKW-25B", "mx_id": "20645455"},
    "171": {"name": "FKW-26B", "mx_id": "20645456"},
    "172": {"name": "FKW-27B", "mx_id": "20645457"},
    "173": {"name": "FKW-28B", "mx_id": "20645458"},
    "174": {"name": "FKW-29B", "mx_id": "20645459"},
    "175": {"name": "FKW-30B", "mx_id": "20645460"},
    "176": {"name": "FKW-31B", "mx_id": "20645461"},
    "177": {"name": "FKW-32B", "mx_id": "20645462"},
    "178": {"name": "FKW-33B", "mx_id": "20645463"},
    "179": {"name": "FKW-34B", "mx_id": "20645464"},
    "180": {"name": "FKW-35B", "mx_id": "20645465"},
    "181": {"name": "FKW-36B", "mx_id": "20645466"},
    "182": {"name": "FKW-37B", "mx_id": "20645467"},
    "183": {"name": "FKW-38B", "mx_id": "20645468"},
    "184": {"name": "FKW-39B", "mx_id": "20645469"},
    "185": {"name": "FKW-40B", "mx_id": "20645470"},
    "186": {"name": "FKW-41B", "mx_id": "20645471"},
    "187": {"name": "FKW-42B", "mx_id": "20645472"},
    "188": {"name": "FKW-43B", "mx_id": "20645473"},
    "189": {"name": "FKW-44B", "mx_id": "20645474"},
    "190": {"name": "FKW-45B", "mx_id": "20645475"},
    
    # --- โครงการ KR2 (45 ต้น) ---
    "196": {"name": "KR2-01A", "mx_id": "20645477"},
    "197": {"name": "KR2-02A", "mx_id": "20645478"},
    "198": {"name": "KR2-03A", "mx_id": "20645479"},
    "199": {"name": "KR2-04A", "mx_id": "20645480"},
    "200": {"name": "KR2-05A", "mx_id": "20645481"},
    "201": {"name": "KR2-06A", "mx_id": "20645482"},
    "202": {"name": "KR2-07A", "mx_id": "20645483"},
    "203": {"name": "KR2-08A", "mx_id": "20645484"},
    "204": {"name": "KR2-09A", "mx_id": "20645485"},
    "205": {"name": "KR2-10A", "mx_id": "20645486"},
    "206": {"name": "KR2-11A", "mx_id": "20645487"},
    "207": {"name": "KR2-12A", "mx_id": "20645488"},
    "208": {"name": "KR2-13A", "mx_id": "20645489"},
    "209": {"name": "KR2-14A", "mx_id": "20645490"},
    "210": {"name": "KR2-15A", "mx_id": "20645491"},
    "211": {"name": "KR2-16A", "mx_id": "20645492"},
    "212": {"name": "KR2-17A", "mx_id": "20645493"},
    "213": {"name": "KR2-18A", "mx_id": "20645494"},
    "214": {"name": "KR2-19A", "mx_id": "20645495"},
    "215": {"name": "KR2-20A", "mx_id": "20645496"},
    "216": {"name": "KR2-21A", "mx_id": "20645497"},
    "217": {"name": "KR2-22A", "mx_id": "20645498"},
    "218": {"name": "KR2-23A", "mx_id": "20645499"},
    "219": {"name": "KR2-24A", "mx_id": "20645500"},
    "220": {"name": "KR2-25A", "mx_id": "20645501"},
    "221": {"name": "KR2-26A", "mx_id": "20645502"},
    "222": {"name": "KR2-27A", "mx_id": "20645503"},
    "223": {"name": "KR2-28A", "mx_id": "20645504"},
    "224": {"name": "KR2-29A", "mx_id": "20645505"},
    "225": {"name": "KR2-30A", "mx_id": "20645506"},
    "226": {"name": "KR2-31A", "mx_id": "20645507"},
    "227": {"name": "KR2-32A", "mx_id": "20645508"},
    "228": {"name": "KR2-33A", "mx_id": "20645509"},
    "229": {"name": "KR2-34A", "mx_id": "20645510"},
    "230": {"name": "KR2-35A", "mx_id": "20645511"},
    "231": {"name": "KR2-36A", "mx_id": "20645512"},
    "232": {"name": "KR2-37A", "mx_id": "20645513"},
    "233": {"name": "KR2-38A", "mx_id": "20645514"},
    "234": {"name": "KR2-39A", "mx_id": "20645515"},
    "235": {"name": "KR2-40A", "mx_id": "20645516"},
    "236": {"name": "KR2-41A", "mx_id": "20645517"},
    "237": {"name": "KR2-42A", "mx_id": "20645518"},
    "238": {"name": "KR2-43A", "mx_id": "20645519"},
    "239": {"name": "KR2-44A", "mx_id": "20645520"},
    "240": {"name": "KR2-45A", "mx_id": "20645521"}
}

# ---------------------------------------------------------
# 2. ฟังก์ชันเรียก API
# ---------------------------------------------------------
def get_latest_greenbyte_data(device_id):
    now = datetime.now(THAI_TZ)
    past_30_mins = now - timedelta(minutes=30)
    
    timestamp_start = past_30_mins.strftime("%Y-%m-%dT%H:%M:%S")
    timestamp_end = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    url = "https://weh.greenbyte.cloud/api/2/data"
    headers = {"x-api-key": GREENBYTE_TOKEN, "Content-Type": "application/json"}
    params = {
        "DeviceIds": device_id,
        "DataSignalIds": "1,5,80",  # 1=Wind, 5=Power, 80=Blade Angle A
        "TimestampStart": timestamp_start,
        "TimestampEnd": timestamp_end
    }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json()
        elif res.status_code in [401, 403]:
            print(f"   [CRITICAL ERROR] Greenbyte API Unauthorized (Status {res.status_code})")
            return "AUTH_ERROR"
    except Exception as e:
        print(f"   [Error] Greenbyte Connection failed: {e}")
    return None

def get_current_maintainx_status(asset_id):
    url = f"https://api.getmaintainx.com/v1/assets/{asset_id}"
    headers = {"Authorization": f"Bearer {MAINTAINX_TOKEN}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json().get("asset", {}).get("status", {}).get("status")
    except Exception:
        pass
    return None

def switch_maintainx_realtime(asset_id, status_name):
    url = f"https://api.getmaintainx.com/v1/assets/{asset_id}/status"
    headers = {
        "Authorization": f"Bearer {MAINTAINX_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"status": status_name}
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        if res.status_code in [200, 201]:
            print(f"   --> [SUCCESS] MaintainX -> {status_name}")
        else:
            print(f"   --> [ERROR] Switch failed: {res.text}")
    except Exception:
        pass

# ---------------------------------------------------------
# 3. ลอจิกหลัก (ตรวจสอบกังหัน 1 รอบ)
# ---------------------------------------------------------
def run_realtime_sync():
    print(f"\n=== Start Check: {datetime.now(THAI_TZ).strftime('%Y-%m-%d %H:%M:%S')} (TH Local Time) ===")
    
    error_count = 0
    total_turbines = len(TURBINE_MAPPING)
    
    for gb_id, info in TURBINE_MAPPING.items():
        turbine_name = info["name"]
        mx_id = info["mx_id"]
        
        print(f"--- Turbine {turbine_name} [GB: {gb_id} | MX: {mx_id}] ---")
        
        gb_data = get_latest_greenbyte_data(gb_id)
        
        if gb_data == "AUTH_ERROR":
            print("[CRITICAL] Greenbyte Token Invalid! Stopping script...")
            sys.exit(1)
            
        if gb_data is None: 
            print("   -> Connection error, skip...\n")
            error_count += 1
            continue

        power_data = {}
        wind_data = {}
        pitch_data = {}
        
        for item in gb_data:
            signal_id = item.get("dataSignal", {}).get("dataSignalId")
            if signal_id == 5:
                power_data = item.get("data", {})
            elif signal_id == 1:
                wind_data = item.get("data", {})
            elif signal_id == 80:
                pitch_data = item.get("data", {})

        valid_power_ts = sorted([ts for ts, val in power_data.items() if val is not None])
        valid_wind_ts = sorted([ts for ts, val in wind_data.items() if val is not None])
        valid_pitch_ts = sorted([ts for ts, val in pitch_data.items() if val is not None])

        if not valid_power_ts or not valid_wind_ts or not valid_pitch_ts:
            print("   -> Data is null -> Force OFFLINE")
            target_status = "OFFLINE"
            print("   - Power: N/A | Wind: N/A | Pitch: N/A")
        else:
            latest_p_ts = valid_power_ts[-1]
            latest_w_ts = valid_wind_ts[-1]
            latest_pitch_ts = valid_pitch_ts[-1]

            p_val = float(power_data[latest_p_ts])
            w_val = float(wind_data[latest_w_ts])
            pitch_val = float(pitch_data[latest_pitch_ts])
            
            # ลอจิกตัดสินสถานะ:
            # - Pitch Angle < 50 deg แสดงถึงใบพัดอยู่ในองศาทำงาน (ONLINE หากลมต่ำและไม่ผลิตไฟ)
            # - OFFLINE เมื่อ Power < 10 kW ร่วมกับ (Wind >= 3 m/s OR Pitch Angle >= 50 deg)
            target_status = "OFFLINE" if (p_val < 10 and (w_val >= 3 or pitch_val >= 50)) else "ONLINE"
            print(f"   - Power: {p_val:.1f} kW | Wind: {w_val:.1f} m/s | Pitch: {pitch_val:.1f}°")
            
        print(f"   - Target Status: {target_status}")
        actual_status = get_current_maintainx_status(mx_id)
        print(f"   - Current Status: {actual_status}")
        
        if target_status != actual_status:
            print("   -> Status changed! Switching MaintainX...")
            switch_maintainx_realtime(mx_id, target_status)
        else:
            print("   -> Status matched, skip API")
        
        print("") 
        time.sleep(0.5)

    if error_count == total_turbines:
        print("[CRITICAL ERROR] Failed to fetch data for ALL turbines!")
        sys.exit(1)

if __name__ == "__main__":
    print(f"=== Auto-Sync Start for {len(TURBINE_MAPPING)} Turbines ===")
    run_realtime_sync()
    print("=== Sync Completed ===")
