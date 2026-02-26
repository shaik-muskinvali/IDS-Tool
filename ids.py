import os
import time
import fnmatch
import threading
import tkinter as tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileMovedEvent, FileModifiedEvent

from monitor import monitor_network_connections, monitor_system_processes
from detector import AdvancedAnomalyDetector


# Custom Event IDs
EVENT_IDS = {
    "CREATED": 1001,
    "DELETED": 1002,
    "MOVED": 1003,
    "MODIFIED": 1004,
    "ANOMALY": 9001
}


class IDPSEventHandler(FileSystemEventHandler):
    def __init__(self, ignore_patterns=None, anomaly_detector=None, alert_callback=None):
        super().__init__()
        self.ignore_patterns = ignore_patterns or []
        self.anomaly_detector = anomaly_detector
        self.alert_callback = alert_callback

    def should_ignore(self, path):
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False

    def log_event(self, message):
        os.makedirs("./logs", exist_ok=True)
        with open("./logs/file_log.txt", "a") as log_file:
            log_file.write(message + "\n")

    def process_event(self, action, event):
        file_name = os.path.basename(event.src_path)
        full_path = event.src_path
        event_id = EVENT_IDS.get(action, 0)

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        message = (
            f"[{timestamp}] [FILE EVENT] "
            f"EventID={event_id} | "
            f"Action={action} | "
            f"File={file_name} | "
            f"Path={full_path}"
        )

        if self.alert_callback:
            self.alert_callback(message)

        feature_vector = [
            event_id,
            os.path.getsize(full_path) if os.path.exists(full_path) else 0
        ]

        if self.anomaly_detector:
            self.anomaly_detector.add_event(feature_vector)

        self.log_event(message)

    def on_created(self, event):
        if not self.should_ignore(event.src_path):
            self.process_event("CREATED", event)

    def on_deleted(self, event):
        if not self.should_ignore(event.src_path):
            self.process_event("DELETED", event)

    def on_moved(self, event):
        if not self.should_ignore(event.src_path):
            self.process_event("MOVED", event)

    def on_modified(self, event):
        if not self.should_ignore(event.src_path):
            self.process_event("MODIFIED", event)


class IDSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDS App - SOC Monitor")
        self.root.geometry("900x550")

        # ==============================
        # 🟢 FULL LOG SECTION
        # ==============================
        self.log_frame = tk.Frame(root)
        self.log_frame.pack(fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.log_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.alert_box = tk.Text(
            self.log_frame,
            bg="black",
            fg="#00FF7F",
            font=("Consolas", 10),
            yscrollcommand=self.scrollbar.set
        )
        self.alert_box.pack(fill="both", expand=True)

        self.scrollbar.config(command=self.alert_box.yview)

        # ==============================
        # 🔵 CONTROL PANEL SECTION
        # ==============================
        self.control_frame = tk.Frame(root, height=60)
        self.control_frame.pack(fill="x")

        # Start Button
        self.start_button = tk.Button(
            self.control_frame,
            text="Start Monitoring",
            command=self.start_monitoring,
            width=18,
            bg="SystemButtonFace"
        )
        self.start_button.pack(side="left", padx=20, pady=10)

        # 🔥 CENTER LABEL ADDED (Your Name)
        self.center_label = tk.Label(
            self.control_frame,
            text="Created by Shaik Muskinvali",
            font=("Segoe UI", 11, "bold"),
            fg="#F6094D"   # Blue professional color
        )
        self.center_label.pack(side="left", expand=True)

        # Stop Button
        self.stop_button = tk.Button(
            self.control_frame,
            text="Stop Monitoring",
            command=self.stop_monitoring,
            width=18,
            bg="SystemButtonFace"
        )
        self.stop_button.pack(side="right", padx=20, pady=10)

        self.observer = None
        self.running = False

    def log_to_gui(self, message):
        self.alert_box.insert(tk.END, message + "\n")
        self.alert_box.see(tk.END)

    def anomaly_alert(self):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        message = (
            f"⚠️  [{timestamp}] [ANOMALY ALERT] "
            f"EventID={EVENT_IDS['ANOMALY']} | "
            f"Unusual file activity detected!"
        )
        self.log_to_gui(message)

    def start_monitoring(self):
        if self.running:
            return

        self.running = True
        self.start_button.config(bg="blue", fg="white")
        self.stop_button.config(bg="SystemButtonFace", fg="black")

        paths = [r"D:\\"]  
        ignore_patterns = ["*.tmp", "*.log", "*\\logs\\*"]

        anomaly_detector = AdvancedAnomalyDetector(threshold=10, time_window=60)
        event_handler = IDPSEventHandler(ignore_patterns, anomaly_detector, self.log_to_gui)

        self.observer = Observer()
        for path in paths:
            self.observer.schedule(event_handler, path, recursive=True)

        self.observer.start()

        threading.Thread(target=monitor_network_connections, daemon=True).start()
        threading.Thread(target=monitor_system_processes, daemon=True).start()

        self.log_to_gui("Monitoring Started...")

    def stop_monitoring(self):
        if not self.running:
            return

        if self.observer:
            self.observer.stop()
            self.observer.join()

        self.running = False
        self.stop_button.config(bg="Orange", fg="black")
        self.start_button.config(bg="SystemButtonFace", fg="black")

        self.log_to_gui("Monitoring Stopped.")


if __name__ == "__main__":
    root = tk.Tk()
    app = IDSApp(root)
    root.mainloop()