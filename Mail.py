import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import json
import time
import datetime
import os
import ttkbootstrap as ttkb

API_BASE = "https://api.mail.tm"

headers = {
   "Content-Type": "application/json"
}

class MailToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("https://github.com/skun0")
        self.root.geometry("800x600")
        self.root.resizable(False, False) 
        self.root.configure(bg="#282c34")

        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")

        self.style = ttkb.Style(theme="darkly")
        self.style.configure(".", background="#1e2127", foreground="#abb2bf", fieldbackground="#1e2127")
        self.style.configure("Treeview", background="#282c34", foreground="#abb2bf", fieldbackground="#282c34")
        self.style.configure("Treeview.Heading", background="#2c313a", foreground="#61afef")
        self.style.configure("TButton", background="#2c313a", foreground="#abb2bf")
        self.style.configure("info.Outline.TButton", background="#2c313a", foreground="#61afef")
        self.style.configure("danger.Outline.TButton", background="#2c313a", foreground="#e06c75")
        self.style.configure("success.Outline.TButton", background="#2c313a", foreground="#98c379")
        self.style.configure("primary.Outline.TButton", background="#2c313a", foreground="#61afef")
        self.style.map('TCombobox', selectbackground=[('readonly','#2c313a')], selectforeground=[('readonly','#abb2bf')])
        self.style.configure("TCombobox", background="#282c34", foreground="#abb2bf", fieldbackground="#282c34")
        self.style.configure("TEntry", background="#282c34", foreground="#abb2bf", fieldbackground="#282c34")
        self.style.configure("TFrame", background="#1e2127")
        self.style.configure("TLabel", background="#1e2127", foreground="#abb2bf")

        self.email = None
        self.password = None
        self.token = None
        self.duration = "infinita"
        self.seen_ids = set()
        self.inbox_thread = None
        self.check_job = None

        self.setup_login_ui()

    def fade_out(self, widget, callback=None):
        def fade(alpha=1.0):
            if alpha > 0:
                widget.winfo_toplevel().attributes('-alpha', alpha)
                widget.after(20, lambda: fade(alpha - 0.05))
            else:
                widget.winfo_toplevel().attributes('-alpha', 0)
                widget.after(100, lambda: self._complete_fade_out(widget, callback))
        fade()
        
    def _complete_fade_out(self, widget, callback):
        try:
            widget.destroy()
            if callback:
                callback()
        except tk.TclError:
            pass

    def fade_in(self):
        self.root.attributes('-alpha', 0.0)
        def fade(alpha=0.0):
            if alpha <= 1.0:
                self.root.attributes('-alpha', alpha)
                if alpha < 1.0:
                    self.root.after(20, lambda: fade(alpha + 0.05))
        self.root.after(100, lambda: fade())

    def setup_login_ui(self):
        
        main_frame = ttkb.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.fade_in()

        
        center_container = ttkb.Frame(main_frame)
        center_container.pack(expand=True, pady=(50, 0))

        
        title_label = ttkb.Label(center_container, text="Mail Service", font=("Helvetica", 22, "bold"), foreground="#6172ef")
        title_label.pack(pady=50)

        
        account_frame = ttkb.Frame(center_container, padding="10")
        account_frame.pack()

        
        ttkb.Label(account_frame, text="Username:", foreground="#abb2bf").grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.username_var = tk.StringVar()
        ttkb.Entry(account_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, padx=10, pady=5)

        ttkb.Label(account_frame, text="Password:", foreground="#abb2bf").grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.password_var = tk.StringVar()
        ttkb.Entry(account_frame, textvariable=self.password_var, show="*", width=30).grid(row=1, column=1, padx=10, pady=5)

        ttkb.Label(account_frame, text="Domain:", foreground="#abb2bf").grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.domain_var = tk.StringVar()
        self.domain_combobox = ttkb.Combobox(account_frame, textvariable=self.domain_var, state='readonly', width=30)
        self.domain_combobox.grid(row=2, column=1, padx=10, pady=5)
        self.domain_combobox.bind("<<ComboboxSelected>>", self.on_domain_select)

        
        button_frame = ttkb.Frame(account_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        self.create_button = ttkb.Button(button_frame, text="Create Account", command=self.create_account, style="primary.Outline.TButton")
        self.create_button.pack(side=tk.LEFT, padx=10)

        self.login_button = ttkb.Button(button_frame, text="Login", command=self.login, style="primary.Outline.TButton")
        self.login_button.pack(side=tk.LEFT, padx=10)

        
        self.load_domains()

    def load_domains(self):
        domains = self.get_domains()
        if domains:
            self.domain_combobox['values'] = domains
            self.domain_combobox.current(0)
        else:
            messagebox.showerror("Errore", "Nessun dominio disponibile. Controlla la connessione.")

    def on_domain_select(self, event):
        selected_domain = self.domain_var.get()
        print(f"Selected domain: {selected_domain}")

    def get_domains(self):
        response = requests.get(f"{API_BASE}/domains")
        if response.status_code == 200:
            domains = response.json()["hydra:member"]
            return [d["domain"] for d in domains]
        return []

    def create_account(self):
        username = self.username_var.get()
        password = self.password_var.get()
        domain = self.domain_var.get()
        if not username or not password or not domain:
            messagebox.showwarning("Wait", "Insert all field required.")
            return

        email = self.create_account_api(username, password, domain)
        if email:
            self.email = email
            self.password = password
            self.token = self.get_token(email, password)
            if self.token:
                if self.save_credentials(email, password):
                    messagebox.showinfo("Success", f"Email created and credentials saved: {email}")
                else:
                    messagebox.showinfo("Success", f"Email created: {email}")
                self.setup_inbox_ui()

    def create_account_api(self, username, password, domain):
        email = f"{username}@{domain}"
        payload = {
            "address": email,
            "password": password
        }
        response = requests.post(f"{API_BASE}/accounts", headers=headers, json=payload)
        if response.status_code == 201:
            return email
        elif "exists" in response.text:
            messagebox.showerror("Error", "This address already exists. Please try again.")
        elif "address" in response.text:
            messagebox.showerror("Error", "The email address is invalid. Try a shorter username.")
        else:
            messagebox.showerror("Error", f"Error during creation: {response.text}")
        return None

    def get_token(self, email, password):
        payload = {
            "address": email,
            "password": password
        }
        response = requests.post(f"{API_BASE}/token", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["token"]
        return None

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        domain = self.domain_var.get()

        
        if not username and not password:
            self.load_saved_credentials()
            if not self.email or not self.password:
                messagebox.showwarning("Attention", "There are no credentials saved.")
                return
        else:
            email = username + "@" + domain
            self.email = email
            self.password = password

        self.token = self.get_token(self.email, self.password)
        if self.token:
            self.save_credentials(self.email, self.password)
            self.setup_inbox_ui()
        else:
            messagebox.showerror("Error", "Access failed.")

    def save_credentials(self, email, password):
        try:
            data = {
                "email": email,
                "password": password
            }
            with open("email_temp.json", "w") as f:
                json.dump(data, f)
            os.chmod("email_temp.json", 0o600)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error in saving credentials: {str(e)}")
            return False

    def load_saved_credentials(self):
        if os.path.exists("email_temp.json"):
            with open("email_temp.json", "r") as f:
                data = json.load(f)
                self.email = data.get("email")
                self.password = data.get("password")
                if self.email and self.password:
                    self.token = self.get_token(self.email, self.password)
                    if self.token:
                        return True
                    else:
                        messagebox.showerror("Error", "Failed login with saved credentials.")
                        os.remove("email_temp.json")
        return False

    def setup_inbox_ui(self):
        
        old_widgets = list(self.root.winfo_children())
        if old_widgets:
            self.fade_out(old_widgets[0], lambda: self.setup_inbox_ui_content())
        else:
            self.setup_inbox_ui_content()

    def setup_inbox_ui_content(self):
        
        for widget in self.root.winfo_children():
            widget.destroy()

        
        main_frame = ttkb.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        
        title_label = ttkb.Label(main_frame, text="MailBox", font=("Helvetica", 18, "bold"), foreground="#61afef")
        title_label.pack(pady=10)

        
        inbox_frame = ttkb.Frame(main_frame, padding="10")
        inbox_frame.pack(fill=tk.BOTH, expand=True)

        
        self.tree = ttkb.Treeview(inbox_frame, columns=("Sender", "Object", "Date", "ID"), show="headings")
        self.tree.heading("Sender", text="Sender")
        self.tree.heading("Object", text="Object")
        self.tree.heading("Date", text="Date")
        self.tree.heading("ID", text="ID")
        self.tree.column("Sender", width=200)
        self.tree.column("Object", width=300)
        self.tree.column("Date", width=150)
        self.tree.column("ID", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        
        controls_frame = ttkb.Frame(inbox_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        
        self.logout_button = ttkb.Button(controls_frame, text="Logout", command=self.logout, style="danger.Outline.TButton")
        self.logout_button.pack(side=tk.LEFT, padx=5)

        
        right_controls = ttkb.Frame(controls_frame)
        right_controls.pack(side=tk.RIGHT)

        
        email_frame = ttkb.Frame(right_controls)
        email_frame.pack(side=tk.LEFT, expand=True, padx=5)
        
        self.email_var = tk.StringVar(value=self.email)
        self.email_entry = ttkb.Entry(email_frame, textvariable=self.email_var, state="readonly", width=40, style="info.TEntry")
        self.email_entry.pack(side=tk.LEFT)
        self.email_entry.bind("<Button-1>", self.copy_email_to_clipboard)

        
        self.tree.bind('<Double-1>', lambda e: self.read_selected_message())

        
        self.start_checking_inbox()

        
        self.fade_in()

    def start_checking_inbox(self):
        self.seen_ids = set()
        self.check_inbox()

    def check_inbox(self):
        if not self.token:
            messagebox.showwarning("Attention", "You must first create or log in to an account.")
            return

        auth_headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(f"{API_BASE}/messages", headers=auth_headers)
            if response.status_code == 200:
                messages = response.json()["hydra:member"]
                new_messages = [msg for msg in messages if msg["id"] not in self.seen_ids]

                if new_messages:
                    for msg in new_messages:
                        self.seen_ids.add(msg["id"])
                        self.tree.insert("", tk.END, values=(
                            msg['from']['address'],
                            msg['subject'] or "(senza oggetto)",
                            msg['createdAt'][:19].replace("T", " "),
                            msg['id']
                        ))

            else:
                messagebox.showerror("Error", f"Error in message retrieval: {response.text}")
        except requests.exceptions.RequestException as e:
            messagebox.showwarning("Error", f"Connection error: {str(e)}")
        except Exception as e:
            messagebox.showwarning("Error", f"Unexpected error: {str(e)}")

        
        self.check_job = self.root.after(5000, self.check_inbox)

    def read_selected_message(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Select a message to read.")
            return

        item = self.tree.item(selected_item)
        message_id = item['values'][3]
        self.read_message(message_id)

    def read_message(self, message_id):
        auth_headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_BASE}/messages/{message_id}", headers=auth_headers)
        if response.status_code == 200:
            msg = response.json()
            
            self.display_email(msg)
        else:
            messagebox.showerror("Error", f"Error while reading the message: {response.text}")

    def display_email(self, msg):
        
        email_window = tk.Toplevel(self.root)
        email_window.title("Mail Received")
        email_window.geometry("800x600")

        
        main_frame = ttkb.Frame(email_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        
        header_text = f"From: {msg['from']['address']}\n"
        header_text += f"Object: {msg.get('subject', '(no object)')}\n"
        header_text += f"Date: {msg['createdAt'][:19].replace('T', ' ')}\n\n"

       
        text_content = msg.get('text', '').strip()
        if not text_content:
            text_content = '(no content)'

        
        email_content = ttkb.Text(main_frame, wrap=tk.WORD, width=80, height=30)
        email_content.pack(fill=tk.BOTH, expand=True)

        
        email_content.insert('1.0', header_text + text_content)
        email_content.configure(state='disabled') 

       
        scrollbar = ttkb.Scrollbar(main_frame, command=email_content.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        email_content.configure(yscrollcommand=scrollbar.set)

        
        close_button = ttkb.Button(main_frame, text="Close", command=email_window.destroy, style="info.TButton")
        close_button.pack(pady=10)

    def show_notification(self, message):
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        notification.configure(bg="#282c34")
        

        x = self.root.winfo_x() + self.root.winfo_width() - 200
        y = self.root.winfo_y() + self.root.winfo_height() - 50
        notification.geometry(f"200x40+{x}+{y}")
        

        label = ttkb.Label(
            notification,
            text=message,
            font=("Helvetica", 10),
            foreground="#61afef",
            background="#282c34",
            padding=5
        )
        label.pack(expand=True, fill=tk.BOTH)
        
        
        def fade_away():
            notification.destroy()
            
        
        notification.after(1500, fade_away)

    def copy_email_to_clipboard(self, event):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.email)
        self.show_notification("Email copied to clipboard!")

    def logout(self):
        
        if self.check_job:
            self.root.after_cancel(self.check_job)
            self.check_job = None
        
        
        self.email = None
        self.password = None
        self.token = None
        self.duration = "infinity"
        self.seen_ids = set()
        
        
        old_widgets = list(self.root.winfo_children())
        if old_widgets:
            self.fade_out(old_widgets[0], self.setup_login_ui)
        else:
            self.setup_login_ui()

if __name__ == "__main__":
    root = ttkb.Window(themename="cosmo")
    app = MailToolApp(root)
    root.mainloop()