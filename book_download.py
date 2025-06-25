import shlex
import urllib.request
import urllib.parse
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess

curl_bash_cmd = """
curl 'https://r3-ndr-private.ykt.cbern.com.cn/edu_product/esp/assets/e5618f17-c06e-4c4c-944e-0ee8ced25391.pkg/%E4%B9%89%E5%8A%A1%E6%95%99%E8%82%B2%E6%95%99%E7%A7%91%E4%B9%A6%20%E7%89%A9%E7%90%86%20%E5%85%AB%E5%B9%B4%E7%BA%A7%20%E4%B8%8A%E5%86%8C_1725097555765.pdf' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'if-none-match: "f813272e25506c083e04079e7ba9a042"' \
  -H 'origin: https://basic.smartedu.cn' \
  -H 'priority: u=1, i' \
  -H 'range: bytes=0-65535' \
  -H 'referer: https://basic.smartedu.cn/' \
  -H 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: cross-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' \
  -H 'x-nd-auth: MAC id="7F938B205F876FC398BCDC5BCE419D07B10490E81C34C6651A79321A13F10AAE8BCAA05E3D1DD833B954BF13E4BAF5317924342E0D234CBD",nonce="1750837810649:B91T6955",mac="K2OycMxZonb3jtCMmkIdRFg6jI2Y7BVIR7m65g6mCVA="'
"""

def download_file_from_curl(curl_command):
    # Parse the curl command
    lexer = shlex.shlex(curl_command, posix=True)
    lexer.whitespace_split = True
    lexer.escape = '' # Disable escape character handling to treat '' as a literal character
    parts = list(lexer)

    url = None
    headers = {}

    i = 0
    while i < len(parts):
        part = parts[i]
        if part.startswith('http'):
            url = part.strip("'")
        elif part == '-H':
            i += 1
            header_parts = parts[i].strip("'").split(': ', 1)
            if len(header_parts) == 2:
                key, value = header_parts
                if key.lower() != 'range' and key.lower() != 'if-none-match':  # Exclude the 'range' and 'if-none-match' headers
                    headers[key] = value
        i += 1

    if not url:
        messagebox.showerror("Error", "URL not found in curl command.")
        return

    # Create a Request object
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            # Extract filename from the URL
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(urllib.parse.unquote(parsed_url.path))

            if not filename:
                messagebox.showerror("Error", "Could not determine filename from URL.")
                return

            # Save the content to a local file
            with open(filename, 'wb') as f:
                f.write(response.read())
            messagebox.showinfo("Success", f"Downloaded '{filename}' successfully.")

            # Open the containing directory and select the downloaded file
            try:
                file_path = os.path.join(os.getcwd(), filename)
                subprocess.run(["explorer.exe", "/select,", file_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file explorer: {e}")
    except urllib.error.URLError as e:
        messagebox.showerror("Download Error", f"Error downloading the file: {e.reason}")
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

def create_gui():
    window = tk.Tk()
    window.title("Book Downloader")

    # Text area for curl command input
    lbl = tk.Label(window, text="Paste Curl(Bash) Command Here:")
    lbl.pack()

    txt_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20)
    txt_area.pack()

    def on_download_click():
        curl_cmd = txt_area.get(1.0, tk.END).strip()
        if curl_cmd:
            download_file_from_curl(curl_cmd)
        else:
            messagebox.showwarning("Input Error", "Please paste a curl command.")

    btn = tk.Button(window, text="Download", command=on_download_click)
    btn.pack()

    window.mainloop()

if __name__ == "__main__":
    create_gui()

