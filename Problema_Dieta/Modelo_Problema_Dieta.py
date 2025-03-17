import numpy as np
import pandas as pd
from pyomo.environ import * 

class Problema_Dieta:
    def __init__(self, name=None):
        self.Data = []

    def ReadExcelFile(self, FileName):
        self.Data = pd.read_excel(FileName, sheet_name='Data')
        self.Nforrajes = len(self.Data)

    def Model (self):
        model = AbstractModel(name='Model')

        ## SETS ##
        model.A = Set(initialize=np.arange(1,self.Nforrajes+1))

        ## PARAMETERS ##
        def C_init(model,i):
            return self.Data['Costo'].loc[i-1]
        model.C = Param(model.A, rule=C_init)

        def P_init(model,i):
            return self.Data['Proteina'].loc[i-1]
        model.P = Param(model.A, rule=P_init)

        def F_init(model,i):
            return self.Data['Fibra'].loc[i-1]
        model.F = Param(model.A, rule=F_init)

        ## VARIABLES ##
        model.x = Var(model.A, within = NonNegativeReals, initialize = 0)

        ## OBJECTIVE FUNCTION ##
        def Fun_obj(model):
            return sum(model.C[i]*model.x[i] for i in model.A)
        model.FunObj = Objective(rule = Fun_obj, sense = minimize)

        # ## CONSTRAINTS ##
        def Restriccion_1 (model):
            return sum(model.x[i] for i in model.A) >= 800
        model.restriccion_1 = Constraint(rule=Restriccion_1)

        def Restriccion_2 (model):
            return sum(model.P[i]*model.x[i] for i in model.A) >= 0.3*sum(model.x[i] for i in model.A)
        model.restriccion_2 = Constraint(rule=Restriccion_2)

        def Restriccion_3 (model):
            return sum(model.F[i]*model.x[i] for i in model.A) <= 0.05*sum(model.x[i] for i in model.A)
        model.restriccion_3 = Constraint(rule=Restriccion_3)

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
    runing.ReadExcelFile('Data_Problema_Dieta.xlsx')
    modelo = runing.Solver()
    runing.Print_Results(modelo)
