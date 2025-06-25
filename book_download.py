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
from tkinter import messagebox, scrolledtext


def download_file_from_curl(curl_command):
    """
    Download a file by parsing a curl command and extracting URL and headers.
    
    This function parses a curl command string to extract the target URL and
    relevant headers, then downloads the file using urllib.request. It excludes
    certain headers like 'range' and 'if-none-match' that might interfere with
    the download process.
    
    Args:
        curl_command (str): A complete curl command string, typically copied from
                           browser developer tools or curl command line.
    
    Returns:
        None: This function doesn't return a value but shows message boxes for
              user feedback and saves the downloaded file to the current directory.
    
    Raises:
        No explicit exceptions are raised, but error messages are shown via
        messagebox for various error conditions including:
        - URL not found in curl command
        - Network errors during download
        - File system errors
        - Invalid URL format
    
    Example:
        >>> curl_cmd = '''curl 'https://example.com/file.pdf' \\
        ...   -H 'accept: */*' \\
        ...   -H 'user-agent: Mozilla/5.0...' '''
        >>> download_file_from_curl(curl_cmd)
        # Downloads file.pdf to current directory and shows success message
    
    Note:
        - The downloaded file is saved in the current working directory
        - After successful download, Windows Explorer opens to show the file
        - Headers 'range' and 'if-none-match' are automatically excluded
        - The filename is extracted from the URL path
    """
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
                if key.lower() != "range" and key.lower() != "if-none-match":  # Exclude the 'range' and 'if-none-match' headers
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
            with open(filename, "wb") as f:
                f.write(response.read())
            messagebox.showinfo("Success", f"Downloaded '{filename}' successfully.")

            # Open the containing directory and select the downloaded file
            try:
                file_path = os.path.join(os.getcwd(), filename)
                subprocess.run(["explorer.exe", "/select,", file_path], check=False)
            except (subprocess.SubprocessError, OSError) as e:
                messagebox.showerror("Error", f"Could not open file explorer: {e}")
    except urllib.error.URLError as e:
        messagebox.showerror("Download Error", f"Error downloading the file: {e.reason}")
    except (OSError, IOError) as e:
        messagebox.showerror("File System Error", f"Error saving the file: {e}")
    except ValueError as e:
        messagebox.showerror("Value Error", f"Invalid URL or data format: {e}")


def create_gui():
    """
    Create and display the main GUI window for the book downloader application.

    This function creates a tkinter-based graphical user interface with:
    - A label instructing users to paste curl commands
    - A large text area for inputting curl commands
    - A download button to initiate the download process
    - Error handling and user feedback through message boxes

    Args:
        None: This function takes no parameters.

    Returns:
        None: This function doesn't return a value but starts the GUI event loop.

    Raises:
        No explicit exceptions are raised, but the GUI may show error messages
        for various conditions including:
        - Empty input when download is attempted
        - Errors during the download process (handled by download_file_from_curl)

    Example:
        >>> create_gui()
        # Opens a window with text area and download button

    Note:
        - The GUI runs in the main thread and blocks until the window is closed
        - The window title is set to "Book Downloader"
        - The text area supports scrolling and word wrapping
        - The download button triggers the download_file_from_curl function
        - Input validation is performed before attempting download
    """
    window = tk.Tk()
    window.title("Book Downloader")

    # Text area for curl command input
    lbl = tk.Label(window, text="Paste Curl(Bash) Command Here:")
    lbl.pack()

    txt_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20)
    txt_area.pack()

    def on_download_click():
        """
        Handle the download button click event.

        This inner function is called when the download button is clicked.
        It retrieves the curl command from the text area, validates that it's
        not empty, and calls download_file_from_curl to perform the download.

        Args:
            None: This function takes no parameters but accesses the txt_area
                  widget from the outer scope.

        Returns:
            None: This function doesn't return a value but may show message
                  boxes for user feedback.

        Raises:
            No explicit exceptions are raised, but may show warning messages
            for empty input or error messages from download_file_from_curl.
        """
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
