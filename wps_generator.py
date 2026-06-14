#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import re
import subprocess
import platform

try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

def get_current_wifi_mac():
    """جلب عنوان MAC (BSSID) للشبكة المتصل بها حالياً حسب نظام التشغيل."""
    system = platform.system()
    try:
        if system == "Windows":
            output = subprocess.check_output(
                "netsh wlan show interfaces", shell=True, text=True,
                stderr=subprocess.DEVNULL
            )
            match = re.search(r"BSSID\s*:\s*([0-9A-Fa-f:]{17})", output)
            if match:
                return match.group(1).strip()

        elif system == "Linux":
            try:
                bssid = subprocess.check_output(
                    ["iwgetid", "-r", "-a"], text=True, stderr=subprocess.DEVNULL
                ).strip()
                return bssid
            except FileNotFoundError:
                output = subprocess.check_output(
                    "iwconfig", shell=True, text=True, stderr=subprocess.DEVNULL
                )
                match = re.search(r"Access Point:\s*([0-9A-Fa-f:]{17})", output)
                if match:
                    return match.group(1).strip()

        elif system == "Darwin":
            airport_cmd = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            output = subprocess.check_output(
                [airport_cmd, "-I"], text=True, stderr=subprocess.DEVNULL
            )
            match = re.search(r"BSSID:\s*([0-9A-Fa-f:]{17})", output)
            if match:
                return match.group(1).strip()

    except Exception:
        pass
    return None


class WPSGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مولّد رمز WPS PIN - بدون نت")
        self.root.geometry("580x440")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # عنوان التطبيق
        title_label = tk.Label(root, text="مولّد رمز WPS PIN", font=("Arial", 18, "bold"),
                               fg="#1a5276", bg="#f0f0f0")
        title_label.pack(pady=10)

        # إطار إدخال MAC مع زر الجلب التلقائي
        mac_frame = tk.Frame(root, bg="#f0f0f0")
        mac_frame.pack(pady=5)
        tk.Label(mac_frame, text="عنوان MAC (BSSID):", font=("Arial", 11), bg="#f0f0f0").grid(
            row=0, column=0, padx=(5,2), sticky="w")
        self.mac_entry = tk.Entry(mac_frame, font=("Arial", 11), width=20, justify='center')
        self.mac_entry.grid(row=0, column=1, padx=2)
        self.mac_entry.insert(0, "00:11:22:33:44:55")  # مثال

        self.fetch_btn = tk.Button(mac_frame, text="جلب تلقائي", font=("Arial", 9), bg="#d4e6f1",
                                   command=self.auto_fill_mac)
        self.fetch_btn.grid(row=0, column=2, padx=5)

        tk.Label(mac_frame, text="مثال: 00:11:22:33:44:55", font=("Arial", 8), fg="gray", bg="#f0f0f0").grid(
            row=1, column=1, columnspan=2, sticky="w")

        # خيارات الخوارزميات
        algo_frame = tk.Frame(root, bg="#f0f0f0")
        algo_frame.pack(pady=10, fill="x", padx=20)
        tk.Label(algo_frame, text="اختر الخوارزميات:", font=("Arial", 11, "bold"), bg="#f0f0f0").pack(anchor="w")

        self.algo_vars = {
            "D-Link (الخوارزمية الشائعة)": tk.BooleanVar(value=True),
            "Thomson/SpeedTouch": tk.BooleanVar(value=True),
            "Arcadyan (بعض موديلات)": tk.BooleanVar(value=True),
            "Pirelli (بعض أجهزة)": tk.BooleanVar(value=True),
        }
        for text, var in self.algo_vars.items():
            cb = tk.Checkbutton(algo_frame, text=text, variable=var, bg="#f0f0f0", font=("Arial", 10))
            cb.pack(anchor="w", padx=10)

        # زر التوليد
        generate_btn = tk.Button(root, text="توليد الأرقام", font=("Arial", 12, "bold"),
                                 bg="#2e86c1", fg="white", padx=15, pady=5,
                                 command=self.generate_pins)
        generate_btn.pack(pady=5)

        # منطقة النتائج
        result_frame = tk.Frame(root, bg="#f0f0f0")
        result_frame.pack(pady=10, fill="both", expand=True, padx=20)

        tk.Label(result_frame, text="الـ PINs المُحتملة:", font=("Arial", 11, "bold"), bg="#f0f0f0").pack(anchor="w")
        self.result_text = tk.Text(result_frame, height=8, width=50, font=("Consolas", 11),
                                   state="disabled", bg="#ffffff")
        self.result_text.pack(fill="both", expand=True, pady=5)

        # أزرار النسخ
        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=5)
        copy_btn = tk.Button(btn_frame, text="نسخ جميع الأرقام", font=("Arial", 10), bg="#27ae60", fg="white",
                             command=self.copy_to_clipboard)
        copy_btn.grid(row=0, column=0, padx=5)

        # تذييل
        tk.Label(root, text="للأغراض التعليمية واختبار أمان شبكتك فقط", font=("Arial", 8),
                 fg="red", bg="#f0f0f0").pack(side="bottom", pady=5)

        # محاولة الجلب التلقائي عند البدء
        self.root.after(200, self.auto_fill_mac)

    def auto_fill_mac(self):
        self.fetch_btn.config(text="جاري الجلب...", state="disabled")
        self.root.update()
        mac = get_current_wifi_mac()
        if mac:
            self.mac_entry.delete(0, tk.END)
            self.mac_entry.insert(0, mac)
            self.fetch_btn.config(text="✓ تم الجلب", bg="#a9dfbf")
        else:
            messagebox.showwarning("فشل", "لم نتمكن من جلب عنوان MAC تلقائياً.\n"
                                    "تأكد من اتصالك بشبكة واي فاي أو أدخله يدوياً.")
            self.fetch_btn.config(text="إعادة المحاولة", bg="#f5b7b1")
        self.root.after(1500, lambda: self.fetch_btn.config(
            text="جلب تلقائي", bg="#d4e6f1", state="normal"))

    def validate_mac(self, mac):
        pattern = r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$'
        return re.match(pattern, mac) is not None

    def generate_checksum(self, pin_without_checksum):
        digits = [int(d) for d in pin_without_checksum]
        if len(digits) != 7:
            return None
        odd_sum = sum(digits[i] for i in range(0, 7, 2))
        even_sum = sum(digits[i] for i in range(1, 7, 2))
        total = (odd_sum * 3) + even_sum
        checksum = (10 - (total % 10)) % 10
        return checksum

    def dlink_algorithm(self, mac_bytes):
        last_three = mac_bytes[3:6]
        decimal_values = [str(b) for b in last_three]
        pin_core = ''.join(decimal_values).zfill(7)
        return pin_core[:7]

    def thomson_algorithm(self, mac_bytes):
        b0, b1, b2, b3, b4, b5 = mac_bytes
        pin = (b3 ^ b5) * 256 + (b2 ^ b4)
        pin = pin % 10000000
        return str(pin).zfill(7)

    def arcadyan_algorithm(self, mac_bytes):
        b3, b4, b5 = mac_bytes[3:6]
        val = (b3 * b4 * b5) % 10000000
        return str(val).zfill(7)

    def pirelli_algorithm(self, mac_bytes):
        b3, b4, b5 = mac_bytes[3:6]
        xor_val = b3 ^ b4 ^ b5
        pin = xor_val * 65536
        pin = pin % 10000000
        return str(pin).zfill(7)

    def generate_pins(self):
        mac_input = self.mac_entry.get().strip()
        if not self.validate_mac(mac_input):
            messagebox.showerror("خطأ", "صيغة MAC غير صحيحة. استخدم الصيغة 00:11:22:33:44:55")
            return

        mac_bytes = [int(b, 16) for b in mac_input.split(':')]
        results = []

        if self.algo_vars["D-Link (الخوارزمية الشائعة)"].get():
            core = self.dlink_algorithm(mac_bytes)
            checksum = self.generate_checksum(core)
            results.append(f"D-Link   : {core}{checksum}")

        if self.algo_vars["Thomson/SpeedTouch"].get():
            core = self.thomson_algorithm(mac_bytes)
            checksum = self.generate_checksum(core)
            results.append(f"Thomson  : {core}{checksum}")

        if self.algo_vars["Arcadyan (بعض موديلات)"].get():
            core = self.arcadyan_algorithm(mac_bytes)
            checksum = self.generate_checksum(core)
            results.append(f"Arcadyan : {core}{checksum}")

        if self.algo_vars["Pirelli (بعض أجهزة)"].get():
            core = self.pirelli_algorithm(mac_bytes)
            checksum = self.generate_checksum(core)
            results.append(f"Pirelli  : {core}{checksum}")

        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        if results:
            self.result_text.insert(tk.END, "\n".join(results))
        else:
            self.result_text.insert(tk.END, "لم تختر أي خوارزمية.")
        self.result_text.config(state="disabled")

    def copy_to_clipboard(self):
        content = self.result_text.get(1.0, tk.END).strip()
        if content and "لم تختر" not in content:
            if HAS_CLIPBOARD:
                pyperclip.copy(content)
                messagebox.showinfo("تم", "تم نسخ جميع الأرقام إلى الحافظة.")
            else:
                messagebox.showerror("خطأ", "مكتبة pyperclip غير مثبتة.\nثبتها عبر: pip install pyperclip")
        else:
            messagebox.showwarning("تحذير", "لا توجد أرقام لنسخها.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WPSGeneratorApp(root)
    root.mainloop()
