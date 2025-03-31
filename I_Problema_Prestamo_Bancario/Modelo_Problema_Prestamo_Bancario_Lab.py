import numpy as np
import pandas as pd
from pyomo.environ import * 

class Problema_Prestamo:
    def __init__(self, name=None):
        self.Data = []

    def ReadExcelFile(self, FileName):
        self.Data = pd.read_excel(FileName, sheet_name='Data')
        self.Nprestamos = 

    def Model (self):
        model = AbstractModel(name='Model')

        ## SETS ##
        model.A = Set(initialize=np.arange(1,self.Nprestamos+1))

        ## PARAMETERS ##
        def T_init(model,i):
            return self.Data['Tasa'].loc[i-1]
        model.T = Param(model.A, rule=T_init)




        ## VARIABLES ##
        model.x = Var()

        ## OBJECTIVE FUNCTION ##
        def Fun_obj(model):
            return sum(model.T[i]*(1-model.D[i])*model.x[i] )
        model.FunObj = Objective(rule = Fun_obj, sense = maximize)

        # ## CONSTRAINTS ##
        def Restriccion_1 (model):
            return sum(model.x[i] for i in model.A) <= 12
        model.restriccion_1 = Constraint(rule=Restriccion_1)


        return model.create_instance()
    
    def Solver(self):

        Modelo_Prestamo = self.Model()
        Modelo_Prestamo.pprint()
        self.opt = SolverFactory("glpk")
        results = self.opt.solve(Modelo_Prestamo)
        results.write()

        print('Valor Función Objetivo: ' + str(value(Modelo_Prestamo.FunObj)))

        return Modelo_Prestamo

    def Print_Results(self,Modelo_Prestamo):

        Table = pd.DataFrame()

        r=0
        for i in Modelo_Prestamo.A:
            Table.loc[r,'Tipo Préstamo'] = str(i)
            Table.loc[r,'Valor del préstamo'] = round(Modelo_Prestamo.x[i].value,4)
            r += 1

        with pd.ExcelWriter('Resultados.xlsx') as data: 
            Table.to_excel(data, sheet_name="Resultados")

if __name__ == "__main__":
    runing = Problema_Prestamo()
    runing.ReadExcelFile('Data_Prestamo_Bancario.xlsx')
    modelo = runing.Solver()
    runing.Print_Results(modelo)
