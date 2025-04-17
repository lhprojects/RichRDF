def show_metadata(file, branch_name="metadata"):
    tree = file.Get("metadata")
    entry = tree.GetEntry(0) # cursor to the first entry
    branches = tree.GetListOfBranches()

    for branch in branches:
        name = branch.GetName()
        print(name)
        value = getattr(tree, name)
        print(f"{name}: {value}")

        if name == "metadata___idTable":
            print(value.metadata___idTable.m_collectionIDs)


def show_branches(file, tree_name="events"):
    tree = file.Get(tree_name)

    branches = tree.GetListOfBranches()

    for branch in branches:
        name = branch.GetName()
        print(name)
