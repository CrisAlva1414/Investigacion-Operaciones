import numpy as np
import pandas as pd
import pyomo.environ as pyo

class Scheduling_Problem:
    def _init_(self, name=None):
        self.Data = []

    def ReadExcelFile(self,FileName):
        self.T = 3
        self.T_Max = 480
        self.Z_Total = 6
        self.Producto = pd.read_excel(FileName, sheet_name='Producto')
        self.Zonas = pd.read_excel(FileName, sheet_name='Zonas')
        self.Camiones = pd.read_excel(FileName, sheet_name='Camiones')
        self.N_Prod = len(self.Producto)
        self.N_Zonas = len(self.Zonas)
        self.N_Cam = len(self.Camiones)
    
    def model(self):

        model = pyo.AbstractModel()

        # Conjuntos

        model.A = pyo.Set(initialize=np.arange(1,self.N_Cam+1)) # Camiones
        model.B = pyo.Set(initialize=np.arange(1,self.N_Zonas+1)) # Zonas
        model.C = pyo.Set(initialize=np.arange(1,self.N_Prod+1)) # Productos
        model.T = pyo.Set(initialize=np.arange(1,self.T+1)) # Tiempo

        # Parametros

        def volumen(model,l):
            return self.Producto['Volumen'].loc[l-1]
        model.V = pyo.Param(model.C, rule = volumen)

        def C_NP(model,l):
            return self.Producto['CNP'].loc[l-1]
        model.CNP = pyo.Param(model.C, rule = C_NP)

        def D_d(model,j,l,t):
            return self.Zonas['Demanda_'+str(l)+'_'+str(t)].loc[j-1]
        model.D_d = pyo.Param(model.B,model.C,model.T,rule = D_d)

        def CC(model,i):
            return self.Camiones['Capacidad'].loc[i-1]
        model.CC= pyo.Param(model.A, rule = CC)

        def ZNV(model,j):
            return self.Zonas['ZNV'].loc[j-1]
        model.ZNV = pyo.Param(model.B, rule = ZNV)

        def TV(model,j):
            return self.Zonas['T_Visita'].loc[j-1]
        model.TV = pyo.Param(model.B, rule = TV)

        # Variables

        model.x = pyo.Var(model.A,model.B,model.T, within = pyo.Binary, initialize = 0) 
        model.y = pyo.Var(model.B,model.T, within = pyo.Binary, initialize = 0)
        model.z = pyo.Var(model.A,model.T,model.C,model.B, within = pyo.NonNegativeIntegers, initialize = 0)
        model.w = pyo.Var(model.T,model.B,model.C, within = pyo.NonNegativeIntegers, initialize = 0)
        model.d = pyo.Var(model.B,model.C,model.T, within = pyo.NonNegativeIntegers, initialize = 0)

        def Fun_obj(model):
            return sum(model.y[j,t]*model.ZNV[j] for j in model.B for t in model.T) + \
                sum(model.w[t,j,l]*model.CNP[l] for t in model.T for j in model.B for l in model.C)
        model.FunObj = pyo.Objective(rule = Fun_obj, sense = pyo.minimize)

        # Restricciones

        def t_visita(model,i,t):
            return sum(model.x[i,j,t]*model.TV[j] for j in model.B) <= self.T_Max
        model.t_visita = pyo.Constraint(model.A, model.T, rule = t_visita)

        def demanda_1(model,j,l,t):
            if t == 1:
                return model.d[j,l,t] == model.D_d[j,l,t]
            else:
                return model.d[j,l,t] == model.D_d[j,l,t] + model.w[t-1,j,l]
        model.demanda_1 = pyo.Constraint(model.B, model.C, model.T, rule = demanda_1)

        def demanda_2 (model,j,l,t):
            return sum(model.z[i, t, l, j] for i in model.A) + model.w[t,j,l] == model.d[j,l,t] 
        model.demanda_2 = pyo.Constraint(model.B, model.C, model.T, rule = demanda_2)

        def visitas_1(model,t):
            return sum(model.x[i,j,t] for i in model.A for j in model.B) + sum(model.y[j,t] for j in model.B) == self.Z_Total
        model.visitas_1 = pyo.Constraint(model.T, rule = visitas_1)

        def cap_cam(model,i,t):
            return sum(model.z[i,t,l,j]*model.V[l] for l in model.C for j in model.B) <= model.CC[i]
        model.cap_cam = pyo.Constraint(model.A, model.T, rule = cap_cam)

        def visitas_2(model,i,j,t):
            return sum(model.z[i,t,l,j] for l in model.C) <= 10000*model.x[i,j,t]
        model.visitas_2 = pyo.Constraint(model.A,model.B, model.T, rule = visitas_2)

        def v_oblg(model,i,t):
            return sum(model.x[i,j,t] for j in model.B) >= 1
        model.v_oblg = pyo.Constraint(model.A, model.T, rule = v_oblg)

        def un_camion(model,j,t):
            return sum(model.x[i,j,t] for i in model.A) + model.y[j,t] == 1
        model.un_camion = pyo.Constraint(model.B, model.T, rule = un_camion)

        return model.create_instance()

    def Solver(self):

        Modelo_SP = self.model()
        self.opt = pyo.SolverFactory('glpk', executable=r"/home/notebook01/anaconda3/envs/io/bin/glpsol")
        results = self.opt.solve(Modelo_SP)
        results.write()

        print('Valor Función Objetivo: ' + str(value(Modelo_SP.FunObj)))

        return Modelo_SP

    def Print_Results(self,Modelo_SP):

        # ### Creating Excel Output ## ---------------------------------->
        Table_Visitas = pd.DataFrame()
        Table_No_Visitas = pd.DataFrame()
        Table_No_Entregados = pd.DataFrame()

        r=0
        for i in Modelo_SP.C:
            for t in Modelo_SP.T:
                for j in Modelo_SP.B:
                    Table_Visitas.loc[r,'Camiones'] = i
                    Table_Visitas.loc[r,'Tiempo'] = t
                    Table_Visitas.loc[r,'Zona'] = j
                    Table_Visitas.loc[r,'Valor'] = round(Modelo_SP.x[i,j,t].value,6)
                    r += 1

        r=0
        for t in Modelo_SP.T:
            for j in Modelo_SP.B:
                Table_No_Visitas.loc[r,'Tiempo'] = t
                Table_No_Visitas.loc[r,'Zona'] = j
                Table_No_Visitas.loc[r,'Valor'] = round(Modelo_SP.y[j,t].value,6)
                r += 1

        r=0
        for t in Modelo_SP.T:
            for j in Modelo_SP.B:
                for l in Modelo_SP.C:
                    Table_No_Entregados.loc[r,'Tiempo'] = t
                    Table_No_Entregados.loc[r,'Zona'] = j
                    Table_No_Entregados.loc[r,'Producto'] = l
                    Table_No_Entregados.loc[r,'Valor'] = round(Modelo_SP.w[t,j,l].value,6)
                    r += 1

        with pd.ExcelWriter('Results.xlsx') as data:
            Table_Visitas.to_excel(data, sheet_name='Visitas')
            Table_No_Visitas.to_excel(data, sheet_name='No_Visitas')
            Table_No_Entregados.to_excel(data, sheet_name='No_Entregados')


if __name__ == "__main__":
    runing = Scheduling_Problem()
    runing.ReadExcelFile(r'/home/notebook01/Proyectos/Investigacion-Operaciones/Problema_05_05/Data_Input_SM.xlsx')
    modelo = runing.Solver()
    runing.Print_Results(modelo)