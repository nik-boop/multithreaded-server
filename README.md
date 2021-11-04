# multithreaded-server


### Контрольные вопросы на «Создание простого многопоточного сервера»
1. Почему однопоточное приложение не может решить задачу одновременного подключения?
>*Ответ: Ввиду того, что однопоточное приложение будет ждать ответа только одного из пользователей, и в процесе ожидания будут игнорироватся сообщения от других пользователя. Приложение просто не в состоянии одновременно обработать несколько пользовательских запросов*
3. Чем поток отличается от процесса?
>*Ответ:Если рассматривать с точки зрения аппаратной части то процесс будет выполняться на каком-то отдельном процессоре, а поток будет выполняться в каком-то отдельном процессе,
>если с точки зрения доступа к весурсам как апаратным так и информационным то процесс это отдельный экземпляр программы выполняемый в отдельном адресном пространстве
> один процесс не может получить доступ к переменным и структурам данных другого,
> поток-же выполняется в процесе и в случае изменения данных в отдельном потоке 
> все измененные данные будут доступны другим потокам*
4. Как создать новый поток?
>*Ответ: Надо выделить определённый участок кода при помощи функции, после чего создать отдельный поток и запустить в нем функцию, библиотека threading (как вариант на Python)*
5. Как выделить участок кода так, чтобы он выполнялся в другом потоке?
>*Ответ:Выделить код как функцию и из выполняемого потока запустить новый для этой функциию \
> пример кода:\
>new_thread = threading.Thread(target=function, name='name_new_thread')*
6. В чем проблема потокобезопасности?
>*Ответ: Проблема в сложности предсказания момента переключения процесса между выполнением разных потоков,
> и ввиду чего может возникнуть проблема с одновременные попытки подключения разных потоков к одному и томеже месту (допустим, к терминалу),
> что может привести к наклажению отного потока на другой, например, первый поток выводит в терминал строчку 'Привет', а второй 'Пак дела?', в случае если произойдет непредвиденое переключение с первого потока на второй и обратно то в терминал будет выведено 'ПрКак дела?вет', в виду чего произойдет потеря данных*
7. Какие методы обеспечения потокобезопасности существуют?
>*Ответ: блокировка потока - блокирует переключение на другие потоки или переключение на конкретный поток до разблокировки, предотвращает подключение потоков к одному и томуже терминалу как в примере*



