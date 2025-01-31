import requests
import re
import random
import string
import base64
import urllib.parse
import json
import time
import os
import sys
from requests_toolbelt import MultipartEncoder
from rich import print as printf
from PIL import Image
import pytesseract
from rich.panel import Panel
from rich.console import Console
from requests.exceptions import RequestException

# Variáveis globais
COOKIES, SUKSES, LOGOUT, GAGAL = {"Cookie": None}, [], [], []

class DIPERLUKAN:
    def __init__(self) -> None:
        pass

    def LOGIN(self):
        with requests.Session() as session:
            session.headers.update(
                {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Host': 'zefoy.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document'
                }
            )
            response = session.get('https://zefoy.com/').text
            if 'Sorry, you have been blocked' in str(response) or 'Just a moment...' in str(response):
                printf(Panel(f"[bold red]Zefoy server is currently affected by Cloudflare. Try again later.\nVisit [bold green]zefoy.com[bold red] to check.", width=56, style="bold bright_white", title="[bold bright_white][ Cloudflare ]"))
                sys.exit()
            else:
                self.captcha_image = re.search(r'src="(.*?)" onerror="errimg\(\)"', str(response)).group(1).replace('amp;', '')
                self.form = re.search(r'type="text" name="(.*?)"', str(response)).group(1)
                session.headers.update(
                    {
                        'Cookie': "; ".join([str(x) + "=" + str(y) for x, y in session.cookies.get_dict().items()]),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
                    }
                )
                response2 = session.get('https://zefoy.com{}'.format(self.captcha_image))

                with open('Penyimpanan/Gambar.png', 'wb') as w:
                    w.write(response2.content)
                w.close()
                session.headers.update(
                    {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Connection': 'keep-alive',
                        'Origin': 'null',
                        'Cache-Control': 'max-age=0',
                        'Cookie': "; ".join([str(x) + "=" + str(y) for x, y in session.cookies.get_dict().items()])
                    }
                )
                data = {
                    self.form: self.BYPASS_CAPTCHA(),
                }
                response3 = session.post('https://zefoy.com/', data=data).text

                if 'placeholder="Enter Video URL"' in str(response3):
                    COOKIES.update(
                        {
                            "Cookie": "; ".join([str(x) + "=" + str(y) for x, y in session.cookies.get_dict().items()])
                        }
                    )
                    printf(f"[bold bright_white]   ──>[bold green] LOGIN SUCCESSFUL!                ", end='\r')
                    time.sleep(2.5)
                    return COOKIES['Cookie']
                else:
                    printf(f"[bold bright_white]   ──>[bold red] LOGIN FAILED!                     ", end='\r')
                    time.sleep(2.5)
                    return False

    def BYPASS_CAPTCHA(self):
        self.file_gambar = 'Penyimpanan/Gambar.png'
        self.image = Image.open(self.file_gambar)
        self.image_string = pytesseract.image_to_string(self.image)
        return self.image_string.replace('\n', '')

    def MENDAPATKAN_FORMULIR(self, video_url):
        with requests.Session() as session:
            session.headers.update(
                {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Host': 'zefoy.com',
                    'Cookie': f'{COOKIES["Cookie"]}; window_size=1280x551; user_agent=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F131.0.0.0%20Safari%2F537.36; language=en-US; languages=en-US; cf-locale=en-US;',
                    'Sec-Fetch-Site': 'none',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                }
            )
            response = session.get('https://zefoy.com/').text

            if 'placeholder="Enter Video URL"' in str(response):
                self.video_form = re.search(r'name="(.*?)" placeholder="Enter Video URL"', str(response)).group(1)
                self.post_action = re.findall(r'action="(.*?)">', str(response))[3]
                printf(f"[bold bright_white]   ──>[bold green] SUCCESSFULLY FOUND VIDEO FORM!   ", end='\r')
                time.sleep(1.5)
                self.MENGIRIMKAN_FAVORITOS(self.video_form, self.post_action, video_url)
            else:
                printf(f"[bold bright_white]   ──>[bold red] VIDEO FORM NOT FOUND!        ", end='\r')
                time.sleep(3.5)
                COOKIES.update({"Cookie": None})
                return False

    def MENGIRIMKAN_FAVORITOS(self, video_form, post_action, video_url):
        global SUKSES, GAGAL
        with requests.Session() as session:
            boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
            session.headers.update(
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Cookie': f'{COOKIES["Cookie"]}; {self.BYPASS_IKLAN_GOOGLE()}; window_size=1280x551; user_agent=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F131.0.0.0%20Safari%2F537.36; language=en-US; languages=en-US; time_zone=Asia/Jakarta; cf-locale=en-US;',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Connection': 'keep-alive',
                    'Origin': 'https://zefoy.com',
                    'Sec-Fetch-Dest': 'empty',
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'Accept': '*/*'
                }
            )

            data = MultipartEncoder(
                {video_form: (None, video_url)},
                boundary=boundary
            )

            response = session.post(f'https://zefoy.com/{post_action}', data=data).text
            self.base64_string = self.DECRYPTION