import pandas as pd
import numpy as np

class Verificacion_Holgura:
    def __init__(self):
        self.primal = None
        self.dual = None
        self.tolerancia = 1e-1  # Tolerancia para considerar un número como cero
    
    def ReadResults(self):
        # Leer resultados del primal
        self.transporte = pd.read_excel('Resultados_GreenPharma.xlsx', sheet_name='Transporte')
        self.inventario = pd.read_excel('Resultados_GreenPharma.xlsx', sheet_name='Inventario')
        self.stock = pd.read_excel('Resultados_GreenPharma.xlsx', sheet_name='Stock')
        
        # Leer resultados del dual
        self.balance_prod = pd.read_excel('Resultados_GreenPharma_Dual.xlsx', sheet_name='Balance_Produccion')
        self.balance_inv = pd.read_excel('Resultados_GreenPharma_Dual.xlsx', sheet_name='Balance_Inventario')
        self.capacidad = pd.read_excel('Resultados_GreenPharma_Dual.xlsx', sheet_name='Capacidad_Transporte')

    def Verificar_Holgura(self):
        print("Verificación de Holgura Complementaria:")
        print("-" * 50)

        # 1. Restricción de Transporte
        print("\n1. Restricción de Transporte:")
        for _, row in self.transporte.iterrows():
            t = row['Periodo']
            i = row['Fabrica']
            j = row['Centro']
            x = row['Cantidad']
            a = self.balance_prod[(self.balance_prod['Periodo'] == t) & 
                                  (self.balance_prod['Fabrica'] == i)]['Valor_a'].values[0]
            b = self.balance_inv[(self.balance_inv['Periodo'] == t) & 
                                 (self.balance_inv['Centro'] == j)]['Valor_b'].values[0]
            c = self.capacidad[(self.capacidad['Periodo'] == t) & 
                               (self.capacidad['Fabrica'] == i)]['Valor_c'].values[0]
            holgura_dual = (a + b + c)  # Debe ser igual a C[i,j] en el modelo, pero aquí solo usamos el dual
            producto = x * (holgura_dual)
            cumple = abs(producto) < self.tolerancia
            print(f"x[{i},{j},{t}] = {x:.4f}, (a+b+c) = {holgura_dual:.4f}, x*(a+b+c) = {producto:.2e} -> {'OK' if cumple else 'NO'}")

        # 2. Restricción de Inventario
        print("\n2. Restricción de Inventario:")
        periodos = sorted(self.inventario['Periodo'].unique())
        for _, row in self.inventario.iterrows():
            t = row['Periodo']
            j = row['Centro']
            y = row['Inventario']
            if t < periodos[-1]:
                b_actual = self.balance_inv[(self.balance_inv['Periodo'] == t) & 
                                            (self.balance_inv['Centro'] == j)]['Valor_b'].values[0]
                b_siguiente = self.balance_inv[(self.balance_inv['Periodo'] == t+1) & 
                                               (self.balance_inv['Centro'] == j)]['Valor_b'].values[0]
                holgura_dual = (-b_actual + b_siguiente)
            else:
                b_actual = self.balance_inv[(self.balance_inv['Periodo'] == t) & 
                                            (self.balance_inv['Centro'] == j)]['Valor_b'].values[0]
                holgura_dual = -b_actual  # Inventario final
            producto = y * holgura_dual
            cumple = abs(producto) < self.tolerancia
            print(f"y[{j},{t}] = {y:.4f}, holgura dual = {holgura_dual:.4f}, y*holgura = {producto:.2e} -> {'OK' if cumple else 'NO'}")

        # 3. Restricción de Stock
        print("\n3. Restricción de Stock:")
        for _, row in self.stock.iterrows():
            t = row['Periodo']
            i = row['Fabrica']
            s = row['Stock']
            a = self.balance_prod[(self.balance_prod['Periodo'] == t) & 
                                  (self.balance_prod['Fabrica'] == i)]['Valor_a'].values[0]
            holgura_dual = a  # En el dual, a <= G, así que holgura es a-G, pero para la complementaria usamos a
            producto = s * holgura_dual
            cumple = abs(producto) < self.tolerancia
            print(f"s[{i},{t}] = {s:.4f}, a = {a:.4f}, s*a = {producto:.2e} -> {'OK' if cumple else 'NO'}")

if __name__ == "__main__":
    verificador = Verificacion_Holgura()
    verificador.ReadResults()
    verificador.Verificar_Holgura()