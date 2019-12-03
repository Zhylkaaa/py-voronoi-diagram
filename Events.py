
def get_parent_idx(i):
    return (i+1) // 2 - 1


def get_left_idx(i):
    return 2*i + 1


def get_right_idx(i):
    return 2*i + 2


class Events:

    def __init__(self):
        self.heap = []
        self.length = 0

    def empty(self):
        return self.length == 0

    def insert(self, node):
        if self.empty():
            self.heap = [node]
            self.length = 1
        else:
            idx = self.length
            self.length += 1
            self.heap.append(node)

            parent = get_parent_idx(idx)

            while idx != 0 and self.heap[idx] < self.heap[parent]:
                self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
                idx = parent
                parent = get_parent_idx(idx)

    def heapify(self, idx):
        min_idx = idx

        while True:
            idx = min_idx

            left = get_left_idx(idx)
            right = get_right_idx(idx)

            if left < self.length and self.heap[left] < self.heap[min_idx]:
                min_idx = left
            if right < self.length and self.heap[right] < self.heap[min_idx]:
                min_idx = right

            if min_idx == idx:
                break

            self.heap[idx], self.heap[min_idx] = self.heap[min_idx], self.heap[idx]

    def pop(self):
        if self.empty():
            raise RuntimeError('Can\'t pop element from the empty heap')

        result = self.heap[0]

        self.heap[0], self.heap[self.length-1] = self.heap[self.length-1], self.heap[0]

        self.length -= 1

        self.heap.pop()

        self.heapify(0)

        return result
