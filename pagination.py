class Paginator:
    def __init__(self, records_lst, words_per_page):
        """
        Инициализация класса с именем файла и количеством слов на страницу.
        :param file_name: Имя файла для чтения.
        :param words_per_page: Количество слов на одной странице.
        """
        self.records_lst = records_lst
        self.pages = words_per_page
        self.sublists = {}  # Словарь для хранения страниц и соответствующих слов

    async def pagination(self):

        page_number = 1
        n = 0
        while n < len(self.records_lst):
            # Разделение списка слов на страницы
            self.sublists[page_number] = self.records_lst[n:n + self.pages]
            page_number += 1
            n += self.pages

    def get_page(self, page_number):
        """
        Возвращает список слов на указанной странице.
        :param page_number: Номер страницы для возврата.
        :return: Список слов на странице.
        """
        return self.sublists.get(page_number, [])

    def total_pages(self):
        """
        Возвращает общее количество страниц.
        :return: Количество страниц.
        """
        return len(self.sublists)


class TextPagination:
    def __init__(self, lst):
        self.lst = lst
        self.current_page = 1
        self.last_page = len(self.lst)

    async def mains(self):
        while True:
            # Показать текущую страницу
            await self.show_page()

            print("Выберите опцию:")
            print("1 - Следующая страница, 2 - Предыдущая страница, 3 - Перейти на первую страницу, 4 - Перейти на последнюю страницу, 0 - Завершить просмотр")

            # Получить выбор пользователя
            choice = input("Введите ваш выбор: ")
            if choice.isdigit():
                choice = int(choice)
                if choice == 1 and self.current_page < self.last_page:
                    self.current_page += 1
                elif choice == 2 and self.current_page > 1:
                    self.current_page -= 1
                elif choice == 3:
                    self.current_page = 1
                elif choice == 4:
                    self.current_page = self.last_page
                elif choice == 0:
                    print("Завершение программы...")
                    break
                else:
                    print("Некорректный ввод. Попробуйте снова.")
            else:
                print("Пожалуйста, введите числовое значение.")

    async def show_page(self):
        print(f"Страница {self.current_page} из {self.last_page}")
        for line in self.lst.get(self.current_page, []):
            print(line)
        print("\n")




