import streamlit as st
import urllib.parse
from datetime import datetime
import csv
import io
import json
import gspread
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
        "package": "Select Package",
        "people": "Number of People",
        "date": "Preferred Date",
        "pickup": "I need Free Pick-up & Drop-off in Kuşadası",
        "hotel": "Hotel Name / Address (Leave blank if no pick-up needed)",
        "notes": "Special Requests (Allergies, pressure preference, etc.)",
        "btn_save": "Save Reservation Details",
        "err_name": "Please enter your Full Name.",
        "err_hotel": "Please provide your Hotel Name so we can arrange your driver.",
        "success": "Details saved successfully",
        "wa_link": "👉 Click here to send these details to our WhatsApp and confirm your booking!",
        "wa_greet": "Hello Maximum Hamam! I would like to confirm my booking:",
        "wa_id": "Reservation ID",
        "wa_name": "Name",
        "wa_pack": "Package",
        "wa_ppl": "People",
        "wa_date": "Date",
        "wa_pick": "Pick-up Hotel",
        "wa_notes": "Notes"
    },
    "🇹🇷 Türkçe": {
        "title": "Maximum Hamam & Spa",
        "sub": "Kuşadası'nda Lüks Türk Hamamı Rezervasyonu",
        "desc": "Rezervasyon talebiniz için lütfen aşağıdaki formu doldurun. WhatsApp üzerinden onaylayacağız.",
        "name": "Adınız ve Soyadınız *",
        "package": "Paket Seçin",
        "people": "Kişi Sayısı",
        "date": "Tercih Edilen Tarih",
        "pickup": "Kuşadası içi ücretsiz servis (Pick-up) istiyorum",
        "hotel": "Otel Adı / Adresi (Servis istemiyorsanız boş bırakın)",
        "notes": "Özel İstekleriniz (Alerji, masaj sertlik tercihi vb.)",
        "btn_save": "Rezervasyon Bilgilerini Kaydet",
        "err_name": "Lütfen Adınızı ve Soyadınızı giriniz.",
        "err_hotel": "Şoförümüzün sizi alabilmesi için lütfen Otel Adını giriniz.",
        "success": "Bilgiler başarıyla kaydedildi",
        "wa_link": "👉 Rezervasyonunuzu onaylamak ve bilgileri WhatsApp'tan göndermek için buraya tıklayın!",
        "wa_greet": "Merhaba Maximum Hamam! Rezervasyonumu onaylamak istiyorum:",
        "wa_id": "Rezervasyon No",
        "wa_name": "İsim",
        "wa_pack": "Paket",
        "wa_ppl": "Kişi",
        "wa_date": "Tarih",
        "wa_pick": "Alınacak Otel",
        "wa_notes": "Notlar"
    },
    "🇩🇪 Deutsch": {
        "title": "Maximum Hamam & Spa",
        "sub": "Luxuriöse Türkische Bad-Reservierung in Kuşadası",
        "desc": "Bitte füllen Sie das untenstehende Formular aus. Wir werden es über WhatsApp bestätigen.",
        "name": "Vollständiger Name *",
        "package": "Paket auswählen",
        "people": "Anzahl der Personen",
        "date": "Bevorzugtes Datum",
        "pickup": "Ich benötige eine kostenlose Abholung in Kuşadası",
        "hotel": "Hotelname / Adresse (Leer lassen, falls keine Abholung benötigt wird)",
        "notes": "Spezielle Wünsche (Allergien, Druckpräferenz usw.)",
        "btn_save": "Reservierungsdetails speichern",
        "err_name": "Bitte geben Sie Ihren vollständigen Namen ein.",
        "err_hotel": "Bitte geben Sie Ihren Hotelnamen an, damit wir den Fahrer arrangieren können.",
        "success": "Details erfolgreich gespeichert",
        "wa_link": "👉 Klicken Sie hier, um diese Details an unser WhatsApp zu senden und zu bestätigen!",
        "wa_greet": "Hallo Maximum Hamam! Ich möchte meine Buchung bestätigen:",
        "wa_id": "Reservierungs-ID",
        "wa_name": "Name",
        "wa_pack": "Paket",
        "wa_ppl": "Personen",
        "wa_date": "Datum",
        "wa_pick": "Abholhotel",
        "wa_notes": "Notizen"
    },
    "🇳🇱 Dutch": {
        "title": "Maximum Hamam & Spa",
        "sub": "Luxe Turks Bad Reservering in Kuşadası",
        "desc": "Vul het onderstaande formulier in om uw reservering aan te vragen. Wij bevestigen via WhatsApp.",
        "name": "Volledige Naam *",
        "package": "Selecteer Pakket",
        "people": "Aantal Personen",
        "date": "Voorkeursdatum",
        "pickup": "Ik heb gratis ophaalservice nodig in Kuşadası",
        "hotel": "Hotelnaam / Adres (Laat leeg als er geen ophaalservice nodig is)",
        "notes": "Speciale Verzoeken (Allergieën, drukvoorkeur, enz.)",
        "btn_save": "Reserveringsgegevens Opslaan",
        "err_name": "Vul alstublieft uw volledige naam in.",
        "err_hotel": "Geef uw hotelnaam op zodat we uw chauffeur kunnen regelen.",
        "success": "Gegevens succesvol opgeslagen",
        "wa_link": "👉 Klik hier om deze details naar onze WhatsApp te sturen en uw boeking te bevestigen!",
        "wa_greet": "Hallo Maximum Hamam! Ik wil graag mijn boeking bevestigen:",
        "wa_id": "Reserverings-ID",
        "wa_name": "Naam",
        "wa_pack": "Pakket",
        "wa_ppl": "Personen",
        "wa_date": "Datum",
        "wa_pick": "Ophaalhotel",
        "wa_notes": "Opmerkingen"
    },
    "🇧🇪 Vlaams (Flemenkçe)": {
        "title": "Maximum Hamam & Spa",
        "sub": "Luxe Turks Bad Reservatie in Kuşadası",
        "desc": "Vul het onderstaande formulier in om uw reservatie aan te vragen. Wij bevestigen via WhatsApp.",
        "name": "Volledige Naam *",
        "package": "Selecteer Pakket",
        "people": "Aantal Personen",
        "date": "Voorkeursdatum",
        "pickup": "Ik heb gratis ophaalservice nodig in Kuşadası",
        "hotel": "Hotelnaam / Adres (Laat leeg als er geen ophaalservice nodig is)",
        "notes": "Speciale Verzoeken (Allergieën, drukvoorkeur, enz.)",
        "btn_save": "Reservatiegegevens Opslaan",
        "err_name": "Vul alstublieft uw volledige naam in.",
        "err_hotel": "Geef uw hotelnaam op zodat we uw chauffeur kunnen regelen.",
        "success": "Gegevens succesvol opgeslagen",
        "wa_link": "👉 Klik hier om deze details naar onze WhatsApp te sturen en uw boeking te bevestigen!",
        "wa_greet": "Hallo Maximum Hamam! Ik wil graag mijn boeking bevestigen:",
        "wa_id": "Reservatie-ID",
        "wa_name": "Naam",
        "wa_pack": "Pakket",
        "wa_ppl": "Personen",
        "wa_date": "Datum",
        "wa_pick": "Ophaalhotel",
        "wa_notes": "Opmerkingen"
    },
    "🇫🇷 Français": {
        "title": "Maximum Hamam & Spa",
        "sub": "Réservation de Bain Turc de Luxe à Kuşadası",
        "desc": "Veuillez remplir le formulaire ci-dessous. Nous confirmerons via WhatsApp.",
        "name": "Nom Complet *",
        "package": "Sélectionner le Forfait",
        "people": "Nombre de Personnes",
        "date": "Date Préférée",
        "pickup": "J'ai besoin d'une navette gratuite à Kuşadası",
        "hotel": "Nom / Adresse de l'Hôtel (Laissez vide si non nécessaire)",
        "notes": "Demandes Spéciales (Allergies, préférence de pression, etc.)",
        "btn_save": "Enregistrer les Détails",
        "err_name": "Veuillez entrer votre nom complet.",
        "err_hotel": "Veuillez indiquer le nom de votre hôtel pour le chauffeur.",
        "success": "Détails enregistrés avec succès",
        "wa_link": "👉 Cliquez ici pour envoyer ces détails sur notre WhatsApp et confirmer!",
        "wa_greet": "Bonjour Maximum Hamam! Je souhaite confirmer ma réservation:",
        "wa_id": "ID de Réservation",
        "wa_name": "Nom",
        "wa_pack": "Forfait",
        "wa_ppl": "Personnes",
        "wa_date": "Date",
        "wa_pick": "Hôtel de ramassage",
        "wa_notes": "Notes"
    },
    "🇸🇪 Svenska": {
        "title": "Maximum Hamam & Spa",
        "sub": "Bokning av Lyxigt Turkiskt Bad i Kuşadası",
        "desc": "Vänligen fyll i formuläret nedan för att begära din bokning. Vi bekräftar via WhatsApp.",
        "name": "Fullständigt Namn *",
        "package": "Välj Paket",
        "people": "Antal Personer",
        "date": "Önskat Datum",
        "pickup": "Jag behöver gratis upphämtning i Kuşadası",
        "hotel": "Hotellnamn / Adress (Lämna tomt om upphämtning ej behövs)",
        "notes": "Särskilda Önskemål (Allergier, tryckpreferens, etc.)",
        "btn_save": "Spara Bokningsdetaljer",
        "err_name": "Vänligen ange ditt fullständiga namn.",
        "err_hotel": "Vänligen ange ditt hotellnamn så vi kan ordna en chaufför.",
        "success": "Detaljer sparade framgångsrikt",
        "wa_link": "👉 Klicka här för att skicka dessa detaljer till vår WhatsApp och bekräfta!",
        "wa_greet": "Hej Maximum Hamam! Jag vill bekräfta min bokning:",
        "wa_id": "Boknings-ID",
        "wa_name": "Namn",
        "wa_pack": "Paket",
        "wa_ppl": "Personer",
        "wa_date": "Datum",
        "wa_pick": "Upphämtningshotell",
        "wa_notes": "Anteckningar"
    }
}

# ==========================================
# 1. GOOGLE SHEETS DATABASE FUNCTIONS
# ==========================================

# Performansı artırmak için Google Sheets bağlantısını hafızada tutuyoruz
@st.cache_resource
def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # İnternetteyken (Streamlit Cloud)
        creds_dict = json.loads(st.secrets["gcp_service_account"])
    except Exception:
        # Bilgisayarınızdayken (Local)
        with open("credentials.json", "r", encoding="utf-8") as f:
            creds_dict = json.load(f)
            
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    sheet = gc.open("Maximum_Hamam_DB").sheet1
    return sheet

def init_db():
    sheet = get_sheet()
    # Eğer tablo bomboşsa başlıkları otomatik olarak en üste yaz
    if len(sheet.get_all_values()) == 0:
        headers = ['id', 'name', 'package', 'people', 'date', 'hotel', 'notes', 'timestamp', 'status']
        sheet.append_row(headers)

def add_booking(name, package, people, date, hotel, notes):
    sheet = get_sheet()
    records = sheet.get_all_records()
    
    # Yeni Sıra Numarası (ID) Hesaplama
    if not records:
        new_id = 1
    else:
        ids = [int(r['id']) for r in records if str(r.get('id', '')).isdigit()]
        new_id = max(ids) + 1 if ids else 1
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = 'Bekliyor'
    
    new_row = [new_id, name, package, people, str(date), hotel, notes, timestamp, status]
    sheet.append_row(new_row)
    return new_id

def view_all_bookings(status_filter="Tümü"):
    sheet = get_sheet()
    records = sheet.get_all_records()
    
    if status_filter != "Tümü":
        records = [r for r in records if r.get('status') == status_filter]
        
    # En yeni rezervasyonlar tablonun en üstünde görünsün
    records.reverse()
    
    columns = ['id', 'name', 'package', 'people', 'date', 'hotel', 'notes', 'timestamp', 'status']
    rows = [[r.get(c, "") for c in columns] for r in records]
    
    return records, columns, rows

def update_booking(booking_id, name, package, people, date, hotel, notes, status):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for i, row in enumerate(records):
        if str(row['id']) == str(booking_id):
            row_idx = i + 2 # +1 başlıklar için, +1 de index 0'dan başladığı için
            updated_row = [booking_id, name, package, people, str(date), hotel, notes, row['timestamp'], status]
            sheet.update(values=[updated_row], range_name=f"A{row_idx}:I{row_idx}")
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

init_db()

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
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LANGUAGE SELECTOR (TOP RIGHT)
# ==========================================
col_empty, col_lang = st.columns([8, 2])
with col_lang:
    selected_lang = st.selectbox(
        "Language", 
        options=list(LANGUAGES.keys()), 
        index=0, 
        label_visibility="collapsed"
    )

t = LANGUAGES[selected_lang]
t_en = LANGUAGES["🇬🇧 English"]

# ==========================================
# 4. SAYFA GÖRÜNÜMLERİ (FUNCTIONS)
# ==========================================

# A. Müşteri Rezervasyon Sayfası İçeriği
def view_booking_page():
    st.title(t["title"])
    st.subheader(t["sub"])
    st.write(t["desc"])
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(t["name"])
            package = st.selectbox(t["package"], [
                "Just Facility Use - 40€", "Traditional Turkish Bath - 50€", 
                "Express Journey - 85€", "Recovery Journey - 150€", 
                "Lux Turkish Bath - 70€", "Relax Journey - 110€", 
                "Luxury Mix - 125€", "Sultan Journey - 200€"
            ])
        with col2:
            people = st.number_input(t["people"], min_value=1, max_value=10)
            date = st.date_input(t["date"])
        
        pickup_needed = st.checkbox(t["pickup"])
        hotel = st.text_input(t["hotel"])
        notes = st.text_area(t["notes"])
        
        submit = st.form_submit_button(t["btn_save"])
        
        if submit:
            if not name:
                st.error(t["err_name"])
            elif pickup_needed and not hotel:
                st.error(t["err_hotel"])
            else:
                booking_id = add_booking(name, package, people, date, hotel, notes)
                st.success(f"{t['success']}, {name}! (ID: #{booking_id})")
                
                business_phone = "905396690127"
                
                msg_local = f"{t['wa_greet']}\n"
                msg_local += f"{t['wa_id']}: #{booking_id}\n"
                msg_local += f"{t['wa_name']}: {name}\n"
                msg_local += f"{t['wa_pack']}: {package}\n"
                msg_local += f"{t['wa_ppl']}: {people}\n"
                msg_local += f"{t['wa_date']}: {date}\n"
                if hotel:
                    msg_local += f"{t['wa_pick']}: {hotel}\n"
                if notes:
                    msg_local += f"{t['wa_notes']}: {notes}\n"
                
                final_msg = msg_local 
                
                if selected_lang != "🇬🇧 English":
                    msg_eng = f"\n--- ENGLISH ---\n{t_en['wa_greet']}\n"
                    msg_eng += f"Reservation ID: #{booking_id}\n"
                    msg_eng += f"Name: {name}\n"
                    msg_eng += f"Package: {package}\n"
                    msg_eng += f"People: {people}\n"
                    msg_eng += f"Date: {date}\n"
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
    st.title("Maximum Hamam & Spa")
    st.subheader("Yönetici Paneli (Admin Dashboard)")
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "volkanAdmin":
        st.success("Sisteme başarıyla giriş yapıldı.")
        
        st.write("### 📊 Rezervasyon Özeti")
        counts = get_status_counts()
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("⏳ Bekleyen", counts.get("Bekliyor", 0))
        m2.metric("✅ Onaylanan", counts.get("Onaylandı", 0))
        m3.metric("🚶‍♂️ Gelen", counts.get("Geldi", 0))
        m4.metric("❌ Gelmeyen", counts.get("Gelmedi", 0))
        m5.metric("🚫 İptal Edilen", counts.get("İptal", 0))
        
        st.divider() 
        
        st.write("### 📋 Rezervasyon Listesi")
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
                    label="📥 Listeyi CSV Olarak İndir",
                    data=csv_data,
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

            event = st.dataframe(
                data, 
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            current_table_selection = event.selection.rows
            if current_table_selection != st.session_state.prev_table_selection:
                if current_table_selection:
                    selected_id_from_table = data[current_table_selection[0]]["id"]
                    st.session_state.admin_selectbox = selected_id_from_table
                else:
                    st.session_state.admin_selectbox = "Seçiniz..."
                st.session_state.prev_table_selection = current_table_selection
            
            st.divider()
            
            st.write("### ⚙️ Rezervasyon Yönetim Konsolu")
            st.write("Değişiklik yapmak istediğiniz rezervasyonu **yukarıdaki tablodan tıklayarak** veya **aşağıdaki listeden** seçebilirsiniz.")
            
            available_ids = [row["id"] for row in data]
            dropdown_options = ["Seçiniz..."] + available_ids
            
            if st.session_state.admin_selectbox not in dropdown_options:
                st.session_state.admin_selectbox = "Seçiniz..."
                
            selected_id = st.selectbox(
                "İşlem Yapılacak ID Seçin:", 
                dropdown_options, 
                key="admin_selectbox"
            )
            
            if selected_id != "Seçiniz...":
                selected_data = next((item for item in data if item["id"] == selected_id), None)
                
                with st.form("edit_form"):
                    st.write(f"**ID: #{selected_id} Düzenleniyor**")
                    status_options = ["Bekliyor", "Onaylandı", "Geldi", "Gelmedi", "İptal"]
                    new_status = st.selectbox("Durum *", status_options, index=status_options.index(selected_data["status"]))
                    
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        new_name = st.text_input("Müşteri Adı", value=selected_data["name"])
                        new_package = st.selectbox("Paket", [
                            "Just Facility Use - 40€", "Traditional Turkish Bath - 50€", 
                            "Express Journey - 85€", "Recovery Journey - 150€", 
                            "Lux Turkish Bath - 70€", "Relax Journey - 110€", 
                            "Luxury Mix - 125€", "Sultan Journey - 200€"
                        ], index=0 if selected_data["package"] not in [
                            "Just Facility Use - 40€", "Traditional Turkish Bath - 50€", 
                            "Express Journey - 85€", "Recovery Journey - 150€", 
                            "Lux Turkish Bath - 70€", "Relax Journey - 110€", 
                            "Luxury Mix - 125€", "Sultan Journey - 200€"
                        ] else [
                            "Just Facility Use - 40€", "Traditional Turkish Bath - 50€", 
                            "Express Journey - 85€", "Recovery Journey - 150€", 
                            "Lux Turkish Bath - 70€", "Relax Journey - 110€", 
                            "Luxury Mix - 125€", "Sultan Journey - 200€"
                        ].index(selected_data["package"]))
                        new_people = st.number_input("Kişi Sayısı", min_value=1, value=int(selected_data["people"]))
                    
                    with col_e2:
                        try:
                            parsed_date = datetime.strptime(selected_data["date"], "%Y-%m-%d").date()
                        except:
                            parsed_date = datetime.now().date()
                            
                        new_date = st.date_input("Tarih", value=parsed_date)
                        new_hotel = st.text_input("Otel/Transfer", value=selected_data["hotel"])
                        new_notes = st.text_area("Notlar", value=selected_data["notes"])
                    
                    col_upd, col_del = st.columns(2)
                    with col_upd:
                        btn_update = st.form_submit_button("💾 Değişiklikleri Kaydet")
                    with col_del:
                        btn_delete = st.form_submit_button("🗑️ Bu Rezervasyonu Sil")
                        
                if btn_update:
                    update_booking(selected_id, new_name, new_package, new_people, new_date, new_hotel, new_notes, new_status)
                    st.success(f"ID #{selected_id} başarıyla güncellendi!")
                    st.rerun() 
                    
                if btn_delete:
                    delete_booking(selected_id)
                    st.warning(f"ID #{selected_id} sistemden tamamen silindi!")
                    st.session_state.admin_selectbox = "Seçiniz..."
                    st.rerun() 

    elif password != "":
        st.error("Hatalı Şifre.")

# ==========================================
# 5. SAYFA YÖNLENDİRİCİSİ (NAVIGATION SİSTEMİ)
# ==========================================

# Müşteri sayfasının "Ana Sayfa (Default)" olduğunu belirtiyoruz
page_customer = st.Page(view_booking_page, title="Book a Session", default=True)

# Admin sayfasının /admin adresinde olduğunu belirtiyoruz
page_admin = st.Page(view_admin_page, title="Admin Dashboard", url_path="admin")

# Sayfaları çalıştırıyoruz (position="hidden" sayesinde sol menü TAMAMEN GİZLENİR)
pg = st.navigation([page_customer, page_admin], position="hidden")
pg.run()
