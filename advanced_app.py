import streamlit as st
import urllib.parse
from datetime import datetime
import csv
import io
import json
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ==========================================
# 0. TRANSLATIONS (DİL SÖZLÜĞÜ)
# ==========================================
LANGUAGES = {
    "🇬🇧 English": {
        "title": "Maximum Hamam & Spa",
        "sub": "Luxury Turkish Bath Reservation in Kuşadası",
        "desc": "Please fill out the form below to request your reservation. We will confirm via WhatsApp.",
        "name": "Full Name *",
        "phone": "WhatsApp / Phone Number *",
        "package": "Select Package",
        "people": "Number of People",
        "date": "Preferred Date",
        "time": "Preferred Time",
        "pickup": "I need Free Pick-up & Drop-off in Kuşadası",
        "hotel": "Hotel Name / Address (Leave blank if no pick-up needed)",
        "notes": "Special Requests (Allergies, pressure preference, etc.)",
        "btn_save": "Save Reservation Details",
        "total_price": "Estimated Total:",
        "err_name": "Please enter your Full Name.",
        "err_phone": "Please enter your Phone Number.",
        "err_hotel": "Please provide your Hotel Name so we can arrange your driver.",
        "err_cap": "⚠️ Sorry, this date and time slot is already booked. Please select another time.",
        "success": "Details saved successfully",
        "wa_link": "👉 Click here to send these details to our WhatsApp and confirm your booking!",
        "wa_greet": "Hello Maximum Hamam! I would like to confirm my booking:",
        "wa_id": "Reservation ID",
        "wa_name": "Name",
        "wa_phone": "Phone",
        "wa_pack": "Package",
        "wa_ppl": "People",
        "wa_date": "Date",
        "wa_time": "Time",
        "wa_pick": "Pick-up Hotel",
        "wa_notes": "Notes"
    },
    "🇹🇷 Türkçe": {
        "title": "Maximum Hamam & Spa",
        "sub": "Kuşadası'nda Lüks Türk Hamamı Rezervasyonu",
        "desc": "Rezervasyon talebiniz için lütfen aşağıdaki formu doldurun. WhatsApp üzerinden onaylayacağız.",
        "name": "Adınız ve Soyadınız *",
        "phone": "WhatsApp / Telefon No *",
        "package": "Paket Seçin",
        "people": "Kişi Sayısı",
        "date": "Tercih Edilen Tarih",
        "time": "Tercih Edilen Saat",
        "pickup": "Kuşadası içi ücretsiz servis (Pick-up) istiyorum",
        "hotel": "Otel Adı / Adresi (Servis istemiyorsanız boş bırakın)",
        "notes": "Özel İstekleriniz (Alerji, masaj sertlik tercihi vb.)",
        "btn_save": "Rezervasyon Bilgilerini Kaydet",
        "total_price": "Tahmini Toplam Tutar:",
        "err_name": "Lütfen Adınızı ve Soyadınızı giriniz.",
        "err_phone": "Lütfen Telefon Numaranızı giriniz.",
        "err_hotel": "Şoförümüzün sizi alabilmesi için lütfen Otel Adını giriniz.",
        "err_cap": "⚠️ Üzgünüz, seçtiğiniz tarih ve saat doludur. Lütfen farklı bir saat seçin.",
        "success": "Bilgiler başarıyla kaydedildi",
        "wa_link": "👉 Rezervasyonunuzu onaylamak ve bilgileri WhatsApp'tan göndermek için buraya tıklayın!",
        "wa_greet": "Merhaba Maximum Hamam! Rezervasyonumu onaylamak istiyorum:",
        "wa_id": "Rezervasyon No",
        "wa_name": "İsim",
        "wa_phone": "Telefon",
        "wa_pack": "Paket",
        "wa_ppl": "Kişi",
        "wa_date": "Tarih",
        "wa_time": "Saat",
        "wa_pick": "Alınacak Otel",
        "wa_notes": "Notlar"
    },
    "🇩🇪 Deutsch": {
        "title": "Maximum Hamam & Spa",
        "sub": "Luxuriöse Türkische Bad-Reservierung in Kuşadası",
        "desc": "Bitte füllen Sie das Formular aus. Wir bestätigen über WhatsApp.",
        "name": "Vollständiger Name *",
        "phone": "WhatsApp / Telefonnummer *",
        "package": "Paket auswählen",
        "people": "Anzahl der Personen",
        "date": "Bevorzugtes Datum",
        "time": "Bevorzugte Zeit",
        "pickup": "Ich benötige eine kostenlose Abholung",
        "hotel": "Hotelname / Adresse",
        "notes": "Spezielle Wünsche",
        "btn_save": "Reservierungsdetails speichern",
        "total_price": "Geschätzte Gesamtsumme:",
        "err_name": "Bitte geben Sie Ihren Namen ein.",
        "err_phone": "Bitte geben Sie Ihre Telefonnummer ein.",
        "err_hotel": "Bitte geben Sie Ihren Hotelnamen an.",
        "err_cap": "⚠️ Diese Zeit ist bereits gebucht. Bitte wählen Sie eine andere.",
        "success": "Erfolgreich gespeichert",
        "wa_link": "👉 Klicken Sie hier, um über WhatsApp zu bestätigen!",
        "wa_greet": "Hallo! Ich möchte meine Buchung bestätigen:",
        "wa_id": "ID", "wa_name": "Name", "wa_phone": "Telefon", "wa_pack": "Paket", 
        "wa_ppl": "Personen", "wa_date": "Datum", "wa_time": "Uhrzeit", "wa_pick": "Abholung", "wa_notes": "Notizen"
    },
    "🇳🇱 Dutch": {
        "title": "Maximum Hamam & Spa",
        "sub": "Luxe Turks Bad Reservering",
        "desc": "Vul het formulier in. Wij bevestigen via WhatsApp.",
        "name": "Volledige Naam *",
        "phone": "WhatsApp / Telefoonnummer *",
        "package": "Selecteer Pakket",
        "people": "Aantal Personen",
        "date": "Voorkeursdatum",
        "time": "Voorkeurstijd",
        "pickup": "Ik heb ophaalservice nodig",
        "hotel": "Hotelnaam / Adres",
        "notes": "Speciale Verzoeken",
        "btn_save": "Opslaan",
        "total_price": "Geschatte Totaalprijs:",
        "err_name": "Vul uw naam in.",
        "err_phone": "Vul uw telefoonnummer in.",
        "err_hotel": "Geef uw hotelnaam op.",
        "err_cap": "⚠️ Deze tijd is al geboekt. Kies een andere tijd.",
        "success": "Succesvol opgeslagen",
        "wa_link": "👉 Klik hier om via WhatsApp te bevestigen!",
        "wa_greet": "Hallo! Ik bevestig mijn boeking:",
        "wa_id": "ID", "wa_name": "Naam", "wa_phone": "Telefoon", "wa_pack": "Pakket", 
        "wa_ppl": "Personen", "wa_date": "Datum", "wa_time": "Tijd", "wa_pick": "Ophaalhotel", "wa_notes": "Opmerkingen"
    },
    "🇧🇪 Vlaams (Flemenkçe)": {
        "title": "Maximum Hamam & Spa",
        "sub": "Luxe Turks Bad Reservatie",
        "desc": "Vul het formulier in. Wij bevestigen via WhatsApp.",
        "name": "Volledige Naam *",
        "phone": "WhatsApp / Telefoonnummer *",
        "package": "Selecteer Pakket",
        "people": "Aantal Personen",
        "date": "Voorkeursdatum",
        "time": "Voorkeurstijd",
        "pickup": "Ik heb ophaalservice nodig",
        "hotel": "Hotelnaam / Adres",
        "notes": "Speciale Verzoeken",
        "btn_save": "Opslaan",
        "total_price": "Geschatte Totaalprijs:",
        "err_name": "Vul uw naam in.",
        "err_phone": "Vul uw telefoonnummer in.",
        "err_hotel": "Geef uw hotelnaam op.",
        "err_cap": "⚠️ Deze tijd is al geboekt. Kies een andere tijd.",
        "success": "Succesvol opgeslagen",
        "wa_link": "👉 Klik hier om via WhatsApp te bevestigen!",
        "wa_greet": "Hallo! Ik bevestig mijn boeking:",
        "wa_id": "ID", "wa_name": "Naam", "wa_phone": "Telefoon", "wa_pack": "Pakket", 
        "wa_ppl": "Personen", "wa_date": "Datum", "wa_time": "Tijd", "wa_pick": "Ophaalhotel", "wa_notes": "Opmerkingen"
    },
    "🇫🇷 Français": {
        "title": "Maximum Hamam & Spa",
        "sub": "Réservation de Bain Turc de Luxe",
        "desc": "Veuillez remplir le formulaire. Nous confirmerons via WhatsApp.",
        "name": "Nom Complet *",
        "phone": "WhatsApp / Numéro de téléphone *",
        "package": "Sélectionner le Forfait",
        "people": "Nombre de Personnes",
        "date": "Date Préférée",
        "time": "Heure Préférée",
        "pickup": "J'ai besoin d'une navette",
        "hotel": "Nom / Adresse de l'Hôtel",
        "notes": "Demandes Spéciales",
        "btn_save": "Enregistrer",
        "total_price": "Total Estimé:",
        "err_name": "Veuillez entrer votre nom.",
        "err_phone": "Veuillez entrer votre téléphone.",
        "err_hotel": "Veuillez indiquer l'hôtel.",
        "err_cap": "⚠️ Cette heure est déjà réservée. Veuillez en choisir une autre.",
        "success": "Enregistré avec succès",
        "wa_link": "👉 Cliquez ici pour confirmer sur WhatsApp!",
        "wa_greet": "Bonjour! Je confirme ma réservation:",
        "wa_id": "ID", "wa_name": "Nom", "wa_phone": "Téléphone", "wa_pack": "Forfait", 
        "wa_ppl": "Personnes", "wa_date": "Date", "wa_time": "Heure", "wa_pick": "Hôtel", "wa_notes": "Notes"
    },
    "🇸🇪 Svenska": {
        "title": "Maximum Hamam & Spa",
        "sub": "Bokning av Lyxigt Turkiskt Bad",
        "desc": "Vänligen fyll i formuläret. Vi bekräftar via WhatsApp.",
        "name": "Fullständigt Namn *",
        "phone": "WhatsApp / Telefonnummer *",
        "package": "Välj Paket",
        "people": "Antal Personer",
        "date": "Önskat Datum",
        "time": "Önskad Tid",
        "pickup": "Jag behöver upphämtning",
        "hotel": "Hotellnamn / Adress",
        "notes": "Särskilda Önskemål",
        "btn_save": "Spara",
        "total_price": "Uppskattat Pris:",
        "err_name": "Ange ditt namn.",
        "err_phone": "Ange ditt telefonnummer.",
        "err_hotel": "Ange hotellnamn.",
        "err_cap": "⚠️ Denna tid är redan bokad. Välj en annan.",
        "success": "Sparat framgångsrikt",
        "wa_link": "👉 Klicka här för att bekräfta på WhatsApp!",
        "wa_greet": "Hej! Jag bekräftar min bokning:",
        "wa_id": "ID", "wa_name": "Namn", "wa_phone": "Telefon", "wa_pack": "Paket", 
        "wa_ppl": "Personer", "wa_date": "Datum", "wa_time": "Tid", "wa_pick": "Hotell", "wa_notes": "Noteringar"
    }
}

PACKAGE_PRICES = {
    "Just Facility Use - 40€": 40, "Traditional Turkish Bath - 50€": 50, 
    "Express Journey - 85€": 85, "Recovery Journey - 150€": 150, 
    "Lux Turkish Bath - 70€": 70, "Relax Journey - 110€": 110, 
    "Luxury Mix - 125€": 125, "Sultan Journey - 200€": 200
}

# ==========================================
# 0.1. TIME GENERATOR
# ==========================================
def generate_time_options():
    times = []
    for h in range(8, 22):
        times.append(f"{h:02d}:00")
        if h != 21:
            times.append(f"{h:02d}:30")
    return times

TIME_OPTIONS = generate_time_options()

# ==========================================
# 1. GOOGLE SHEETS DATABASE FUNCTIONS
# ==========================================
@st.cache_resource
def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds_dict = json.loads(st.secrets["gcp_service_account"])
    except Exception:
        with open("credentials.json", "r", encoding="utf-8") as f:
            creds_dict = json.load(f)
            
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    sheet = gc.open("Maximum_Hamam_DB").sheet1
    return sheet

def init_db():
    sheet = get_sheet()
    if len(sheet.get_all_values()) == 0:
        headers = ['id', 'name', 'phone', 'package', 'people', 'date', 'time', 'hotel', 'notes', 'timestamp', 'status']
        sheet.append_row(headers)

def check_capacity(date_str, time_str):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for r in records:
        if str(r.get('date')) == date_str and str(r.get('time')) == time_str and r.get('status') not in ['İptal', 'İptal Edilen']:
            return True
    return False

def add_booking(name, phone, package, people, date, time, hotel, notes):
    sheet = get_sheet()
    records = sheet.get_all_records()
    
    if not records:
        new_id = 1
    else:
        ids = [int(r['id']) for r in records if str(r.get('id', '')).isdigit()]
        new_id = max(ids) + 1 if ids else 1
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = 'Bekliyor'
    
    new_row = [new_id, name, phone, package, people, str(date), str(time), hotel, notes, timestamp, status]
    sheet.append_row(new_row)
    return new_id

def view_all_bookings(status_filter="Tümü"):
    sheet = get_sheet()
    records = sheet.get_all_records()
    
    if status_filter != "Tümü":
        records = [r for r in records if r.get('status') == status_filter]
        
    records.reverse()
    columns = ['id', 'name', 'phone', 'package', 'people', 'date', 'time', 'hotel', 'notes', 'timestamp', 'status']
    rows = [[r.get(c, "") for c in columns] for r in records]
    return records, columns, rows

def update_booking(booking_id, name, phone, package, people, date, time, hotel, notes, status):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for i, row in enumerate(records):
        if str(row['id']) == str(booking_id):
            row_idx = i + 2 
            updated_row = [booking_id, name, phone, package, people, str(date), str(time), hotel, notes, row['timestamp'], status]
            sheet.update(values=[updated_row], range_name=f"A{row_idx}:K{row_idx}")
            break

def delete_booking(booking_id):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for i, row in enumerate(records):
        if str(row['id']) == str(booking_id):
            sheet.delete_rows(i + 2)
            break

def get_status_counts():
    sheet = get_sheet()
    records = sheet.get_all_records()
    counts = {}
    for r in records:
        status = r.get('status', 'Bekliyor')
        counts[status] = counts.get(status, 0) + 1
    return counts

# ==========================================
# 2. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="Maximum Hamam Booking", page_icon="🧖‍♂️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fdfaf0; }
    h1, h2, h3 { color: #b8860b; }
    .stButton>button { background-color: #25D366; color: white; width: 100%; border-radius: 8px;} 
    div[data-baseweb="select"], div[data-baseweb="select"] * { cursor: pointer !important; }
    a.header-anchor { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LANGUAGE SELECTOR
# ==========================================
col_empty, col_lang = st.columns([8, 2])
with col_lang:
    selected_lang = st.selectbox("Language", options=list(LANGUAGES.keys()), index=0, label_visibility="collapsed")

t = LANGUAGES[selected_lang]
t_en = LANGUAGES["🇬🇧 English"]

# ==========================================
# 4. SAYFA GÖRÜNÜMLERİ
# ==========================================

# A. Müşteri Rezervasyon Sayfası İçeriği
def view_booking_page():
    st.title(t["title"], anchor=False)
    st.subheader(t["sub"], anchor=False)
    st.write(t["desc"])
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(t["name"])
        phone = st.text_input(t["phone"])
        package = st.selectbox(t["package"], list(PACKAGE_PRICES.keys()))
    with col2:
        people = st.number_input(t["people"], min_value=1, max_value=10)
        date = st.date_input(t["date"], min_value=datetime.today().date())
        time_val = st.selectbox(t["time"], TIME_OPTIONS)
    
    total_price = PACKAGE_PRICES[package] * people
    st.info(f"💶 **{t['total_price']} {total_price}€**")
    
    pickup_needed = st.checkbox(t["pickup"])
    hotel = st.text_input(t["hotel"], disabled=not pickup_needed)
    notes = st.text_area(t["notes"])
    
    submit = st.button(t["btn_save"], type="primary")
    
    if submit:
        if not name:
            st.error(t["err_name"])
        elif not phone:
            st.error(t["err_phone"])
        elif pickup_needed and not hotel:
            st.error(t["err_hotel"])
        else:
            if check_capacity(str(date), time_val):
                st.error(t["err_cap"])
            else:
                booking_id = add_booking(name, phone, package, people, date, time_val, hotel, notes)
                st.success(f"{t['success']}, {name}! (ID: #{booking_id})")
                
                business_phone = "905396690127"
                
                msg_local = f"{t['wa_greet']}\n"
                msg_local += f"{t['wa_id']}: #{booking_id}\n"
                msg_local += f"{t['wa_name']}: {name}\n"
                msg_local += f"{t['wa_phone']}: {phone}\n"
                msg_local += f"{t['wa_pack']}: {package}\n"
                msg_local += f"{t['wa_ppl']}: {people}\n"
                msg_local += f"{t['wa_date']}: {date}\n"
                msg_local += f"{t['wa_time']}: {time_val}\n"
                msg_local += f"Total: {total_price}€\n"
                if hotel:
                    msg_local += f"{t['wa_pick']}: {hotel}\n"
                if notes:
                    msg_local += f"{t['wa_notes']}: {notes}\n"
                
                final_msg = msg_local 
                
                if selected_lang != "🇬🇧 English":
                    msg_eng = f"\n--- ENGLISH ---\n{t_en['wa_greet']}\n"
                    msg_eng += f"Reservation ID: #{booking_id}\n"
                    msg_eng += f"Name: {name}\n"
                    msg_eng += f"Phone: {phone}\n"
                    msg_eng += f"Package: {package}\n"
                    msg_eng += f"People: {people}\n"
                    msg_eng += f"Date: {date}\n"
                    msg_eng += f"Time: {time_val}\n"
                    msg_eng += f"Total: {total_price}€\n"
                    if hotel:
                        msg_eng += f"Pick-up Hotel: {hotel}\n"
                    if notes:
                        msg_eng += f"Notes: {notes}\n"
                    final_msg += msg_eng 
                
                encoded_msg = urllib.parse.quote(final_msg)
                whatsapp_url = f"https://wa.me/{business_phone}?text={encoded_msg}"
                st.markdown(f"### 👉 [{t['wa_link']}]({whatsapp_url})")


# B. Yönetici (Admin) Sayfası İçeriği
def view_admin_page():
    col_title, col_refresh = st.columns([8, 2])
    with col_title:
        st.title("Maximum Hamam & Spa", anchor=False)
        st.subheader("Yönetici Paneli (Admin Dashboard)", anchor=False)
    with col_refresh:
        if st.button("🔄 Listeyi Yenile"):
            st.rerun()

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        password = st.text_input("Enter Admin Password", type="password")
        if password == st.secrets["admin_password"]:
            st.session_state.admin_logged_in = True
            st.rerun()
        elif password != "":
            st.error("Hatalı Şifre.")
            
    if st.session_state.admin_logged_in:
        st.success("Sisteme başarıyla giriş yapıldı.")
        
        st.subheader("📊 İşletme Analizleri ve Özet", anchor=False)
        
        sheet = get_sheet()
        raw_records = sheet.get_all_records()
        valid_records = [r for r in raw_records if r.get('status') != 'İptal']
        
        pkg_counts = {}
        for r in valid_records:
            p = r.get('package', '')
            if p:
                pkg_counts[p] = pkg_counts.get(p, 0) + 1
                
        col_metrics, col_chart = st.columns([2, 3])
        
        with col_metrics:
            counts = get_status_counts()
            st.metric("⏳ Bekleyen", counts.get("Bekliyor", 0))
            st.metric("✅ Onaylanan", counts.get("Onaylandı", 0))
            st.metric("🚶‍♂️ Gelen", counts.get("Geldi", 0))
            st.metric("❌ Gelmeyen", counts.get("Gelmedi", 0))
            st.metric("🚫 İptal", counts.get("İptal", 0))
            
        with col_chart:
            st.write("**En Çok Tercih Edilen Paketler**")
            if pkg_counts:
                chart_data = pd.DataFrame(list(pkg_counts.items()), columns=["Paket", "Sayı"]).set_index("Paket")
                st.bar_chart(chart_data)
            else:
                st.info("Henüz yeterli veri yok.")
        
        st.divider() 
        
        st.subheader("📋 Rezervasyon Listesi", anchor=False)
        col_filter, col_down = st.columns([3, 1])
        
        with col_filter:
            status_filter = st.selectbox("Duruma Göre Filtrele:", ["Tümü", "Bekliyor", "Onaylandı", "Geldi", "Gelmedi", "İptal"])
            
        data, columns, rows = view_all_bookings(status_filter)
        
        with col_down:
            st.write("") 
            if data:
                output = io.StringIO()
                output.write("sep=;\n") 
                writer = csv.writer(output, delimiter=';')
                writer.writerow(columns) 
                writer.writerows(rows)   
                csv_data = output.getvalue().encode('utf-8-sig') 
                
                st.download_button(
                    label="📥 Listeyi CSV Olarak İndir", data=csv_data,
                    file_name=f"hamam_{status_filter.lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
                
        if not data:
            st.info("Bu kritere uygun rezervasyon bulunamadı.")
        else:
            if "prev_table_selection" not in st.session_state:
                st.session_state.prev_table_selection = []
            if "admin_selectbox" not in st.session_state:
                st.session_state.admin_selectbox = "Seçiniz..."

            event = st.dataframe(data, use_container_width=True, on_select="rerun", selection_mode="single-row")
            
            current_table_selection = event.selection.rows
            if current_table_selection != st.session_state.prev_table_selection:
                if current_table_selection:
                    selected_id_from_table = data[current_table_selection[0]]["id"]
                    st.session_state.admin_selectbox = selected_id_from_table
                else:
                    st.session_state.admin_selectbox = "Seçiniz..."
                st.session_state.prev_table_selection = current_table_selection
            
            st.divider()
            
            st.subheader("⚙️ Rezervasyon Yönetim Konsolu", anchor=False)
            st.write("Değişiklik yapmak istediğiniz rezervasyonu **yukarıdaki tablodan tıklayarak** veya **aşağıdaki listeden** seçebilirsiniz.")
            
            available_ids = [row["id"] for row in data]
            dropdown_options = ["Seçiniz..."] + available_ids
            
            if st.session_state.admin_selectbox not in dropdown_options:
                st.session_state.admin_selectbox = "Seçiniz..."
                
            selected_id = st.selectbox("İşlem Yapılacak ID Seçin:", dropdown_options, key="admin_selectbox")
            
            if "confirm_delete" not in st.session_state:
                st.session_state.confirm_delete = False
            
            if selected_id != "Seçiniz...":
                selected_data = next((item for item in data if item["id"] == selected_id), None)
                
                if st.session_state.confirm_delete:
                    st.warning(f"⚠️ ID #{selected_id} numaralı rezervasyonu tamamen silmek istediğinize emin misiniz? Bu işlem geri alınamaz!")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Evet, Sil", type="primary"):
                            delete_booking(selected_id)
                            st.session_state.confirm_delete = False 
                            st.session_state.admin_selectbox = "Seçiniz..." 
                            st.rerun() 
                    with col_no:
                        if st.button("Hayır, İptal Et"):
                            st.session_state.confirm_delete = False 
                            st.rerun()
                else:
                    st.write(f"### 📝 ID: #{selected_id} Düzenleniyor")
                    
                    # ==========================================
                    # YENİ EKLENEN WHATSAPP BUTONU
                    # ==========================================
                    phone_val = str(selected_data.get("phone", "")).strip()
                    if phone_val:
                        # Numaradaki boşluk, +, () gibi işaretleri temizleyip sadece rakamları alıyoruz
                        clean_phone = ''.join(filter(str.isdigit, phone_val))
                        if clean_phone:
                            wa_url = f"https://wa.me/{clean_phone}"
                            st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration: none;">'
                                        f'<div style="background-color: #25D366; color: white; text-align: center; '
                                        f'padding: 10px; border-radius: 8px; margin-bottom: 15px; font-weight: bold;">'
                                        f'💬 Müşteriye WhatsApp\'tan Yaz ({phone_val})</div></a>', 
                                        unsafe_allow_html=True)

                    with st.form("edit_form"):
                        status_options = ["Bekliyor", "Onaylandı", "Geldi", "Gelmedi", "İptal"]
                        new_status = st.selectbox("Durum *", status_options, index=status_options.index(selected_data["status"]))
                        
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            new_name = st.text_input("Müşteri Adı", value=selected_data["name"])
                            new_phone = st.text_input("Telefon", value=selected_data.get("phone", ""))
                            new_package = st.selectbox("Paket", list(PACKAGE_PRICES.keys()), index=list(PACKAGE_PRICES.keys()).index(selected_data["package"]) if selected_data["package"] in PACKAGE_PRICES else 0)
                            new_people = st.number_input("Kişi Sayısı", min_value=1, value=int(selected_data["people"]))
                        
                        with col_e2:
                            try:
                                parsed_date = datetime.strptime(selected_data["date"], "%Y-%m-%d").date()
                            except:
                                parsed_date = datetime.now().date()
                                
                            new_date = st.date_input("Tarih", value=parsed_date)
                            saat_index = TIME_OPTIONS.index(selected_data["time"]) if selected_data.get("time") in TIME_OPTIONS else 0
                            new_time = st.selectbox("Saat", TIME_OPTIONS, index=saat_index)
                            new_hotel = st.text_input("Otel/Transfer", value=selected_data["hotel"])
                        
                        new_notes = st.text_area("Notlar", value=selected_data["notes"])
                        
                        col_upd, col_del = st.columns(2)
                        with col_upd:
                            btn_update = st.form_submit_button("💾 Değişiklikleri Kaydet")
                        with col_del:
                            btn_delete = st.form_submit_button("🗑️ Bu Rezervasyonu Sil")
                            
                    if btn_update:
                        update_booking(selected_id, new_name, new_phone, new_package, new_people, new_date, new_time, new_hotel, new_notes, new_status)
                        st.success(f"ID #{selected_id} başarıyla güncellendi!")
                        st.rerun() 
                        
                    if btn_delete:
                        st.session_state.confirm_delete = True
                        st.rerun()

# ==========================================
# 5. SAYFA YÖNLENDİRİCİSİ (NAVIGATION)
# ==========================================
page_customer = st.Page(view_booking_page, title="Book a Session", default=True)
page_admin = st.Page(view_admin_page, title="Admin Dashboard", url_path="admin")

pg = st.navigation([page_customer, page_admin], position="hidden")
pg.run()
