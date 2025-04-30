import numpy as np
import pandas as pd
from pyomo.environ import * 

class Problema_Dieta:
    def __init__(self, name=None):
        self.Data = []

    def ReadExcelFile(self, FileName):
        self.Data = pd.read_excel(FileName, sheet_name='Problema_Banco/Datos.csv')
        self.Nprestamo = len(self.Data)

    def Model (self):
        model = AbstractModel(name='Model')

        ## SETS ##
        model.A = Set(initialize=np.arange(1,self.Nprestamo+1))

        ## PARAMETERS ##
        def T_init(model,i):
            return self.Data['Tasa de interes'].loc[i-1]
        model.T = Param(model.A, rule=T_init)

        def P_init(model,i):
            return self.Data['Per de Deuda'].loc[i-1]
        model.P = Param(model.A, rule=P_init)

        ## VARIABLES ##
        model.x = Var(model.A, within = NonNegativeReals, initialize = 0)

        ## OBJECTIVE FUNCTION ##
        def Fun_obj(model):
            return sum(model.T[i]*(1 - model.P[i])*model.x[i] - model.P[i]*model.x[i] for i in model.A)
        model.FunObj = Objective(rule = Fun_obj, sense = maximize)

        # ## CONSTRAINTS ##
        def Restriccion_1 (model):
            return sum(model.x[i] for i in model.A) <= 12
        model.restriccion_1 = Constraint(rule=Restriccion_1)

        def Restriccion_2 (model):
            return sum((model.x[4]+model.x[5] in model.A)) >= 0.4*sum(model.x[i] for i in model.A)
        model.restriccion_2 = Constraint(rule=Restriccion_2)

        def Restriccion_3 (model):
            return sum(model.x[3] in model.A) >= 0.5*sum(model.x[1] + model.x[2] + model.x[3] in model.A)
        model.restriccion_3 = Constraint(rule=Restriccion_3)

        def Restriccion_4 (model):
            return sum(model.P[i]*model.x[i] in model.A) <= 0.04*sum(model.x[i] in model.A)
        model.restriccion_4 = Constraint(rule=Restriccion_4)

        return model.create_instance()
    
    def Solver(self):

        Modelo_dieta = self.Model()
        #self.opt = SolverFactory('glpk', executable=r'/home/pc01/anaconda3/envs/io/bin/glpsol)
        self.opt = SolverFactory('glpk', executable=r'/home/pc01/anaconda3/envs/io/bin/glpsol')
        #self.opt = SolverFactory("glpk")
        results = self.opt.solve(Modelo_dieta)
        results.write()

        print('Valor Función Objetivo: ' + str(value(Modelo_dieta.FunObj)))

        return Modelo_dieta

    def Print_Results(self,Modelo_dieta):

        Table = pd.DataFrame()

        r=0
        for i in Modelo_dieta.A:
            Table.loc[r,'Tipo Forraje'] = str(i)
            Table.loc[r,'Libras'] = round(Modelo_dieta.x[i].value,4)
            r += 1

        with pd.ExcelWriter('Resultados.xlsx') as data: 
            Table.to_excel(data, sheet_name="Resultados")

if __name__ == "__main__":
    runing = Problema_Dieta()
    runing.ReadExcelFile('Datos.csv')
    modelo = runing.Solver()
    runing.Print_Results(modelo)
