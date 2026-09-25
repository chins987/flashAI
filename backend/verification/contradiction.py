
def check(evidence):
    # Evidence items may explicitly belong to opposing positions.
    conflicts=[]
    for e in evidence:
        if "conflict_group" in e:
            conflicts.append(e["conflict_group"])
    return bool(len(conflicts)!=len(set(conflicts)))
