class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    # see
    # https://www.digitalocean.com/community/tutorials/python-str-repr-functions
    def __repr__(self):
        return f"DBList({self.value!r})"

    # see
    # https://www.digitalocean.com/community/tutorials/python-str-repr-functions
    def __str__(self):
        return f"DBList: {self.value}"

    def append(self, data):
        self.value = self.value + [data]
        return self
