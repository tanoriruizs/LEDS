import tkinter as tk
from PIL import Image, ImageTk
import serial

try:
    arduino = serial.Serial('COM4', 9600)
except:
    print("Verifica el puerto serial")
    exit()

class HomeLightingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Focos de la Casa")

        # Tamaño deseado para las imágenes de los focos
        self.foco_size = (50, 50)

        # Diccionario para mantener el estado de los focos
        self.lights = {
            "Cuarto": False,
            "Cocina": False,
            "Sala": False,
            "Cochera": False
        }

        self.all_lights_on = False  # Estado para todos los focos

        # Cargar y redimensionar la imagen de fondo usando Pillow
        try:
            self.background_image = Image.open("casa.jpg")
            self.background_photo = ImageTk.PhotoImage(self.background_image)
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.background_photo = None

        # Cargar y redimensionar las imágenes de los focos
        try:
            self.foco_apagado_image = Image.open("foco_apagado.png").resize(self.foco_size)
            self.foco_apagado_photo = ImageTk.PhotoImage(self.foco_apagado_image)
            self.foco_encendido_image = Image.open("foco_encendido.png").resize(self.foco_size)
            self.foco_encendido_photo = ImageTk.PhotoImage(self.foco_encendido_image)
        except Exception as e:
            print(f"Error loading light images: {e}")
            self.foco_apagado_photo = self.foco_encendido_photo = None

        # Crear el canvas y añadir la imagen de fondo
        self.canvas = tk.Canvas(root, width=self.background_photo.width() if self.background_photo else 600, height=self.background_photo.height() if self.background_photo else 400)
        self.canvas.pack()
        if self.background_photo:
            self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        # Crear y colocar botones para cada habitación
        self.create_buttons()

        # Dibujar los focos
        self.draw_lights()

    def create_buttons(self):
        self.buttons = {}
        for room in self.lights:
            button_frame = tk.Frame(self.root)
            button_frame.pack(pady=5, padx=10, side=tk.LEFT)

            button = tk.Button(button_frame, text=f"Encender {room}", command=lambda r=room: self.toggle_light(r))
            button.pack()
            self.buttons[room] = button
        
        # Botón para encender/apagar todos los focos
        all_button_frame = tk.Frame(self.root)
        all_button_frame.pack(pady=5, padx=10, side=tk.LEFT)

        self.all_button = tk.Button(all_button_frame, text="Encender Todos", command=self.toggle_all_lights)
        self.all_button.pack()

        # Botón para cerrar la ventana
        exit_button_frame = tk.Frame(self.root)
        exit_button_frame.pack(pady=5, padx=10, side=tk.LEFT)

        exit_button = tk.Button(exit_button_frame, text="Cerrar", command=self.root.quit)
        exit_button.pack()

    def draw_lights(self):
        self.canvas.delete("foco")  # Limpiar los focos del canvas antes de redibujar
        positions = {
            "Cuarto": (500, 130),
            "Cocina": (530, 300),
            "Sala": (730, 420),
            "Cochera": (750, 140)
        }
        for room, (x, y) in positions.items():
            image = self.foco_encendido_photo if self.lights[room] else self.foco_apagado_photo
            if image:
                self.canvas.create_image(x, y, anchor="center", image=image, tags="foco")
            self.canvas.create_text(x, y+40, text=room, tags="foco")

    def toggle_light(self, room):
        self.lights[room] = not self.lights[room]
        new_state = "Apagar" if self.lights[room] else "Encender"
        self.buttons[room].config(text=f"{new_state} {room}")
        self.draw_lights()

        # Enviar comando al Arduino
        if room == "Cuarto":
            arduino.write(b'a' if self.lights[room] else b'A')
        elif room == "Cocina":
            arduino.write(b's' if self.lights[room] else b'S')
        elif room == "Sala":
            arduino.write(b'd' if self.lights[room] else b'D')
        elif room == "Cochera":
            arduino.write(b'f' if self.lights[room] else b'F')

    def toggle_all_lights(self):
        self.all_lights_on = not self.all_lights_on
        new_state = "Apagar Todos" if self.all_lights_on else "Encender Todos"
        self.all_button.config(text=new_state)
        
        # Actualizar todos los focos
        for room in self.lights:
            self.lights[room] = self.all_lights_on
            self.buttons[room].config(text=f"Apagar {room}" if self.all_lights_on else f"Encender {room}")

        self.draw_lights()

        # Enviar comando al Arduino
        if self.all_lights_on:
            arduino.write(b'a')
            arduino.write(b's')
            arduino.write(b'd')
            arduino.write(b'f')
        else:
            arduino.write(b'A')
            arduino.write(b'S')
            arduino.write(b'D')
            arduino.write(b'F')

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeLightingApp(root)
    root.mainloop()
