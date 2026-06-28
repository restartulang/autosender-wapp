from dataclasses import dataclass
from datetime import datetime, timezone
import re

@dataclass
class ParseResult:
    tipe: str
    target_utc: datetime
    raw: str
    stasiun: str = ''
    is_valid: bool = True
    error_msg: str = ''

def _build_target_utc(dd: int, hh: int, mm: int, now_utc: datetime) -> datetime:
    year = now_utc.year
    month = now_utc.month
    
    if dd < now_utc.day - 1:
        month += 1
        if month > 12:
            month = 1
            year += 1
            
    try:
        return datetime(year, month, dd, hh, mm, tzinfo=timezone.utc)
    except ValueError as e:
        raise ValueError(str(e))

def format_gts(raw_text: str) -> str:
    """Format sandi into standard GTS format (newlines after header/report id)."""
    clean = re.sub(r'\s+', ' ', raw_text.strip())
    
    # Extract WMO Header
    m = re.search(r'^([A-Z]{4}\d{2}\s[A-Z]{4}\s\d{6})', clean)
    if m:
        header = m.group(1)
        rest = clean[m.end():].strip()
        
        # Check for AAXX/BBXX (SYNOP/SHIP) or WXREV
        m2 = re.match(r'^(AAXX|BBXX|WXREV)\s\d{5}', rest)
        if m2:
            report_id = m2.group(0)
            rest = rest[m2.end():].strip()
            return f'{header}\n{report_id}\n{rest}'
            
        # Check for METAR/SPECI/TAF
        m3 = re.match(r'^(METAR|SPECI|TAF)', rest)
        if m3:
            report_id = m3.group(0)
            rest = rest[m3.end():].strip()
            return f'{header}\n{report_id} {rest}'
            
        # Fallback if no specific report id
        return f'{header}\n{rest}'
        
    return raw_text.strip()

def parse(raw_text: str, now_utc: datetime = None) -> ParseResult:
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    # Format the text correctly before parsing
    formatted_text = format_gts(raw_text)

    # 1. GTS BMKG Format Validation
    # Format: TTAAii CCCC YYGGgg
    # Example: SAID31 WAPP 221200
    ahl_pattern = re.compile(r'^([A-Z]{4})\d{2}\s([A-Z]{4})\s(\d{2})(\d{2})(\d{2})', re.MULTILINE)
    m_ahl = ahl_pattern.search(formatted_text)
    
    has_equal = bool(re.search(r'=\s*$', formatted_text.strip()))
    
    if not m_ahl:
        return ParseResult(tipe='UNKNOWN', target_utc=now_utc, raw=formatted_text, is_valid=False, 
                           error_msg="Sandi tidak memiliki WMO Header yang valid (contoh: SAID31 WAPP 221200).")
    if not has_equal:
        return ParseResult(tipe='UNKNOWN', target_utc=now_utc, raw=formatted_text, is_valid=False, 
                           error_msg="Sandi tidak diakhiri dengan tanda '='.")

    ttaa = m_ahl.group(1).upper()
    stasiun = m_ahl.group(2).upper()
    dd, hh, mm = int(m_ahl.group(3)), int(m_ahl.group(4)), int(m_ahl.group(5))
    
    # Deteksi tipe berdasarkan WMO Header (seperti BMKGSoft)
    if ttaa == 'SAID':
        tipe = 'METAR'
    elif ttaa == 'SPID':
        tipe = 'SPECI'
    elif ttaa in ['SMID', 'SIID', 'SNID']:
        tipe = 'SYNOP'
    elif ttaa == 'FTID':
        tipe = 'TAFOR'
    elif ttaa == 'MMID':
        tipe = 'WXREV'
    else:
        tipe = 'UNKNOWN'
        return ParseResult(tipe=tipe, target_utc=now_utc, raw=formatted_text, is_valid=False, 
                           error_msg=f"Header {ttaa} tidak dikenali oleh BMKGSoft.")

    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        return ParseResult(tipe=tipe, target_utc=now_utc, raw=formatted_text, is_valid=False, 
                           error_msg=f"Waktu pada header invalid: HH={hh}, MM={mm}")
        
    try:
        target = _build_target_utc(dd, hh, mm, now_utc)
        return ParseResult(tipe=tipe, target_utc=target, raw=formatted_text, stasiun=stasiun)
    except ValueError as e:
        return ParseResult(tipe=tipe, target_utc=now_utc, raw=formatted_text, is_valid=False, error_msg=f"Tanggal invalid: {e}")
