import numpy as np
import pandas as pd
from pyomo.environ import * 

class Problema_Produccion:
    def __init__(self, name=None):
        self.Data = []

    def ReadExcelFile(self, FileName):
        self.Data = pd.read_excel(FileName, sheet_name='Data')
        self.Nproductos = len(self.Data)
        self.Dptos = ['Corte','Aislamiento','Costura','Empaque']
        self.NDptos = len(self.Dptos)

    def Model (self):
        model = AbstractModel(name='Model')

        ## SETS ##
        model.A = Set(initialize=np.arange(1,self.Nproductos+1))

        ## PARAMETERS ##
        def C_init(model,i,j):
            return self.Data[self.Dptos[j-1]].loc[i-1]
        model.C = Param(model.A,model.B, rule=C_init)


        ## VARIABLES ##
        model.x = Var(model.A, within = NonNegativeReals, initialize = 0)
        model.y = Var(model.A, within = NonNegativeReals, initialize = 0)

        ## OBJECTIVE FUNCTION ##
        def Fun_obj(model):
            return sum(model.U[i]*model.x[i] ) 
        model.FunObj = Objective(rule = Fun_obj, sense = maximize)



        return model.create_instance()
    
    def Solver(self):

        Modelo_Prod = self.Model()
        Modelo_Prod.pprint()
        self.opt = SolverFactory("glpk")
        results = self.opt.solve(Modelo_Prod)
        results.write()

        print('Valor Función Objetivo: ' + str(value(Modelo_Prod.FunObj)))

        return Modelo_Prod

    def Print_Results(self,Modelo_Prod):

        Table = pd.DataFrame()

        r=0
        for i in Modelo_Prod.A:
            Table.loc[r,'Tipo Producto'] = str(i)
            Table.loc[r,'Prod Fabricados'] = round(Modelo_Prod.x[i].value,4)
            Table.loc[r,'Prod NO Fabricados'] = round(Modelo_Prod.y[i].value,4)
            r += 1

        with pd.ExcelWriter('Resultados.xlsx') as data: 
            Table.to_excel(data, sheet_name="Resultados")

if __name__ == "__main__":
    runing = Problema_Produccion()
    runing.ReadExcelFile('Data_Produccion.xlsx')
    modelo = runing.Solver()
    runing.Print_Results(modelo)
