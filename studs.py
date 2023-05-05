import smtplib
from email.mime.text import MIMEText
from re import match


class Student:
    mail = None
    first_name = None
    last_name = None
    project = None
    lists = None
    home_works = None
    final = None
    status = None

    def __init__(self, mail: str,
                 first_name: str,
                 last_name: str,
                 project: int,
                 lists: list[int],
                 home_works: list[int],
                 final: int,
                 status: str):

        if len(lists) != 3 or len(home_works) != 10:
            raise Exception("Niepoprawna liczba ocen.")

        if project < -1 or project > 40:
            raise Exception("Niepoprawna ocena z projektu.")
        for grade in lists:
            if grade < -1 or grade > 20:
                raise Exception("Niepoprawna ocena z listy z zadaniami")

        for grade in home_works:
            if grade < -1 or grade > 100:
                raise Exception("Niepoprawna ocena z pracy domowej")

        self.mail = mail
        self.first_name = first_name
        self.last_name = last_name
        self.project = project
        self.lists = lists
        self.home_works = home_works
        self.final = final
        self.status = status

    @staticmethod
    def from_str(line: str):
        split = line.split(",")
        if len(split) < 19:
            print(line)
            raise Exception("Niepoprawny format studenta")
        mail = split[0]
        first_name = split[1]
        last_name = split[2]
        project = int(split[3])

        lists_str = split[4:7]
        lists = []
        for i in range(0, 3):
            lists.append(int(lists_str[i]))

        home_works_str = split[7:17]
        home_works = []
        for i in range(0, 10):
            home_works.append(int(home_works_str[i]))

        final = int(split[17])
        status = split[18]

        return Student(mail, first_name, last_name, project, lists, home_works, final, status)

    def calculate_final(self):
        """
        Wylicza ocenę końcową studenta.
        Punkty to suma oceny za projekt i ocen za listy z zadaniami.

        Gdy średnia ocen za prace domowe jest większa od progów (60, 70, 80), to
        zamiast ocen za listy suma jest wyliczana zgodnie z założeniami zadania.
        Przy tym nie jest zmieniana oryginalna ocena za listę!
        """
        if self.final != -1:
            return
        if self.project == -1:
            return
        if -1 in self.lists:
            return
        if -1 in self.home_works:
            return

        average = 0
        for grade in self.home_works:
            average += grade
        average /= 10

        sorted_lists = sorted(self.lists)

        if average >= 60:
            sorted_lists[0] = 20
        if average >= 70:
            sorted_lists[1] = 20
        if average >= 80:
            sorted_lists[2] = 20

        points = self.project + sum(sorted_lists)
        if points < 51:
            self.final = 2
        else:
            self.final = (points / 20).__ceil__()

        self.status = "GRADED"

    def show(self):
        data = [self.first_name, self.last_name, self.project]
        for grade in self.lists:
            data.append(grade)
        for grade in self.home_works:
            data.append(grade)
        data.append(self.final)
        data.append(self.status)
        print(f"{self.mail}: {data}")

    def __le__(self, other):
        """
        Użyte, żeby można było dodać studenta do MySortedList
        """
        return self.mail <= other.mail

    def __eq__(self, other):
        if other is None:
            return False
        if self.mail is None:
            return other.mail is None
        return self.mail == other.mail

    def __ne__(self, other):
        return self.mail != other.mail

    def __ge__(self, other):
        """
        Użyte, żeby można było dodać studenta do MySortedList
        """
        return self.mail >= other.mail

    def __str__(self):
        line = f"{self.mail},{self.first_name},{self.last_name},{self.project},"

        for grade in self.lists:
            line += str(grade) + ","

        for grade in self.home_works:
            line += str(grade) + ","

        line += f"{self.final},{self.status}"

        return line


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


class MySortedListIterator:
    """
    Użyta, żeby stosować operator in.
    """
    current = None

    def __init__(self, head):
        self.current = head

    def __iter__(self):
        return self

    def __next__(self):
        if self.current.nextE is None:
            raise StopIteration
        else:
            item = self.current.data
            self.current = self.current.nextE
            return item


class MySortedList:
    head = None
    tail = None
    size = 0

    def __init__(self):
        self.tail = Element()
        self.head = Element(nextE=self.tail)

    def __str__(self):
        elem = self.head
        answer = "[ "
        while elem.nextE != self.tail:
            elem = elem.nextE
            answer += f"{elem}, "
        if answer.__len__() > 2:
            answer = answer[0:answer.__len__() - 2]
        answer += " ]"
        return answer

    def __len__(self):
        return self.size

    def __iter__(self):
        return MySortedListIterator(self.head.nextE)

    def __contains__(self, mail):
        for elem in self:
            if elem.mail == mail:
                return True
        return False

    def get(self, e: int):
        a = 0
        elem = self.head
        while elem.nextE != self.tail:
            if a == e:
                return elem.data
            a += 1
        raise Exception(f"No element with index = {e}")

    def find(self, e: str):
        elem = self.head
        while elem.nextE != self.tail:
            if elem.data.mail == e:
                return elem.data
        raise Exception(f"No element with mail = {e}")

    def delete(self, e: int):
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

    def pop(self, mail: str):
        elem = self.head
        while elem.nextE != self.tail:
            if elem.nextE.data.mail == mail:
                elem.nextE = elem.nextE.nextE
                return
            elem = elem.nextE


file_path = input("Prosze wpisać ścieżkę do pliku ze studentami\n")


def read_students():
    _students = MySortedList()
    with open(file_path) as file:
        for line in file:
            _students.append(Student.from_str(line.removesuffix("\n")))
    return _students


students = read_students()


print("Prosze wpisać swój mail:")
email = input("Mail: ")
print("Prosze wpisać swoje hasło do aplikacji:")
password = input("Password: ")


def show_students():
    for student in students:
        student.show()


def save():
    with open(file_path, "w") as file:
        for student in students:
            file.write(str(student) + "\n")
    file.close()


def send_email(subject: str,
               body: str,
               recipient: Student):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = ', '.join(recipient.mail)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(email, password)
    smtp_server.sendmail(email, recipient.mail, msg.as_string())
    smtp_server.quit()
    save()


def send_email_to(recipient: Student):
    if recipient not in students:
        return
    subject = "Ocena końcowa"
    body = "Twoja końcowa ocena jest " + str(recipient.final)
    send_email(subject, body, recipient)
    recipient.status = input(f"Prosze podać nowy status dla studenta "
                             f"[{recipient.mail}, {recipient.first_name}, {recipient.last_name}]")


def calc_grads():
    for student in students:
        student.calculate_final()
    save()


possible_grades = ["project", "final"]
for i in range(1, 4):
    possible_grades.append(f"l_{i}")
for i in range(1, 11):
    possible_grades.append(f"h_{i}")
project_grades = []
for i in range(-1, 41):
    project_grades.append(str(i))
list_grades = []
for i in range(-1, 21):
    list_grades.append(str(i))
home_work_grades = []
for i in range(-1, 101):
    home_work_grades.append(str(i))
final_grades = ['2', '3', '3.5', '4', '4.5', '5', '-1']


def change_grad():
    mail = input("Prosze wpisać mail studenta, któremu trzeba zmienić ocenę:\n")
    if mail not in students:
        print(f"Student z mailem \"{mail}\" nie istnieje")
        return
    student = students.find(mail)
    grade_type = input('Prosze wpisać ocenę, którą trzeba zmienić.\n'
                       'Możliwe oceny to: "project", "l_{1-3}", "h_{1-10)" oraz "grade".\n')
    while grade_type not in project_grades:
        grade_type = input("Niepoprawna ocena.\n")
    if grade_type == "project":
        new_grade = input("Prosze wpisać nową ocenę za projekt. Ocena musi być od 0 do 40, \n"
                          "lub -1, dla wpisania oceny pustej.\n")
        while new_grade not in project_grades:
            new_grade = input("Niepoprawna ocena za projekt.\n")

        student.project = int(new_grade)
    elif grade_type == "final":
        if student.project == -1 or -1 in student.home_works or -1 in student.lists:
            print("Nie wolno przypisać oceny końcowej, gdy nie są wystawione pozostałe oceny")
            return
        new_grade = input("Prosze wpisać nową ocenę końcową. Możliwe oceny końcowe to:\n"
                          "2, 3, 3.5, 4, 4.5, 5, lub -1, dla wpisania oceny pustej.\n")
        while new_grade not in final_grades:
            new_grade = input("Niepoprawna ocena końcowa.\n")

        student.final = int(new_grade)
    elif grade_type[0] == 'l':
        list_num = int(grade_type.split('_')[1])
        new_grade = input(f"Prosze wpisać nową ocenę za listę {list_num}. Ocena musi być od 0 do 20, \n"
                          "lub -1, dla wpisania oceny pustej.\n")
        while new_grade not in list_grades:
            new_grade = input("Niepoprawna ocena za listę.\n")

        student.lists[list_num-1] = int(new_grade)
    else:
        hw_num = int(grade_type.split('_')[1])
        new_grade = input(f"Prosze wpisać nową ocenę za pracę domową {hw_num}. Ocena musi być od 0 do 100, \n"
                          "lub -1, dla wpisania oceny pustej.\n")
        while new_grade not in home_work_grades:
            new_grade = input("Niepoprawna ocena za pracę domową.\n")

        student.home_works[hw_num - 1] = int(new_grade)


def can_send_mail_to(student: Student) -> bool:
    """
    Sprawdza, czy do podanego studenta można wysyłać maile.
    Nie do końca zrozumiałem, co oznacza, że status pozwala wysłać mail, więc
    założyłem, że status, który nie pozwala wysłać mail, zawiera "MAILED".
    :param student: student, dla którego trzeba sprawdzić możliwość wysłania maila
    :return: False, gdy status studenta zawiera "MAILED"
    """
    return not bool(match(".*MAILED.*", student.status))


def send_mails():
    for student in students:
        if student.final != -1:
            if can_send_mail_to(student):
                send_email_to(student)


def delete_student():
    mail = input("Prosze wpisać mail studenta, którego trzeba usunąć:\n")
    if mail not in students:
        print(f"Student z mailem \"{mail}\" nie istnieje")
        return
    students.pop(mail)
    save()
    print(f"Student z mailem \"{mail}\" został usunięty")


def add_student():
    mail = input("Prosze wpisać mail studenta, którego trzeba dodać:\n")
    if mail in students:
        print(f"Student z mailem \"{mail}\" już istnieje")
        return
    data = input("Prosze podać dane studenta w formacie:\n"
                 "\"<imie>,<nazwisko>,<oceny>,<status>\"\n"
                 "gdzie oceny to ocena za projekt (max 40), 3 oceny za listy (max 20), "
                 "10 ocen za prace domowe (max 100) i ocena końcowa.\n"
                 "Gdy jakaś ocena nie jest jeszcze wystawiona należy wpisać -1.\n")
    if not match("^[A-Za-z]+,[A-Za-z]+,(-?\\d{1,3},){14}(-?\\d(\\.\\d)?),[A-Za-z_]+$", data):
        print("Niepoprawne dane")
        return
    student = Student.from_str(mail + "," + data)
    try:
        students.append(student)
    except Exception as e:
        print(e)
        return
    save()
    print("Student został dodany")


commands = ["rate all", "send mails", "change grade", "add", "delete", "show", "exit"]

print(f'Prosze wpisywać komendy. Dostępne komendy to {commands}:')
command = input()
while command != "exit":
    if command not in commands:
        command = input("Podana komenda nie istnieje\n")
        continue
    if command == "rate all":
        calc_grads()
        command = input("Oceny studentów zostały przeliczone\n")
        continue
    if command == "change grade":
        change_grad()
        command = input()
        continue
    if command == "send mails":
        send_mails()
        command = input("Maile zostały wysłane\n")
        continue
    if command == "add":
        add_student()
        command = input()
        continue
    if command == "show":
        show_students()
        command = input()
        continue
    if command == "delete":
        delete_student()
        command = input()
        continue
