class Swap:
    def __init__(self, id1, id2, owner1, owner2):
        self.id1 = id1
        self.id2 = id2
        self.owner1 = owner1
        self.owner2 = owner2


class Traker:
    def __init__(self, patience = 5):
        self.swaps = []
        self.errors = []
        self.patience = patience
        self.current_patience = 0
        self.detect = []
    
    def add_swap(self, swap):
        self.swaps.append(swap)

    def get_swaps(self):
        return self.swaps
    
    def add_error(self, error):       
        self.errors.append(error)

    def _(self):
        if self.errors[-2] == self.errors[-1]:
            self.current_patience += 1
        else:
            self.current_patience = 0

        # if self.current_patience > self.patience: