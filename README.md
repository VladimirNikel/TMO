# Имитационное моделирование
## Четвёртая лабораторная работа по предмету "Теория массового обслуживания"

### Задание
> Необходимо написать приложение, позволяющее моделировать СМО (Систему Массового Обслуживания) без использования сторонних библиотек.
> 
> Желательно взять модель системы из дипломной работы - провести моделирование нагрузки на часть разрабатываемой системы для дипломной работы.

### Описание
Была реализована модель для оценивания надежности системы, обрабатывающей два типа запросов при следующих условиях:
- имеется несколько видов экземпляров обработчиков соответствующих запросов;
- количество экземпляров сервисов можно изменять из кода;
- можно изменять значения RPS ля каждого из типов запросов;
- можно изменять значения времён обработки заявок.

В [коде](https://github.com/VladimirNikel/TMO/blob/main/laba4.py) имеется достаточное количество комментариев к блокам и строкам кода.


### Пример запуска
Ниже приведен пример запуска программы моделирования на приведенных значениях переменных:

**(!) Обязательно обратите внимание на количество затрачиваемого времени и свободной памяти ОЗУ, для выполнения моделирования при тех параметрах, которые прописаны сейчас в коде!**
```bash
nikel@Aspire-A717-71G:~/dev/University/TMO$ python3 laba4.py 
Началась генерация очереди событий в 2021-12-28 05:42:04.030969
Генерация очереди завершена на 99%      Осталось заполнить 108 000 элементов......
Генерация очереди завершилась за 159 секунд(-ы).

Время старта моделирования: 2021-12-28 05:44:43.052101
!====Сводка====!
        Обработчиков заявок первого типа: 1
        Обработчиков заявок второго типа: 2

        Поступило 10 800 000 заявок.
        Было обработано 9 827 862 заявок.
        Было потеряно 972 138 заявок => Надежность системы с такими параметрами равна 90.999%.
!====Сводка====!

Моделирование заняло 519 секунд(-ы).
Для выполнения моделирования потребовалось в пике памяти в 2114587KB, что равно 2065MB
```

### Запуск
1. Необходимо установить Python (версии не менее 3.8) - `sudo apt-get install python`
2. Необходимо стянуть содержимое репозитория - `git clone git@github.com:VladimirNikel/TMO.git`
3. Совершить переход в папку с проектом - `cd TMO`
4. Запустить моделирование командой - `python3 laba4.py`
5. При необходимости внести изменения в переменные, согласно их описания
```python
27. """===============================================основные=переменные================================================"""
28. time_to_modeling = timedelta(hours=1)       # количество времени моделирования
29. count_handler_select = 1                    # количество обработчиков первого типа запросов
30. count_handler_get_data = 2                  # количество обработчиков второго типа запросов
31. min_processing_time = 15                    # минимальное время обработки запросов (обоих типов)
32. max_processing_time_order_select = 75       # максимальное время обработки первого типа запроса
33. max_processing_time_order_get_data = 150    # максимальное время обработки второго типа запроса
34. rps_select = 1700                           # количество поступающих запросов первого типа в секунду
35. rps_get_data = 1300                         # количество поступающих запросов второго типа в секунду
36. fork_handler_free_time = [30, 200]          # вилка (min-max) времени освобождения обработчика (обоих типов)
37. """===============================================основные=переменные================================================"""
```