import numpy as np
import pandas as pd
from pyomo.environ import * 

class Problema_Inventario:
    def __init__(self, name=None):
        self.Data = []

    def ReadExcelFile(self, FileName):
        self.Data = pd.read_excel(FileName, sheet_name='Data')
        self.NMeses = len(self.Data)

    def Model (self):
        model = AbstractModel(name='Model')

        ## SETS ##
        model.T = Set(initialize=np.arange(1,self.NMeses+1))

        ## PARAMETERS ##
        def D_init(model,i):
            return self.Data['Demanda'].loc[i-1]
        model.D = Param(model.T, rule=D_init)

        ## VARIABLES ##
        model.x = Var(model.T, within = NonNegativeReals, initialize = 0)


        ## OBJECTIVE FUNCTION ##
        def Fun_obj(model):
            return sum(model.C[i]*model.x[i] for i in model.A) 
        model.FunObj = Objective(rule = Fun_obj, sense = minimize)

        # ## CONSTRAINTS ##


        def Restriccion_3 (model):
            return model.y[6] == 0
        model.restriccion_3 = Constraint(rule=Restriccion_3)

        return model.create_instance()
    
    def Solver(self):

        Modelo_Inventario = self.Model()
        Modelo_Inventario.pprint()
        self.opt = SolverFactory("glpk")
        results = self.opt.solve(Modelo_Inventario)
        results.write()

        print('Valor Función Objetivo: ' + str(value(Modelo_Inventario.FunObj)))

        return Modelo_Inventario

    def Print_Results(self,Modelo_Inventario):

        Table = pd.DataFrame()

        r=0
        for i in Modelo_Inventario.A:
            Table.loc[r,'Mes'] = str(i)
            Table.loc[r,'Prod Fabricados'] = round(Modelo_Inventario.x[i].value,4)
            Table.loc[r,'Prod Almacenados'] = round(Modelo_Inventario.y[i].value,4)
            r += 1

        with pd.ExcelWriter('Resultados.xlsx') as data: 
            Table.to_excel(data, sheet_name="Resultados")

if __name__ == "__main__":
    runing = Problema_Inventario()
    runing.ReadExcelFile('Data_Inventario.xlsx')
    modelo = runing.Solver()
    runing.Print_Results(modelo)
