import os
import sys
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner

# Determine the base path of the app
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # When running as a packaged app
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Paths for database and images
db_path = os.path.join(base_path, "actresses.db")
image_folder = os.path.join(base_path, "actress_images")

class ActressViewer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)

        # Fetch and sort actress names
        self.actress_names = sorted(self.get_actress_names())

        # Top layout for dropdown and text input
        top_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, 0.1))

        # Dropdown (Spinner)
        self.spinner = Spinner(
            text="Select Actress",
            values=self.actress_names,
            size_hint=(0.5, 1),
            background_color=(0.902, 0.902, 0.980, 1),  # #E6E6FA in RGBA (Lavender)
        )
        self.spinner.bind(text=self.on_spinner_select)
        top_layout.add_widget(self.spinner)

        # Text input for manual search
        self.text_input = TextInput(
            hint_text="Type actress name, then Enter",
            size_hint=(0.5, 1),
            multiline=False,
            background_color=(0.902, 0.902, 0.980, 1),
            padding_y=(45, 20),
            foreground_color=(0, 0, 1, 1)  # Blue text
        )
        self.text_input.bind(on_text_validate=self.on_text_enter)
        top_layout.add_widget(self.text_input)

        self.add_widget(top_layout)

        # Image display
        self.image = Image(size_hint=(1, 0.5))
        self.add_widget(self.image)

        # Movies & Series Label
        self.movies_label = Label(
            text="",
            size_hint=(1, 0.3),
            halign="center",
            valign="top",
            markup=True
        )
        self.movies_label.bind(size=self.movies_label.setter('text_size'))  # Enable text wrapping
        self.add_widget(self.movies_label)

    def get_actress_names(self):
        """Fetch all actress names from the database and return them sorted."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Person FROM actresses ORDER BY Person ASC")
        names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return names

    def get_actress_data(self, name):
        """Fetch actress image and movies/series from the database."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Image FROM actresses WHERE Person = ? LIMIT 1", (name,))
        result = cursor.fetchone()
        image_file = result[0] if result else None

        # Get Movies
        cursor.execute("SELECT Title FROM actresses WHERE Person = ? AND Type = 'Movie'", (name,))
        movies = [row[0] for row in cursor.fetchall()]

        # Get Series
        cursor.execute("SELECT Title FROM actresses WHERE Person = ? AND Type = 'Series'", (name,))
        series = [row[0] for row in cursor.fetchall()]

        conn.close()
        return image_file, movies, series

    def show_info(self, actress_name):
        """Display actress image and separate movies/series."""
        if not actress_name:
            return

        image_file, movies, series = self.get_actress_data(actress_name)

        if image_file:
            image_path = os.path.join(image_folder, image_file)
            if os.path.exists(image_path):
                self.image.source = image_path
                self.spinner.text = actress_name  # Update dropdown selection
                self.text_input.text = ""  # Clear manual input field

                # Format movie and series text
                movie_text = f"[b]Movies:[/b]\n" + "\n".join(movies) if movies else ""
                series_text = f"[b]TV Series:[/b]\n" + "\n".join(series) if series else ""

                self.movies_label.text = "\n\n".join(filter(None, [movie_text, series_text]))
            else:
                self.movies_label.text = "Image file not found!"
        else:
            self.movies_label.text = "Actress not found in database!"

    def on_spinner_select(self, spinner, text):
        """Handle selection from the dropdown."""
        self.show_info(text)

    def on_text_enter(self, instance):
        """Handle manual text entry and pressing Enter."""
        actress_name = self.text_input.text.strip()
        self.show_info(actress_name)

class ActressApp(App):
    def build(self):
        return ActressViewer()

if __name__ == "__main__":
    ActressApp().run()
