import modules.variables as var


def getPhases(int_mask, all_phases=None):
    if all_phases == None:
        all_phases = var.all_phases
    return [all_phases[i] for i in range(len(all_phases)) if (int(int_mask) & (1 << i)) > 0]


def phasesToMask(phases, all_phases=None):
    if all_phases == None:
        all_phases = var.all_phases
    phases.sort()
    mask = [1 if phase in phases else 0 for phase in all_phases][::-1]
    return int(''.join(map(str, mask)), 2)


def phaseToMask(phase, all_phases=None):
    if all_phases == None:
        all_phases = var.all_phases
    mask = [1 if phase == phase_ else 0 for phase_ in all_phases][::-1]
    return int(''.join(map(str, mask)), 2)


def compToMask(components, all_components=None):
    if all_components == None:
        all_components = var.all_components
    components.sort()
    mask = [1 if comp in components else 0 for comp in all_components][::-1]
    return int(''.join(map(str, mask)), 2)


def getComponents(int_mask, all_components=None):
    if all_components == None:
        all_components = var.all_components
    return [all_components[i] for i in range(len(all_components)) if (int_mask & (1 << i)) > 0]
