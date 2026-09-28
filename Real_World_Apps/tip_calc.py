from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class TipCalculatorApp(App):
    def build(self):
        # Set up a vertical layout for a mobile screen
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Title Screen
        self.layout.add_widget(Label(text="Mobile Tip Calculator", font_size=24, bold=True, size_hint_y=None, height=50))

        # Bill Input Fields
        self.layout.add_widget(Label(text="Bill Amount ($):", halign='left', size_hint_y=None, height=30))
        self.bill_input = TextInput(text='', input_filter='float', multiline=False, size_hint_y=None, height=50)
        self.layout.add_widget(self.bill_input)

        # Tip Input Fields
        self.layout.add_widget(Label(text="Tip Percentage (%):", halign='left', size_hint_y=None, height=30))
        self.tip_input = TextInput(text='15', input_filter='int', multiline=False, size_hint_y=None, height=50)
        self.layout.add_widget(self.tip_input)

        # Calculate Button
        calc_button = Button(text="Calculate", background_color=(0, 0.6, 0.8, 1), size_hint_y=None, height=60, font_size=18)
        calc_button.bind(on_press=self.calculate_tip)
        self.layout.add_widget(calc_button)

        # Results Label
        self.result_label = Label(text="Total Bill: $0.00", font_size=20, bold=True)
        self.layout.add_widget(self.result_label)

        return self.layout

    def calculate_tip(self, instance):
        try:
            bill = float(self.bill_input.text)
            tip_pct = float(self.tip_input.text)
            
            total_tip = bill * (tip_pct / 100)
            total_bill = bill + total_tip
            
            self.result_label.text = f"Total Bill: ${total_bill:.2f}"
        except ValueError:
            self.result_label.text = "Please enter valid numbers!"

if __name__ == '__main__':
    TipCalculatorApp().run()
