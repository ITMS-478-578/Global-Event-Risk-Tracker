import customtkinter as ctk

#Set the appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TravelApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Global Event & Risk Tracker")
        self.geometry("1100x600")

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

        # Create Main Frame
        self.main_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)

        #Intelligence Score Header
        self.score_card = ctk.CTkFrame(self.main_frame, height=150)
        self.score_card.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.score_label = ctk.CTkLabel(self.score_card, text="Travel Readiness Score: --", font=ctk.CTkFont(size=24, weight="bold"))
        self.score_label.pack(pady=20)

        # API Data Cards (Placeholders)
        self.create_data_card("Weather Forecast", 1, 0)
        self.create_data_card("Local Safety (Hospitals)", 1, 1)
        self.create_data_card("Recent News Headlines", 2, 0)
        self.create_data_card("Exchange Rate (USD)", 2, 1)

    def create_data_card(self, title, row, col):
        card = ctk.CTkFrame(self.main_frame)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(weight="bold"))
        label.pack(padx=10, pady=5)
        # Update text with API data later
        data_display = ctk.CTkLabel(card, text="--", wraplength=300)
        data_display.pack(padx=10, pady=10)

    def search_event(self):
        # This is wehre you will implement the logic to fetch data from APIs and update the UI
        city = self.city_input.get()
        print(f"Analyzing {city}...")  # Placeholder for actual functionality

if __name__ == "__main__":
    app = TravelApp()
    app.mainloop()