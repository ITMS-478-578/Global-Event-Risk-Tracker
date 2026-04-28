import sys
import os
import threading
import traceback

# Ensure the project root is on the path so `backend` is importable
# regardless of which directory the script is launched from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import matplotlib.pyplot as plt
from PIL import Image
from dotenv import load_dotenv

from backend.utils import analyze_city

load_dotenv()

#Set the appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TravelApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Global Event & Risk Tracker")
        self.geometry("1100x700") # Increased height for more room

        # Dictionary to store labels for API data cards for easy updates
        self.data_labels = {}

        # Configure Grid (1x2) - Siderbar and Main Frame
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="TravelGuard AI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.city_input = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Enter City Name")
        self.city_input.grid(row=1, column=0, padx=20, pady=10)

        self.search_button = ctk.CTkButton(self.sidebar_frame, text="Analyze Risk", command=self.search_event)
        self.search_button.grid(row=2, column=0, padx=20, pady=10)

        # Loading Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.sidebar_frame, width=150, height=10)
        self.progress_bar.grid(row=3, column=0, padx=20, pady=10)
        self.progress_bar.set(0)  # Start with an empty progress bar
        self.progress_bar.grid_remove()  # Hide it until needed

        # --- MAIN TABS (For Analytics) ---
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.tab_live = self.tabview.add("Live Tracker")
        self.tab_analysis = self.tabview.add("Data Analysis Report")

        # Live Tracker Tab Content
        self.tab_live.grid_columnconfigure((0, 1), weight=1)

        #Intelligence Score Header
        self.score_card = ctk.CTkFrame(self.tab_live, height=150)
        self.score_card.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.score_label = ctk.CTkLabel(self.score_card, text="Travel Readiness Score: --", font=ctk.CTkFont(size=28, weight="bold"))
        self.score_label.pack(pady=30)

        # API Data Cards (Placeholders)
        self.create_data_card("Weather Forecast", 1, 0)
        self.create_data_card("Local Safety (Hospitals)", 1, 1)
        self.create_data_card("Recent News Headlines", 2, 0)
        self.create_data_card("Exchange Rate (USD)", 2, 1)

        # Status Bar 
        self.status_label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="w")

    # Live Tracker Tab

    def create_data_card(self, title, row, col):
        card = ctk.CTkFrame(self.tab_live)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(weight="bold", size=14))
        label.pack(padx=10, pady=5)

        # Store the label in dictionary using the title as key for easy updates later
        data_display = ctk.CTkLabel(card,text="Waiting for search...", wraplength=350, justify="left")
        data_display.pack(padx=10, pady=15)
        self.data_labels[title] = data_display  # Store reference for updates

    def search_event(self):
        city = self.city_input.get().strip()

        if not city:
            self.status_label.configure(text="Status: Error - No city entered", text_color="red")
            return

        self.status_label.configure(text=f"Status: Analyzing {city}...", text_color="white")
        self.progress_bar.grid()
        self.progress_bar.start()
        self.search_button.configure(state="disabled", text="Analyzing...")

        def run():
            try:
                data = analyze_city(city)
            except Exception as e:
                # Capture the message NOW — Python 3 sets e=None after the
                # except block ends, so a lambda closing over `e` would always
                # see None by the time tkinter calls it.
                msg = str(e) or type(e).__name__
                traceback.print_exc()  # full trace visible in the terminal
                self.after(0, lambda: self._on_analysis_error(msg))
                return
            self.after(0, lambda: self._on_analysis_complete(city, data))

        threading.Thread(target=run, daemon=True).start()

    def _on_analysis_complete(self, city, data):
        self.update_dashboard(data)
        self.generate_city_charts(data, city)
        self.display_analysis_tab(data, city)
        self._save_city_data(city, data)

    def _save_city_data(self, city: str, data: dict):
        try:
            from backend.data_pipeline import build_city_dataframe
            build_city_dataframe(city, {
                "final_score": data["score"],
                "breakdown": {
                    "weather_weight":  data["weather_weight"],
                    "safety_weight":   data["safety_weight"],
                    "news_weight":     data["news_weight"],
                    "exchange_weight": data["exchange_weight"],
                },
            })
        except Exception:
            pass

    def _on_analysis_error(self, message):
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.search_button.configure(state="normal", text="Analyze Risk")
        self.status_label.configure(text=f"Status: Error — {message}", text_color="red")

    # Update the GUI with API data (placeholder function)
    def update_dashboard(self, data):
        # Update the score label and data cards with real API data
        self.progress_bar.stop()  # Stop the progress bar animation
        self.progress_bar.grid_remove()  # Hide the progress bar
        self.search_button.configure(state="normal", text="Analyze Risk")  # Re-enable the search button

        # Reset Status Bar
        self.status_label.configure(text="Status: Analysis Complete", text_color="green")

        # Update Score
        self.score_label.configure(text=f"Travel Readiness Score: {data['score']}")
        
        # Color logic for score card background based on score value
        if data['score'] > 75:
            color = "green"
        elif data['score'] > 50:
            color = "orange"
        else:
            color = "red"

        self.score_card.configure(fg_color=color)  # Match the card color to the label color
        self.score_label.configure(fg_color=color)  # Match the label color to the card color

        # Update API Data Cards
        for key, value in data.items():
            if key in self.data_labels:
                display_text =  value if value else "No data available"
                self.data_labels[key].configure(text=display_text)

    # ------------------------------------------------------------------ #
    #  Data Analysis Report Tab                                          #
    # ------------------------------------------------------------------ #

    def generate_city_charts(self, data: dict, city_name: str):
        """Save a combined figure: bar chart (weights) + radar (raw scores)."""
        import numpy as np

        DARK    = "#1e1e1e"
        PANEL   = "#2b2b2b"
        WHITE   = "white"
        COLORS  = ["#4A90D9", "#F39C12", "#2ECC71", "#E74C3C"]
        CATS    = ["Weather", "Safety", "News", "Currency"]

        fig = plt.figure(figsize=(12, 4.5), facecolor=DARK)

        # --- Bar chart ---
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.set_facecolor(PANEL)
        weights = [data["weather_weight"], data["safety_weight"],
                   data["news_weight"],    data["exchange_weight"]]
        bars = ax1.bar(CATS, weights, color=COLORS, width=0.55, edgecolor="none")
        ax1.set_ylim(0, 35)
        ax1.set_ylabel("Points contributed", color=WHITE, fontsize=9)
        ax1.set_title("Score Breakdown", color=WHITE, fontsize=11, pad=8)
        ax1.tick_params(colors=WHITE, labelsize=9)
        for spine in ax1.spines.values():
            spine.set_color("#555")
        for bar, val in zip(bars, weights):
            ax1.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.4,
                     str(val), ha="center", color=WHITE, fontsize=10, fontweight="bold")

        # --- Radar chart ---
        ax2 = fig.add_subplot(1, 2, 2, polar=True)
        ax2.set_facecolor(PANEL)
        raw = [data.get("weather_raw_score",  50),
               data.get("safety_raw_score",   50),
               data.get("news_raw_score",     50),
               data.get("currency_raw_score", 50)]
        N      = len(CATS)
        angles = [n / N * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        raw_c  = raw + raw[:1]

        ax2.set_theta_offset(np.pi / 2)
        ax2.set_theta_direction(-1)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(CATS, color=WHITE, fontsize=9)
        ax2.set_ylim(0, 100)
        ax2.set_yticks([25, 50, 75, 100])
        ax2.set_yticklabels(["25", "50", "75", "100"], color="#888", fontsize=7)
        ax2.grid(color="#555", linestyle="--", alpha=0.6)
        ax2.plot(angles, raw_c, "o-", linewidth=2, color="#4A90D9")
        ax2.fill(angles, raw_c, alpha=0.25, color="#4A90D9")
        ax2.set_title("City Risk Profile", color=WHITE, fontsize=11, pad=14)

        country = data.get("country", "")
        loc     = f"{city_name.title()}, {country}" if country else city_name.title()
        fig.suptitle(f"{loc}  ·  Travel Readiness Score: {data.get('score', 0)} / 100",
                     color=WHITE, fontsize=12, y=1.01)

        plt.tight_layout()
        plt.savefig("analysis_chart.png", dpi=100,
                    bbox_inches="tight", facecolor=DARK)
        plt.close()

    def _generate_history_chart(self) -> bool:
        """Generate and save a horizontal bar chart of all analyzed cities.
        Returns True if a chart was saved, False if there is insufficient data."""
        try:
            from backend.data_pipeline import load_history
            df = load_history()
            if df.empty:
                return False

            DARK  = "#1e1e1e"
            WHITE = "white"
            scores = [int(s) for s in df["final_score"].tolist()]
            cities = df["city"].tolist()
            bar_c  = ["#2ECC71" if s > 75 else "#F39C12" if s > 50 else "#E74C3C"
                      for s in scores]

            h = max(2.5, len(cities) * 0.55 + 0.8)
            _, ax = plt.subplots(figsize=(8, h), facecolor=DARK)
            ax.set_facecolor("#2b2b2b")
            ax.barh(cities, scores, color=bar_c, height=0.5, edgecolor="none")
            ax.set_xlim(0, 108)
            ax.set_xlabel("Travel Readiness Score", color=WHITE, fontsize=9)
            ax.tick_params(colors=WHITE, labelsize=9)
            for spine in ax.spines.values():
                spine.set_color("#555")
            ax.axvline(75, color="#2ECC71", linestyle="--", alpha=0.45, linewidth=1)
            ax.axvline(50, color="#F39C12", linestyle="--", alpha=0.45, linewidth=1)
            for i, score in enumerate(scores):
                ax.text(score + 1.5, i, str(score),
                        va="center", color=WHITE, fontsize=9, fontweight="bold")
            ax.set_title("Cities Analyzed — Comparison", color=WHITE, fontsize=10, pad=8)
            plt.tight_layout()
            plt.savefig("history_chart.png", dpi=90,
                        bbox_inches="tight", facecolor=DARK)
            plt.close()
            return True
        except Exception:
            return False

    def display_analysis_tab(self, data: dict, city_name: str):
        """Rebuild the Data Analysis Report tab with charts, AI summary, and history."""
        for child in self.tab_analysis.winfo_children():
            child.destroy()

        scroll = ctk.CTkScrollableFrame(self.tab_analysis)
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # Combined bar + radar chart
        try:
            img     = Image.open("analysis_chart.png")
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(700, 265))
            ctk.CTkLabel(scroll, image=ctk_img, text="").pack(pady=(8, 2))
        except Exception:
            pass

        # Score verdict banner
        score   = data.get("score", 0)
        verdict = ("Safe to Travel"       if score > 75 else
                   "Travel with Caution"  if score > 50 else
                   "High Risk")
        v_color = ("#2ECC71" if score > 75 else
                   "#F39C12" if score > 50 else
                   "#E74C3C")
        country = data.get("country", "")
        loc     = f"{city_name.title()}, {country}" if country else city_name.title()
        ctk.CTkLabel(scroll,
                     text=f"{loc}  ·  {score}/100  ·  {verdict}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=v_color).pack(pady=(4, 10))

        # AI summary
        ai_text = data.get("ai_summary", "").strip()
        if ai_text:
            ctk.CTkLabel(scroll, text="AI Travel Intelligence",
                         font=ctk.CTkFont(size=12, weight="bold")
                         ).pack(anchor="w", padx=16, pady=(4, 2))
            ai_box = ctk.CTkTextbox(scroll, width=690, height=175,
                                    font=ctk.CTkFont(size=12))
            ai_box.pack(padx=10, pady=(0, 10))
            ai_box.insert("1.0", ai_text)
            ai_box.configure(state="disabled")

        # Historical comparison chart
        if self._generate_history_chart():
            ctk.CTkLabel(scroll, text="Cities Compared",
                         font=ctk.CTkFont(size=12, weight="bold")
                         ).pack(anchor="w", padx=16, pady=(6, 2))
            try:
                hi     = Image.open("history_chart.png")
                hi_ctk = ctk.CTkImage(light_image=hi, dark_image=hi, size=(690, 180))
                ctk.CTkLabel(scroll, image=hi_ctk, text="").pack(pady=(0, 8))
            except Exception:
                pass
       
if __name__ == "__main__":
    app = TravelApp()
    app.mainloop()