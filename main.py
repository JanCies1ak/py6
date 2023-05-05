class Element:
    data = None
    nextE = None

    def __init__(self, data=None, nextE=None):
        self.data = data
        self.nextE = nextE

    def __str__(self):
        return str(self.data)

    def __eq__(self, other):
        if other is None:
            return False
        return self.data == other.data

    def __ne__(self, other):
        if other is None:
            return False
        return not self == other

    def __ge__(self, other):
        if other is None or other.data is None:
            return False

        return self.data >= other.data


class MyLinkedList:
    head = None
    tail = None
    size = 0

    def __init__(self):
        self.tail = Element()
        self.head = Element(nextE=self.tail)

    def __str__(self):
        elem = self.head
        answer = "["
        while elem.nextE != self.tail:
            elem = elem.nextE
            answer += f"{elem}, "
        if answer.__len__() > 2:
            answer = answer[0:answer.__len__() - 2]
        answer += "]"
        return answer

    def __len__(self):
        return self.size

    def get(self, e):
        a = 0
        elem = self.head
        while elem.nextE != self.tail:
            if a == e:
                return elem.data
            a += 1
        raise Exception(f"No element with index = {e}")

    def delete(self, e):
        a = 0
        elem = self.head
        while elem.nextE != self.tail:
            if a == e:
                elem.nextE = elem.nextE.nextE
                self.size -= 1
                return
            a += 1
        raise Exception(f"No element with index = {e}")

    def append(self, e, func=None):
        if func is None:
            func = Element.__ge__

        to_append = Element(e)
        elem = self.head

        while elem.nextE != self.tail:
            if func(elem.nextE, to_append):
                break
            elem = elem.nextE
        to_append.nextE = elem.nextE
        elem.nextE = to_append
        self.size += 1


lst = MyLinkedList()
print(lst)
lst.append(1)
print(lst)
lst.append(3)
print(lst)
lst.append(2)
print(lst)

# Własne funkcje porównywania
lst.append(4, lambda a, b: b >= a)
print(lst)
lst.append("abcd", lambda a, b: len(b.data) != a.data)
print(lst)

# Nie zadziała, bo poprzednio było dodane "abcd", więc jest potrzebna funkcja porównywania
# lst.append(6)

lst.append(6, lambda a, b: str(a) >= str(b))

print(lst)
