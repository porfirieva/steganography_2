import  contrast_mode
import lsb_mode

programm_type = int(input('Укажите режим работы программы:'
                          '\n1 - внедрение через секретный ключ, '
                          '\n2 - адаптация по локальному контрасту\n'))

if programm_type == 1:
    lsb_mode.main()
if programm_type == 2:
    contrast_mode.main()

    