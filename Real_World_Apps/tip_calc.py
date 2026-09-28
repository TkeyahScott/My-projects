#KeyS DevOps
#27.09.2026
#version ctrl trial.
#v2.0

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

class TipCalculatorApp(App):
    def build(self):
        # 1. Main vertical window container
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # App Header Title
        self.layout.add_widget(Label(text="Mobile Tip Calculator", font_size=24, bold=True, size_hint_y=None, height=45))

        # Input Forms Section
        self.layout.add_widget(Label(text="Bill Amount ($):", size_hint_y=None, height=20, text_size=(400, None), halign='left'))
        self.bill_input = TextInput(text='', hint_text='0.00', input_filter='float', multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.bill_input)

        self.layout.add_widget(Label(text="Tip Percentage (%):", size_hint_y=None, height=20, text_size=(400, None), halign='left'))
        self.tip_input = TextInput(text='15', hint_text='15', input_filter='int', multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.tip_input)

        self.layout.add_widget(Label(text="Number of People:", size_hint_y=None, height=20, text_size=(400, None), halign='left'))
        self.people_input = TextInput(text='1', hint_text='1', input_filter='int', multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.people_input)

        # Action Button
        calc_button = Button(text="Calculate Split", background_color=(0, 0.6, 0.8, 1), size_hint_y=None, height=50, font_size=18, bold=True)
        calc_button.bind(on_press=self.calculate_tip)
        self.layout.add_widget(calc_button)

        # ==========================================
        # NEW DESIGN: SPLIT LOWER SCREEN (LEFT & RIGHT)
        # ==========================================
        lower_section = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=1)
        
        # --- LEFT SIDE PANEL (Metrics Display) ---
        left_panel = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.5)
        
        # Grid layout cleanly keeps labels on the left and values on the right
        metrics_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=60)
        
        metrics_grid.add_widget(Label(text="Tip Amount:", font_size=16, halign='left', text_size=(120, None)))
        self.tip_label = Label(text="$0.00", font_size=16, bold=True, halign='left', text_size=(120, None))
        metrics_grid.add_widget(self.tip_label)
        
        metrics_grid.add_widget(Label(text="Total Bill:", font_size=16, halign='left', text_size=(120, None)))
        self.total_label = Label(text="$0.00", font_size=16, bold=True, halign='left', text_size=(120, None))
        metrics_grid.add_widget(self.total_label)
        
        left_panel.add_widget(metrics_grid)
        
        # Large prominent display for the Per Person final answer below them
        left_panel.add_widget(Label(text="Per Person:", font_size=16, halign='left', text_size=(240, None)))
        self.per_person_label = Label(text="$0.00", font_size=28, bold=True, color=(0, 1, 0.5, 1), halign='left', text_size=(240, None))
        left_panel.add_widget(self.per_person_label)
        
        lower_section.add_widget(left_panel)

        # --- RIGHT SIDE PANEL (Past Calculations) ---
        right_panel = BoxLayout(orientation='vertical', spacing=5, size_hint_x=0.5)
        right_panel.add_widget(Label(text="--- Past Calculations ---", font_size=14, bold=True, color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=20))
        
        scroll_container = ScrollView()
        self.history_list = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.history_list.bind(minimum_height=self.history_list.setter('height'))
        
        scroll_container.add_widget(self.history_list)
        right_panel.add_widget(scroll_container)
        
        lower_section.add_widget(right_panel)
        
        # Add the unified split layout to our app window
        self.layout.add_widget(lower_section)

        return self.layout

    def calculate_tip(self, instance):
        try:
            bill_text = self.bill_input.text.strip()
            bill = float(bill_text) if bill_text else 0.00
            
            tip_text = self.tip_input.text.strip()
            tip_pct = float(tip_text) if tip_text else 15.0
            
            people_text = self.people_input.text.strip()
            people = int(people_text) if people_text else 1
            if people < 1:
                people = 1
                self.people_input.text = '1'

            total_tip = bill * (tip_pct / 100)
            total_bill = bill + total_tip
            per_person = total_bill / people
            
            # Update UI values seamlessly inside their clean layout grids
            self.tip_label.text = f"${total_tip:.2f}"
            self.total_label.text = f"${total_bill:.2f}"
            self.per_person_label.text = f"${per_person:.2f}"
            
            # Simpler log design format to sit comfortably on the right column
            history_entry = f"${bill:.2f} + {int(tip_pct)}% ({people}x) = ${per_person:.2f}"
            new_history_label = Label(text=history_entry, font_size=12, size_hint_y=None, height=20, text_size=(240, None), halign='left', color=(0.8, 0.8, 0.8, 1))
            
            self.history_list.add_widget(new_history_label, index=len(self.history_list.children))
            
        except ValueError:
            self.per_person_label.text = "Error!"

if __name__ == '__main__':
    TipCalculatorApp().run()
