import numpy as np
import pandas as pd
from pyomo.environ import *

class Problema_GreenPharma:
    def __init__(self):
        self.Data = None
    
    def ReadExcelFile(self, FileName):
        self.Produccion = pd.read_excel(FileName, sheet_name='Produccion')
        self.Demanda = pd.read_excel(FileName, sheet_name='Demanda')
        self.Costos_Fabricas = pd.read_excel(FileName, sheet_name='Costos_Fabricas')
        self.Costos_Transporte = pd.read_excel(FileName, sheet_name='Costos_Transporte')
        self.Costos_Centros = pd.read_excel(FileName, sheet_name='Costos_Centros')
        
        self.N_fabricas = len(self.Produccion.columns) - 1  # Assuming first column is index
        self.N_centros = len(self.Demanda.columns) - 1     # Assuming first column is index
        self.N_periodos = len(self.Produccion)             # Number of rows in Produccion

    def Model(self):
        model = AbstractModel(name='Model')

        ## SETS ##
        model.I = Set(initialize=range(1, self.N_fabricas + 1))
        model.J = Set(initialize=range(1, self.N_centros + 1))
        model.T = Set(initialize=range(1, self.N_periodos + 1))

        ## PARAMETERS ##
        def C_init(model, i, j):
            return self.Costos_Transporte.iloc[i-1, j]
        model.C = Param(model.I, model.J, rule=C_init)

        def H_init(model, j):
            return self.Costos_Centros.iloc[j-1, 1]
        model.H = Param(model.J, rule=H_init)

        def G_init(model, i):
            return self.Costos_Fabricas.iloc[i-1, 1]
        model.G = Param(model.I, rule=G_init)

        def P_init(model, i, t):
            return self.Produccion.iloc[t-1, i]
        model.P = Param(model.I, model.T, rule=P_init)

        def D_init(model, j, t):
            return self.Demanda.iloc[t-1, j]
        model.D = Param(model.J, model.T, rule=D_init)

        def K_init(model, i):
            return self.Costos_Fabricas.iloc[i-1, 2]
        model.K = Param(model.I, rule=K_init) 

        ## VARIABLES ##
        model.x = Var(model.I, model.J, model.T, within=NonNegativeReals, initialize=0)
        model.y = Var(model.J, model.T, within=NonNegativeReals, initialize=0)
        model.s = Var(model.I, model.T, within=NonNegativeReals, initialize=0)

        ## OBJECTIVE FUNCTION ##
        def Fun_obj(model):
            costos_transporte = sum(model.C[i,j] * model.x[i,j,t] for i in model.I for j in model.J for t in model.T)
            costos_inventario = sum(model.H[j] * model.y[j,t] for j in model.J for t in model.T)
            costos_stock = sum(model.G[i] * model.s[i,t] for i in model.I for t in model.T)
            return costos_transporte + costos_inventario + costos_stock
        model.FunObj = Objective(rule=Fun_obj, sense=minimize)

        ## CONSTRAINTS ##
        def Balance_Fabricas(model, i, t):
            return sum(model.x[i,j,t] for j in model.J) + model.s[i,t] == model.P[i,t]
        model.balance_fabricas = Constraint(model.I, model.T, rule=Balance_Fabricas)

        def Balance_Centros_P1(model, j):
            return sum(model.x[i,j,1] for i in model.I) == model.D[j,1] + model.y[j,1]
        model.balance_centros_p1 = Constraint(model.J, rule=Balance_Centros_P1)

        def Balance_Centros_Resto(model, j, t):
            if t > 1:
                return model.y[j,t-1] + sum(model.x[i,j,t] for i in model.I) == model.D[j,t] + model.y[j,t]
            return Constraint.Skip
        model.balance_centros_resto = Constraint(model.J, model.T, rule=Balance_Centros_Resto)

        def Capacidad_Transporte(model, i, t):
            return sum(model.x[i,j,t] for j in model.J) <= model.K[i]
        model.capacidad_transporte = Constraint(model.I, model.T, rule=Capacidad_Transporte)
        
        return model.create_instance()

    def Solver(self):
        Modelo_greenpharma = self.Model()
        self.opt = SolverFactory('glpk', executable=r'/home/pc01/anaconda3/envs/io/bin/glpsol')
        results = self.opt.solve(Modelo_greenpharma)
        results.write()

        print('Valor Función Objetivo: ' + str(value(Modelo_greenpharma.FunObj)))
        return Modelo_greenpharma

    def Print_Results(self, Modelo_greenpharma):
        Table_Transport = pd.DataFrame()
        Table_Inventory = pd.DataFrame()
        Table_Stock = pd.DataFrame()

        r = 0
        for t in Modelo_greenpharma.T:
            for i in Modelo_greenpharma.I:
                for j in Modelo_greenpharma.J:
                    Table_Transport.loc[r,'Periodo'] = t
                    Table_Transport.loc[r,'Fabrica'] = i
                    Table_Transport.loc[r,'Centro'] = j
                    Table_Transport.loc[r,'Cantidad'] = round(Modelo_greenpharma.x[i,j,t].value,4)
                    r += 1

        r = 0
        for t in Modelo_greenpharma.T:
            for j in Modelo_greenpharma.J:
                Table_Inventory.loc[r,'Periodo'] = t
                Table_Inventory.loc[r,'Centro'] = j
                Table_Inventory.loc[r,'Inventario'] = round(Modelo_greenpharma.y[j,t].value,4)
                r += 1

        r = 0
        for t in Modelo_greenpharma.T:
            for i in Modelo_greenpharma.I:
                Table_Stock.loc[r,'Periodo'] = t
                Table_Stock.loc[r,'Fabrica'] = i
                Table_Stock.loc[r,'Stock'] = round(Modelo_greenpharma.s[i,t].value,4)
                r += 1

        with pd.ExcelWriter('Resultados_GreenPharma.xlsx') as writer:
            Table_Transport.to_excel(writer, sheet_name='Transporte', index=False)
            Table_Inventory.to_excel(writer, sheet_name='Inventario', index=False)
            Table_Stock.to_excel(writer, sheet_name='Stock', index=False)

class Problema_GreenPharma_Dual:
    def __init__(self):
        self.Data = None
    
    def ReadExcelFile(self, FileName):
        # Mantener la misma lectura de datos que el primal
        self.Produccion = pd.read_excel(FileName, sheet_name='Produccion')
        self.Demanda = pd.read_excel(FileName, sheet_name='Demanda')
        self.Costos_Fabricas = pd.read_excel(FileName, sheet_name='Costos_Fabricas')
        self.Costos_Transporte = pd.read_excel(FileName, sheet_name='Costos_Transporte')
        self.Costos_Centros = pd.read_excel(FileName, sheet_name='Costos_Centros')
        
        self.N_fabricas = len(self.Produccion.columns) - 1
        self.N_centros = len(self.Demanda.columns) - 1
        self.N_periodos = len(self.Produccion)

    def Model(self):
        model = AbstractModel(name='Model_Dual')

        ## SETS ##
        model.I = Set(initialize=range(1, self.N_fabricas + 1))
        model.J = Set(initialize=range(1, self.N_centros + 1))
        model.T = Set(initialize=range(1, self.N_periodos + 1))

        ## PARAMETERS ##
        def C_init(model, i, j):
            return self.Costos_Transporte.iloc[i-1, j]
        model.C = Param(model.I, model.J, rule=C_init)

        def H_init(model, j):
            return self.Costos_Centros.iloc[j-1, 1]
        model.H = Param(model.J, rule=H_init)

        def G_init(model, i):
            return self.Costos_Fabricas.iloc[i-1, 1]
        model.G = Param(model.I, rule=G_init)

        def K_init(model, i):
            return self.Costos_Fabricas.iloc[i-1, 2]
        model.K = Param(model.I, rule=K_init)

        def P_init(model, i, t):
            return self.Produccion.iloc[t-1, i]
        model.P = Param(model.I, model.T, rule=P_init)

        def D_init(model, j, t):
            return self.Demanda.iloc[t-1, j]
        model.D = Param(model.J, model.T, rule=D_init)

        ## VARIABLES ##
        model.a = Var(model.I, model.T, within=Reals)
        model.b = Var(model.J, model.T, within=Reals)
        model.c = Var(model.I, model.T, within=NonPositiveReals)

        ## OBJECTIVE FUNCTION ##
        def Fun_obj(model):
            return (sum(model.P[i,t] * model.a[i,t] for i in model.I for t in model.T) + 
                   sum(model.D[j,t] * model.b[j,t] for j in model.J for t in model.T) + 
                   sum(model.K[i] * model.c[i,t] for i in model.I for t in model.T))
        model.FunObj = Objective(rule=Fun_obj, sense=maximize)

        ## CONSTRAINTS ##
        def Rest_Transporte(model, i, j, t):
            return model.a[i,t] + model.b[j,t] + model.c[i,t] <= model.C[i,j]
        model.rest_transporte = Constraint(model.I, model.J, model.T, rule=Rest_Transporte)

        def Rest_Inventario_Centros(model, j, t):
            if t < self.N_periodos:
                return -model.b[j,t] + model.b[j,t+1] <= model.H[j]
            return Constraint.Skip
        model.rest_inventario_centros = Constraint(model.J, model.T, rule=Rest_Inventario_Centros)

        def Rest_Inventario_Final(model, j):
            return -model.b[j,self.N_periodos] <= model.H[j]
        model.rest_inventario_final = Constraint(model.J, rule=Rest_Inventario_Final)

        def Rest_Stock_Fabricas(model, i, t):
            return model.a[i,t] <= model.G[i]
        model.rest_stock_fabricas = Constraint(model.I, model.T, rule=Rest_Stock_Fabricas)

        return model.create_instance()
    
    def Solver(self):
        Modelo_dual = self.Model()
        self.opt = SolverFactory('glpk', executable=r'/home/pc01/anaconda3/envs/io/bin/glpsol')
        results = self.opt.solve(Modelo_dual)
        results.write()

        print('Valor Función Objetivo Dual: ' + str(value(Modelo_dual.FunObj)))
        return Modelo_dual

    def Print_Results(self, Modelo_dual):
        Table_Dual_Fab = pd.DataFrame()
        Table_Dual_Centros = pd.DataFrame()
        Table_Dual_Capacidad = pd.DataFrame()

        r = 0
        for t in Modelo_dual.T:
            for i in Modelo_dual.I:
                Table_Dual_Fab.loc[r,'Periodo'] = t
                Table_Dual_Fab.loc[r,'Fabrica'] = i
                Table_Dual_Fab.loc[r,'Valor_a'] = round(Modelo_dual.a[i,t].value,4)
                r += 1

        r = 0
        for t in Modelo_dual.T:
            for j in Modelo_dual.J:
                Table_Dual_Centros.loc[r,'Periodo'] = t
                Table_Dual_Centros.loc[r,'Centro'] = j
                Table_Dual_Centros.loc[r,'Valor_b'] = round(Modelo_dual.b[j,t].value,4)
                r += 1

        r = 0
        for t in Modelo_dual.T:
            for i in Modelo_dual.I:
                Table_Dual_Capacidad.loc[r,'Periodo'] = t
                Table_Dual_Capacidad.loc[r,'Fabrica'] = i
                Table_Dual_Capacidad.loc[r,'Valor_c'] = round(Modelo_dual.c[i,t].value,4)
                r += 1

        with pd.ExcelWriter('Resultados_GreenPharma_Dual.xlsx') as writer:
            Table_Dual_Fab.to_excel(writer, sheet_name='Balance_Produccion', index=False)
            Table_Dual_Centros.to_excel(writer, sheet_name='Balance_Inventario', index=False)
            Table_Dual_Capacidad.to_excel(writer, sheet_name='Capacidad_Transporte', index=False)

if __name__ == "__main__":
    problema = Problema_GreenPharma()
    problema.ReadExcelFile('Data_Input.xlsx')
    modelo = problema.Solver()
    problema.Print_Results(modelo)

    problema_dual = Problema_GreenPharma_Dual()
    problema_dual.ReadExcelFile('Data_Input.xlsx')
    modelo_dual = problema_dual.Solver()
    problema_dual.Print_Results(modelo_dual)

