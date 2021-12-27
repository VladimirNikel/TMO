import random
from datetime import timedelta, datetime
from enum import Enum
from queue import PriorityQueue
from dataclasses import dataclass, field


class EventStatus(Enum):
    new_s = 'new_select'
    new_d = 'new_get_data'
    blocked_s = 'select_blocked'
    blocked_d = 'data_blocked'
    processed = 'processed'


@dataclass(order=True)
class Event:
    occurrence_time = datetime
    status: EventStatus = field(compare=False, default=EventStatus.new_s)


"""=================================================================================================================="""
time_to_modeling = timedelta(hours=1)
count_handler_select = 2
count_handler_get_data = 3
min_processing_time = 15
max_processing_time_order_select = 75
max_processing_time_order_get_data = 150
rps_select = 170
rps_get_data = 130
"""=================================================================================================================="""


def calculate_percentage(maxsize: int, count_first: int, count_second: int) -> int:
    return int(((maxsize - (count_first + count_second))/maxsize)*100)


def decomposition(input_number: int) -> str:
    return '{0:,}'.format(input_number).replace(',', ' ')


def generate_queue(count_first: int, count_second: int) -> PriorityQueue:
    """
    функция генерации очереди событий
    """
    gen_queue = PriorityQueue(count_first + count_second)
    start_gen = datetime.now()
    print(f"Началась генерация очереди событий в {start_gen}\n")

    occurrence_time = start_gen
    math_expect_s = (10 ** 3) // rps_select
    math_expect_d = (10 ** 3) // rps_get_data

    while count_first > 0 or count_second > 0:
        # красивый вывод процента выполнения генерации очереди
        percentage = calculate_percentage(gen_queue.maxsize, count_first, count_second)
        if calculate_percentage(gen_queue.maxsize, count_first + 1, count_second) < percentage:
            print(f"\033[AГенерация очереди завершена на {percentage}%\t"
                  f"Осталось заполнить {decomposition(count_first+count_second)} элементов...\033[F")
        # красивый вывод процента выполнения генерации очереди завершился

        ev = Event()
        bool_tmp = random.choice([True, False])

        if bool_tmp and count_first != 0:
            count_first -= 1
            ev.status = EventStatus.new_s
            occurrence_time += timedelta(microseconds=random.randint(math_expect_s * 1000, (math_expect_s + 1) * 1000))

        elif not bool_tmp and count_second != 0:
            count_second -= 1
            ev.status = EventStatus.new_d
            occurrence_time += timedelta(microseconds=random.randint(math_expect_d * 1000, (math_expect_d + 1) * 1000))

        else:
            continue

        ev.occurrence_time = occurrence_time
        gen_queue.put(ev)
    print(f"Генерация очереди завершилась за {(datetime.now() - start_gen).seconds} секунд(-ы).\n")
    return gen_queue


def handle_select(time_start: datetime) -> Event:
    """
    обработчик события select
    """
    global count_handler_select
    event = Event()
    event.status = EventStatus.processed
    event.occurrence_time = time_start
    if count_handler_select > 0:
        count_handler_select -= 1
        event.occurrence_time = time_start + timedelta(microseconds=random.randint(
            min_processing_time, max_processing_time_order_select)
        )
    else:
        event.status = EventStatus.blocked_s
    return event


def handle_get_data(time_start: datetime) -> Event:
    """
    обработчик события get_data
    """
    global count_handler_get_data
    event = Event()
    event.status = EventStatus.processed
    event.occurrence_time = time_start
    if count_handler_get_data > 0:
        count_handler_get_data -= 1
        event.occurrence_time = time_start + timedelta(microseconds=random.randint(
            min_processing_time, max_processing_time_order_get_data)
        )
    else:
        event.status = EventStatus.blocked_d
    return event


if __name__ == "__main__":
    size_select = rps_select * time_to_modeling.seconds
    size_data = rps_get_data * time_to_modeling.seconds
    queue = generate_queue(count_first=size_select, count_second=size_data)

    count_lost_order = 0

    start_time = datetime.now()
    print(f"Время старта моделирования: {start_time}")

    current_time = start_time
    while not queue.empty():
        e = queue.get()
        if e == EventStatus.new_s:
            result = handle_select(current_time)
            if result.status == EventStatus.processed:
                count_handler_select += 1
            else:
                count_lost_order += 1
            current_time = result.occurrence_time

        elif e == EventStatus.new_d:
            result = handle_get_data(current_time)
            if result.status == EventStatus.processed:
                count_handler_get_data += 1
            else:
                count_lost_order += 1
            current_time = result.occurrence_time

    print(f"!====Сводка====!")
    print(f"Обработчиков заявок первого типа: {count_handler_select}\n"
          f"Обработчиков заявок второго типа: {count_handler_get_data}\n")
    print(f"Было обработано {decomposition(size_select+size_data)} заявок.\n"          
          f"Было потеряно {decomposition(count_lost_order)} заявок => Надежность системы с такими параметрами равна "
          f"{((1-(count_lost_order/(size_select+size_data)))*100):.3f}%.\n\n"
          f"Моделирование заняло {(datetime.now()-start_time).seconds} секунд(-ы).")
    print(f"!====Сводка====!")
