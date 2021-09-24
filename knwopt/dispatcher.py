import pulp

def dispatcher(expected_power:float, portfolio:dict)->dict:
    
    fixed_power = 0.
    drop = []
    for p in portfolio:
        if not portfolio[p]["available"]:
            fixed_power += portfolio[p]["power"]
            drop.append(p)
    for d in drop:
        portfolio.pop(d)
    deviation_power = expected_power - fixed_power
    x = pulp.LpVariable.dict("potentials", list(portfolio.keys()), cat= pulp.LpBinary)
    up = pulp.LpVariable("positive_deviation", lowBound=0, upBound=abs(deviation_power)*1.01,  cat= pulp.LpContinuous) # we just look for solutions that are not worse than the current state
    down = pulp.LpVariable("negative_deviation", lowBound=0, upBound=abs(deviation_power)*1.01,  cat= pulp.LpContinuous) # we just look for solutions that are not worse than the current state
    problem = pulp.LpProblem("Energy_Deviation_Dispatching", pulp.LpMinimize)
    problem += (pulp.lpSum([portfolio[p]["max_power"] * x[p] for p in portfolio]) + up - down == deviation_power,"deviation of portfolio from expected power")
    problem += (up + down, "l1 deviation")
    problem.solve(pulp.PULP_CBC_CMD(msg=0, threads=6))
    call = {}
    if problem.sol_status == pulp.LpSolutionOptimal or problem.sol_status == pulp.LpSolutionIntegerFeasible:
        for p in portfolio:
            call[p] = portfolio[p]["max_power"] * x[p].value()
    return call
