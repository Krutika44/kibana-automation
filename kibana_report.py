import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from reportlab.pdfgen import canvas
from PIL import Image
from datetime import datetime
 
load_dotenv()
 
# ================= CONFIG =================
 
BASE_URL = os.getenv("KIBANA_BASE_URL")
USERNAME = os.getenv("KIBANA_USERNAME")
PASSWORD = os.getenv("KIBANA_PASSWORD")
 
if not BASE_URL:
    raise Exception("KIBANA_BASE_URL not set in .env")
 
LOGIN_URL = f"{BASE_URL}/login"
 
VIEWPORT = {"width": 1920, "height": 1080}
 
business_units = ['mat', 'mfr', 'mch', 'icibe', 'icinl', 'tps', 'wtctr']
 
dashboard_map = {
    "mat": "f55df050-19d8-11f0-abd4-2db2b9242c8f",
    "mfr": "f55df050-19d8-11f0-abd4-2db2b9242c8f",
    "icibe": "f55df050-19d8-11f0-abd4-2db2b9242c8f",
    "icinl": "f55df050-19d8-11f0-abd4-2db2b9242c8f",
    "wtctr": "f55df050-19d8-11f0-abd4-2db2b9242c8f",
    "tps": "b7539a70-c933-11f0-abd4-2db2b9242c8f",
    "mch": "34bfacd0-c932-11f0-abd4-2db2b9242c8f",
}
 
def get_dashboard_url(space):
    return f"{BASE_URL}/s/{space}/app/kibana#/dashboard/{dashboard_map[space]}?_g=(time:(from:now-24h,to:now))"
 
# ================= MAIN =================
 
screenshots = []
 
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # set True later for scheduler
    context = browser.new_context(viewport=VIEWPORT)
    page = context.new_page()
 
    print("🔐 Opening Kibana login page...")
    page.goto(LOGIN_URL, wait_until="load")
    time.sleep(85)
 
    print("🧑‍💻 Logging in...")
    time.sleep(85)
    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
 
    time.sleep(85)
 
    for bu in business_units:
        print(f"📊 Capturing {bu.upper()}")
        page.goto(get_dashboard_url(bu), wait_until="load")
        time.sleep(30)
 
        screenshot_file = f"dashboard_{bu}.png"
        page.screenshot(path=screenshot_file, full_page=True)
        screenshots.append((bu, screenshot_file))
 
    browser.close()
 
# ================= PDF =================
 
today = datetime.now().strftime("%Y-%m-%d")
pdf_name = f"All_BU_Dashboards_{today}.pdf"
 
# 🔽 CHANGE THIS PATH TO YOUR **OneDrive SYNCED FOLDER**
ONEDRIVE_FOLDER = r"C:\Users\KRSHARAD\OneDrive - Capgemini\Desktop\Krutika\Kibana Report"
 
os.makedirs(ONEDRIVE_FOLDER, exist_ok=True)
pdf_path = os.path.join(ONEDRIVE_FOLDER, pdf_name)
 
c = canvas.Canvas(pdf_path)
 
for bu, img_path in screenshots:
    img = Image.open(img_path)
    width, height = img.size
 
    c.setPageSize((width, height + 50))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height + 20, f"{bu.upper()} DASHBOARD")
    c.drawImage(img_path, 0, 0, width=width, height=height)
    c.showPage()
 
c.save()
 
print("📄 PDF saved to OneDrive:", pdf_path)
