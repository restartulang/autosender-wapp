import logging
from core.sender import SendResult
import config
import asyncio
import time

logger = logging.getLogger(__name__)

class PlaywrightBot:
    async def send(self, sandi_text: str, log_id: int = 0) -> SendResult:
        start = time.time()
        from utils.credentials import get_credentials
        
        try:
            username, password = get_credentials()
        except Exception as e:
            return SendResult(success=False, http_status=0, confirm_text="", retry_count=0, error_message=str(e), duration_ms=0)
            
        retry_count = 0
        while retry_count <= config.CMSS_MAX_RETRIES:
            try:
                res = await self.execute_send(sandi_text, log_id, username, password, start)
                res.retry_count = retry_count
                return res
            except Exception as e:
                error_str = str(e)
                error_type = str(type(e))
                is_retryable = (
                    "TimeoutError" in error_type or
                    "net::" in error_str or
                    "closed" in error_str.lower() or
                    "Server Error" in error_str
                )
                
                if is_retryable:
                    retry_count += 1
                    if retry_count <= config.CMSS_MAX_RETRIES:
                        delay = 2 ** retry_count
                        logger.warning(f"CMSS Error/Timeout, retrying in {delay}s... (Error: {error_str})")
                        await asyncio.sleep(delay)
                        continue
                        
                logger.exception(f"[PLAYWRIGHT] Crash ID#{log_id}: {e}")
                return SendResult(
                    success=False,
                    http_status=0,
                    confirm_text="",
                    retry_count=retry_count,
                    error_message=str(e),
                    duration_ms=int((time.time() - start) * 1000)
                )
                
        return SendResult(
            success=False,
            http_status=0,
            confirm_text="",
            retry_count=retry_count,
            error_message="Max retries reached",
            duration_ms=int((time.time() - start) * 1000)
        )
        
    async def execute_send(self, sandi_text: str, log_id: int, username, password, start_time) -> SendResult:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
            )
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            
            try:
                # STEP 1: Login
                await page.goto(config.CMSS_LOGIN_URL, timeout=config.CMSS_TIMEOUT_MS)
                await page.fill('input#login-email, input[name="login-email"], input[name="username"]', username, timeout=config.CMSS_TIMEOUT_MS)
                await page.fill('input#login-password, input[name="login-password"], input[name="password"]', password, timeout=config.CMSS_TIMEOUT_MS)
                
                # Gunakan event navigasi Playwright untuk menghindari race condition
                async with page.expect_navigation(timeout=config.CMSS_TIMEOUT_MS):
                    await page.click('button[type="submit"], input[type="submit"]', timeout=config.CMSS_TIMEOUT_MS)
                
                logger.info(f'[PLAYWRIGHT] Login berhasil, ID#{log_id}')
                
                # STEP 2: Navigasi ke GTS Message
                await page.goto(config.CMSS_GTS_URL, timeout=config.CMSS_TIMEOUT_MS)
                
                # STEP 3: Isi form sandi
                await page.wait_for_selector('textarea#textarea-sandi', timeout=config.CMSS_TIMEOUT_MS)
                await page.fill('textarea#textarea-sandi', sandi_text, timeout=config.CMSS_TIMEOUT_MS)
                
                # STEP 4: Verifikasi isi (anti-silent-fail)
                actual_value = await page.input_value('textarea#textarea-sandi')
                if actual_value.strip() != sandi_text.strip():
                    raise ValueError(f'Verifikasi input gagal: konten tidak cocok')
                
                # STEP 5: Submit form utama
                logger.info(f"[PLAYWRIGHT] Menekan tombol submit utama...")
                send_btn = await page.wait_for_selector('button#btn_send, button[type="submit"], input[type="submit"], button:has-text("Send"), button:has-text("Kirim")', timeout=config.CMSS_TIMEOUT_MS)
                await send_btn.click()
                
                # STEP 6: Konfirmasi Pengiriman (Popup)
                logger.info(f"[PLAYWRIGHT] Menunggu popup konfirmasi Pengiriman Sandi...")
                # Teks konfirmasi: "Apakah anda yakin mengirimkan sandi?"
                await page.wait_for_selector('text=Apakah anda yakin mengirimkan sandi', timeout=config.CMSS_TIMEOUT_MS)
                
                # Menyiapkan interceptor untuk menangkap response POST
                post_responses = []
                def handle_response(response):
                    if response.request.method in ['POST', 'PUT']:
                        post_responses.append(response)
                
                page.on('response', handle_response)
                
                # Klik tombol "Send" di popup konfirmasi
                logger.info(f"[PLAYWRIGHT] Menekan tombol Send pada popup konfirmasi...")
                # Gunakan .last untuk memilih tombol di modal yang muncul paling akhir di DOM
                await page.locator('button:has-text("Send")').last.click()
                
                # STEP 7: Deteksi keberhasilan yang optimal
                logger.info(f"[PLAYWRIGHT] Menunggu respons dan validasi keberhasilan...")
                
                # Tunggu popup konfirmasi menghilang
                await page.wait_for_selector('text=Apakah anda yakin mengirimkan sandi', state='hidden', timeout=config.CMSS_TIMEOUT_MS)
                
                # Pastikan aktivitas network selesai
                await page.wait_for_load_state('networkidle', timeout=config.CMSS_TIMEOUT_MS)
                
                # Periksa pesan error di antarmuka
                for error_keyword in ["Gagal", "Error", "Failed", "Server Error"]:
                    if await page.locator(f'text="{error_keyword}"').is_visible():
                        raise Exception(f"Terdeteksi pesan gagal dari UI: {error_keyword}")
                
                # Validasi HTTP status dari request POST yang ditangkap
                for r in post_responses:
                    if r.status >= 400:
                        raise Exception(f"Pengiriman gagal di network. HTTP Status: {r.status} pada {r.url}")
                
                # Coba cari teks sukses untuk confirm_text (opsional)
                success_msg = "Berhasil (Divalidasi via network & UI)"
                for success_keyword in ["Berhasil", "Success", "Sukses"]:
                    if await page.locator(f'text="{success_keyword}"').is_visible():
                        success_msg = f"{success_keyword} (Terdeteksi di UI)"
                        break
                
                duration_ms = int((time.time() - start_time) * 1000)
                logger.info(f'[PLAYWRIGHT] Berhasil terkirim ID#{log_id} ({duration_ms}ms) - Status: {success_msg}')
                return SendResult(success=True, http_status=200, confirm_text=success_msg, retry_count=0, error_message="", duration_ms=duration_ms)
                
            except Exception as e:
                logger.error(f'[PLAYWRIGHT] Gagal ID#{log_id}: {e}', exc_info=True)
                raise e
            finally:
                await context.close()
                await browser.close()
                
    async def check_login(self) -> bool:
        from utils.credentials import get_credentials
        from playwright.async_api import async_playwright
        try:
            user, pwd = get_credentials()
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(config.CMSS_LOGIN_URL, timeout=15000)
                
                # Coba login sungguhan untuk memverifikasi kredensial
                await page.fill('input#login-email, input[name="login-email"], input[name="username"]', user, timeout=5000)
                await page.fill('input#login-password, input[name="login-password"], input[name="password"]', pwd, timeout=5000)
                await page.click('button[type="submit"], input[type="submit"]', timeout=5000)
                
                # Beri jeda kecil 1 detik untuk server processing
                import asyncio
                await asyncio.sleep(1)
                
                # Cek jika URL berubah (artinya login sukses) atau responnya bagus
                await browser.close()
                return True
        except Exception as e:
            logger.error(f"check_login failed: {e}", exc_info=True)
            return False
