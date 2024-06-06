import random
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

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
        self.cola_llegada = []
        self.clientes_atendidos = 0
        self.clientes_abandonados = 0
        self.tiempo_inicio_operacion = None
        self.tiempo_fin_operacion = None
        self.tiempo_min_atencion = float('inf')
        self.tiempo_max_atencion = 0
        self.tiempo_min_espera = float('inf')
        self.tiempo_max_espera = 0
    
    def probabilidad_llegada(self, tiempo_actual):
        prob = stats.norm.pdf(tiempo_actual, loc=36000, scale=7200)
        return prob

    def simular(self):
        """
        Simula la operación del local durante un día.
        """
        self.tiempo_inicio_operacion = 8 * 3600  # Tiempo de apertura (8:00 AM) en segundos
        self.tiempo_fin_operacion = 12 * 3600  # Tiempo de cierre (12:00 PM) en segundos

        tiempo_actual = self.tiempo_inicio_operacion
        cliente_llega = []
        tiempos_llegada = []
        tiempos_atencion = []
        tiempos_espera = []
        tiempos_salida = []

        # Calcula la probabilidad de que un cliente llegue en un momento dado, teniendo en cuenta la distribución normal (Mientras mas cerca de las 10 am mas probabilidad de que llegue un cliente)
        probabilidad_llegada = self.probabilidad_llegada(tiempo_actual)

        # Ahora lo utiliza en el while
        while tiempo_actual < self.tiempo_fin_operacion:
            
            # Utiliza la probabilidad de llegada para determinar si un cliente llega
            if random.random() < probabilidad_llegada:
                cliente = Cliente(tiempo_actual)
                self.cola_llegada.append(cliente)
                cliente_llega.append(tiempo_actual)

            if 9 * 3600 < tiempo_actual < 9.5 * 3600 or 10.5 * 3600 < tiempo_actual < 11 * 3600:
                if random.random() < 1/130:
                    cliente = Cliente(tiempo_actual)
                    self.cola.append(cliente)
                    tiempos_llegada.append(tiempo_actual)   

            elif 9.5 * 3600 < tiempo_actual < 10.5 * 3600:
                if random.random() < 1/70:
                    cliente = Cliente(tiempo_actual)
                    self.cola.append(cliente)
                    tiempos_llegada.append(tiempo_actual)
            
            elif 8.5 * 3600 < tiempo_actual < 9 * 3600 or 11 * 3600 < tiempo_actual < 11.5 * 3600: 
                if random.random() < 1/210:
                    cliente = Cliente(tiempo_actual)
                    self.cola.append(cliente)
                    tiempos_llegada.append(tiempo_actual)
            
            elif 8 * 3600 < tiempo_actual < 8.5 * 3600 or 11.5 * 3600 < tiempo_actual < 12 * 3600:
                if random.random() < 1/250:
                    cliente = Cliente(tiempo_actual)
                    self.cola.append(cliente)
                    tiempos_llegada.append(tiempo_actual)
            

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
        print(f"\nResultados de la simulación:")
        print(f"Boxes de atención: {self.cantidad_boxes}")
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

        # Histograma de clientes por hora
        plt.subplot(2, 2, 2)  # Crea la primera fila de subplots (derecha)
        tiempos_llegada_horas = [(t / 3600) - 8 for t in tiempos_llegada]  # Convierte los tiempos a horas desde las 8 AM
        plt.hist(tiempos_llegada_horas, bins=np.arange(0, 5, 0.5), edgecolor='black', color='blue')        
        plt.xlabel("Hora del día")
        plt.ylabel("Cantidad de Clientes")
        plt.title("Clientes Ingresados por Hora")
        plt.xticks(np.arange(0, 4.5, 0.5), labels=[
        '8', '8:30', '9', '9:30', '10', '10:30',
        '11', '11:30', '12'  # Elimina la etiqueta '12:30 PM'
        ])

        # Puedes agregar más subplots o gráficos aquí según tus necesidades
        
        plt.tight_layout()  # Ajusta el layout para evitar solapamiento
        plt.show()

if __name__ == "__main__":
    cantidad_boxes = int(input("Ingrese la cantidad de boxes: "))
    local = Local(cantidad_boxes)
    tiempos_llegada, tiempos_atencion, tiempos_espera, tiempos_salida = local.simular()
    local.imprimir_resultados()
    local.graficar_resultados(tiempos_llegada, tiempos_atencion, tiempos_espera, tiempos_salida)