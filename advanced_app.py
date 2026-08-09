# ==========================================
# 0.1. ZAMAN FONKSİYONLARI
# ==========================================
def get_turkey_time():
    return datetime.utcnow() + timedelta(hours=3)

def get_full_time_options():
    times = []
    for h in range(9, 22): # Saat 9'dan başlıyoruz
        for m in ["00", "30"]:
            if h == 9 and m == "00": 
                continue # 09:00'ı atla, doğrudan 09:30'dan başlasın
            if h == 21 and m == "30":
                continue # 21:30'u atla, son saat 21:00 olsun
            times.append(f"{h:02d}:{m}")
    return times

FULL_TIME_OPTIONS = get_full_time_options()

def generate_dynamic_time_options(selected_date):
    times = []
    now_tr = get_turkey_time()
    
    is_today = (selected_date == now_tr.date())
    current_time_str = now_tr.strftime("%H:%M")
    
    for h in range(9, 22): # Saat 9'dan başlıyoruz
        for m in ["00", "30"]:
            if h == 9 and m == "00":
                continue # 09:00'ı atla
            if h == 21 and m == "30":
                continue # 21:30'u atla
                
            time_str = f"{h:02d}:{m}"
            
            if is_today:
                if time_str > current_time_str:
                    times.append(time_str)
            else:
                times.append(time_str)
                
    return times
