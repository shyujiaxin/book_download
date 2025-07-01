"""
Book downloader module for downloading files using curl commands via GUI.

This module provides a graphical user interface for downloading files by parsing
curl commands. It extracts the URL and headers from curl commands and downloads
files using Python's urllib library.

Features:
- Parse curl commands and extract URLs and headers
- Download files with proper headers
- GUI interface for easy input
- Automatic file explorer opening after download
- Error handling and user feedback

Example:
    python book_download.py
    # Opens GUI where you can paste a curl command and download the file
"""

import os
import shlex
import subprocess
import tkinter as tk
import urllib.parse
import urllib.request
import webbrowser
import yaml
from tkinter import font
from tkinter import messagebox, scrolledtext


def download_file_from_curl(curl_command, log_callback):
    """
    Download a file by parsing a curl command and extracting URL and headers.
    
    This function parses a curl command string to extract the target URL and
    relevant headers, then downloads the file using urllib.request. It excludes
    certain headers like 'range' and 'if-none-match' that might interfere with
    the download process.
    
    Args:
        curl_command (str): A complete curl command string, typically copied from
                           browser developer tools or curl command line.
        log_callback (function): A function to call for logging messages.
    
    Returns:
        None: This function doesn't return a value but logs feedback and saves
              the downloaded file to the current directory.
    
    Raises:
        No explicit exceptions are raised, but error messages are logged for
        various error conditions including:
        - URL not found in curl command
        - Network errors during download
        - File system errors
        - Invalid URL format
    
    Example:
        >>> def my_logger(msg):
        ...     print(msg)
        >>> curl_cmd = '''curl 'https://example.com/file.pdf' \\
        ...   -H 'accept: */*' \\
        ...   -H 'user-agent: Mozilla/5.0...' '''
        >>> download_file_from_curl(curl_cmd, my_logger)
        # Downloads file.pdf to current directory and logs success message
    
    Note:
        - The downloaded file is saved in the current working directory
        - After successful download, Windows Explorer opens to show the file
        - Headers 'range' and 'if-none-match' are automatically excluded
        - The filename is extracted from the URL path
    """
    log_callback("Parsing curl command...")
    # Parse the curl command
    lexer = shlex.shlex(curl_command, posix=True)
    lexer.whitespace_split = True
    lexer.escape = ""  # Disable escape character handling to treat '' as a literal character
    parts = list(lexer)

    url = None
    headers = {}

    i = 0
    while i < len(parts):
        part = parts[i]
        if part.startswith("http"):
            url = part.strip("'")
        elif part == "-H":
            i += 1
            header_parts = parts[i].strip("'").split(": ", 1)
            if len(header_parts) == 2:
                key, value = header_parts
                if key.lower() not in ["range", "if-none-match", "if-modified-since"]:  # Exclude headers that prevent full download
                    headers[key] = value
        i += 1

    if not url:
        log_callback("Error: URL not found in curl command.")
        return

    unquoted_url = urllib.parse.unquote(url)
    log_callback(f"Found URL: {unquoted_url}")
    if headers:
        log_callback(f"Found headers:\n{yaml.dump(headers, default_flow_style=False, allow_unicode=True)}")
    else:
        log_callback("No headers found.")

    # Create a Request object
    log_callback("Creating request object...")
    req = urllib.request.Request(url, headers=headers)

    try:
        log_callback(f"Starting download from {unquoted_url}...")
        with urllib.request.urlopen(req) as response:
            log_callback("Successfully opened URL.")
            # Extract filename from the URL
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(urllib.parse.unquote(parsed_url.path))

            if not filename:
                log_callback("Error: Could not determine filename from URL.")
                return

            log_callback(f"Determined filename: {filename}")

            # Save the content to a local file
            log_callback(f"Saving content to '{filename}'...")
            with open(filename, "wb") as f:
                f.write(response.read())
            log_callback(f"Downloaded '{filename}' successfully.")

            # Open the containing directory and select the downloaded file
            try:
                log_callback("Opening file explorer to show the downloaded file...")
                file_path = os.path.join(os.getcwd(), filename)
                subprocess.run(["explorer.exe", "/select,", file_path], check=False)
            except (subprocess.SubprocessError, OSError) as e:
                log_callback(f"Error: Could not open file explorer: {e}")
    except urllib.error.URLError as e:
        log_callback(f"Download Error: {e.reason}")
    except (OSError, IOError) as e:
        log_callback(f"File System Error: Error saving the file: {e}")
    except ValueError as e:
        log_callback(f"Value Error: Invalid URL or data format: {e}")


def create_gui():
    """
    Create and display the main GUI window for the book downloader application.

    This function creates a tkinter-based graphical user interface with:
    - A label instructing users to paste curl commands
    - A large text area for inputting curl commands
    - A download button to initiate the download process
    - A log display area for showing detailed progress and errors

    Args:
        None: This function takes no parameters.

    Returns:
        None: This function doesn't return a value but starts the GUI event loop.

    Raises:
        No explicit exceptions are raised.

    Example:
        >>> create_gui()
        # Opens a window with text area, download button, and log display

    Note:
        - The GUI runs in the main thread and blocks until the window is closed
        - The window title is set to "Book Downloader"
        - The text area supports scrolling and word wrapping
        - The download button triggers the download_file_from_curl function
        - Input validation is performed before attempting download
    """
    window = tk.Tk()
    window.title("Book Downloader")

    # Define a default font for the application
    app_font = font.Font(family="Calibri", size=9)

    # Banner with hyperlink
    url = "https://basic.smartedu.cn/tchMaterial"
    banner_label = tk.Label(window, text=f"{url}", fg="blue", cursor="hand2", font=app_font)
    banner_label.pack(pady=5)

    # Apply underline directly
    underline_font = font.Font(banner_label, banner_label.cget("font"))
    underline_font.configure(underline=True)
    banner_label.configure(font=underline_font)

    def open_link(_event):
        webbrowser.open_new(url)

    banner_label.bind("<Button-1>", open_link)

    # Text area for curl command input
    lbl_input = tk.Label(window, text="Paste Curl(Bash) Command Here:", font=app_font)
    lbl_input.pack(pady=5)

    txt_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=15, font=app_font)
    txt_area.pack(pady=5, padx=10, fill="both", expand=True)

    # Log display area
    lbl_log = tk.Label(window, text="Logs:", font=app_font)
    lbl_log.pack(pady=5)

    log_output = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=10, state=tk.DISABLED, font=app_font)
    log_output.pack(pady=5, padx=10, fill="both", expand=True)

    def log_message(message):
        """Helper function to add a message to the log window."""
        log_output.config(state=tk.NORMAL)
        log_output.insert(tk.END, message + "\n")
        log_output.see(tk.END)
        log_output.config(state=tk.DISABLED)
        window.update_idletasks()

    def on_download_click():
        """
        Handle the download button click event.

        This inner function is called when the download button is clicked.
        It retrieves the curl command from the text area, validates that it's
        not empty, and calls download_file_from_curl to perform the download.

        Args:
            None: This function takes no parameters but accesses the txt_area
                  and log_message from the outer scope.

        Returns:
            None: This function doesn't return a value but may log messages
                  for user feedback.

        Raises:
            No explicit exceptions are raised, but may log warning messages
            for empty input.
        """
        log_output.config(state=tk.NORMAL)
        log_output.delete(1.0, tk.END)
        log_output.config(state=tk.DISABLED)

        curl_cmd = txt_area.get(1.0, tk.END).strip()
        if curl_cmd:
            download_file_from_curl(curl_cmd, log_message)
        else:
            log_message("Input Error: Please paste a curl command.")

    btn = tk.Button(window, text="Download", command=on_download_click, font=app_font)
    btn.pack(pady=10)

    window.mainloop()


if __name__ == "__main__":
    create_gui()
