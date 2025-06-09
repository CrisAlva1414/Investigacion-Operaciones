import numpy as np
import pandas as pd

def check_dataframe_shapes(modelo):
    print("=== SHAPES DE LOS DATAFRAMES ===")
    print("Buses:", modelo.Buses.shape)
    print("Lines:", modelo.Lines.shape)
    print("Adj_Matrix:", modelo.Adj_Matrix.shape)
    print("Profiles:", modelo.Profiles.shape)
    print("Circum:", modelo.Circum.shape)
    print("bus_ids:", modelo.bus_ids)
    print("PL:", modelo.PL.shape)
    print("QL:", modelo.QL.shape)
    print("Vmax:", modelo.Vmax.shape)
    print("Vmin:", modelo.Vmin.shape)
    print("PGmax (Profiles):", modelo.PGmax.shape)
    print("Prices:", modelo.Prices.shape)
    print("Selling_Prices:", modelo.Selling_Prices.shape)
    print("Adjacency matrix:", modelo.adj_matrix.shape)
    print("alpha:", modelo.alpha.shape)
    print("beta:", modelo.beta.shape)
    print("delta:", modelo.delta.shape)
    print("from_bus:", modelo.from_bus.shape)
    print("to_bus:", modelo.to_bus.shape)
    print("R:", modelo.R.shape)
    print("X:", modelo.X.shape)
    print("Smax:", modelo.Smax.shape)
    print("N_buses:", modelo.N_buses)
    print("N_lines:", modelo.N_lines)
    print("N_periods:", modelo.N_periods)
    print("N_circum:", modelo.N_circum)
    print("===============================")

def check_pyomo_sets(model):
    print("=== SETS DEL MODELO PYOMO ===")
    print("Buses:", list(model.B))
    print("Lines:", list(model.L))
    print("Periods:", list(model.T))
    print("Circum:", list(model.R))
    print("=============================")

def check_pyomo_params(model):
    print("=== PARAMS DEL MODELO PYOMO ===")
    for b in model.B:
        print(f"PL[{b}]={model.PL[b]}, Vmax[{b}]={model.Vmax[b]}, Vmin[{b}]={model.Vmin[b]}")
    for t in model.T:
        print(f"Price[{t}]={model.Price[t]}, Selling_Price[{t}]={model.Selling_Price[t]}")
    for l in model.L:
        print(f"Res[{l}]={model.Res[l]}, X[{l}]={model.X[l]}, Smax[{l}]={model.Smax[l]}")
    print("===============================")

def check_pyomo_vars(model):
    print("=== VARIABLES DEL MODELO PYOMO ===")
    print("pg keys:", list(model.pg.keys())[:5], "...")
    print("kb keys:", list(model.kb.keys())[:5], "...")
    print("ks keys:", list(model.ks.keys())[:5], "...")
    print("e keys:", list(model.e.keys())[:5], "...")
    print("v keys:", list(model.v.keys())[:5], "...")
    print("pf keys:", list(model.pf.keys())[:5], "...")
    print("qf keys:", list(model.qf.keys())[:5], "...")
    print("y keys:", list(model.y.keys())[:5], "...")
    print("dp keys:", list(model.dp.keys())[:5], "...")
    print("===============================")

def check_pyomo_constraints(model):
    print("=== CONSTRAINTS DEL MODELO PYOMO ===")
    print("BalanceActiva:", model.BalanceActiva)
    print("BalanceReactiva:", model.BalanceReactiva)
    print("Tension:", model.Tension)
    print("VminConstraint:", model.VminConstraint)
    print("VmaxConstraint:", model.VmaxConstraint)
    print("ThermalLimit:", model.ThermalLimit)
    print("DemandaNeta:", model.DemandaNeta)
    print("DPDescomposition:", model.DPDescomposition)
    print("Exclusividad1:", model.Exclusividad1)
    print("Exclusividad2:", model.Exclusividad2)
    print("Vslack:", model.Vslack)
    print("GenLimit:", model.GenLimit)
    print("BuyLimit:", model.BuyLimit)
    print("SellLimit:", model.SellLimit)
    print("Nodo1_pg_zero:", model.Nodo1_pg_zero)
    print("===============================")

def print_model_status(modelo):
    print("=== ESTADO DEL MODELO ===")
    if hasattr(modelo, 'model'):
        model = modelo.model
        check_pyomo_sets(model)
        check_pyomo_params(model)
        check_pyomo_vars(model)
        check_pyomo_constraints(model)
    else:
        print("Modelo aún no construido.")
    print("=========================")

def print_results(modelo):
    print("=== RESULTADOS DEL MODELO ===")
    if hasattr(modelo, 'results'):
        print("Solver status:", modelo.results.solver.status)
        print("Termination condition:", modelo.results.solver.termination_condition)
        if modelo.results.solver.termination_condition.name == "optimal":
            print("Objective Value:", value(modelo.model.OBJ))
            for k in modelo.model.kb:
                print(f'kb[{k}] = {value(modelo.model.kb[k])}')
        else:
            print("No se encontró solución óptima.")
    else:
        print("No hay resultados para mostrar.")
    print("=============================")

def check_for_nans(modelo):
    print("=== CHEQUEO DE NaNs ===")
    for name, arr in [
        ("PL", modelo.PL), ("QL", modelo.QL), ("Vmax", modelo.Vmax), ("Vmin", modelo.Vmin),
        ("PGmax", modelo.PGmax), ("Prices", modelo.Prices), ("Selling_Prices", modelo.Selling_Prices),
        ("alpha", modelo.alpha), ("beta", modelo.beta), ("delta", modelo.delta)
    ]:
        if np.any(pd.isnull(arr)):
            print(f"¡ATENCIÓN! Hay NaNs en {name}")
    print("=======================")

def debug_all(modelo):
    check_dataframe_shapes(modelo)
    check_for_nans(modelo)
    if hasattr(modelo, 'model'):
        print_model_status(modelo)
    else:
        print("Modelo aún no construido.")
