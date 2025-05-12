import numpy as np
import pandas as pd
from pyomo.environ import * 

class Problema_Parking_Electrico:
    def __init__(self, name=None):
        self.Data = []

    def ReadExcelFile(self, FileName):
        self.Data = pd.read_excel(FileName, sheet_name='Parameters')
        self.Time = 24
        self.Nodos = 3
        self.Cap_Bat_VE = 50
        self.PCR = 35
        self.PCL = 15
        self.Cap_Panel = 200
        self.Cap_Bat = 200
        self.PCB = 50
        self.SOC_Max = 0.9
        self.SOC_Min = 0.1
        self.Fi = 0.95

    def Model (self):
        model = AbstractModel(name='Model')

        ## SETS ##
        model.T = Set(initialize=np.arange(1,self.Time+1))
        model.N = Set(initialize=np.arange(1,self.Nodos+1))

        ## PARAMETERS ##
        def SOC_Min_Init(model,i,t):
            return 
        model.SOC_Min = Param(model.N,model.T, rule=SOC_Min_Init)

        def Irr_init(model,t):
            return self.Data['Irradiancia'].loc[t-1]
        model.Irr = Param(model.T, rule=Irr_init)

        def PC_Init(model,i,t):
            return self.Data['PC_'+str(i)].loc[t-1]
        model.PC = Param(model.N,model.T, rule=PC_Init)

        def P_Compra_init(model,t):
            return 
        model.Lambda_Compra = Param(model.T, rule=P_Compra_init)

        def P_Venta_init(model,t):
            return self.Data['P_Venta'].loc[t-1]
        model.Lambda_Venta = Param(model.T, rule=P_Venta_init)

        def SOC_Inicial_init(model,i):
            return self.Data['SOCinit_'+str(i)].loc[0]
        model.SOC_Inicial = Param(model.N, rule=SOC_Inicial_init)

        ## VARIABLES ##
        model.pl = Var(model.N, model.T, within = NonNegativeReals, initialize = 0)

        model.ch_ve = Var(model.N, model.T, within = NonNegativeReals, initialize = 0)
        model.soc_ve = Var(model.N, model.T, within = NonNegativeReals, initialize = 0)

        model.ch_bt = Var(model.T, within = NonNegativeReals, initialize = 0)
        model.ds_bt = Var(model.T, within = NonNegativeReals, initialize = 0)

        model.pv = Var(model.T, within = NonNegativeReals, initialize = 0)
        model.cm = Var(model.T, within = NonNegativeReals, initialize = 0) # Compra
        model.vt = Var(model.T, within = NonNegativeReals, initialize = 0) # Venta

        ## OBJECTIVE FUNCTION ##
        def Fun_obj(model):
            return sum(model.cm[t]*model.Lambda_Compra[t] ) 
        model.FunObj = Objective(rule = Fun_obj, sense = minimize)

        # ## CONSTRAINTS ##
        def Balance (model,t):
            return model.pv[t] -  == 0
        model.balance_R_1 = Constraint(model.T, rule=Balance)

        def Panel_Solar (model,t):
            return model.pv[t] <= self.Cap_Panel*model.Irr[t]
        model.panel_R_2 = Constraint(model.T, rule=Panel_Solar)

        def SOC_VE (model,i,t):
            if t == 1:
                return model.soc_ve[i,t] == model.SOC_Inicial[i]*model.PC[i,t]*self.Cap_Bat_VE + model.ch_ve[i,t]*self.Fi
            else:
                return model.soc_ve[i,t] ==  
        model.soc_ve_R_3 = Constraint(model.N,model.T, rule=SOC_VE)

        def SOC_VE_2 (model,i,t):
            return inequality(self.Cap_Bat_VE*model.SOC_Min[i,t]*model.PC[i,t] ,model.soc_ve[i,t],self.Cap_Bat_VE*self.SOC_Max) 
        model.soc_ve_R_4= Constraint(model.N,model.T, rule=SOC_VE_2)

        def CH_VE (model,i,t):
            return model.ch_ve[i,t] <= model.PC[i,t]*self.PCR
        model.ch_ve_R_5 = Constraint(model.N,model.T, rule=CH_VE)

        def SOC_BT (model,t):
            if t == 1:
                return model.soc_bt[t] <= 
            else:
                return model.soc_bt[t] <= model.soc_bt[t-1] + self.Fi*model.ch_bt[t] - model.ds_bt[t]/self.Fi
        model.soc_bt_R_6 = Constraint(model.T, rule=SOC_BT)

        def SOC_BT_2 (model,t):
            return inequality(self.Cap_Bat*self.SOC_Min ,model.soc_bt[t],self.Cap_Bat*self.SOC_Max) 
        model.soc_bt_R_7= Constraint(model.T, rule=SOC_BT_2)


        return model.create_instance()
    
    def Solver(self):

        Modelo_PE = self.Model()
        #Modelo_PE.pprint()
        self.opt = SolverFactory("glpk")
        results = self.opt.solve(Modelo_PE)
        results.write()

        print('Valor Función Objetivo: ' + str(value(Modelo_PE.FunObj)))

        return Modelo_PE

    def Print_Results(self,Modelo_PE):

        Table_PL = pd.DataFrame()
        Table_CH_VE = pd.DataFrame()
        Table_SOC_VE = pd.DataFrame()
        Table_Resumen = pd.DataFrame()
 
        for t in Modelo_PE.T:
            Table_Resumen.loc[t-1,'CH_BT'] = round(Modelo_PE.ch_bt[t].value,4)
            Table_Resumen.loc[t-1,'DS_BT'] = round(Modelo_PE.ds_bt[t].value,4)
            Table_Resumen.loc[t-1,'SOC_BT'] = round(Modelo_PE.soc_bt[t].value,4)
            Table_Resumen.loc[t-1,'W_BT'] = round(Modelo_PE.w_bt[t].value,4)
            Table_Resumen.loc[t-1,'PV'] = round(Modelo_PE.pv[t].value,4)
            Table_Resumen.loc[t-1,'CM'] = round(Modelo_PE.cm[t].value,4)
            Table_Resumen.loc[t-1,'VT'] = round(Modelo_PE.vt[t].value,4)

        r=0
        for n in Modelo_PE.N:
            for t in Modelo_PE.T:
                Table_CH_VE.loc[r,'Nodo'] = str(n)
                Table_CH_VE.loc[r,str(t)] = round(Modelo_PE.ch_ve[n,t].value,4)
                Table_SOC_VE.loc[r,'Nodo'] = str(n)
                Table_SOC_VE.loc[r,str(t)] = round(Modelo_PE.soc_ve[n,t].value,4)
            r +=1


        with pd.ExcelWriter('Resultados.xlsx') as data: 
            Table_Resumen.to_excel(data, sheet_name="Resumen")
            Table_CH_VE.to_excel(data, sheet_name="Ch_VE")
            Table_SOC_VE.to_excel(data, sheet_name="Soc_VE")

if __name__ == "__main__":
    runing = Problema_Parking_Electrico()
    runing.ReadExcelFile('Data_Input.xlsx')
    modelo = runing.Solver()
    runing.Print_Results(modelo)
