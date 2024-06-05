import pygame
import random
import numpy as np
import threading
import cv2 
import os

class Cliente:
    """
    Representa un cliente que ingresa al local.
    """
    def __init__(self, tiempo_llegada):
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_atencion = None
        self.tiempo_salida = None
        self.tiempo_espera = None

class Box:
    """
    Representa un box de atención al cliente.
    """
    def __init__(self):
        self.ocupado = False
        self.cliente_actual = None
        self.tiempo_inicio_atencion = None

class Local:
    """
    Representa el local de servicio.
    """
    def __init__(self, cantidad_boxes, fps):
        self.cantidad_boxes = cantidad_boxes
        self.boxes = [Box() for _ in range(cantidad_boxes)]
        self.fps = fps
        self.cola = []
        self.clientes_atendidos = 0
        self.clientes_abandonados = 0
        self.tiempo_inicio_operacion = None
        self.tiempo_fin_operacion = None
        self.tiempo_min_atencion = float('inf')
        self.tiempo_max_atencion = 0
        self.tiempo_min_espera = float('inf')
        self.tiempo_max_espera = 0

    def simular(self):
        """
        Simula la operación del local durante un día.
        """
        self.tiempo_inicio_operacion = 0  # Tiempo de apertura (8:00 AM)
        self.tiempo_fin_operacion = 14400  # Tiempo de cierre (12:00 AM) en segundos

        tiempo_actual = self.tiempo_inicio_operacion

        while tiempo_actual < self.tiempo_fin_operacion:
            # 1. Verificar si un cliente ingresa
            if random.random() < 1/144:
                cliente = Cliente(tiempo_actual)
                self.cola.append(cliente)

            # 2. Atender a los clientes en la cola
            for i, box in enumerate(self.boxes):
                if not box.ocupado and self.cola:
                    cliente = self.cola.pop(0)
                    box.ocupado = True
                    box.cliente_actual = cliente
                    box.tiempo_inicio_atencion = tiempo_actual
                    cliente.tiempo_atencion = max(0, np.random.normal(loc=600, scale=300))  # Tiempo de atención en segundos, asegurando que sea no negativo

            # 3. Actualizar el estado de los boxes y manejar clientes que abandonan
            for i, box in enumerate(self.boxes):
                if box.ocupado:
                    tiempo_restante_atencion = box.cliente_actual.tiempo_atencion - (tiempo_actual - box.tiempo_inicio_atencion)
                    if tiempo_restante_atencion <= 0:
                        # Cliente termina atención
                        box.ocupado = False
                        box.cliente_actual.tiempo_salida = tiempo_actual
                        box.cliente_actual.tiempo_espera = box.cliente_actual.tiempo_salida - box.cliente_actual.tiempo_llegada
                        self.clientes_atendidos += 1

                        # Actualizar tiempos min y max de atención
                        self.tiempo_min_atencion = min(self.tiempo_min_atencion, box.cliente_actual.tiempo_atencion)
                        self.tiempo_max_atencion = max(self.tiempo_max_atencion, box.cliente_actual.tiempo_atencion)

                        # Actualizar tiempos min y max de espera
                        self.tiempo_min_espera = min(self.tiempo_min_espera, box.cliente_actual.tiempo_espera)
                        self.tiempo_max_espera = max(self.tiempo_max_espera, box.cliente_actual.tiempo_espera)

                    elif box.cliente_actual.tiempo_llegada + 1800 < tiempo_actual:
                        # Cliente que estaba siendo atendido abandona el local
                        box.ocupado = False
                        self.clientes_abandonados += 1  # Incrementa el contador de clientes abandonados

            # 4. Eliminar clientes que abandonan la cola
            for i in range(len(self.cola) - 1, -1, -1):
                if self.cola[i].tiempo_llegada + 1800 < tiempo_actual:  # 30 minutos en segundos
                    self.cola.pop(i)
                    self.clientes_abandonados += 1

            # 5. Animar con pygame (actualización más rápida)
            if tiempo_actual % 100 == 0:  # Actualizar cada 100 unidades de tiempo
                self.actualizar_pantalla(tiempo_actual)

            tiempo_actual += 1  # Incrementar el tiempo para avanzar la simulación

        # 6. Al finalizar la simulación, agregar los clientes que quedaron en la cola a los abandonados
        self.clientes_abandonados += len(self.cola)

    def calcular_costo(self):
        """
        Calcula el costo total de la operación.
        """
        costo_boxes = self.cantidad_boxes * 1000  # Costo de los boxes
        costo_perdida_clientes = self.clientes_abandonados * 10000  # Costo por clientes abandonados
        costo_total = costo_boxes + costo_perdida_clientes
        return costo_total

    def actualizar_pantalla(self, tiempo_actual):
        """
        Actualiza la pantalla con los datos de la simulación.
        """
        # --- Bloquear la superficie de la pantalla antes de modificarla ---
        with screen_lock:
            screen.fill((255, 255, 255))  # Limpiar pantalla

            # Mostrar boxes
            x_boxes = 525
            for i, box in enumerate(self.boxes):
                color = (255, 0, 0) if box.ocupado else (0, 255, 0)
                pygame.draw.rect(screen, color, (x_boxes + i * 60, 50, 50, 50))
                
                # Mostrar número del box
                font = pygame.font.SysFont(None, 20)
                text = font.render(f"Box {i + 1}", True, (0, 0, 0))
                text_rect = text.get_rect(center=(x_boxes + i * 60 + 25, 25))
                screen.blit(text, text_rect)

                # Mostrar circulo azul si está ocupado
                if box.ocupado:
                    pygame.draw.circle(screen, (0, 0, 255), (x_boxes + i * 60 + 25, 50 + 25), 15)

            # Mostrar la cola de clientes
            x_cola = 650   
            y_cola = 150  

            radio_circulo = 15
            for i, cliente in enumerate(self.cola):
                pygame.draw.circle(screen, (0, 0, 255), (x_cola, y_cola + i * (radio_circulo * 2 + 10)), radio_circulo)  # Circulo azul para cada cliente en la cola

            # Mostrar textos

            # Pasa los segundos a minutos y segundos solo si es mayor a 60 segundos. Los segundos se muestran como enteros
            if self.tiempo_min_atencion >= 60:
                text_min_atencion = f"{self.tiempo_min_atencion // 60} minutos y {self.tiempo_min_atencion % 60:.0f} segundos"
            else: 
                text_min_atencion = f"{self.tiempo_min_atencion:.0f} segundos"
            
            if self.tiempo_max_atencion >= 60:
                text_max_atencion = f"{self.tiempo_max_atencion // 60} minutos y {self.tiempo_max_atencion % 60:.0f} segundos"
            else:
                text_max_atencion = f"{self.tiempo_max_atencion:.0f} segundos"
            
            if self.tiempo_min_espera >= 60:
                text_min_espera = f"{self.tiempo_min_espera // 60} minutos y {self.tiempo_min_espera % 60:.0f} segundos"
            else:
                text_min_espera = f"{self.tiempo_min_espera:.0f} segundos"
            
            if self.tiempo_max_espera >= 60:
                text_max_espera = f"{self.tiempo_max_espera // 60} minutos y {self.tiempo_max_espera % 60:.0f} segundos"
            else:
                text_max_espera = f"{self.tiempo_max_espera:.0f} segundos"
            
            # Hora actual en formato HH:MM arrancando desde las 8:00 AM
            hora_actual = f"{tiempo_actual // 3600 + 8:02.0f}:{(tiempo_actual % 3600) // 60+1:02.0f}"

            font = pygame.font.SysFont(None, 23)
            textos = [
                f"Hora: {hora_actual}",
                f"Cantidad de clientes Ingresados: {self.clientes_atendidos + self.clientes_abandonados}",
                f"Cantidad de clientes Atendidos: {self.clientes_atendidos}",
                f"Cantidad de clientes Perdidos: {self.clientes_abandonados}",
                f"Tiempo máximo de atención: {text_max_atencion}",
                f"Tiempo mínimo de atención: {text_min_atencion}",
                f"Tiempo máximo de espera: {text_max_espera}",
                f"Tiempo mínimo de espera: {text_min_espera}",
                f"Costo de tener abiertos los boxes: {self.cantidad_boxes * 1000}",
                f"Costo de los clientes perdidos: {self.clientes_abandonados * 10000}",
                f"Costo operacional total: {self.calcular_costo()}"
            ]

            for i, texto in enumerate(textos):
                img = font.render(texto, True, (0, 0, 0))
                screen.blit(img, (50, 150 + i * 30))  # Mostrar textos a la izquierda de la pantalla

            pygame.display.flip()
            clock.tick(self.fps)  # Incrementar el framerate para hacer la simulación aún más rápida

if __name__ == "__main__":
    # Inicializar pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 600))
    pygame.display.set_caption("Simulación de Boxes de Atención")
    clock = pygame.time.Clock()

    # Cantidad_boxes entre 1 y 10 y los fps entre 5, 15 y 30. Si no ingresa uno valido le vuelve a pedir
    
    cantidad_boxes = int(input("\nIngrese la cantidad de boxes (entre 1 y 10): "))
    fps = int(input("\nIngrese una velocidad (1: 5 fps, 2: 15 fps, 3: 30 fps): "))
    
    while cantidad_boxes < 1 or cantidad_boxes > 10:
        print("\n\nPor favor ingrese una cantidad de box válida\n\n")
        cantidad_boxes = int(input("Ingrese la cantidad de boxes (entre 1 y 10): "))
    
    while fps != 1 and fps != 2 and fps != 3:
        print("\n\nPor favor ingrese una velocidad válida\n\n")
        fps = int(input("Ingrese una velocidad (1: 5 fps, 2: 15 fps, 3: 30 fps): "))
    
    if fps == 1:
        fps = 5
    elif fps == 2:
        fps = 15
    elif fps == 3:
        fps = 30
    
    local = Local(cantidad_boxes, fps)

# --- Buscar un nombre de archivo disponible ---
    nombre_archivo = "animacion.avi"
    contador = 2
    while os.path.exists(nombre_archivo):
        nombre_archivo = f"animacion{contador}.avi"
        contador += 1


    # --- Configuración de la exportación de video ---
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(nombre_archivo, fourcc, fps, (1200, 600))

    # --- Bandera para indicar cuándo grabar ---
    grabando = True

    # --- Crear un Lock para proteger la superficie de la pantalla ---
    screen_lock = threading.Lock()

    # Simular en un thread separado
    simulation_thread = threading.Thread(target=local.simular)
    simulation_thread.start()

    # Loop principal de pygame
    running = True
    while running:
        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Bloquear la superficie de la pantalla antes de modificarla ---
        with screen_lock:
            # --- Exportar el frame actual a video solo durante la simulación ---
            if grabando and simulation_thread.is_alive():
                # Capturar el frame de Pygame y convertirlo a un array de NumPy
                frame = np.array(pygame.surfarray.pixels3d(screen))
                frame = frame.swapaxes(0, 1)  # Intercambiar ejes para que coincida con OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convertir a BGR

                out.write(frame)
            else:
                grabando = False  # Detener la grabación cuando la simulación termina

                # --- Mantener la ventana abierta por un breve tiempo después de la simulación ---
                pygame.time.delay(500)  # Esperar 500 milisegundos (medio segundo)
                running = False  # Salir del bucle principal

    # --- Esperar a que la simulación termine antes de cerrar el archivo ---
    simulation_thread.join()  # Espera a que el hilo termine

    # --- Liberar recursos ---
    out.release()  # Cierra el archivo de video
    pygame.quit()