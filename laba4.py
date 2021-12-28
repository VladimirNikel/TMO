import random
from datetime import timedelta, datetime
from enum import Enum
from queue import PriorityQueue
from dataclasses import dataclass, field
import tracemalloc


__author__ = 'Nikel'


class EventStatus(Enum):
    new_s = 'new_select'
    new_d = 'new_get_data'
    blocked_s = 'select_blocked'
    blocked_d = 'data_blocked'
    processed_s = 'select_processed'
    processed_d = 'data_processed'


@dataclass(order=True)
class Event:
    occurrence_time: datetime = field(default=datetime.now())
    status: EventStatus = field(compare=False, default=EventStatus.new_s)


"""===============================================основные=переменные================================================"""
time_to_modeling = timedelta(hours=1)       # количество времени моделирования
count_handler_select = 1                    # количество обработчиков первого типа запросов
count_handler_get_data = 2                  # количество обработчиков второго типа запросов
min_processing_time = 15                    # минимальное время обработки запросов (обоих типов)
max_processing_time_order_select = 75       # максимальное время обработки первого типа запроса
max_processing_time_order_get_data = 150    # максимальное время обработки второго типа запроса
rps_select = 1700                           # количество поступающих запросов первого типа в секунду
rps_get_data = 1300                         # количество поступающих запросов второго типа в секунду
fork_handler_free_time = [30, 200]          # вилка (min-max) времени освобождения обработчика (обоих типов)
"""===============================================основные=переменные================================================"""


"""================================================функции-украшения================================================="""


def calculate_percentage(maxsize: int, count_first: int, count_second: int) -> int:
    """функция подсчета процента выполненной генерации"""
    return int(((maxsize - (count_first + count_second))/maxsize)*100)


def decomposition(input_number: int) -> str:
    """функция разбиения числа на разряды и приведения к строке"""
    return '{0:,}'.format(input_number).replace(',', ' ')


"""================================================функции-украшения================================================="""


def handler_s_occupation() -> bool:
    """
    функция занятия обработчика запросов первого типа "select"
    true - если успешно удалось занять одного обработчика
    false - если занять обработчик не удалось
    """
    global count_handler_select
    if count_handler_select > 0:
        count_handler_select -= 1
        return True
    return False


def handler_d_occupation() -> bool:
    """
    функция занятия обработчика запросов второго типа "get_data"
    true - если успешно удалось занять одного обработчика
    false - если занять обработчик не удалось
    """
    global count_handler_get_data
    if count_handler_get_data > 0:
        count_handler_get_data -= 1
        return True
    return False


def handler_s_freeing() -> bool:
    """
    функция освобождения обработчика запросов первого типа "select"
    true - если успешно удалось освободить одного обработчика
    false - если освободить обработчик не удалось
    """
    global count_handler_select
    if count_handler_select >= 0:
        count_handler_select += 1
        return True
    return False


def handler_d_freeing() -> bool:
    """
    функция освобождения обработчика запросов второго типа "get_data"
    true - если успешно удалось освободить одного обработчика
    false - если освободить обработчик не удалось
    """
    global count_handler_get_data
    if count_handler_get_data > 0:
        count_handler_get_data += 1
        return True
    return False


def generate_queue(count_first: int, count_second: int) -> PriorityQueue:
    """
    функция генерации очереди событий
    """
    gen_queue = PriorityQueue(count_first + count_second)           # инициализация очереди
    start_gen = datetime.now()
    print(f"Началась генерация очереди событий в {start_gen}\n")

    occurrence_time = start_gen                             # принимаем время старта генерации за точку отсчёта
    math_expect_s = (10 ** 3) // rps_select                 # считаем время между появлением запросов первого типа
    math_expect_d = (10 ** 3) // rps_get_data               # считаем время между появлением запросов второго типа

    while count_first > 0 or count_second > 0:
        # красивый вывод процента выполнения генерации очереди
        percentage = calculate_percentage(gen_queue.maxsize, count_first, count_second)
        if calculate_percentage(gen_queue.maxsize, count_first + 1, count_second) < percentage:
            print(f"\033[AГенерация очереди завершена на {percentage}%\t"
                  f"Осталось заполнить {decomposition(count_first+count_second)} элементов...\033[F")
        # красивый вывод процента выполнения генерации очереди завершился

        ev = Event()
        bool_tmp = random.choice([True, False])             # выбор типа события

        if bool_tmp and count_first != 0:
            count_first -= 1
            ev.status = EventStatus.new_s
            occurrence_time += timedelta(microseconds=random.randint(math_expect_s * 1000, (math_expect_s + 1) * 1000))

        elif not bool_tmp and count_second != 0:
            count_second -= 1
            ev.status = EventStatus.new_d
            occurrence_time += timedelta(microseconds=random.randint(math_expect_d * 1000, (math_expect_d + 1) * 1000))

        else:               # обход проблем с выбором того типа событий, количество которых уже превышено допустимое
            continue

        ev.occurrence_time = occurrence_time
        gen_queue.put(ev)
    print(f"Генерация очереди завершилась за {(datetime.now() - start_gen).seconds} секунд(-ы).\n")
    return gen_queue


def handle_select(time_start: datetime) -> Event:
    """
    обработчик события select
    """
    event = Event(status=EventStatus.processed_s, occurrence_time=time_start)
    if handler_s_occupation():
        event.occurrence_time = time_start + timedelta(microseconds=random.randint(
            min_processing_time, max_processing_time_order_select)
        )                           # добавляем время обработки события первого типа
    else:               # если доступных обработчиков нет
        event.status = EventStatus.blocked_s
    return event


def handle_get_data(time_start: datetime) -> Event:
    """
    обработчик события get_data
    """
    event = Event(status=EventStatus.processed_d, occurrence_time=time_start)
    if handler_d_occupation():
        event.occurrence_time = time_start + timedelta(microseconds=random.randint(
            min_processing_time, max_processing_time_order_get_data)
        )                           # добавляем время обработки события второго типа
    else:               # если доступных обработчиков нет
        event.status = EventStatus.blocked_d
    return event


def handle_processing_select(occurrence_time) -> datetime:
    """
    функция обработки события на освобождение обработчика первого типа событий с добавлением времени для освобождения
    """
    if handler_s_freeing():
        occurrence_time += timedelta(microseconds=random.randint(fork_handler_free_time[0], fork_handler_free_time[1]))
    return occurrence_time


def handle_processing_data(occurrence_time) -> datetime:
    """
    функция обработки события на освобождение обработчика второго типа событий с добавлением времени для освобождения
    """
    if handler_d_freeing():
        occurrence_time += timedelta(microseconds=random.randint(fork_handler_free_time[0], fork_handler_free_time[1]))
    return occurrence_time


if __name__ == "__main__":
    tracemalloc.start()
    size_select = rps_select * time_to_modeling.seconds
    size_data = rps_get_data * time_to_modeling.seconds
    count_lost_order = 0
    summary = f"!====Сводка====!\n\tОбработчиков заявок первого типа: {count_handler_select}\n" \
              f"\tОбработчиков заявок второго типа: {count_handler_get_data}\n"

    queue = generate_queue(count_first=size_select, count_second=size_data)     # генерация очереди

    start_time = datetime.now()
    print(f"Время старта моделирования: {start_time}")

    first_item = queue.get()    # получение первого элемента, для получения времени
    queue.put(first_item)       # возвращение элемента в список
    current_time = first_item.occurrence_time   # получение времени начала моделирования

    while not queue.empty():
        e = queue.get()

        if e.status == (EventStatus.blocked_s, EventStatus.blocked_d) or e.occurrence_time < current_time:
            count_lost_order += 1

        elif e.status == EventStatus.new_s:
            result = handle_select(e.occurrence_time)
            queue.put(result)
            current_time = result.occurrence_time

        elif e.status == EventStatus.new_d:
            result = handle_get_data(e.occurrence_time)
            queue.put(result)
            current_time = result.occurrence_time

        elif e.status == EventStatus.processed_s:
            current_time = handle_processing_select(e.occurrence_time)

        elif e.status == EventStatus.processed_d:
            current_time = handle_processing_data(e.occurrence_time)

    print(summary)
    print(f"\tПоступило {decomposition(size_select + size_data)} заявок.\n" 
          f"\tБыло обработано {decomposition(size_select + size_data - count_lost_order)} заявок.\n"          
          f"\tБыло потеряно {decomposition(count_lost_order)} заявок => Надежность системы с такими параметрами равна "
          f"{((1 - (count_lost_order / (size_select + size_data)))*100):.3f}%.")
    print(f"!====Сводка====!")

    _, peak = tracemalloc.get_traced_memory()
    print(f"\nМоделирование заняло {(datetime.now()-start_time).seconds} секунд(-ы).")
    print(f"Для выполнения моделирования потребовалось в пике памяти в {peak // 1024}KB, что равно {peak // 1024**2}MB")
    tracemalloc.stop()
