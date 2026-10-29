import os
import re
import json
import time
import hashlib
from datetime import datetime, timezone
from urllib.parse import quote_plus
import requests

# Konfigurasi Environment Variables dari GitHub Secrets / Vars
AMAZON_TAG = os.environ.get("AMAZON_TAG", "aegisdomus-20").strip()
SITE_URL = os.environ.get("SITE_URL", "https://username.github.io/aegisdomus-us").rstrip("/")
REPO_NAME = os.environ.get("GITHUB_REPOSITORY", "user/aegisdomus-us")

# Kunci verifikasi IndexNow deterministik untuk Bing, Yahoo, Yandex, DuckDuckGo
INDEXNOW_KEY = hashlib.md5(f"{REPO_NAME}_{AMAZON_TAG}_aegis12h".encode("utf-8")).hexdigest()

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "aegis_state.json")
IMAGE_CACHE_FILE = os.path.join(DATA_DIR, "security_image_cache.json")
DOCS_DIR = "docs"
PRODUCTS_DIR = os.path.join(DOCS_DIR, "products")
REVIEWS_DIR = os.path.join(DOCS_DIR, "reviews")
CATEGORIES_DIR = os.path.join(DOCS_DIR, "categories")

HEADERS = {
    "User-Agent": "AegisDomusSecuritySEO/2.0 (https://github.com; security-storefront@github.com)"
}

# Taksonomi Spesialis Smart Home & Security Tech (6 Kategori Utama, 18 Subkategori)
TAXONOMY = [
    {
        "category": "Perimeter & Outdoor Cameras",
        "cat_slug": "perimeter-outdoor-cameras",
        "icon": "📹",
        "subcategories": [
            {
                "name": "4K Dual-Lens Solar PTZ Cameras",
                "slug": "4k-dual-lens-solar-ptz-cameras",
                "img_q": "security camera outdoor surveillance",
                "brands": ["eufy Security", "Reolink", "Arlo", "TP-Link Tapo", "AosU"],
                "models": ["SoloCam S340 Dual-Lens 360° Solar", "TrackMix Wi-Fi / LTE Solar 4K PTZ", "Ultra 2 4K Spotlight Solar Kit", "C660KIT Solar Pan-Tilt 4K AI", "SolarCam D1 Max 360° Auto-Track"],
                "specs": {
                    "Optical System": "Dual-Lens Wide + Telephoto 8x Hybrid Zoom (4K UHD)",
                    "Power Architecture": "High-Efficiency Detachable Solar Panel + 10,000mAh Battery",
                    "Local Storage": "Built-in eMMC / MicroSD up to 512GB (Zero Monthly Cloud Fee)",
                    "Smart Detection": "On-Device AI Human, Vehicle & Pet Motion Lock"
                },
                "buy_if": "You want 360-degree driveway and yard surveillance with license-plate zoom clarity and zero wiring or monthly subscription fees.",
                "skip_if": "You need 24/7 continuous high-bitrate recording to a central rack-mounted NVR (choose a wired PoE system instead)."
            },
            {
                "name": "PoE NVR Multi-Camera Kits",
                "slug": "poe-nvr-multi-camera-security-kits",
                "img_q": "cctv camera system building",
                "brands": ["Reolink", "Lorex", "Annke", "Amcrest", "Ubiquiti UniFi"],
                "models": ["RLK8-800D4 / RLK16-1200D8 12MP PoE System", "Fusion 4K+ 16-Channel 4TB NVR Bundle", "H800 4K PoE ColorVu 8-Cam Turret Kit", "NV4108E-A2 4K 8CH PoE Dome System", "Protect G5 Pro 4K PoE Vision Suite"],
                "specs": {
                    "Resolution & Frame Rate": "4K (8MP) to 12MP Ultra-HD @ 25–30 FPS",
                    "Cabling & Power": "Single-Cable Cat6 Power-over-Ethernet (IEEE 802.3af/at)",
                    "NVR Pre-Installed Drive": "2TB to 4TB Surveillance-Grade SATA HDD (Expandable to 16TB)",
                    "Night Vision": "Color Night Vision with F1.6 Aperture + IR Cut Filter"
                },
                "buy_if": "You want unjammable, hardwired 24/7 continuous recording around a residential home or commercial property.",
                "skip_if": "You rent an apartment and cannot run Cat6 Ethernet cables through walls or soffits."
            },
            {
                "name": "AI Floodlight Security Cameras",
                "slug": "ai-floodlight-security-cameras",
                "img_q": "floodlight outdoor security",
                "brands": ["eufy Security", "Ring", "Arlo", "Wyze", "Blink"],
                "models": ["Floodlight Cam E340 Dual-Cam 24/7", "Floodlight Cam Wired Pro Bird's-Eye", "Pro 3 Floodlight Wireless 2K HDR", "Floodlight v2 2800-Lumen 180° PIR", "Wired Floodlight 2600-Lumen LED"],
                "specs": {
                    "Illumination Output": "2,000 to 3,000 Lumens Dimmable Motion-Activated LEDs",
                    "Field of View": "360° Pan-Tilt or 180° Wide-Angle Radar Zone Mapping",
                    "Siren Deterrence": "105 dB – 110 dB Remote & Automated Intruder Siren",
                    "Connectivity": "Dual-Band 2.4GHz / 5GHz Wi-Fi 6 High-Gain Antenna"
                },
                "buy_if": "You have an existing outdoor junction box above your garage or patio and want powerful lighting combined with active AI deterrence.",
                "skip_if": "You lack hardwired 110V–240V outdoor floodlight wiring and prefer a compact battery camera."
            }
        ]
    },
    {
        "category": "Biometric Locks & Access",
        "cat_slug": "biometric-locks-access-control",
        "icon": "🔐",
        "subcategories": [
            {
                "name": "3D Fingerprint & Palm-Vein Deadbolts",
                "slug": "fingerprint-palm-vein-smart-deadbolts",
                "img_q": "electronic door lock keypad",
                "brands": ["Philips", "eufy Security", "ULTRALOQ", "Lockly", "Kwikset"],
                "models": ["Palm Recognition Wi-Fi Smart Deadbolt", "Video Smart Lock S330 3-in-1 Camera+Lock", "Bolt Fingerprint Matter / Wi-Fi Pro", "Vision Elite Video Biometric Deadbolt", "Halo Touch Fingerprint Wi-Fi Modern"],
                "specs": {
                    "Biometric Sensor": "Sub-0.3s 3D Semiconductor Fingerprint / Touchless Palm-Vein Scanner",
                    "Security Grade": "ANSI/BHMA Grade 1 / Grade AAA Certified Deadbolt Bolt",
                    "Access Modes": "Biometric, Anti-Peep Passcode, App, Voice & Mechanical Key",
                    "Emergency Power": "10-Month Lithium/AA Battery + Exterior USB-C Jump Port"
                },
                "buy_if": "You want instant keyless entry even when your hands are wet or aged, plus real-time audit logs of every door unlock.",
                "skip_if": "Your front door uses an antique mortise lock cylinder incompatible with standard US deadbolt boreholes."
            },
            {
                "name": "Matter & HomeKey Smart Locks",
                "slug": "matter-apple-homekey-smart-locks",
                "img_q": "smart door lock home",
                "brands": ["Schlage", "Aqara", "Yale", "Level", "SwitchBot"],
                "models": ["Encode Plus Wi-Fi Apple HomeKey", "Smart Lock U100 / U200 Matter-Over-Thread", "Assure Lock 2 Plus Apple HomeKey", "Lock+ Connect Invisible Bluetooth/Matter", "Lock Pro Retrofit + Keypad Touch"],
                "specs": {
                    "Smart Ecosystem": "Native Apple HomeKey (iPhone/Watch Tap) & Matter-Over-Thread",
                    "Encryption": "AES-128 Bit Local Hardware Secure Element",
                    "Auto-Lock Sensor": "Built-In Gyroscopic Door-Ajar Position Sensor",
                    "Guest Management": "Up to 250 Scheduled & One-Time Contractor Access Codes"
                },
                "buy_if": "You use Apple Home, Google Home, or Home Assistant and want tap-to-unlock convenience with your Apple Watch or smartphone.",
                "skip_if": "You have no interest in smartphone automation and only want a mechanical keypad."
            },
            {
                "name": "Smart Garage Controllers",
                "slug": "smart-wifi-garage-door-controllers",
                "img_q": "garage door house exterior",
                "brands": ["Meross", "Chamberlain myQ", "Tailwind", "Genie", "Konnected"],
                "models": ["MSG100HK / MSG200HK CarPlay & HomeKit", "Smart Garage Video Keypad + Hub Bundle", "iQ3 Pro Auto-Sense Vehicle Controller", "Aladdin Connect Smartphone Opener", "blaQ Local ESPHome Garage Opener"],
                "specs": {
                    "Voice & Car Integration": "Apple CarPlay, Siri, Alexa, Google Assistant & Local API",
                    "Door Compatibility": "Supports Over 200+ Opener Models (With Yellow/Purple Learn Adapter)",
                    "Safety Alerting": "Overnight Forgotten-Open Alert + Audible Closing Beep",
                    "Multi-Bay Support": "Controls 1 to 3 Individual Garage Doors from One Module"
                },
                "buy_if": "You want your garage door to close automatically when you drive away and alert your phone if left open after 10 PM.",
                "skip_if": "Your garage has manual swing-out carriage doors without an overhead motorized rail opener."
            }
        ]
    },
    {
        "category": "Video Doorbells & Intercoms",
        "cat_slug": "video-doorbells-intercoms",
        "icon": "🔔",
        "subcategories": [
            {
                "name": "Dual-Camera Package Doorbells",
                "slug": "dual-camera-package-video-doorbells",
                "img_q": "doorbell front door delivery",
                "brands": ["eufy Security", "Ring", "TP-Link Tapo", "Arlo", "Lorex"],
                "models": ["Video Doorbell E340 Dual-Cam + HomeBase", "Battery Doorbell Pro Head-to-Toe Radar", "D235 2K 5MP 180° Head-to-Toe Doorbell", "2K Wireless Video Doorbell + Chime", "4K Dual-Lens Parcel Guard Doorbell"],
                "specs": {
                    "Camera Array": "Front 2K/4K Visitor Camera + Downward Porch Package Camera",
                    "Blind-Spot Coverage": "Eliminates Porch Floor Blind Spots Down to 0 Inches",
                    "Power Options": "Quick-Swap Rechargeable Battery OR 8–24V AC Hardwired",
                    "Porch Protection": "AI Delivery Guard Alerts When Packages Are Dropped Off or Approached"
                },
                "buy_if": "You receive frequent Amazon and courier deliveries and want dedicated downward camera verification of packages on your doormat.",
                "skip_if": "You live in a gated high-rise building where packages are held at a front concierge desk."
            },
            {
                "name": "Wired 4K Chime Doorbells",
                "slug": "wired-4k-chime-video-doorbells",
                "img_q": "front door bell entrance",
                "brands": ["Reolink", "Google Nest", "Ring", "Ecobee", "Amcrest"],
                "models": ["Video Doorbell Wi-Fi / PoE 2K+ 5MP", "Doorbell (Wired, 2nd Gen) 24/7 History", "Wired Doorbell Pro 3D Motion Radar", "Smart Video Doorbell Wired + Thermostat View", "4MP AD410 AI Human-Detection Wired"],
                "specs": {
                    "Pre-Roll Recording": "6-Second Color Pre-Roll Captures Motion Prior to Trigger",
                    "Chime Included": "Plug-In Wireless Indoor Chime + Mechanical Chime Bypass",
                    "Weather Resistance": "IP65 Weatherproof (-4°F to 131°F Operating Range)",
                    "NVR / RTSP Support": "Supports ONVIF / RTSP Local Recording on Select Models"
                },
                "buy_if": "You have existing 16V–24V doorbell wires at your front entrance and never want to recharge a doorbell battery.",
                "skip_if": "Your front doorframe has no existing low-voltage doorbell wiring."
            },
            {
                "name": "PoE Smart Video Intercoms",
                "slug": "poe-smart-video-intercom-panels",
                "img_q": "intercom access panel building",
                "brands": ["Ubiquiti UniFi", "Akuvox", "Hikvision", "2N IP", "Dahua"],
                "models": ["Access G2 Reader Pro PoE Video Intercom", "R20A / E12W SIP Video Doorphone + Touch Monitor", "DS-KIS603-P IP Video Intercom Kit", "IP Verso Modular PoE Security Intercom", "7-Inch Touchscreen PoE Gate Intercom Bundle"],
                "specs": {
                    "Communication Protocol": "Standard SIP / PoE IP Two-Way HD Video & Audio",
                    "Gate & Strike Relay": "Built-In Dry/Wet Contact Relay for Electric Strikes & Maglocks",
                    "Unlock Credentials": "NFC Card, PIN Code, Mobile App Bluetooth & Remote Indoor Screen",
                    "Enclosure Rating": "IK08 Vandal-Resistant & IP65 Weatherproof Aluminum Housing"
                },
                "buy_if": "You manage a gated driveway, multi-family property, or modern custom home requiring hardwired PoE intercom and gate release.",
                "skip_if": "You just need a simple peel-and-stick battery doorbell."
            }
        ]
    },
    {
        "category": "Mesh Wi-Fi 7 & Firewalls",
        "cat_slug": "mesh-wifi-7-firewalls",
        "icon": "📡",
        "subcategories": [
            {
                "name": "Wi-Fi 7 Tri-Band Mesh Routers",
                "slug": "wifi-7-tri-band-mesh-routers",
                "img_q": "wireless router internet antenna",
                "brands": ["TP-Link Deco", "Amazon eero", "ASUS ZenWiFi", "NETGEAR Orbi", "Linksys"],
                "models": ["BE85 / BE65 Pro Tri-Band Wi-Fi 7 (3-Pack)", "Max 7 Tri-Band 10Gbps Mesh System", "BQ16 Pro Quad-Band Wi-Fi 7 30,000 Mbps", "970 / 770 Series Tri-Band Wi-Fi 7", "Velop Pro 7 Cognitive Mesh 3-Node"],
                "specs": {
                    "Wi-Fi Generation": "Wi-Fi 7 (802.11be) with 320MHz Channels & 4K-QAM",
                    "Multi-Link Operation": "Simultaneous 2.4GHz + 5GHz + 6GHz Wireless/Wired Backhaul",
                    "WAN / LAN Ports": "2.5Gbps & 10Gbps Multi-Gig Ethernet Ports per Node",
                    "IoT Camera Capacity": "Supports 200+ Simultaneous 4K Cameras & Smart Devices"
                },
                "buy_if": "You run multiple 4K wireless security cameras around your exterior walls and need high-throughput 6GHz backhaul.",
                "skip_if": "Your internet service plan is under 100 Mbps in a small single-room studio."
            },
            {
                "name": "Multi-Gig VPN Security Gateways",
                "slug": "multi-gig-vpn-security-gateways",
                "img_q": "network switch ethernet server",
                "brands": ["Ubiquiti UniFi", "Firewalla", "GL.iNet", "TP-Link Omada", "Protectli"],
                "models": ["Cloud Gateway Max / Dream Machine Pro SE", "Gold SE / Gold Pro Dual-2.5G Cyber Firewall", "Flint 2 (GL-MT6000) WireGuard VPN Router", "ER707-M2 Multi-Gigabit VPN Gateway", "Vault Pro 4-Port 2.5G OPNsense/pfSense Appliance"],
                "specs": {
                    "Intrusion Prevention": "Real-Time Deep Packet Inspection (IDS/IPS) @ 2.5Gbps+",
                    "VLAN Segmentation": "Isolates IoT Cameras & Smart Locks onto Secure Guest/IoT VLANs",
                    "VPN Throughput": "Built-In WireGuard & OpenVPN Server/Client Hardware Acceleration",
                    "Failover Redundancy": "Dual-WAN Auto-Failover to 5G/LTE or Starlink Backup"
                },
                "buy_if": "You want enterprise-grade network segmentation that isolates your smart home cameras from your work computers.",
                "skip_if": "You prefer a zero-configuration ISP rental router."
            },
            {
                "name": "Outdoor PoE Access Points",
                "slug": "outdoor-poe-wifi-access-points",
                "img_q": "wireless antenna outdoor pole",
                "brands": ["TP-Link Omada", "Ubiquiti UniFi", "WAVLINK", "EnGenius", "Cudy"],
                "models": ["EAP650-Outdoor / EAP610-Outdoor Wi-Fi 6 PoE", "U6 Mesh Pro / Swiss Army Knife Ultra Outdoor", "AX3000 High-Power Weatherproof PoE Extender", "EWS850-FIT Wi-Fi 6 IP67 Outdoor AP", "AP3000 Outdoor 2.5G PoE Mesh Point"],
                "specs": {
                    "Outdoor Coverage": "Up to 650–1,000 Feet Open-Yard & Detached Barn Range",
                    "Enclosure Protection": "IP67 / IP68 Waterproof, Dustproof & 6kV Lightning Protection",
                    "Power Delivery": "802.3at PoE+ Single Ethernet Cable Power & Data",
                    "Mounting Hardware": "Pole-Mount & Wall-Mount Stainless Brackets Included"
                },
                "buy_if": "You need strong Wi-Fi signal at your driveway gate, detached workshop, pool house, or perimeter solar cameras.",
                "skip_if": "You do not have an outdoor patio, yard, or detached garage."
            }
        ]
    },
    {
        "category": "Smart Climate & Leak Defense",
        "cat_slug": "smart-climate-leak-defense",
        "icon": "🌡️",
        "subcategories": [
            {
                "name": "Multi-Zone Learning Thermostats",
                "slug": "multi-zone-learning-smart-thermostats",
                "img_q": "thermostat wall temperature home",
                "brands": ["Ecobee", "Google Nest", "Honeywell Home", "Amazon", "Sensi"],
                "models": ["Smart Thermostat Premium + SmartSensor", "Learning Thermostat (4th Gen) + Temp Sensor", "T9 / T10 Pro Smart with Remote Room Sensors", "Smart Thermostat ENERGY STAR Certified", "Touch 2 Smart Color Touchscreen"],
                "specs": {
                    "Room Occupancy Sensors": "Wireless Radar Occupancy & Temperature Balancing Sensors",
                    "HVAC Compatibility": "Supports Multi-Stage Heat Pumps, Dual-Fuel & Conventional Systems",
                    "Air Quality Monitor": "Built-In VOC, CO2 & Humidity Indoor Air Quality Sensor (Premium)",
                    "Energy Savings": "ENERGY STAR Certified (Saves Up to 23%–26% Annual HVAC Cost)"
                },
                "buy_if": "You want your HVAC system to prioritize the temperature in your occupied bedroom at night rather than an empty hallway.",
                "skip_if": "Your home uses high-voltage 120V/240V electric baseboard heaters (requires a dedicated line-voltage thermostat)."
            },
            {
                "name": "Ultrasonic Auto Water Shutoff Valves",
                "slug": "ultrasonic-automatic-water-shutoff-valves",
                "img_q": "plumbing water pipe valve",
                "brands": ["Moen", "Phyn", "YoLink", "Flume", "Kidde"],
                "models": ["Flo Smart Water Monitor & Auto Shutoff (3/4\" & 1\")", "Plus 2nd-Gen Ultrasonic Smart Water Assistant", "LoRa Bulldog Robot Valve + 4 Leak Sensors", "2 Smart Home Water Monitor + Strap", " Ring-Compatible Smart Water Shutoff"],
                "specs": {
                    "Leak Detection Tech": "24/7 Ultrasonic Flow, Pressure & Micro-Drip Testing",
                    "Automatic Action": "Motorized Ball Valve Shuts Off Main Water Supply in Seconds",
                    "Wireless Range": "Wi-Fi + LoRa 1,000-Ft Basement-Penetrating Sensor Link",
                    "Insurance Benefit": "Qualifies for Homeowner Insurance Water-Damage Discounts"
                },
                "buy_if": "You want to prevent catastrophic $15,000+ burst-pipe or water-heater flooding while you are away on vacation.",
                "skip_if": "You live in a multi-unit apartment where the main water shutoff valve is locked in a utility basement."
            },
            {
                "name": "Smart Smoke & CO Detectors",
                "slug": "smart-smoke-carbon-monoxide-detectors",
                "img_q": "smoke detector ceiling alarm",
                "brands": ["Google Nest", "First Alert", "Kidde", "X-Sense", "Aqara"],
                "models": ["Protect 2nd-Gen Split-Spectrum Smoke + CO", "Onelink Safe & Sound Smart Hardwired", "Smart Smoke + Carbon Monoxide + Indoor Air Quality", "SC07-WX Wi-Fi 10-Year Sealed Battery Combo", "Zigbee 3.0 Smart Photoelectric Smoke Detector"],
                "specs": {
                    "Sensor Chemistry": "Split-Spectrum Photoelectric Smoke + Electrochemical CO Sensor",
                    "Smartphone Alerts": "Instant Push Notification + Voice Room-Location Announcement",
                    "Self-Testing": "Automated Silent Microphone & Sensor Health Check",
                    "Lifespan": "10-Year UL-Listed Sensor & Sealed Lithium Battery Backup"
                },
                "buy_if": "You want instant smartphone alerts if smoke or carbon monoxide is detected while you are away from home.",
                "skip_if": "Your building uses a commercial 24V hardwired fire panel managed by an HOA."
            }
        ]
    },
    {
        "category": "Matter Hubs, Shades & Lighting",
        "cat_slug": "matter-hubs-shades-lighting",
        "icon": "⚡",
        "subcategories": [
            {
                "name": "Local Zigbee/Thread/Matter Hubs",
                "slug": "local-zigbee-thread-matter-hubs",
                "img_q": "smart home automation hub",
                "brands": ["Home Assistant", "Hubitat", "Aqara", "Aeotec", "SwitchBot"],
                "models": ["Green Smart Home Hub + SkyConnect ZBT-1", "Elevation C-8 Pro Local Z-Wave 800 / Zigbee", "Hub M3 Matter Controller & Thread Border Router", "SmartThings Station Matter/Zigbee/Z-Wave", "Hub 2 Matter IR + Thermo-Hygrometer"],
                "specs": {
                    "Radios Onboard": "Matter Controller, Thread Border Router, Zigbee 3.0 & Z-Wave 800",
                    "Cloud Dependency": "100% Local Automation Execution (Works When Internet Is Down)",
                    "Cross-Platform Bridge": "Bridges 1,000+ Sensors into Apple Home, Alexa & Google Home",
                    "Power & Network": "PoE / Ethernet Wired Port + Dual-Band Wi-Fi"
                },
                "buy_if": "You want sub-50ms instant sensor automations that keep working even during an ISP internet outage.",
                "skip_if": "You only own a single Wi-Fi smart plug."
            },
            {
                "name": "Motorized Smart Roller Shades",
                "slug": "motorized-smart-roller-shades",
                "img_q": "window blinds living room modern",
                "brands": ["Lutron", "Eve MotionBlinds", "SmartWings", "SwitchBot", "Yoolax"],
                "models": ["Serena / Caseta Wireless Smart Roller Shade", "Upgrade Kit for Roller Blinds Matter-Over-Thread", "Motorized 100% Blackout Linen Shade (Matter/Zigbee)", "Curtain 3 Rod/U-Rail Solar Retrofit Motor", "Motorized Cellular Honeycomb Blackout Blind"],
                "specs": {
                    "Motor Acoustic Rating": "Whisper-Quiet 35 dB – 42 dB Brushless Tubular Motor",
                    "Power Supply": "USB-C Rechargeable Battery (6–12 Months) + Window Solar Strip",
                    "Smart Protocols": "Matter-Over-Thread, Apple HomeKit, Zigbee 3.0 & Alexa",
                    "Scheduling": "Automated Sunrise/Sunset & Thermostat Heat-Gain Schedules"
                },
                "buy_if": "You have hard-to-reach bedroom or living room windows and want automated sunrise wake-up and afternoon solar heat blocking.",
                "skip_if": "Your windows have non-standard arched semicircular frames."
            },
            {
                "name": "In-Wall Matter Dimmer Switches",
                "slug": "in-wall-matter-smart-dimmer-switches",
                "img_q": "light switch wall interior",
                "brands": ["Lutron Caséta", "Inovelli", "Leviton", "TP-Link Tapo", "Kasa Smart"],
                "models": ["Diva Smart Dimmer Starter Kit + Pico Remote", "White Series 2-1 Smart Switch (Matter-Over-Thread)", "Decora Smart Dimmer (2nd Gen Matter Certified)", "S505D Matter Smart Wi-Fi Dimmer (3-Pack)", "HS220P3 Single-Pole Smart Dimmer Bundle"],
                "specs": {
                    "Wiring Flexibility": "Works With or Without Neutral Wire (Lutron / Inovelli)",
                    "Multi-Way Support": "Single-Pole & 3-Way Staircase/Hallway Circuit Ready",
                    "Load Rating": "150W Dimmable LED / CFL & 600W Incandescent/Halogen",
                    "Safety Listing": "UL / ETL Listed for US & Canadian 120V 60Hz Electrical Boxes"
                },
                "buy_if": "You want smart voice and schedule lighting control while keeping physical wall switches intuitive for family and guests.",
                "skip_if": "Your home uses low-voltage proprietary DMX commercial lighting panels."
            }
        ]
    }
]

EDITIONS = [
    ("2026 Pro Security Bundle", "updated 2026 hardware revision featuring encrypted local storage and extended range"),
    ("Whole-Home Starter Kit", "complete multi-room security package engineered for rapid DIY installation"),
    ("Commercial-Grade Spec", "heavy-duty weather-sealed edition built for 24/7 continuous property protection")
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "security-device"


def make_amazon_url(query: str) -> str:
    """
    Membuat tautan afiliasi Amazon US dengan Tracking ID otomatis,
    diurutkan berdasarkan Best-Sellers (exact-aware-popularity-rank) dan rating 4 bintang ke atas.
    """
    encoded = quote_plus(query)
    return (
        f"https://www.amazon.com/s?k={encoded}"
        f"&s=exact-aware-popularity-rank&rh=p_72%3A1248873011&tag={AMAZON_TAG}"
    )


def load_image_cache() -> dict:
    if os.path.exists(IMAGE_CACHE_FILE):
        try:
            with open(IMAGE_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_image_cache(cache: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(IMAGE_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def fetch_free_stock_image(query: str, variant_idx: int, cache: dict) -> dict:
    """
    Mengambil gambar gratis berlisensi bebas dari API publik tanpa API key:
    1. Openverse Public API (https://api.openverse.org/v1/images/)
    2. Wikimedia Commons Public API (https://commons.wikimedia.org/w/api.php)
    3. Fallback deterministik ke LoremFlickr Stock Photo CDN agar gambar selalu tampil.
    """
    cache_key = f"{query}_{variant_idx % 5}"
    if cache_key in cache:
        return cache[cache_key]

    # 1. Openverse Public API (Tanpa API Key)
    try:
        ov_url = f"https://api.openverse.org/v1/images/?q={quote_plus(query)}&page_size=6"
        r = requests.get(ov_url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                picked = results[variant_idx % len(results)]
                img_url = picked.get("thumbnail") or picked.get("url")
                if img_url and img_url.startswith("http"):
                    res_obj = {
                        "url": img_url,
                        "credit": f"Openverse CC ({picked.get('license', 'CC0').upper()})"
                    }
                    cache[cache_key] = res_obj
                    return res_obj
    except Exception:
        pass

    # 2. Wikimedia Commons Public MediaWiki API (Tanpa API Key)
    try:
        wm_url = (
            "https://commons.wikimedia.org/w/api.php"
            f"?action=query&generator=search&gsrsearch=filetype:bitmap+{quote_plus(query)}"
            "&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url&iiurlwidth=640&format=json"
        )
        r = requests.get(wm_url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            pages = list(r.json().get("query", {}).get("pages", {}).values())
            if pages:
                picked = pages[variant_idx % len(pages)]
                ii = picked.get("imageinfo", [{}])[0]
                img_url = ii.get("thumburl") or ii.get("url")
                if img_url and img_url.startswith("http"):
                    res_obj = {
                        "url": img_url,
                        "credit": "Wikimedia Commons Public Media"
                    }
                    cache[cache_key] = res_obj
                    return res_obj
    except Exception:
        pass

    # 3. Fallback deterministik ke CDN foto stok bebas lisensi
    clean_tag = re.sub(r"[^a-zA-Z0-9]", ",", query.split()[0])
    fallback_obj = {
        "url": f"https://loremflickr.com/640/440/{clean_tag}?lock={variant_idx + 200}",
        "credit": "Creative Commons Public Stock"
    }
    cache[cache_key] = fallback_obj
    return fallback_obj


def init_or_load_state() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                if state.get("products"):
                    return state
        except Exception:
            pass

    # Bangun antrean 540 produk Smart Home & Security Tech
    products = []
    idx = 1
    for ed_name, ed_desc in EDITIONS:
        for model_i in range(10):
            for cat in TAXONOMY:
                for sub in cat["subcategories"]:
                    brand = sub["brands"][model_i % len(sub["brands"])]
                    model = sub["models"][model_i % len(sub["models"])]
                    series_tag = "Series A" if model_i < 5 else "Pro Series B"
                    title = f"{brand} {model} — {ed_name} ({series_tag})"
                    slug = f"{slugify(brand)}-{slugify(model)}-{slugify(ed_name)}-{idx}"
                    products.append({
                        "id": f"AD-{idx:04d}",
                        "idx": idx,
                        "slug": slug,
                        "name": title,
                        "brand": brand,
                        "category": cat["category"],
                        "cat_slug": cat["cat_slug"],
                        "cat_icon": cat["icon"],
                        "subcategory": sub["name"],
                        "sub_slug": sub["slug"],
                        "img_q": sub["img_q"],
                        "image_url": "",
                        "image_credit": "",
                        "search_query": f"{brand} {model} {sub['name']}",
                        "summary": f"The {title} is an Amazon best-selling {sub['name'].lower()}—an {ed_desc}.",
                        "specs": sub["specs"],
                        "buy_if": sub["buy_if"],
                        "skip_if": sub["skip_if"],
                        "pros": [
                            f"Authentic {brand} security architecture with encrypted telemetry",
                            f"{list(sub['specs'].keys())[0]}: {list(sub['specs'].values())[0]}",
                            f"{list(sub['specs'].keys())[1]}: {list(sub['specs'].values())[1]}"
                        ],
                        "cons": [
                            "Requires a stable 2.4GHz/5GHz Wi-Fi, PoE, or Thread/Zigbee signal at mounting point",
                            "Verify physical mounting bracket or junction box dimensions before installation"
                        ],
                        "published": False,
                        "published_at": ""
                    })
                    idx += 1

    state = {"products": products, "reviews": [], "cycle_count": 0}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    return state


def save_state(state: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_common_styles() -> str:
    return """
        :root {
            --bg: #ffffff;
            --surface: #f8fafc;
            --border: #e2e8f0;
            --navy: #090d16;
            --slate: #475569;
            --cyan: #0284c7;
            --cyan-dark: #0369a1;
            --cyan-light: #e0f2fe;
            --emerald: #059669;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--navy); line-height: 1.65; }
        .compliance-bar { background: var(--navy); color: #f8fafc; font-size: 0.79rem; text-align: center; padding: 9px 16px; }
        .compliance-bar strong { color: #38bdf8; }
        header { background: rgba(255,255,255,0.97); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; backdrop-filter: blur(8px); }
        .nav-wrap { max-width: 1260px; margin: 0 auto; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
        .brand { font-size: 1.45rem; font-weight: 900; color: var(--navy); text-decoration: none; letter-spacing: -0.5px; }
        .brand span { color: var(--cyan); }
        .nav-links { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
        .nav-link { color: var(--navy); text-decoration: none; font-size: 0.9rem; font-weight: 600; padding: 6px 10px; border-radius: 6px; }
        .nav-link:hover { background: var(--surface); color: var(--cyan); }
        .mega-dropdown { position: relative; display: inline-block; }
        .mega-menu { display: none; position: absolute; right: 0; top: 100%; width: 860px; max-width: 94vw; background: #fff; border: 1px solid var(--border); border-radius: 14px; box-shadow: 0 22px 40px rgba(9,13,22,0.16); padding: 22px; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 18px; z-index: 200; }
        .mega-dropdown:hover .mega-menu { display: grid; }
        .mega-col h4 { font-size: 0.85rem; color: var(--cyan-dark); margin-bottom: 6px; border-bottom: 1px solid var(--border); padding-bottom: 4px; }
        .mega-col a { display: block; color: var(--slate); text-decoration: none; font-size: 0.8rem; padding: 3px 0; }
        .mega-col a:hover { color: var(--cyan); font-weight: 600; }
        .container { max-width: 1260px; margin: 36px auto; padding: 0 20px; }
        .btn-amz { display: inline-block; background: var(--cyan); color: #ffffff; font-weight: 700; text-decoration: none; padding: 11px 18px; border-radius: 8px; font-size: 0.86rem; text-align: center; transition: background 0.15s; }
        .btn-amz:hover { background: var(--cyan-dark); }
        .btn-outline { display: inline-block; background: #fff; color: var(--navy); border: 1px solid var(--border); font-weight: 600; text-decoration: none; padding: 10px 14px; border-radius: 8px; font-size: 0.84rem; text-align: center; }
        .btn-outline:hover { border-color: var(--cyan); color: var(--cyan); }
        .grid-3 { display: grid; grid-template-columns: repeat(auto-fill, minmax(305px, 1fr)); gap: 22px; }
        .card { background: #fff; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.15s, box-shadow 0.15s; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 12px 24px rgba(9,13,22,0.07); border-color: #cbd5e1; }
        .card-img { width: 100%; height: 190px; object-fit: cover; background: #f1f5f9; border-bottom: 1px solid var(--border); }
        .card-body { padding: 20px; display: flex; flex-direction: column; flex: 1; justify-content: space-between; }
        .pill { display: inline-block; background: var(--cyan-light); color: var(--cyan-dark); font-size: 0.73rem; font-weight: 700; padding: 4px 10px; border-radius: 999px; margin-bottom: 8px; width: fit-content; }
        .micro-disclosure { font-size: 0.72rem; color: #64748b; margin: 10px 0 6px; }
        footer { background: var(--surface); border-top: 1px solid var(--border); margin-top: 70px; padding: 48px 20px; color: var(--slate); font-size: 0.84rem; }
        .footer-inner { max-width: 1260px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 28px; }
        .footer-inner h4 { color: var(--navy); margin-bottom: 10px; font-size: 0.94rem; }
        .footer-inner a { display: block; color: var(--slate); text-decoration: none; padding: 3px 0; }
        .footer-inner a:hover { color: var(--cyan); }
    """


def build_header_html() -> str:
    mega_cols = ""
    for cat in TAXONOMY:
        sub_links = "".join(
            f'<a href="{SITE_URL}/categories/{sub["slug"]}.html">&rsaquo; {sub["name"]}</a>'
            for sub in cat["subcategories"]
        )
        mega_cols += f"""
        <div class="mega-col">
            <h4><a href="{SITE_URL}/categories/{cat['cat_slug']}.html" style="color:var(--cyan-dark);font-size:0.85rem;">{cat['icon']} {cat['category']}</a></h4>
            {sub_links}
        </div>
        """

    return f"""
    <div class="compliance-bar">
        <strong>AFFILIATE DISCLOSURE:</strong> As an Amazon Associate I earn from qualifying purchases. Stock photography provided via Openverse &amp; Wikimedia Commons Public APIs.
    </div>
    <header>
        <div class="nav-wrap">
            <a href="{SITE_URL}/" class="brand">🛡️ Aegis<span>Domus</span> US</a>
            <nav class="nav-links">
                <a href="{SITE_URL}/" class="nav-link">Storefront</a>
                <div class="mega-dropdown">
                    <a href="#departments" class="nav-link">Smart Security Categories &#9662;</a>
                    <div class="mega-menu">
                        {mega_cols}
                    </div>
                </div>
                <a href="{SITE_URL}/#featured" class="nav-link">Featured Systems</a>
                <a href="{SITE_URL}/#reviews" class="nav-link">12H Security Reviews</a>
                <a href="{SITE_URL}/legal.html" class="nav-link">Policies</a>
            </nav>
        </div>
    </header>
    """


def build_footer_html(today: str) -> str:
    cat_links = "".join(
        f'<a href="{SITE_URL}/categories/{c["cat_slug"]}.html">{c["icon"]} {c["category"]}</a>'
        for c in TAXONOMY
    )
    return f"""
    <footer>
        <div class="footer-inner">
            <div>
                <h4>AegisDomus US Security Storefront</h4>
                <p>Independent US buying-guide and specification comparison platform dedicated to Smart Home &amp; Physical Security Tech. Updated automatically every 12 hours.</p>
                <p style="margin-top:10px;font-weight:700;color:var(--navy);">As an Amazon Associate I earn from qualifying purchases.</p>
            </div>
            <div>
                <h4>Security &amp; Automation Departments</h4>
                {cat_links}
            </div>
            <div>
                <h4>Compliance &amp; Indexing Feeds</h4>
                <a href="{SITE_URL}/legal.html#disclosure">Amazon Affiliate Disclosure</a>
                <a href="{SITE_URL}/legal.html#privacy">Privacy Policy</a>
                <a href="{SITE_URL}/legal.html#terms">Terms of Use</a>
                <a href="{SITE_URL}/sitemap.xml">XML Sitemap</a>
                <a href="{SITE_URL}/feed.xml">RSS 2.0 WebSub Feed</a>
            </div>
        </div>
        <div style="max-width:1260px;margin:28px auto 0;padding-top:20px;border-top:1px solid var(--border);text-align:center;font-size:0.78rem;">
            &copy; {today[:4]} AegisDomus US. Not operated, endorsed, or sponsored by Amazon.com, Inc. Last 12-Hour Automated Build: {today}.
        </div>
    </footer>
    """


def render_product_page(prod: dict, related: list, today: str) -> str:
    os.makedirs(PRODUCTS_DIR, exist_ok=True)
    page_url = f"{SITE_URL}/products/{prod['slug']}.html"
    amz_url = make_amazon_url(prod["search_query"])

    specs_rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in prod["specs"].items())
    pros_html = "".join(f"<li style='margin-bottom:6px;color:#065f46;'>&#10004; {p}</li>" for p in prod["pros"])
    cons_html = "".join(f"<li style='margin-bottom:6px;color:#991b1b;'>&#9888; {c}</li>" for c in prod["cons"])

    rel_cards = ""
    for r in related[:3]:
        if r["slug"] == prod["slug"]:
            continue
        r_amz = make_amazon_url(r["search_query"])
        rel_cards += f"""
        <div class="card">
            <img src="{r['image_url']}" alt="{r['name']}" class="card-img" loading="lazy">
            <div class="card-body">
                <div>
                    <span class="pill">{r['subcategory']}</span>
                    <h3 style="font-size:1.05rem;margin-bottom:8px;"><a href="{SITE_URL}/products/{r['slug']}.html" style="color:var(--navy);text-decoration:none;">{r['name']}</a></h3>
                    <p style="font-size:0.85rem;color:var(--slate);">{r['summary']}</p>
                </div>
                <div style="margin-top:14px;">
                    <a href="{r_amz}" target="_blank" rel="nofollow sponsored noopener noreferrer" class="btn-amz" style="width:100%;">Check Price on Amazon &rarr;</a>
                </div>
            </div>
        </div>
        """

    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"Who should buy the {prod['name']}?",
                "acceptedAnswer": {"@type": "Answer", "text": prod["buy_if"]}
            },
            {
                "@type": "Question",
                "name": f"Who should skip the {prod['name']}?",
                "acceptedAnswer": {"@type": "Answer", "text": prod["skip_if"]}
            }
        ]
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prod['name']} Review, Specs & Security Guide | AegisDomus US</title>
    <meta name="description" content="{prod['summary']} Compare verified security specifications, pros, cons, and check live price on Amazon.">
    <link rel="canonical" href="{page_url}">
    <script type="application/ld+json">{json.dumps(faq_schema)}</script>
    <style>
        {get_common_styles()}
        .hero-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 28px; margin-bottom: 32px; display: grid; grid-template-columns: 360px 1fr; gap: 28px; align-items: center; }}
        .hero-img {{ width: 100%; height: 260px; object-fit: cover; border-radius: 12px; border: 1px solid var(--border); }}
        .spec-table {{ width: 100%; border-collapse: collapse; margin: 20px 0 32px; }}
        .spec-table th, .spec-table td {{ border: 1px solid var(--border); padding: 12px 16px; text-align: left; font-size: 0.92rem; }}
        .spec-table th {{ background: var(--surface); width: 34%; }}
        .verdict-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 20px; margin: 24px 0; }}
        .v-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 22px; }}
        .calc-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 22px; margin: 28px 0; }}
        .calc-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-top: 12px; }}
        select {{ width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border); font-size: 0.9rem; background: #fff; }}
        @media (max-width: 780px) {{ .hero-box {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    {build_header_html()}
    <main class="container">
        <div style="font-size:0.84rem;color:var(--slate);margin-bottom:16px;">
            <a href="{SITE_URL}/" style="color:var(--cyan);text-decoration:none;font-weight:600;">Home</a> &rsaquo;
            <a href="{SITE_URL}/categories/{prod['cat_slug']}.html" style="color:var(--cyan);text-decoration:none;font-weight:600;">{prod['category']}</a> &rsaquo;
            <a href="{SITE_URL}/categories/{prod['sub_slug']}.html" style="color:var(--cyan);text-decoration:none;font-weight:600;">{prod['subcategory']}</a> &rsaquo;
            <span>{prod['name']}</span>
        </div>

        <section class="hero-box">
            <div>
                <img src="{prod['image_url']}" alt="{prod['name']}" class="hero-img">
                <div style="font-size:0.7rem;color:#64748b;margin-top:4px;text-align:center;">Illustrative Category Photo: {prod['image_credit']}</div>
            </div>
            <div>
                <span class="pill">{prod['cat_icon']} {prod['subcategory']} &bull; Smart Security Pick</span>
                <h1 style="font-size:1.9rem;line-height:1.25;margin-bottom:10px;">{prod['name']}</h1>
                <p style="color:var(--slate);margin-bottom:14px;">{prod['summary']}</p>
                <div class="micro-disclosure">Affiliate Disclosure: As an Amazon Associate I earn from qualifying purchases.</div>
                <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;">
                    <a href="{amz_url}" target="_blank" rel="nofollow sponsored noopener noreferrer" class="btn-amz">Check Price on Amazon &rarr;</a>
                    <a href="{amz_url}" target="_blank" rel="nofollow sponsored noopener noreferrer" class="btn-outline">View on Amazon</a>
                </div>
            </div>
        </section>

        <section class="calc-box">
            <h2 style="font-size:1.2rem;">Interactive Smart Home Network &amp; NVR Storage Estimator</h2>
            <div class="calc-row">
                <div>
                    <label style="font-size:0.8rem;color:var(--slate);display:block;margin-bottom:4px;">Number of Smart Security Devices / Cameras</label>
                    <select id="devCount" onchange="calcNet()">
                        <option value="2">1 – 2 Devices (Starter Entry)</option>
                        <option value="4" selected>3 – 4 Devices (Standard Home)</option>
                        <option value="8">6 – 8 Devices (Full Perimeter)</option>
                        <option value="16">12 – 16 Devices (Large Estate)</option>
                    </select>
                </div>
                <div>
                    <label style="font-size:0.8rem;color:var(--slate);display:block;margin-bottom:4px;">Video Stream / Telemetry Resolution</label>
                    <select id="resBitrate" onchange="calcNet()">
                        <option value="2">1080p HD / Smart Sensor Telemetry (2 Mbps)</option>
                        <option value="5" selected>2K QHD High-Bitrate Stream (5 Mbps)</option>
                        <option value="8">4K UHD H.265 Stream (8 Mbps)</option>
                    </select>
                </div>
            </div>
            <div id="calcOutput" style="margin-top:14px;padding:12px 16px;background:#fff;border-left:4px solid var(--cyan);border-radius:6px;font-weight:700;font-size:0.92rem;">
                Estimated Upload Bandwidth: 20 Mbps Minimum &bull; Recommended Local Storage for 14-Day Archive: 2 TB Drive
            </div>
        </section>

        <div class="verdict-grid">
            <div class="v-box">
                <h3 style="color:var(--emerald);margin-bottom:8px;">Who Should Buy This</h3>
                <p style="font-size:0.93rem;color:var(--slate);">{prod['buy_if']}</p>
            </div>
            <div class="v-box">
                <h3 style="color:#b91c1c;margin-bottom:8px;">Who Should Skip This</h3>
                <p style="font-size:0.93rem;color:var(--slate);">{prod['skip_if']}</p>
            </div>
        </div>

        <h2 style="font-size:1.4rem;margin-top:30px;">Verified Technical Specifications</h2>
        <table class="spec-table">
            <tbody>{specs_rows}</tbody>
        </table>

        <div class="verdict-grid">
            <div class="v-box">
                <h3 style="margin-bottom:10px;">Key Strengths (Pros)</h3>
                <ul style="list-style:none;">{pros_html}</ul>
            </div>
            <div class="v-box">
                <h3 style="margin-bottom:10px;">Considerations (Cons)</h3>
                <ul style="list-style:none;">{cons_html}</ul>
            </div>
        </div>

        <h2 style="font-size:1.4rem;margin:40px 0 18px;">Related Smart Security Alternatives</h2>
        <div class="grid-3">{rel_cards}</div>
    </main>
    {build_footer_html(today)}
    <script>
        function calcNet() {{
            const devs = parseInt(document.getElementById('devCount').value);
            const mbps = parseInt(document.getElementById('resBitrate').value);
            const totalMbps = devs * mbps;
            const storageTb = Math.max(1, Math.ceil((devs * mbps * 0.12)));
            document.getElementById('calcOutput').innerText =
                'Estimated Upload Bandwidth: ' + totalMbps + ' Mbps Minimum • Recommended Local Storage for 14-Day Archive: ' + storageTb + ' TB Drive';
        }}
    </script>
</body>
</html>"""

    with open(os.path.join(PRODUCTS_DIR, f"{prod['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return page_url


def render_review_article(group: list, cycle_num: int, art_idx: int, today: str) -> dict:
    os.makedirs(REVIEWS_DIR, exist_ok=True)
    sub = group[0]["subcategory"]
    cat = group[0]["category"]
    slug = f"best-{slugify(sub)}-security-review-c{cycle_num}-{art_idx}"
    title = f"Top 4 {sub} Compared ({today[:4]} Smart Security Buyer's Guide)"
    page_url = f"{SITE_URL}/reviews/{slug}.html"
    cover_img = group[0]["image_url"]

    th_cols = "".join(f"<th>{p['name']}</th>" for p in group)
    spec_keys = list(group[0]["specs"].keys())
    matrix_rows = ""
    for k in spec_keys:
        tds = "".join(f"<td>{p['specs'].get(k, 'Verified')}</td>" for p in group)
        matrix_rows += f"<tr><th>{k}</th>{tds}</tr>"

    cta_tds = "".join(
        f'<td><a href="{make_amazon_url(p["search_query"])}" target="_blank" rel="nofollow sponsored noopener noreferrer" class="btn-amz" style="padding:8px 12px;font-size:0.8rem;">Check Price on Amazon</a></td>'
        for p in group
    )

    sections_html = ""
    for rank, p in enumerate(group, 1):
        amz_url = make_amazon_url(p["search_query"])
        sections_html += f"""
        <section style="background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:24px;margin-bottom:24px;display:grid;grid-template-columns:220px 1fr;gap:22px;align-items:center;">
            <img src="{p['image_url']}" alt="{p['name']}" style="width:100%;height:160px;object-fit:cover;border-radius:10px;border:1px solid var(--border);" loading="lazy">
            <div>
                <span class="pill">Editor's Security Pick #{rank} &bull; {p['brand']}</span>
                <h2 style="font-size:1.3rem;margin-bottom:8px;"><a href="{SITE_URL}/products/{p['slug']}.html" style="color:var(--navy);text-decoration:none;">{p['name']}</a></h2>
                <p style="color:var(--slate);margin-bottom:8px;font-size:0.92rem;">{p['summary']}</p>
                <p style="font-size:0.88rem;margin-bottom:6px;"><strong>Ideal Deployment:</strong> {p['buy_if']}</p>
                <div class="micro-disclosure">As an Amazon Associate I earn from qualifying purchases.</div>
                <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;">
                    <a href="{amz_url}" target="_blank" rel="nofollow sponsored noopener noreferrer" class="btn-amz">Check Price on Amazon &rarr;</a>
                    <a href="{SITE_URL}/products/{p['slug']}.html" class="btn-outline">Full Spec Sheet</a>
                </div>
            </div>
        </section>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | AegisDomus US</title>
    <meta name="description" content="Side-by-side smart home security comparison of {', '.join(p['name'] for p in group)}.">
    <link rel="canonical" href="{page_url}">
    <style>
        {get_common_styles()}
        .table-scroll {{ overflow-x: auto; margin: 26px 0 36px; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 720px; }}
        th, td {{ border: 1px solid var(--border); padding: 12px 14px; text-align: left; font-size: 0.88rem; }}
        th {{ background: var(--surface); color: var(--navy); }}
    </style>
</head>
<body>
    {build_header_html()}
    <main class="container">
        <span class="pill">{cat} &rsaquo; 12-Hour Comparative Review</span>
        <h1 style="font-size:2rem;margin-bottom:12px;">{title}</h1>
        <p style="color:var(--slate);max-width:860px;margin-bottom:22px;">Selecting reliable {sub.lower()} requires evaluating local storage encryption, wireless or PoE range, and Matter/HomeKit ecosystem support. Compare our top four hardware picks side-by-side below.</p>

        <div class="table-scroll">
            <table>
                <thead>
                    <tr><th>Security Attribute</th>{th_cols}</tr>
                </thead>
                <tbody>
                    {matrix_rows}
                    <tr><th>Amazon Availability</th>{cta_tds}</tr>
                </tbody>
            </table>
        </div>

        {sections_html}
    </main>
    {build_footer_html(today)}
</body>
</html>"""

    with open(os.path.join(REVIEWS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "slug": slug,
        "title": title,
        "category": cat,
        "subcategory": sub,
        "image_url": cover_img,
        "excerpt": f"Side-by-side security benchmark of {group[0]['name']}, {group[1]['name']}, and 2 more top systems.",
        "published_at": today,
        "url": page_url
    }


def render_category_and_subcategory_pages(published_prods: list, today: str) -> list:
    os.makedirs(CATEGORIES_DIR, exist_ok=True)
    cat_urls = []

    def write_listing(slug: str, heading: str, desc: str, items: list):
        cards = ""
        for p in items[:36]:
            amz_url = make_amazon_url(p["search_query"])
            cards += f"""
            <article class="card">
                <img src="{p['image_url']}" alt="{p['name']}" class="card-img" loading="lazy">
                <div class="card-body">
                    <div>
                        <span class="pill">{p['cat_icon']} {p['subcategory']}</span>
                        <h3 style="font-size:1.06rem;margin-bottom:8px;"><a href="{SITE_URL}/products/{p['slug']}.html" style="color:var(--navy);text-decoration:none;">{p['name']}</a></h3>
                        <p style="font-size:0.86rem;color:var(--slate);margin-bottom:10px;">{p['summary']}</p>
                    </div>
                    <div>
                        <div class="micro-disclosure">As an Amazon Associate I earn from qualifying purchases.</div>
                        <div style="display:flex;gap:8px;">
                            <a href="{amz_url}" target="_blank" rel="nofollow sponsored noopener noreferrer" class="btn-amz" style="flex:1;">Check Price on Amazon</a>
                            <a href="{SITE_URL}/products/{p['slug']}.html" class="btn-outline">Specs</a>
                        </div>
                    </div>
                </div>
            </article>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{heading} — Smart Home &amp; Security Guides | AegisDomus US</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{SITE_URL}/categories/{slug}.html">
    <style>{get_common_styles()}</style>
</head>
<body>
    {build_header_html()}
    <main class="container">
        <h1 style="font-size:2rem;margin-bottom:8px;">{heading}</h1>
        <p style="color:var(--slate);margin-bottom:28px;">{desc}</p>
        <div class="grid-3">{cards or '<p>New security devices in this subcategory will populate in the next 12-hour automated cycle.</p>'}</div>
    </main>
    {build_footer_html(today)}
</body>
</html>"""
        with open(os.path.join(CATEGORIES_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(html)
        cat_urls.append(f"{SITE_URL}/categories/{slug}.html")

    for cat in TAXONOMY:
        c_items = [p for p in published_prods if p["cat_slug"] == cat["cat_slug"]]
        write_listing(
            cat["cat_slug"],
            f"{cat['icon']} {cat['category']}",
            f"Compare verified security specifications and Amazon best-seller links across {', '.join(s['name'] for s in cat['subcategories'])}.",
            c_items
        )
        for sub in cat["subcategories"]:
            s_items = [p for p in published_prods if p["sub_slug"] == sub["slug"]]
            write_listing(
                sub["slug"],
                f"{sub['name']} ({cat['category']})",
                f"Side-by-side comparison of top-rated {sub['name'].lower()} for US homeowners.",
                s_items
            )

    return cat_urls


def render_legal_page(today: str):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amazon Affiliate Disclosure, Privacy Policy &amp; Terms | AegisDomus US</title>
    <link rel="canonical" href="{SITE_URL}/legal.html">
    <style>
        {get_common_styles()}
        .legal-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 26px; margin-bottom: 22px; }}
    </style>
</head>
<body>
    {build_header_html()}
    <main class="container">
        <div class="legal-box" id="disclosure">
            <h2>Amazon Associates Program Disclosure</h2>
            <p style="margin-top:8px;"><strong>As an Amazon Associate I earn from qualifying purchases.</strong></p>
            <p style="margin-top:8px;color:var(--slate);">AegisDomus US is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com. Category photography is retrieved via public Creative Commons APIs (Openverse &amp; Wikimedia Commons) for illustrative editorial use.</p>
        </div>
        <div class="legal-box" id="privacy">
            <h2>Privacy Policy</h2>
            <p style="margin-top:8px;color:var(--slate);">We do not collect personal payment details or process direct checkouts. Clicking "Check Price on Amazon" redirects you securely to Amazon.com.</p>
        </div>
        <div class="legal-box" id="terms">
            <h2>Terms of Use</h2>
            <p style="margin-top:8px;color:var(--slate);">All hardware specifications are compiled for comparative buying guidance. Always verify local electrical codes, voltage ratings, and current pricing directly on Amazon.com.</p>
        </div>
    </main>
    {build_footer_html(today)}
</body>
</html>"""
    with open(os.path.join(DOCS_DIR, "legal.html"), "w", encoding="utf-8") as f:
        f.write(html)


def render_storefront_homepage(published_prods: list, reviews: list, today: str):
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(os.path.join(DOCS_DIR, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    latest_prods = list(reversed(published_prods))[:48]
    latest_revs = list(reversed(reviews))[:12]

    cat_tiles = ""
    for c in TAXONOMY:
        subs = " &bull; ".join(s["name"] for s in c["subcategories"])
        cat_tiles += f"""
        <a href="{SITE_URL}/categories/{c['cat_slug']}.html" class="card" style="text-decoration:none;color:inherit;">
            <div class="card-body">
                <div>
                    <div style="font-size:2rem;margin-bottom:8px;">{c['icon']}</div>
                    <h3 style="font-size:1.1rem;color:var(--navy);margin-bottom:6px;">{c['category']}</h3>
                    <p style="font-size:0.83rem;color:var(--slate);">{subs}</p>
                </div>
                <span style="margin-top:14px;font-size:0.84rem;font-weight:700;color:var(--cyan);">Explore Security Category &rarr;</span>
            </div>
        </a>
        """

    prod_cards = ""
    for p in latest_prods:
        amz_url = make_amazon_url(p["search_query"])
        prod_cards += f"""
        <article class="card prod-card" data-cat="{p['cat_slug']}">
            <img src="{p['image_url']}" alt="{p['name']}" class="card-img" loading="lazy">
            <div class="card-body">
                <div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span class="pill" style="margin:0;">{p['cat_icon']} {p['subcategory']}</span>
                        <span style="font-size:0.74rem;font-weight:700;color:var(--emerald);">★ Verified Spec</span>
                    </div>
                    <h3 style="font-size:1.06rem;margin-bottom:8px;"><a href="{SITE_URL}/products/{p['slug']}.html" style="color:var(--navy);text-decoration:none;">{p['name']}</a></h3>
                    <p style="font-size:0.85rem;color:var(--slate);margin-bottom:10px;">{p['summary']}</p>
                </div>
                <div>
                    <div class="micro-disclosure">As an Amazon Associate I earn from qualifying purchases.</div>
                    <div style="display:flex;gap:8px;">
                        <a href="{amz_url}" target="_blank" rel="nofollow sponsored noopener noreferrer" class="btn-amz" style="flex:1;">Check Price on Amazon</a>
                        <a href="{SITE_URL}/products/{p['slug']}.html" class="btn-outline">Specs</a>
                    </div>
                </div>
            </div>
        </article>
        """

    rev_cards = ""
    for r in latest_revs:
        rev_cards += f"""
        <article class="card">
            <img src="{r['image_url']}" alt="{r['title']}" class="card-img" loading="lazy">
            <div class="card-body">
                <div>
                    <span class="pill">{r['category']}</span>
                    <h3 style="font-size:1.08rem;margin-bottom:8px;"><a href="{SITE_URL}/reviews/{r['slug']}.html" style="color:var(--navy);text-decoration:none;">{r['title']}</a></h3>
                    <p style="font-size:0.85rem;color:var(--slate);">{r['excerpt']}</p>
                </div>
                <div style="margin-top:14px;">
                    <a href="{SITE_URL}/reviews/{r['slug']}.html" class="btn-outline" style="width:100%;">Read 4-System Comparison &rarr;</a>
                </div>
            </div>
        </article>
        """

    filter_btns = '<button class="f-btn active" onclick="filterDept(\'all\', this)">All Security Systems</button>'
    for c in TAXONOMY:
        filter_btns += f'<button class="f-btn" onclick="filterDept(\'{c["cat_slug"]}\', this)">{c["icon"]} {c["category"]}</button>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AegisDomus US — Smart Home &amp; Security Tech Buying Guides &amp; Storefront</title>
    <meta name="description" content="Compare verified specifications across 4K Solar Security Cameras, PoE NVR Systems, 3D Biometric Smart Locks, Dual-Cam Video Doorbells, Wi-Fi 7 Mesh Routers, and Ultrasonic Water Shutoff Valves.">
    <link rel="canonical" href="{SITE_URL}/">
    <style>
        {get_common_styles()}
        .hero-banner {{ background: linear-gradient(135deg, #090d16 0%, #0c4a6e 100%); color: #ffffff; padding: 56px 20px; }}
        .hero-inner {{ max-width: 1260px; margin: 0 auto; display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 32px; align-items: center; }}
        .hero-badge {{ display: inline-block; background: rgba(56,189,248,0.18); border: 1px solid #38bdf8; color: #7dd3fc; font-size: 0.78rem; font-weight: 700; padding: 5px 12px; border-radius: 999px; margin-bottom: 14px; }}
        .hero-banner h1 {{ font-size: 2.35rem; line-height: 1.2; margin-bottom: 14px; }}
        .search-bar {{ display: flex; gap: 10px; margin-top: 22px; max-width: 620px; }}
        .search-bar input {{ flex: 1; padding: 14px 18px; border-radius: 10px; border: none; font-size: 1rem; outline: none; }}
        .filter-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 22px 0; }}
        .f-btn {{ background: var(--surface); border: 1px solid var(--border); color: var(--navy); padding: 7px 13px; border-radius: 999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; }}
        .f-btn.active, .f-btn:hover {{ background: var(--cyan); color: #fff; border-color: var(--cyan); }}
        .sec-head {{ display: flex; justify-content: space-between; align-items: baseline; margin: 46px 0 20px; border-bottom: 2px solid var(--border); padding-bottom: 10px; flex-wrap: wrap; gap: 10px; }}
        @media (max-width: 820px) {{ .hero-inner {{ grid-template-columns: 1fr; }} .hero-banner h1 {{ font-size: 1.85rem; }} }}
    </style>
</head>
<body>
    {build_header_html()}
    <section class="hero-banner">
        <div class="hero-inner">
            <div>
                <span class="hero-badge">SMART HOME &amp; SECURITY SPECIALIST &bull; AUTO-UPDATED EVERY 12 HOURS</span>
                <h1>Next-Gen Perimeter Cameras, Biometric Locks &amp; Whole-Home Automation</h1>
                <p style="color:#e0f2fe;font-size:1.04rem;">Compare verified specifications across 4K Dual-Lens Solar Cameras, Hardwired PoE NVR Kits, Palm-Vein &amp; Apple HomeKey Deadbolts, Package-Guard Doorbells, Wi-Fi 7 Mesh Firewalls, and Auto Water Shutoff Valves.</p>
                <div class="search-bar">
                    <input type="text" id="liveSearch" placeholder="Search brand or system (e.g. Reolink, eufy, Schlage, UniFi, Ecobee, Matter, PoE)..." onkeyup="runSearch()">
                </div>
            </div>
            <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.2);border-radius:16px;padding:24px;">
                <div style="font-size:0.78rem;color:#7dd3fc;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Security Catalog Status</div>
                <div style="font-size:1.6rem;font-weight:900;margin-bottom:4px;">{len(published_prods)} Verified Devices</div>
                <div style="font-size:0.9rem;color:#e0f2fe;margin-bottom:14px;">{len(reviews)} Side-by-Side Security Guides</div>
                <a href="#featured" class="btn-amz" style="width:100%;">Browse Featured Security Picks &darr;</a>
            </div>
        </div>
    </section>

    <main class="container">
        <div class="sec-head" id="departments">
            <h2>Browse by Smart Home &amp; Security Department</h2>
            <span style="font-size:0.85rem;color:var(--slate);">6 Specialized Security Categories &bull; 18 Subcategories</span>
        </div>
        <div class="grid-3">{cat_tiles}</div>

        <div class="sec-head" id="featured">
            <h2>Featured Smart Home &amp; Security Products</h2>
            <span style="font-size:0.85rem;color:var(--slate);">+20 New Devices Published Every 12 Hours</span>
        </div>
        <div class="filter-row">{filter_btns}</div>
        <div class="grid-3" id="productsContainer">{prod_cards}</div>

        <div class="sec-head" id="reviews">
            <h2>Latest 12-Hour Comparative Security Review Articles</h2>
            <span style="font-size:0.85rem;color:var(--slate);">+5 New 4-System Buying Guides Every 12 Hours</span>
        </div>
        <div class="grid-3">{rev_cards}</div>
    </main>

    {build_footer_html(today)}
    <script>
        function runSearch() {{
            const q = document.getElementById('liveSearch').value.toLowerCase();
            document.querySelectorAll('.prod-card').forEach(card => {{
                card.style.display = card.innerText.toLowerCase().includes(q) ? '' : 'none';
            }});
        }}
        function filterDept(catSlug, btn) {{
            document.querySelectorAll('.f-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('.prod-card').forEach(card => {{
                if (catSlug === 'all' || card.getAttribute('data-cat') === catSlug) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>"""

    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def build_seo_feeds_and_ping_all_engines(published_prods: list, reviews: list, cat_urls: list, new_urls: list, today: str):
    # 1. Sitemap XML
    urls_xml = f"  <url><loc>{SITE_URL}/</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>\n"
    urls_xml += f"  <url><loc>{SITE_URL}/legal.html</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.5</priority></url>\n"

    for c_url in cat_urls:
        urls_xml += f"  <url><loc>{c_url}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>\n"
    for r in reviews:
        urls_xml += f"  <url><loc>{r['url']}</loc><lastmod>{r['published_at']}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>\n"
    for p in published_prods:
        urls_xml += f"  <url><loc>{SITE_URL}/products/{p['slug']}.html</loc><lastmod>{p.get('published_at', today)}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>\n"

    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls_xml}</urlset>'
    with open(os.path.join(DOCS_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    # 2. RSS 2.0 Feed dengan Google PubSubHubbub / WebSub Hub
    rss_items = ""
    for r in list(reversed(reviews))[:15]:
        rss_items += f"""    <item>
      <title>{r['title']}</title>
      <link>{r['url']}</link>
      <guid>{r['url']}</guid>
      <description>{r['excerpt']}</description>
    </item>\n"""
    for p in list(reversed(published_prods))[:25]:
        p_url = f"{SITE_URL}/products/{p['slug']}.html"
        rss_items += f"""    <item>
      <title>{p['name']}</title>
      <link>{p_url}</link>
      <guid>{p_url}</guid>
      <description>{p['summary']}</description>
    </item>\n"""

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>AegisDomus US — Smart Home &amp; Security Tech Storefront</title>
    <link>{SITE_URL}/</link>
    <description>Automated 12-Hour Smart Home &amp; Security Tech Reviews and Buying Guides</description>
    <atom:link href="https://pubsubhubbub.appspot.com/" rel="hub" />
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />
{rss_items}  </channel>
</rss>"""
    with open(os.path.join(DOCS_DIR, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(rss_xml)

    # 3. robots.txt & file verifikasi IndexNow
    with open(os.path.join(DOCS_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")

    with open(os.path.join(DOCS_DIR, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)

    if "username.github.io" in SITE_URL or not new_urls:
        return

    # 4. Ping IndexNow API (Otomatis mendaftarkan URL ke Bing, Yahoo, DuckDuckGo, Yandex, Naver, Seznam)
    host = SITE_URL.replace("https://", "").replace("http://", "").split("/")[0]
    payload = {
        "host": host,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
        "urlList": new_urls[:100]
    }
    for endpoint in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow", "https://yandex.com/indexnow"]:
        try:
            r = requests.post(endpoint, json=payload, timeout=12)
            print(f"[SEO] IndexNow Ping ({endpoint}) Status: {r.status_code}")
        except Exception as e:
            print(f"[WARN] IndexNow Ping gagal ({endpoint}): {e}")

    # 5. Ping Google WebSub / PubSubHubbub Hub
    try:
        r_google = requests.post(
            "https://pubsubhubbub.appspot.com/",
            data={"hub.mode": "publish", "hub.url": f"{SITE_URL}/feed.xml"},
            timeout=12
        )
        print(f"[SEO] Google WebSub Ping Status: {r_google.status_code}")
    except Exception as e:
        print(f"[WARN] Google WebSub Ping gagal: {e}")


def main():
    state = init_or_load_state()
    img_cache = load_image_cache()
    products = state["products"]
    reviews = state["reviews"]
    cycle = state.get("cycle_count", 0) + 1
    state["cycle_count"] = cycle
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    unpublished = [p for p in products if not p.get("published")]
    if len(unpublished) < 20:
        for p in products:
            p["published"] = False
        unpublished = products

    batch_20 = unpublished[:20]
    new_urls = [f"{SITE_URL}/"]

    # Ambil gambar stok gratis via API publik (Openverse / Wikimedia Commons) untuk 20 produk baru
    for p in batch_20:
        if not p.get("image_url"):
            img_info = fetch_free_stock_image(p["img_q"], p["idx"], img_cache)
            p["image_url"] = img_info["url"]
            p["image_credit"] = img_info["credit"]
            time.sleep(0.2)
        p["published"] = True
        p["published_at"] = today

    save_image_cache(img_cache)
    published_prods = [p for p in products if p.get("published")]

    for p in published_prods:
        if not p.get("image_url"):
            img_info = fetch_free_stock_image(p["img_q"], p["idx"], img_cache)
            p["image_url"] = img_info["url"]
            p["image_credit"] = img_info["credit"]

    for p in published_prods:
        same_cat = [x for x in published_prods if x["cat_slug"] == p["cat_slug"]]
        url = render_product_page(p, same_cat, today)
        if p in batch_20:
            new_urls.append(url)

    # Buat 5 artikel review komparatif baru setiap 12 jam (masing-masing membandingkan 4 produk)
    for i in range(0, len(batch_20), 4):
        group = batch_20[i:i + 4]
        if len(group) == 4:
            rev_meta = render_review_article(group, cycle, (i // 4) + 1, today)
            reviews.append(rev_meta)
            new_urls.append(rev_meta["url"])

    cat_urls = render_category_and_subcategory_pages(published_prods, today)
    render_legal_page(today)
    render_storefront_homepage(published_prods, reviews, today)

    save_state(state)
    build_seo_feeds_and_ping_all_engines(published_prods, reviews, cat_urls, new_urls, today)

    print(f"[DONE] Siklus #{cycle}: +20 Produk Smart Home & Security + 5 Artikel Review berhasil dipublikasikan dan didaftarkan ke IndexNow & Google WebSub.")


if __name__ == "__main__":
    main()
