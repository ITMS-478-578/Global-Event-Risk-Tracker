import customtkinter as ctk

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
        self.progress_bar = ctk.CTkProgressBar(self.sidebar_frame)
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
        # This is wehre you will implement the logic to fetch data from APIs and update the UI
        city = self.city_input.get().strip()

        if not city:
            self.score_label.configure(text="Please enter a city name.", text_color="red")
            return
        
        #Visual feedback: show progress bar and disable button
        self.progress_bar.grid()  # Show the progress bar
        self.progress_bar.start()  # Start the indeterminate animation
        self.search_button.configure(state="disabled", text="Analyzing...")  # Disable the search button

    # Update the GUI with API data (placeholder function)
    def update_dashboard(self, data):
        # Update the score label and data cards with real API data
        self.progress_bar.stop()  # Stop the progress bar animation
        self.progress_bar.grid_remove()  # Hide the progress bar
        self.search_button.configure(state="normal", text="Analyze Risk")  # Re-enable the search button

        # Update Score
        self.score_label.configure(text=f"Travel Readiness Score: {data['score']}")
        
        # Color logic for score card background based on score value
        if data['score'] > 75:
            self.score_label.configure(fg_color="green")
        elif data['score'] > 50:
            self.score_label.configure(fg_color="orange")
        else:
            self.score_label.configure(fg_color="red")

        # Update API Data Cards
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].configure(text=value)

if __name__ == "__main__":
    app = TravelApp()
    app.mainloop()