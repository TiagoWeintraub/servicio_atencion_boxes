import random
import matplotlib.pyplot as plt
import numpy as np

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
    def __init__(self, cantidad_boxes):
        self.cantidad_boxes = cantidad_boxes
        self.boxes = [Box() for _ in range(cantidad_boxes)]
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
        self.tiempo_fin_operacion = 36000  # Tiempo de cierre (12:00 PM) en segundos

        tiempo_actual = self.tiempo_inicio_operacion
        tiempos_llegada = []
        tiempos_atencion = []
        tiempos_espera = []
        tiempos_salida = []

        while tiempo_actual < self.tiempo_fin_operacion:
            # 1. Verificar si un cliente ingresa
            if random.random() < 1/144:
                cliente = Cliente(tiempo_actual)
                self.cola.append(cliente)
                tiempos_llegada.append(tiempo_actual)
                print(f"Cliente llega al local a las {tiempo_actual/3600:.2f} horas")

            # 2. Atender a los clientes en la cola
            for box in self.boxes:
                if not box.ocupado and self.cola:
                    cliente = self.cola.pop(0)
                    box.ocupado = True
                    box.cliente_actual = cliente
                    box.tiempo_inicio_atencion = tiempo_actual
                    cliente.tiempo_atencion = max(0, np.random.normal(loc=600, scale=300))  # Tiempo de atención en segundos, asegurando que sea no negativo
                    tiempos_atencion.append(cliente.tiempo_atencion)
                    print(f"Cliente comienza atención a las {tiempo_actual/3600:.2f} horas")

            # 3. Actualizar el estado de los boxes y manejar clientes que abandonan
            for i, box in enumerate(self.boxes):
                if box.ocupado:
                    tiempo_restante_atencion = box.cliente_actual.tiempo_atencion - (tiempo_actual - box.tiempo_inicio_atencion)
                    if tiempo_restante_atencion <= 0:
                        # Cliente termina atención
                        box.ocupado = False
                        box.cliente_actual.tiempo_salida = tiempo_actual
                        box.cliente_actual.tiempo_espera = box.cliente_actual.tiempo_salida - box.cliente_actual.tiempo_llegada
                        tiempos_espera.append(box.cliente_actual.tiempo_espera)
                        tiempos_salida.append(box.cliente_actual.tiempo_salida)
                        self.clientes_atendidos += 1
                        print(f"Cliente sale del local a las {tiempo_actual/3600:.2f} horas")

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
                        print(f"Cliente que estaba siendo atendido abandona el local a las {tiempo_actual/3600:.2f} horas")

            # 4. Eliminar clientes que abandonan la cola
            for i in range(len(self.cola) - 1, -1, -1):
                if self.cola[i].tiempo_llegada + 1800 < tiempo_actual:  # 30 minutos en segundos
                    self.cola.pop(i)
                    self.clientes_abandonados += 1
                    print(f"Cliente abandona el local a las {tiempo_actual/3600:.2f} horas")

            tiempo_actual += 1

        # 5. Al finalizar la simulación, agregar los clientes que quedaron en la cola a los abandonados
        # (Esta parte ahora solo se ejecuta una vez al final)
        self.clientes_abandonados += len(self.cola)
        print(f"Al cierre del local, {len(self.cola)} clientes abandonan el local")
        
        return tiempos_llegada, tiempos_atencion, tiempos_espera, tiempos_salida

    def calcular_costo(self):
        """
        Calcula el costo total de la operación.
        """
        costo_boxes = self.cantidad_boxes * 1000  # Costo de los boxes
        costo_perdida_clientes = self.clientes_abandonados * 10000  # Costo por clientes abandonados
        costo_total = costo_boxes + costo_perdida_clientes
        return costo_total

    def imprimir_resultados(self):
        """
        Imprime los resultados de la simulación.
        """
        print(f"\nResultados de la simulación:")
        print(f"Clientes ingresados: {self.clientes_atendidos + self.clientes_abandonados}")
        print(f"Clientes atendidos: {self.clientes_atendidos}")
        print(f"Clientes abandonados: {self.clientes_abandonados}")
        print(f"Costo total por clientes abandonados: ${self.clientes_abandonados * 10000}")  
        print(f"Costo total por boxes: ${self.cantidad_boxes * 1000}")
        print(f"Tiempo mínimo de atención en box: {self.tiempo_min_atencion/60:.2f} minutos")
        print(f"Tiempo máximo de atención en box: {self.tiempo_max_atencion/60:.2f} minutos")
        print(f"Tiempo mínimo de espera en salón: {self.tiempo_min_espera/60:.2f} minutos")
        print(f"Tiempo máximo de espera en salón: {self.tiempo_max_espera/60:.2f} minutos")
        print(f"Costo de la operación: ${self.calcular_costo()}")

    def graficar_resultados(self, tiempos_llegada, tiempos_atencion, tiempos_espera, tiempos_salida):
        """
        Grafica los resultados de la simulación.
        """
        plt.figure(figsize=(12, 8))  # Ajusta el tamaño para tres gráficos

        # Histograma de clientes
        plt.subplot(2, 2, 1)  # Crea la primera fila de subplots (izquierda)
        categorias = ['Clientes Ingresados', 'Clientes Atendidos', 'Clientes Perdidos']
        cantidades = [
            self.clientes_atendidos + self.clientes_abandonados,
            self.clientes_atendidos,
            self.clientes_abandonados
        ]
        plt.bar(categorias, cantidades, color=['skyblue', 'green', 'red'])
        plt.ylabel("Cantidad")
        plt.title("Cantidad de Clientes en la Simulación")
        for i, v in enumerate(cantidades):
            plt.text(i, v + 0.5, str(v), ha='center', va='bottom')

        # Histograma de tiempos de atención
        plt.subplot(2, 2, 2)  # Crea la primera fila de subplots (derecha)
        bins = np.arange(0, max(tiempos_atencion) + 60, 60)
        plt.hist(tiempos_atencion, bins=bins, edgecolor='black', label="Tiempos de Atención")
        plt.ylabel("Cantidad de Clientes")
        plt.title("Tiempos de Atención")
        plt.xlim(0, max(tiempos_atencion))

        # Histograma de tiempos de espera
        plt.subplot(2, 2, 3)  # Crea la segunda fila de subplots (abajo)
        bins = np.arange(0, max(tiempos_espera) + 60, 60)
        plt.hist(tiempos_espera, bins=bins, edgecolor='black', label="Tiempos de Espera")
        plt.xlabel("Tiempo (segundos)")
        plt.ylabel("Cantidad de Clientes")
        plt.title("Tiempos de Espera")
        plt.xlim(0, max(tiempos_espera))
        
        # Costos operacionales, muestra el costo de los box, el costo por cliente perdido y el costo total
        plt.subplot(2, 2, 4)
        categorias = ['Costo Total', 'Costo Boxes', 'Costo Clientes Perdidos']
        cantidades = [
            self.calcular_costo(),
            self.cantidad_boxes * 1000,
            self.clientes_abandonados * 10000
        ]
        plt.bar(categorias, cantidades, color=['skyblue', 'green', 'red'])
        plt.ylabel("Cantidad de Plata")
        plt.title("Costos Operacionales")
        

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    cantidad_boxes = int(input("Ingrese la cantidad de boxes: "))
    local = Local(cantidad_boxes)
    tiempos_llegada, tiempos_atencion, tiempos_espera, tiempos_salida = local.simular()
    local.imprimir_resultados()
    local.graficar_resultados(tiempos_llegada, tiempos_atencion, tiempos_espera, tiempos_salida)