from .const import Constants


class Block:
    def __init__(self, const: Constants) -> None:
        self.const = const
        self.clear()

    def read(self):
        if self.index >= self.const.G_BLOCK_DEPTH:
            raise Exception(f"Bufferoverflow: tried to read at {self.index} of block with depth {self.const.G_BLOCK_DEPTH}")
        return self.data[self.index]

    def clear(self):
        self.full = False
        self.data = [0 for x in range(self.const.G_BLOCK_DEPTH)]
        self.index = 0


class BlockBuffer:
    def __init__(self, const: Constants) -> None:
        self.const = const
        self.buffer = [Block(self.const) for x in range(self.const.G_BLOCK_COUNT)]
        self.head = 0
        self.tail = 0
        self.wr_data_i = [0x00 for x in range(self.const.G_BLOCK_DEPTH)]
        self.wr_en_i = False

    def incr_head(self):
        self.head = (self.head + 1) % self.const.G_BLOCK_COUNT

    def incr_tail(self):
        self.tail = (self.tail + 1) % self.const.G_BLOCK_COUNT

    def get_fill_count(self):
        if self.tail > self.head:
            return self.const.G_BLOCK_COUNT - (self.tail - self.head)
        elif self.tail < self.head:
            return self.head - self.tail
        elif self.buffer[self.head].full:
            return self.const.G_BLOCK_COUNT
        else:
            return 0

    def is_full(self):
        return self.buffer[self.head].full and self.head == self.tail

    def is_empty(self):
        return not self.buffer[self.tail].full and self.head == self.tail

    def get_rd_valid(self):
        return self.buffer[self.tail].full

    def get_rd_data(self):
        return self.buffer[self.tail].read()

    def tick(self):
        if self.get_rd_data() == self.const.sequence_terminator:
            self.buffer[self.tail].clear()
            self.incr_tail()
        elif self.buffer[self.tail].full:
            self.buffer[self.tail].index += 1

        if self.wr_en_i and not self.buffer[self.head].full:
            self.buffer[self.head].data = self.wr_data_i
            self.buffer[self.head].full = True
            self.buffer[self.head].index = 0
            self.incr_head()
